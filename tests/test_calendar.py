"""Native calendar behavior using synthetic ICS, never school data."""

import asyncio
from datetime import UTC, date, datetime, timedelta
from unittest.mock import AsyncMock, patch
from zoneinfo import ZoneInfo

import pytest
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.parro.api import ParroAuthError, ParroConnectionError, ParroError
from custom_components.parro.calendar_feed import (
    ParroCalendarError,
    ParroCalendarFeed,
    _events,
    _parse,
)


@pytest.fixture(autouse=True)
def calendar_timezone(hass):
    dt_util.set_default_time_zone(ZoneInfo("Europe/Amsterdam"))


START = datetime(2026, 10, 20, tzinfo=UTC)
END = datetime(2026, 11, 1, tzinfo=UTC)
URL = "https://calendar.example.invalid/synthetic-private-subscription"


def ics(*events):
    return (
        "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Synthetic//EN\r\n"
        + "\r\n".join(
            "BEGIN:VEVENT\r\nUID:"
            + str(index)
            + "\r\nDTSTAMP:20260101T000000Z\r\n"
            + event
            + "\r\nEND:VEVENT"
            for index, event in enumerate(events)
        )
        + "\r\nEND:VCALENDAR\r\n"
    ).encode()


DATA = ics("DTSTART;VALUE=DATE:20261024\r\nDTEND;VALUE=DATE:20261026\r\nSUMMARY:School holiday")


def test_all_day_overlap_and_exclusive_end():
    calendar = _parse(DATA)
    result = _events([calendar, calendar], START, END)
    assert len(result) == 1
    assert result[0].start == date(2026, 10, 24)
    assert result[0].end == date(2026, 10, 26)
    assert _events([calendar], datetime(2026, 10, 25, tzinfo=UTC), END)
    assert not _events([calendar], datetime(2026, 10, 26, tzinfo=UTC), END)
    assert result[0].uid is None


def test_recurrence_across_dst_exclusions_and_cancelled():
    calendar = _parse(
        ics(
            "DTSTART;TZID=Europe/Amsterdam:20261023T090000\r\nDTEND;TZID=Europe/Amsterdam:20261023T100000\r\nRRULE:FREQ=DAILY;COUNT=4\r\nEXDATE;TZID=Europe/Amsterdam:20261024T090000\r\nSUMMARY:<b>School</b>",
            "DTSTART:20261024T080000Z\r\nDTEND:20261024T090000Z\r\nSTATUS:CANCELLED\r\nSUMMARY:Cancelled",
        )
    )
    result = _events([calendar], START, END)
    local = [e.start.astimezone(ZoneInfo("Europe/Amsterdam")) for e in result]
    assert [e.day for e in local] == [23, 25, 26]
    assert [e.hour for e in local] == [9, 9, 9]
    assert [e.utcoffset() for e in local] == [
        timedelta(hours=2),
        timedelta(hours=1),
        timedelta(hours=1),
    ]
    assert all(e.summary == "School" for e in result)


def test_recurrence_override_and_floating_time():
    body = ics(
        "DTSTART:20261023T090000\r\nDTEND:20261023T100000\r\nRRULE:FREQ=DAILY;COUNT=2\r\nSUMMARY:Original",
        "RECURRENCE-ID:20261024T090000\r\nDTSTART:20261024T120000\r\nDTEND:20261024T130000\r\nSUMMARY:Moved",
    ).replace(b"UID:1", b"UID:0")
    result = _events([_parse(body)], START, END)
    assert [e.summary for e in result] == ["Original", "Moved"]
    assert result[1].start.hour == 12
    assert result[1].start.tzinfo == dt_util.DEFAULT_TIME_ZONE


@pytest.mark.parametrize("body", [b"private-provider-error", b"\xff", b"BEGIN:VCALENDAR\ninvalid"])
def test_invalid_content_has_safe_error(body):
    with pytest.raises(ParroCalendarError, match="^The Parro calendar is unavailable$"):
        _parse(body)


async def test_cache_refresh_dedupe_and_webcal(hass, mock_api):
    feed = ParroCalendarFeed(hass, mock_api)
    mock_api.async_get_calendar_urls.return_value = [URL.replace("https:", "webcal:")] * 2
    with patch.object(feed, "_download", AsyncMock(return_value=DATA)) as download:
        assert len(await feed.async_events(START, END)) == 1
        assert len(await feed.async_events(START, END)) == 1
        download.assert_awaited_once_with(URL)
        feed._updated -= 1801
        await feed.async_events(START, END)
        assert download.await_count == 2
    await feed.async_close()
    assert feed._calendars is None
    with pytest.raises(ParroError):
        await feed.async_events(START, END)


