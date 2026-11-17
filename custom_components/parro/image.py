"""Opt-in native images using the same bounded, sanitized media downloader."""

from homeassistant.components.image import ImageEntity
from homeassistant.core import callback
from homeassistant.util import dt as dt_util

from .api import ParroError
from .const import CONF_PHOTO_ENTITIES
from .entity import ParroEntity
from .family import ParroChildEntity, async_add_children
from .feed import _validated_url

PARALLEL_UPDATES = 1


async def async_setup_entry(hass, entry, async_add_entities):
    if not entry.options.get(CONF_PHOTO_ENTITIES):
        return
    async_add_children(entry, async_add_entities, ParroProfileImage)
    async_add_entities([ParroPhotoImage(entry.runtime_data, entry, i) for i in range(6)])


class ProtectedImage(ImageEntity):
    """Never expose Parro URLs in state; check revocation before and after I/O."""

    _attr_content_type = "image/jpeg"
    _source = None
    _changed = None

    @property
    def source(self):
        raise NotImplementedError

    @property
    def image_last_updated(self):
        return self._changed

    @callback
    def _handle_coordinator_update(self):
        source = self.source if self.available else None
        if self._source != source:
            self._source = source
            self._changed = dt_util.utcnow() if source else None
        super()._handle_coordinator_update()

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self._source = self.source if self.available else None
        self._changed = dt_util.utcnow() if self._source else None

    async def async_image(self):
        if not self.available:
            return None
        source = self.source
        if not source:
            return None
        try:
            feed = self.coordinator.feed
            ref = feed._media_id(_validated_url(source))
            data, _ = await feed.async_get_image(ref)
        except ParroError:
            return None
        if not self.available or self.source != source:
            return None
        return data


class ParroProfileImage(ProtectedImage, ParroChildEntity):
    def __init__(self, coordinator, entry, child_id):
        ImageEntity.__init__(self, coordinator.hass)
        ParroChildEntity.__init__(self, coordinator, entry, child_id, "profile_photo")

    @property
    def available(self):
        return (
            ParroChildEntity.available.fget(self)
            and bool(self.source)
            and self.coordinator.config_entry.options.get(CONF_PHOTO_ENTITIES, False)
        )

    @property
    def source(self):
        child = self.coordinator.family.children.get(self.child_id)
        return child.avatar_url if child else None


class ParroPhotoImage(ProtectedImage, ParroEntity):
    def __init__(self, coordinator, entry, index):
        ImageEntity.__init__(self, coordinator.hass)
        ParroEntity.__init__(self, coordinator, entry, f"recent_photo_{index + 1}")
        self._attr_translation_key = "recent_photo"
        self._attr_translation_placeholders = {"number": str(index + 1)}
        self.index = index

    @property
    def available(self):
        return (
            self.coordinator.family.available
            and not self.coordinator.content_auth_failed
            and bool(self.source)
            and self.coordinator.config_entry.options.get(CONF_PHOTO_ENTITIES, False)
        )

    @property
    def source(self):
        photos = self.coordinator.family.photos
        return photos[self.index] if self.index < len(photos) else None
