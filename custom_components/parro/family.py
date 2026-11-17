"""Optional native surfaces; private content stays in bounded memory."""

import asyncio
from datetime import timedelta

from homeassistant.components.calendar import CalendarEvent
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import dt as dt_util

from .api import ParroError, _id
from .const import CONF_ACTIVITY_EVENTS, CONF_CHILD_ENTITIES, CONF_PHOTO_ENTITIES, DOMAIN
from .entity import ParroEntity
from .feed import ParroMediaError, _validated_url
from .models import ParroChatRoom, parse_datetime


class FamilyData:
    """A separate in-memory store, never included in coordinator diagnostics."""

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.closed = False
        self.children = {}
        self.groups = {}
        self.photos = []
        self.available = False
        self.activity = []
        self._seen = None
        self._watermark = None
        self._calendar_cache = None
        self._calendar_at = None
        self._calendar_lock = asyncio.Lock()

    def clear(self):
        self.children = {}
        self.groups = {}
        self.photos = []
        self.activity = []
        self.available = False
        self._seen = None
        self._watermark = None
        self._calendar_cache = None
        self._calendar_at = None

    def close(self):
        self.closed = True
        self.clear()

    async def async_update(self):
        if self.closed:
            raise ParroError("The family store is closed")
        options = self.coordinator.config_entry.options
        children, groups = {}, {}
        if options.get(CONF_CHILD_ENTITIES):
            children, groups = await self.coordinator.api.async_get_family()
        photos, activity = [], []
        if options.get(CONF_ACTIVITY_EVENTS) or options.get(CONF_PHOTO_ENTITIES):
            announcements, rooms, own_ids = await self.coordinator.api.async_get_activity()
            now = dt_util.utcnow()
            for item in announcements:
                if item.get("deleted") or item.get("draft"):
                    continue
                item_id = _id(item)
                published = parse_datetime(item.get("createdAt")) or parse_datetime(
                    item.get("sortDate")
                )
                if item_id and published and published <= now:
                    activity.append(("announcement", item_id, published))
            for raw in rooms:
                room = ParroChatRoom.from_api(raw)
                last = raw.get("lastMessage")
                last = last if isinstance(last, dict) else {}
                if (
                    room
                    and room.last_message_at
                    and room.last_message_at <= now
                    and room.last_sender_id is not None
                    and room.last_sender_id not in own_ids
                    and not last.get("deleted")
                ):
                    # Room lists expose only the latest message, not the whole history.
                    activity.append(("message", str(room.room_id), room.last_message_at))
            if options.get(CONF_PHOTO_ENTITIES):
                from .api import _image_sources

                ordered = sorted(
                    announcements,
                    key=lambda a: (
                        parse_datetime(a.get("sortDate"))
                        or parse_datetime(a.get("createdAt"))
                        or dt_util.utc_from_timestamp(0)
                    ),
                    reverse=True,
                )
                for item in ordered:
                    if item.get("deleted") or item.get("draft"):
                        continue
                    for source in _image_sources(item.get("attachments")):
                        try:
                            url = _validated_url(source["url"])
                        except ParroMediaError:
                            continue
                        if url not in photos:
                            photos.append(url)
                        if len(photos) == 6:
                            break
                    if len(photos) == 6:
                        break
        if self.closed or self.coordinator.content_auth_failed:
            raise ParroError("Authentication required")
        self.children, self.groups, self.photos = children, groups, photos
        self.available = True
        current = {(kind, item_id, at.isoformat()) for kind, item_id, at in activity}
        self.activity = []
        if options.get(CONF_ACTIVITY_EVENTS):
            if self._seen is not None:
                self.activity = sorted(
                    [
                        (kind, item_id, at)
                        for kind, item_id, at in activity
                        if (kind, item_id, at.isoformat()) not in self._seen
                        and at > self._watermark
                    ],
                    key=lambda item: item[2],
                )
            # A restart or enabling events establishes a silent baseline. Backfilled
            # older rows never fire. Retain keys within the most recent timestamp.
            self._watermark = max([self._watermark or dt_util.utcnow(), *(a[2] for a in activity)])
            self._seen = current
        else:
            self._seen = self._watermark = None

    async def async_events(self, child_id, start, end):
        if (
            self.closed
            or not self.available
            or self.coordinator.content_auth_failed
            or child_id not in self.children
        ):
            raise ParroError("Child calendar unavailable")
        if (
            start.tzinfo is None
            or end.tzinfo is None
            or not timedelta(0) < end - start <= timedelta(days=366)
        ):
            raise ParroError("Invalid calendar range")
        async with self._calendar_lock:
            now = dt_util.utcnow()
            # One range cache shared by child entities; exact range key avoids truncation.
            key = (start, end)
            if (
                self._calendar_cache is None
                or self._calendar_cache[0] != key
                or now - self._calendar_at > timedelta(minutes=15)
            ):
                rows = await self.coordinator.api.async_get_child_events(start, end)
                if self.closed or self.coordinator.content_auth_failed:
                    raise ParroError("Child calendar unavailable")
                self._calendar_cache = (key, rows)
                self._calendar_at = now
            if (
                self.closed
                or not self.available
                or self.coordinator.content_auth_failed
                or child_id not in self.children
            ):
                raise ParroError("Child calendar unavailable")
            events = []
            for row in self._calendar_cache[1]:
                if int(child_id) not in row.child_ids:
                    continue
                event = CalendarEvent(start=row.start, end=row.end, summary=row.title)
                if event.start_datetime_local < end and event.end_datetime_local > start:
                    events.append(event)
            return sorted(events, key=lambda event: event.start_datetime_local)


class ParroChildEntity(ParroEntity):
    """Stable identity per account and child; names are only display labels."""

    _unrecorded_attributes = frozenset(
        {"groups", "message", "description", "location", "start_time", "end_time"}
    )

    def __init__(self, coordinator, entry, child_id, key):
        super().__init__(coordinator, entry, f"child_{child_id}_{key}")
        self.child_id = child_id
        self._attr_translation_key = key
        child = coordinator.family.children[child_id]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_child_{child_id}")},
            name=child.first_name or "Parro",
            manufacturer="Parro",
            model="Child",
            via_device=(DOMAIN, entry.entry_id),
        )

    @property
    def available(self):
        return (
            self.coordinator.family.available
            and not self.coordinator.content_auth_failed
            and self.child_id in self.coordinator.family.children
            and self.coordinator.config_entry.options.get(CONF_CHILD_ENTITIES, False)
        )


@callback
def async_add_children(entry, async_add_entities, factory, *, update_before_add=False):
    """Discover new children without restarting; removed children become unavailable."""
    known = set()

    @callback
    def update():
        if not entry.options.get(CONF_CHILD_ENTITIES):
            return
        new = set(entry.runtime_data.family.children) - known
        known.update(new)
        async_add_entities(
            [factory(entry.runtime_data, entry, child_id) for child_id in sorted(new)],
            update_before_add=update_before_add,
        )

    update()
    entry.async_on_unload(entry.runtime_data.async_add_listener(update))