async def test_failed_refresh_does_not_serve_stale_or_partial_calendar(hass, mock_api):
    feed = ParroCalendarFeed(hass, mock_api)
    mock_api.async_get_calendar_urls.return_value = [URL]
    with patch.object(feed, "_download", AsyncMock(return_value=DATA)) as download:
        await feed.async_events(START, END)
        feed._updated -= 1801
        mock_api.async_get_calendar_urls.return_value = [URL, URL + "2"]
        download.side_effect = [DATA, ParroConnectionError("synthetic")]
        with pytest.raises(ParroError):
            await feed.async_events(START, END)
        download.side_effect = None
        download.return_value = ics()
        assert await feed.async_events(START, END) == []
    await feed.async_close()


async def test_close_during_fetch_cannot_repopulate_cache(hass, mock_api):
    feed = ParroCalendarFeed(hass, mock_api)
    mock_api.async_get_calendar_urls.return_value = [URL]
    entered, release = asyncio.Event(), asyncio.Event()

    async def download(_url):
        entered.set()
        await release.wait()
        return DATA

    with patch.object(feed, "_download", download):
        read = asyncio.create_task(feed.async_events(START, END))
        await entered.wait()
        close = asyncio.create_task(feed.async_close())
        await asyncio.sleep(0)
        release.set()
        with pytest.raises(ParroError):
            await read
        await close
        assert feed._calendars is None


@pytest.mark.parametrize(
    "url",
    [
        "http://calendar.example.invalid/a",
        "https://127.0.0.1/a",
        "https://localhost/a",
        "https://user:pass@calendar.example.invalid/a",
    ],
)
async def test_unsafe_subscriptions_rejected(hass, mock_api, url):
    feed = ParroCalendarFeed(hass, mock_api)
    mock_api.async_get_calendar_urls.return_value = [url]
    with pytest.raises(ParroError):
        await feed.async_events(START, END)
    assert feed._session is None
    await feed.async_close()


async def test_bounds_and_account_feed_limit(hass, mock_api):
    feed = ParroCalendarFeed(hass, mock_api)
    for start, end in [
        (START, START),
        (END, START),
        (START, START + timedelta(days=367)),
        (START.replace(tzinfo=None), END),
    ]:
        with pytest.raises(ParroCalendarError):
            await feed.async_events(start, end)
    mock_api.async_get_calendar_urls.return_value = [URL + str(i) for i in range(11)]
    with pytest.raises(ParroCalendarError):
        await feed.async_events(START, END)
    await feed.async_close()


async def test_native_calendar_service_device_and_auth_failure(
    hass, config_entry, mock_api, freezer
):
    freezer.move_to(START)
    config_entry.add_to_hass(hass)
    mock_api.async_get_calendar_urls.return_value = [URL]
    with (
        patch("custom_components.parro.ParroApi", return_value=mock_api),
        patch.object(ParroCalendarFeed, "_download", AsyncMock(return_value=DATA)),
    ):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()
        registry = er.async_get(hass)
        entity_id = registry.async_get_entity_id(
            "calendar", "parro", f"{config_entry.entry_id}_school_calendar"
        )
        state = hass.states.get(entity_id)
        assert state.state == "off"
        assert state.attributes["message"] == "School holiday"
        assert state.attributes["parro_config_entry_id"] == config_entry.entry_id
        assert URL not in str(state.as_dict())
        assert registry.async_get(entity_id).device_id
        response = await hass.services.async_call(
            "calendar",
            "get_events",
            {
                "entity_id": entity_id,
                "start_date_time": START.isoformat(),
                "end_date_time": END.isoformat(),
            },
            blocking=True,
            return_response=True,
        )
        assert len(response[entity_id]["events"]) == 1
        config_entry.runtime_data.calendar_feed._updated -= 1801
        mock_api.async_get_calendar_urls.side_effect = ParroAuthError("synthetic private detail")
        with pytest.raises(HomeAssistantError, match="Parro sign-in has expired"):
            await hass.services.async_call(
                "calendar",
                "get_events",
                {
                    "entity_id": entity_id,
                    "start_date_time": START.isoformat(),
                    "end_date_time": END.isoformat(),
                },
                blocking=True,
                return_response=True,
            )
        assert hass.states.get(entity_id).state == "unavailable"
        assert "message" not in hass.states.get(entity_id).attributes
        assert config_entry.runtime_data.content_auth_failed
        assert config_entry.runtime_data.calendar_feed._closed
        assert config_entry.runtime_data.feed._closed
        assert any(
            f["context"]["source"] == "reauth" for f in hass.config_entries.flow.async_progress()
        )
        assert await hass.config_entries.async_unload(config_entry.entry_id)


