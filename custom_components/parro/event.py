"""Small notification events; no message content is copied into state."""

from homeassistant.components.event import EventEntity
from homeassistant.core import callback

from .const import CONF_ACTIVITY_EVENTS
from .entity import ParroEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(hass, entry, async_add_entities):
    if entry.options.get(CONF_ACTIVITY_EVENTS):
        async_add_entities(
            [
                ParroActivityEvent(entry.runtime_data, entry, kind)
                for kind in ("announcement", "message")
            ]
        )


class ParroActivityEvent(ParroEntity, EventEntity):
    _unrecorded_attributes = frozenset({"item_id", "published_at", "config_entry_id"})

    def __init__(self, coordinator, entry, kind):
        super().__init__(coordinator, entry, f"new_{kind}")
        self.kind = kind
        self._attr_event_types = [f"new_{kind}"]
        self._batch = None

    @property
    def available(self):
        return (
            super().available
            and self.coordinator.family.available
            and not self.coordinator.content_auth_failed
            and self.coordinator.config_entry.options.get(CONF_ACTIVITY_EVENTS, False)
        )

    @callback
    def _handle_coordinator_update(self):
        batch = self.coordinator.family.activity
        if self.available and batch is not self._batch:
            self._batch = batch
            for kind, item_id, at in batch:
                if kind != self.kind:
                    continue
                data = {
                    "config_entry_id": self.coordinator.config_entry.entry_id,
                    "item_id": item_id,
                    "published_at": at.isoformat(),
                }
                self._trigger_event(f"new_{kind}", data)
                self.hass.bus.async_fire(f"parro_new_{kind}", data)
                self.async_write_ha_state()
        super()._handle_coordinator_update()
