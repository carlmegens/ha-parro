"""Compact counters and the last successful summary synchronization."""

from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from .coordinator import ParroCoordinator
from .entity import ParroEntity

SCAN_INTERVAL = timedelta(minutes=15)
PARALLEL_UPDATES = 1

SENSORS = (
    SensorEntityDescription(key="children_count", translation_key="children_count"),
    SensorEntityDescription(key="groups_count", translation_key="groups_count"),
    SensorEntityDescription(key="unread_announcements", translation_key="unread_announcements"),
    SensorEntityDescription(key="unread_chatrooms", translation_key="unread_chatrooms"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[ParroCoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add compact counters and the human-readable next appointment."""
    async_add_entities(
        [ParroCountSensor(entry.runtime_data, entry, description) for description in SENSORS]
        + [ParroLastSuccessSensor(entry.runtime_data, entry)]
    )
    async_add_entities(
        [ParroNextAppointmentSensor(entry.runtime_data, entry)], update_before_add=True
    )


class ParroCountSensor(ParroEntity, SensorEntity):
    """Represent an available count; missing data remains unknown."""

    def __init__(
        self,
        coordinator: ParroCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, entry, description.key)
        self.entity_description = description
        source = {
            "unread_announcements": "announcements",
            "unread_chatrooms": "messages",
        }.get(description.key)
        if source:
            # HA's existing more-info hook receives only routing metadata. The
            # component obtains private content through the authenticated API.
            self._attr_extra_state_attributes = {
                "custom_ui_more_info": "more-info-parro",
                "parro_config_entry_id": entry.entry_id,
                "parro_source": source,
            }

    @property
    def native_value(self) -> int | None:
        """Return only a count, never raw response data."""
        value = (self.coordinator.data or {}).get(self.entity_description.key)
        return value if type(value) is int and value >= 0 else None


class ParroLastSuccessSensor(ParroEntity, SensorEntity):
    """Keep the previous successful timestamp visible during an outage."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_available = True

    def __init__(self, coordinator: ParroCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "last_success")

    @property
    def available(self) -> bool:
        """A failed later poll does not invalidate the historical timestamp."""
        return True

    @property
    def native_value(self) -> datetime | None:
        """Return the last successful summary poll."""
        return self.coordinator.last_success


class ParroNextAppointmentSensor(ParroEntity, SensorEntity):
    """Display a date instead of the calendar's technical on/off state."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_should_poll = True

    def __init__(self, coordinator: ParroCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "next_appointment")
        self._events = []
        self._calendar_available = False

    @property
    def available(self) -> bool:
        return self._calendar_available and not self.coordinator.content_auth_failed

    def _next_event(self):
        now = dt_util.now()
        return next((event for event in self._events if event.start_datetime_local >= now), None)

    @property
    def native_value(self) -> datetime | None:
        if self.available and (event := self._next_event()):
            return event.start_datetime_local
        return None

    @property
    def extra_state_attributes(self):
        if not self.available:
            return None
        if event := self._next_event():
            return {
                "summary": event.summary,
                "location": event.location,
                "all_day": not isinstance(event.start, datetime),
                "end_time": event.end.isoformat(),
            }
        return {"summary": None, "location": None, "all_day": None, "end_time": None}

    async def async_update(self) -> None:
        now = dt_util.now()
        try:
            self._events = await self.coordinator.async_get_calendar_events(
                now, now + timedelta(days=365)
            )
        except HomeAssistantError:
            self._events = []
            self._calendar_available = False
        else:
            self._calendar_available = True

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        # Move to the following appointment when one starts, without downloading
        # the subscriptions more frequently. The listener is removed on unload.
        @callback
        def update_next(_now):
            self.async_write_ha_state()

        self.async_on_remove(
            async_track_time_interval(
                self.hass, update_next, timedelta(minutes=1), cancel_on_shutdown=True
            )
        )