async def test_calendar_failure_does_not_break_counters(hass, config_entry, mock_api):
    config_entry.add_to_hass(hass)
    mock_api.async_get_calendar_urls.side_effect = ParroConnectionError("synthetic")
    with patch("custom_components.parro.ParroApi", return_value=mock_api):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()
    states = hass.states.async_all()
    assert next(s for s in states if s.domain == "calendar").state == "unavailable"
    assert sum(s.state == "unavailable" for s in states) == 2


async def test_next_appointment_time_details_rollover_and_shared_cache(
    hass, config_entry, mock_api, freezer
):
    from pytest_homeassistant_custom_component.common import async_fire_time_changed

    freezer.move_to("2026-10-23T06:00:00Z")
    data = ics(
        "DTSTART:20261023T070000Z\r\nDTEND:20261023T080000Z\r\nSUMMARY:First\r\nLOCATION:School",
        "DTSTART;VALUE=DATE:20261024\r\nDTEND;VALUE=DATE:20261025\r\nSUMMARY:Second",
    )
    config_entry.add_to_hass(hass)
    mock_api.async_get_calendar_urls.return_value = [URL]
    with (
        patch("custom_components.parro.ParroApi", return_value=mock_api),
        patch.object(ParroCalendarFeed, "_download", AsyncMock(return_value=data)) as download,
    ):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()
        registry = er.async_get(hass)
        entity_id = registry.async_get_entity_id(
            "sensor", "parro", f"{config_entry.entry_id}_next_appointment"
        )
        calendar_id = registry.async_get_entity_id(
            "calendar", "parro", f"{config_entry.entry_id}_school_calendar"
        )
        state = hass.states.get(entity_id)
        assert dt_util.parse_datetime(state.state) == datetime(2026, 10, 23, 7, tzinfo=UTC)
        assert state.attributes["summary"] == "First"
        assert state.attributes["custom_ui_more_info"] == "more-info-parro-calendar"
        assert state.attributes["parro_calendar_entity_id"] == calendar_id
        registry.async_update_entity(calendar_id, new_entity_id="calendar.renamed_school")
        await hass.async_block_till_done()
        calendar_id = "calendar.renamed_school"
        state = hass.states.get(entity_id)
        assert state.attributes["parro_calendar_entity_id"] == calendar_id
        assert state.attributes["location"] == "School"
        assert state.attributes["all_day"] is False
        assert registry.async_get(entity_id).device_id == registry.async_get(calendar_id).device_id
        assert URL not in str(state.as_dict())
        download.assert_awaited_once()
        # A started appointment no longer counts as the next one. The minute
        # listener updates the display without needing a calendar download.
        freezer.move_to("2026-10-23T07:01:00Z")
        async_fire_time_changed(hass)
        await hass.async_block_till_done()
        state = hass.states.get(entity_id)
        assert state.attributes["summary"] == "Second"
        assert state.attributes["all_day"] is True
        assert dt_util.parse_datetime(state.state) == datetime(2026, 10, 23, 22, tzinfo=UTC)
        await config_entry.runtime_data.async_invalidate_auth()
        assert hass.states.get(entity_id).state == "unavailable"
        assert "summary" not in hass.states.get(entity_id).attributes
        assert await hass.config_entries.async_unload(config_entry.entry_id)


async def test_next_appointment_empty_and_recovery(hass, config_entry, mock_api):
    config_entry.add_to_hass(hass)
    with patch("custom_components.parro.ParroApi", return_value=mock_api):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()
    entity_id = er.async_get(hass).async_get_entity_id(
        "sensor", "parro", f"{config_entry.entry_id}_next_appointment"
    )
    entity = hass.data["sensor"].get_entity(entity_id)
    assert hass.states.get(entity_id).state == "unknown"
    assert hass.states.get(entity_id).attributes["summary"] is None
    with patch.object(
        config_entry.runtime_data,
        "async_get_calendar_events",
        side_effect=HomeAssistantError("unavailable"),
    ):
        await entity.async_update()
        entity.async_write_ha_state()
    assert hass.states.get(entity_id).state == "unavailable"
    await entity.async_update()
    entity.async_write_ha_state()
    assert hass.states.get(entity_id).state == "unknown"
