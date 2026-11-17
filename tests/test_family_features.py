"""Synthetic tests for opt-in native surfaces, notification baselines and replies."""

from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.util import dt as dt_util

from custom_components.parro.api import ParroError
from custom_components.parro.coordinator import ParroCoordinator
from custom_components.parro.models import ParroChild, ParroEvent, ParroGroup
from custom_components.parro.replies import clean_message


def link(value):
    return [{"rel": "self", "id": value}]


def announcement(value, at):
    return {"links": link(value), "createdAt": at.isoformat(), "contents": "Secret text"}


def room(value, at, sender=98):
    return {
        "links": link(value),
        "type": "SINGLE",
        "repliesEnabled": True,
        "lastMessage": {"createdAt": at.isoformat(), "identity": {"links": link(sender)}},
    }


def coordinator(hass, entry, api, **options):
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(entry, options=options)
    return ParroCoordinator(hass, entry, api)


async def test_default_never_fetches_optional_content(hass, config_entry, mock_api):
    c = coordinator(hass, config_entry, mock_api)
    await c._async_update_data()
    mock_api.async_get_activity.assert_not_called()
    mock_api.async_get_family.assert_not_called()
    assert c.family.children == {}
    await c.async_shutdown()


async def test_baseline_new_activity_backfill_and_self_messages(hass, config_entry, mock_api):
    now = dt_util.utcnow()
    c = coordinator(hass, config_entry, mock_api, activity_events=True)
    mock_api.async_get_activity.return_value = (
        [announcement(1, now - timedelta(days=1))],
        [],
        {99},
    )
    await c.family.async_update()
    assert c.family.activity == []
    future = now + timedelta(minutes=10)
    with patch("custom_components.parro.family.dt_util.utcnow", return_value=future):
        mock_api.async_get_activity.return_value = (
            [
                announcement(1, now - timedelta(days=1)),
                announcement(2, future),
                announcement(3, now - timedelta(days=3)),
            ],
            [room(4, future), room(5, future, 99)],
            {99},
        )
        await c.family.async_update()
        assert [(a[0], a[1]) for a in c.family.activity] == [
            ("announcement", "2"),
            ("message", "4"),
        ]
        assert all(len(a) == 3 for a in c.family.activity)
        await c.family.async_update()
        assert c.family.activity == []
    await c.async_shutdown()


async def test_child_mapping_and_calendar_cache(hass, config_entry, mock_api):
    c = coordinator(hass, config_entry, mock_api, child_entities=True)
    mock_api.async_get_family.return_value = ({"1": ParroChild(1, "Synthetic", None)}, {})
    await c.family.async_update()
    start = dt_util.utcnow()
    end = start + timedelta(days=2)
    mock_api.async_get_child_events.return_value = [
        ParroEvent(3, "Own appointment", "", start, end, False, (), (1,)),
        ParroEvent(4, "Other child", "", start, end, False, (), (2,)),
        ParroEvent(5, "No explicit child", "", start, end, False, (), ()),
    ]
    events = await c.family.async_events("1", start, end)
    assert [e.summary for e in events] == ["Own appointment"]
    await c.family.async_events("1", start, end)
    mock_api.async_get_child_events.assert_awaited_once()
    mock_api.async_get_family.return_value = ({}, {})
    await c.family.async_update()
    with pytest.raises(ParroError):
        await c.family.async_events("1", start, end)
    await c.async_shutdown()


