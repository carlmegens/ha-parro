"""In-memory iCalendar subscriptions using the same guarded transport as photos."""

import time
from datetime import datetime, timedelta
from itertools import islice

from homeassistant.components.calendar import CalendarEvent
from homeassistant.util import dt as dt_util
from ical.calendar_stream import IcsCalendarStream
from ical.event import EventStatus

from .api import ParroError
from .feed import ParroFeed, _plain_text

CALENDAR_TTL = 1800
MAX_CALENDAR_BYTES = 2 * 1024 * 1024
MAX_EVENTS = 5000
MAX_WINDOW = timedelta(days=366)


class ParroCalendarError(ParroError):
    """A fixed error message: subscription links and ICS content are private."""

    def __init__(self):
        super().__init__("The Parro calendar is unavailable")


def _parse(data: bytes):
    """Parse in an executor, with no provider text in public exceptions."""
    try:
        calendar = IcsCalendarStream.calendar_from_ics(data.decode("utf-8-sig"))
        if len(calendar.events) > MAX_EVENTS:
            raise ParroCalendarError()
        return calendar
    except Exception:
        raise ParroCalendarError() from None


def _events(calendars, start: datetime, end: datetime) -> list[CalendarEvent]:
    """Expand recurrences off the event loop and keep exclusive end boundaries."""
    result = {}
    try:
        for calendar in calendars:
            events = calendar.timeline_tz(dt_util.DEFAULT_TIME_ZONE).overlapping(start, end)
            for index, event in enumerate(islice(events, MAX_EVENTS + 1)):
                if index == MAX_EVENTS:
                    raise ParroCalendarError()
                if event.status == EventStatus.CANCELLED:
                    continue
                value = CalendarEvent(
                    summary=_plain_text(event.summary or "", 1000),
                    start=dt_util.as_local(event.start)
                    if isinstance(event.start, datetime)
                    else event.start,
                    end=dt_util.as_local(event.end)
                    if isinstance(event.end, datetime)
                    else event.end,
                    description=_plain_text(event.description or ""),
                    location=_plain_text(event.location or "", 2000),
                )
                if value.end_datetime_local <= start or value.start_datetime_local >= end:
                    continue
                # Group subscriptions can contain the same appointment. Preserve
                # genuinely different appointments at the same time.
                key = (
                    event.uid,
                    value.start,
                    value.end,
                    value.summary,
                    value.description,
                    value.location,
                )
                result[key] = value
                if len(result) > MAX_EVENTS:
                    raise ParroCalendarError()
        return sorted(result.values(), key=lambda e: e.start_datetime_local)
    except Exception:
        raise ParroCalendarError() from None


class ParroCalendarFeed(ParroFeed):
    """One atomic account cache; neither subscription URLs nor ICS go into HA state."""

    download_accept = "text/calendar,text/plain;q=0.9"
    download_limit = MAX_CALENDAR_BYTES

    def __init__(self, hass, api):
        super().__init__(hass, api)
        self._calendars = None
        self._updated = 0.0

    def _clear_data(self):
        super()._clear_data()
        self._calendars = None
        self._updated = 0.0

    async def async_events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        if (
            start.tzinfo is None
            or end.tzinfo is None
            or not timedelta(0) < end - start <= MAX_WINDOW
        ):
            raise ParroCalendarError()
        async with self._feed_lock:
            self._require_open()
            if self._calendars is None or time.monotonic() - self._updated >= CALENDAR_TTL:
                # Ask for one beyond our supported maximum so we never silently
                # present a partial calendar for an unusually large account.
                urls = await self.api.async_get_calendar_urls(limit=11)
                if len(urls) > 10:
                    raise ParroCalendarError()
                calendars = []
                total = 0
                for url in dict.fromkeys(urls):
                    if url.startswith("webcal://"):
                        url = "https://" + url[len("webcal://") :]
                    data = await self._download(url)
                    total += len(data)
                    if total > 8 * 1024 * 1024:
                        raise ParroCalendarError()
                    calendars.append(await self.hass.async_add_executor_job(_parse, data))
                self._require_open()
                self._calendars = calendars
                self._updated = time.monotonic()
            result = await self.hass.async_add_executor_job(_events, self._calendars, start, end)
            self._require_open()
            return result
