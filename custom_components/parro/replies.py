"""Explicit opt-in replies with a durable attempt ledger and no delivery retries."""

import asyncio
import hashlib
import re

from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .api import ParroAuthError, ParroError
from .const import CONF_ALLOW_REPLIES, CONF_REPLY_ROOMS, DOMAIN


def clean_message(value):
    if not isinstance(value, str):
        raise ServiceValidationError("Enter a message")
    text = value.strip().replace("\r\n", "\n")
    if not text or len(text) > 1000 or text.count("\n") >= 20:
        raise ServiceValidationError("Use 1–1000 characters and at most 20 lines")
    if any(ord(c) < 32 and c not in "\n\t" for c in text):
        raise ServiceValidationError("The message contains control characters")
    return text


class ReplyGuard:
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.lock = asyncio.Lock()
        self.store = Store(
            coordinator.hass,
            1,
            f"{DOMAIN}.{coordinator.config_entry.entry_id}.replies",
            private=True,
        )

    async def async_send(self, room, message):
        text = clean_message(message)
        if not isinstance(room, str) or not re.fullmatch(r"[1-9][0-9]{0,19}", room):
            raise ServiceValidationError("Select a valid conversation ID")
        async with self.lock:
            entry = self.coordinator.config_entry
            options = entry.options
            if not options.get(CONF_ALLOW_REPLIES, False) or room not in options.get(
                CONF_REPLY_ROOMS, []
            ):
                raise ServiceValidationError(
                    "Enable replies and explicitly allow this conversation first"
                )
            if self.coordinator.content_auth_failed:
                raise HomeAssistantError("Parro sign-in has expired")
            now = dt_util.utcnow().timestamp()
            stored = await self.store.async_load()
            attempts = stored.get("attempts", []) if isinstance(stored, dict) else []
            attempts = [
                a
                for a in attempts
                if isinstance(a, dict)
                and isinstance(a.get("at"), (int, float))
                and now - a["at"] < 86400
            ]
            digest = hashlib.sha256(f"{room}\n{text}".encode()).hexdigest()
            if (
                len(attempts) >= 20
                or sum(now - a["at"] < 3600 for a in attempts) >= 5
                or any(a.get("room") == room and now - a["at"] < 60 for a in attempts)
            ):
                raise ServiceValidationError("Reply limit reached; try again later")
            if any(a.get("digest") == digest and now - a["at"] < 21600 for a in attempts):
                raise ServiceValidationError(
                    "This reply was recently attempted; check Parro before retrying"
                )
            attempts.append({"at": now, "room": room, "digest": digest})
            # Persist BEFORE the network operation, including uncertain outcomes.
            # Never store plaintext. A failed save must prevent sending.
            await self.store.async_save({"attempts": attempts})
            if not entry.options.get(CONF_ALLOW_REPLIES, False) or room not in entry.options.get(
                CONF_REPLY_ROOMS, []
            ):
                raise ServiceValidationError("Replies were disabled")
            try:
                await self.coordinator.api.async_send_reply(room, text)
            except ParroAuthError:
                await self.coordinator.async_invalidate_auth()
                entry.async_start_reauth(self.coordinator.hass)
                raise HomeAssistantError("Parro sign-in has expired") from None
            except ParroError:
                raise HomeAssistantError(
                    "Delivery could not be confirmed; check Parro before retrying"
                ) from None