async def test_native_entities_load_and_images_withhold_revoked_data(hass, config_entry, mock_api):
    from homeassistant.setup import async_setup_component

    mock_api.async_get_family.return_value = (
        {"1": ParroChild(1, "Synthetic", "https://media.parro.com/test.jpg")},
        {"10": ParroGroup(10, "Group A", "", True, 2026, 0, (1,), None, None)},
    )
    mock_api.async_get_activity.return_value = ([], [], {99})
    mock_api.async_get_child_events.return_value = []
    config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        config_entry,
        options={"child_entities": True, "photo_entities": True, "activity_events": True},
    )
    with patch("custom_components.parro.ParroApi", return_value=mock_api):
        assert await async_setup_component(hass, "parro", {})
        await hass.async_block_till_done()
    states = hass.states.async_all()
    assert any(s.domain == "image" and "profile" in s.entity_id for s in states)
    assert any(s.domain == "calendar" and "synthetic" in s.entity_id for s in states)
    assert any(s.state == "Group A" for s in states)
    assert len([s for s in states if s.domain == "event"]) == 2
    from custom_components.parro.image import ParroProfileImage

    c = config_entry.runtime_data
    photo = ParroProfileImage(c, config_entry, "1")
    c.feed.async_get_image = AsyncMock(return_value=(b"sanitized", "image/jpeg"))
    assert await photo.async_image() == b"sanitized"
    await c.async_invalidate_auth()
    assert await photo.async_image() is None
    assert not photo.available
    assert await hass.config_entries.async_unload(config_entry.entry_id)


async def test_event_entities_emit_minimal_payload_once(hass, config_entry, mock_api):
    from custom_components.parro.event import ParroActivityEvent

    c = coordinator(hass, config_entry, mock_api, activity_events=True)
    c.family.available = True
    c.last_update_success = True
    entity = ParroActivityEvent(c, config_entry, "message")
    entity.hass = hass
    entity.entity_id = "event.synthetic"
    entity.async_write_ha_state = lambda: None
    received = []
    unsub = hass.bus.async_listen("parro_new_message", lambda event: received.append(event.data))
    c.family.activity = [("message", "42", dt_util.utcnow())]
    entity._handle_coordinator_update()
    entity._handle_coordinator_update()
    await hass.async_block_till_done()
    assert len(received) == 1
    assert set(received[0]) == {"config_entry_id", "item_id", "published_at"}
    unsub()
    await c.async_shutdown()


@pytest.mark.parametrize(
    "options", [{}, {"allow_replies": True}, {"allow_replies": False, "reply_rooms": ["42"]}]
)
async def test_reply_opt_in_and_room_allowlist(hass, config_entry, mock_api, options):
    c = coordinator(hass, config_entry, mock_api, **options)
    with pytest.raises(ServiceValidationError):
        await c.replies.async_send("42", "Synthetic test message")
    mock_api.async_send_reply.assert_not_called()
    await c.async_shutdown()


async def test_uncertain_reply_persists_attempt_and_never_retries(hass, config_entry, mock_api):
    c = coordinator(hass, config_entry, mock_api, allow_replies=True, reply_rooms=["42"])
    mock_api.async_send_reply.side_effect = ParroError("private upstream detail")
    with pytest.raises(HomeAssistantError, match="Delivery could not be confirmed"):
        await c.replies.async_send("42", "Synthetic test message")
    mock_api.async_send_reply.assert_awaited_once()
    from custom_components.parro.replies import ReplyGuard

    c.replies = ReplyGuard(c)  # Simulate reload: persisted attempts still apply.
    with pytest.raises(ServiceValidationError):
        await c.replies.async_send("42", "Synthetic test message")
    stored = await c.replies.store.async_load()
    assert "Synthetic test message" not in str(stored)
    assert len(stored["attempts"]) == 1
    await c.async_shutdown()


async def test_store_failure_prevents_delivery(hass, config_entry, mock_api):
    c = coordinator(hass, config_entry, mock_api, allow_replies=True, reply_rooms=["42"])
    with patch.object(c.replies.store, "async_save", side_effect=OSError):
        with pytest.raises(OSError):
            await c.replies.async_send("42", "Synthetic")
    mock_api.async_send_reply.assert_not_called()
    await c.async_shutdown()


@pytest.mark.parametrize("text", ["", "  ", "a" * 1001, "\n".join(["line"] * 21), "a\x00b", None])
def test_reply_text_bounds(text):
    with pytest.raises(ServiceValidationError):
        clean_message(text)


def test_plain_text_reply_preserves_normal_punctuation():
    assert clean_message("  Bedankt, tot morgen! 😊  ") == "Bedankt, tot morgen! 😊"


