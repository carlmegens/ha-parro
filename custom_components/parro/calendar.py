"""Read-only school appointments in Home Assistant's native calendar."""

import logging
from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

from .api import ParroAuthError, ParroError
from .entity import ParroEntity
from .family import ParroChildEntity, async_add_children

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=15)
PARALLEL_UPDATES = 1


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_children(entry, async_add_entities, ParroChildCalendar, update_before_add=True)
    async_add_entities([ParroCalendar(entry.runtime_data, entry)], update_before_add=True)


class ParroCalendar(ParroEntity, CalendarEntity):
    """A single account calendar, attached to the existing Parro device."""

    _unrecorded_attributes = frozenset(
        {"message", "description", "location", "start_time", "end_time"}
    )
    _attr_should_poll = True

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "school_calendar")
        self._entry = entry
        self._attr_extra_state_attributes = {"parro_config_entry_id": entry.entry_id}
        self._events: list[CalendarEvent] = []
        self._calendar_available = False

    @property
    def available(self) -> bool:
        return self._calendar_available and not self.coordinator.content_auth_failed

    @property
    def event(self) -> CalendarEvent | None:
        if not self.available:
            return None
        now = dt_util.now()
        return next((event for event in self._events if event.end_datetime_local > now), None)

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        return await self.coordinator.async_get_calendar_events(start_date, end_date)

    async def async_update(self) -> None:
        now = dt_util.now()
        try:
            self._events = await self.async_get_events(self.hass, now, now + timedelta(days=365))
        except HomeAssistantError:
            if self._calendar_available:
                _LOGGER.warning("The Parro calendar could not be refreshed")
            self._events = []
            self._calendar_available = False
        else:
            self._calendar_available = True


class ParroChildCalendar(ParroChildEntity, CalendarEntity):
    """Only appointments explicitly linked by Parro to this child."""

    _attr_should_poll = True

    def __init__(self, coordinator, entry, child_id):
        super().__init__(coordinator, entry, child_id, "child_calendar")
        self._events = []
        self._calendar_available = False

    @property
    def available(self):
        return super().available and self._calendar_available

    @property
    def event(self):
        if not self.available:
            return None
        return next((e for e in self._events if e.end_datetime_local > dt_util.now()), None)

    async def async_get_events(self, hass, start_date, end_date):
        try:
            return await self.coordinator.family.async_events(self.child_id, start_date, end_date)
        except ParroAuthError:
            await self.coordinator.async_invalidate_auth()
            self.coordinator.config_entry.async_start_reauth(hass)
            raise HomeAssistantError("Parro sign-in has expired") from None
        except ParroError:
            raise HomeAssistantError("The child calendar is unavailable") from None

    async def async_update(self):
        now = dt_util.now().replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            self._events = await self.async_get_events(self.hass, now, now + timedelta(days=365))
            self._calendar_available = True
        except HomeAssistantError:
            self._events = []
            self._calendar_available = False