async def test_reply_service_denies_read_only_users(
    hass, config_entry, mock_api, hass_read_only_user
):
    from homeassistant.config_entries import ConfigEntryState
    from homeassistant.core import Context
    from homeassistant.exceptions import Unauthorized

    from custom_components.parro.services import async_register_services

    c = coordinator(hass, config_entry, mock_api, allow_replies=True, reply_rooms=["42"])
    config_entry.runtime_data = c
    config_entry.mock_state(hass, ConfigEntryState.LOADED)
    async_register_services(hass)
    with pytest.raises(Unauthorized):
        await hass.services.async_call(
            "parro",
            "send_reply",
            {"config_entry_id": config_entry.entry_id, "chatroom_id": "42", "message": "Synthetic"},
            blocking=True,
            context=Context(user_id=hass_read_only_user.id),
        )
    mock_api.async_send_reply.assert_not_called()
    await c.async_shutdown()


async def test_inflight_photo_is_withheld_when_option_revoked(hass, config_entry, mock_api):
    from custom_components.parro.image import ParroProfileImage

    c = coordinator(hass, config_entry, mock_api, child_entities=True, photo_entities=True)
    c.family.children = {"1": ParroChild(1, "Synthetic", "https://media.parro.com/test.jpg")}
    c.family.available = True
    photo = ParroProfileImage(c, config_entry, "1")

    async def download(_):
        hass.config_entries.async_update_entry(config_entry, options={"photo_entities": False})
        return b"private bytes", "image/jpeg"

    c.feed.async_get_image = download
    assert await photo.async_image() is None
    await c.async_shutdown()


async def test_reply_limits_and_duplicate_survive_reload(hass, config_entry, mock_api):
    c = coordinator(hass, config_entry, mock_api, allow_replies=True, reply_rooms=["42"])
    now = dt_util.utcnow()
    with patch("custom_components.parro.replies.dt_util.utcnow", return_value=now):
        await c.replies.async_send("42", "One")
    with patch(
        "custom_components.parro.replies.dt_util.utcnow", return_value=now + timedelta(minutes=2)
    ):
        with pytest.raises(ServiceValidationError, match="recently attempted"):
            await c.replies.async_send("42", "One")
    for i in range(4):
        with patch(
            "custom_components.parro.replies.dt_util.utcnow",
            return_value=now + timedelta(minutes=3 + i),
        ):
            await c.replies.async_send("42", f"Other {i}")
    with patch(
        "custom_components.parro.replies.dt_util.utcnow", return_value=now + timedelta(minutes=9)
    ):
        with pytest.raises(ServiceValidationError, match="limit"):
            await c.replies.async_send("42", "Sixth")
    assert mock_api.async_send_reply.await_count == 5
    await c.async_shutdown()


def test_calendar_merges_same_occurrence_links_without_inventing_child_dates():
    from custom_components.parro.models import events_from_rows

    def row(child, day):
        return {
            "calendarItem": {
                "links": link(10),
                "title": "Synthetic holiday",
                "startDate": f"2026-11-{day}T00:00:00+01:00",
                "endDate": f"2026-11-{day}T00:00:00+01:00",
            },
            "children": [{"child": {"roleId": child}}],
        }

    events = events_from_rows([row(1, 20), row(2, 20), row(2, 22)])
    assert len(events) == 2
    assert events[0].child_ids == (1, 2)
    assert events[1].child_ids == (2,)
    assert events[0].start.isoformat() == "2026-11-20"
    assert events[0].end.isoformat() == "2026-11-21"


async def test_optional_failure_hides_previous_photos(hass, config_entry, mock_api):
    from homeassistant.helpers.update_coordinator import UpdateFailed

    from custom_components.parro.api import ParroConnectionError

    c = coordinator(hass, config_entry, mock_api, photo_entities=True)
    c.family.photos = ["https://media.parro.com/test.jpg"]
    c.family.available = True
    mock_api.async_get_activity.side_effect = ParroConnectionError()
    with pytest.raises(UpdateFailed):
        await c._async_update_data()
    assert not c.family.available
    await c.async_shutdown()
