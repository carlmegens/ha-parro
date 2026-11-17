"""Exercise new API operations through the real adapter and a synthetic transport."""

import json

import httpx
import pytest
from homeassistant.util import dt as dt_util

from custom_components.parro.api import ParroApi, ParroAuthError, ParroError


@pytest.fixture
def transport(monkeypatch):
    original = httpx.Client.__init__
    requests = []
    replies = {"status": 201, "type": "SINGLE", "enabled": True}

    def handler(request):
        requests.append(request)
        if request.url.path.endswith("/account/me"):
            return httpx.Response(200, json={"links": [{"rel": "self", "id": 1}]})
        if request.url.path.endswith("/chatroom"):
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "links": [{"rel": "self", "id": 42}],
                            "type": replies["type"],
                            "repliesEnabled": replies["enabled"],
                        }
                    ]
                },
            )
        if request.method == "POST":
            if replies["status"] == "timeout":
                raise httpx.ReadTimeout("private upstream detail")
            return httpx.Response(replies["status"])
        if request.url.path.endswith("/event"):
            if replies.get("calendar_full"):
                return httpx.Response(200, json={"items": [{}] * 50})
            return httpx.Response(200, json={"items": []})
        if request.url.path.endswith(("/child", "/group")):
            return httpx.Response(
                200,
                json={"items": []},
                headers={
                    "Content-Range": "items 0-0/101" if replies.get("incomplete") else "items 0-0/0"
                },
            )
        return httpx.Response(404)

    def init(self, *args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        original(self, *args, **kwargs)

    monkeypatch.setattr(httpx.Client, "__init__", init)
    return requests, replies


async def test_reply_exact_payload_no_redirects(hass, transport):
    requests, _ = transport
    api = ParroApi(hass, {"access_token": "synthetic"}, "1", lambda _: None)
    await api.async_send_reply("42", "Synthetic reply")
    posts = [r for r in requests if r.method == "POST"]
    assert len(posts) == 1
    assert str(posts[0].url) == "https://rest-v2.parro.com/rest/v2/chatroom/42/chatmessage"
    payload = json.loads(posts[0].content)
    assert payload["items"][0]["text"] == "Synthetic reply"
    assert payload["items"][0]["dtype"] == "chat.RChatTextMessage"
    assert not any("/chatmessage" in r.url.path for r in requests if r.method == "GET")
    await api.async_close()


@pytest.mark.parametrize("status", [401, 403, 429, 500, 302, "timeout"])
async def test_failed_send_is_never_retried(hass, transport, status):
    requests, replies = transport
    replies["status"] = status
    api = ParroApi(
        hass, {"access_token": "synthetic", "refresh_token": "synthetic"}, "1", lambda _: None
    )
    with pytest.raises(ParroAuthError if status == 401 else ParroError):
        await api.async_send_reply("42", "Synthetic")
    assert len([r for r in requests if r.method == "POST"]) == 1
    await api.async_close()


@pytest.mark.parametrize(
    ("room_type", "enabled"), [("GROUP", True), ("SINGLE", False), ("UNKNOWN", True)]
)
async def test_room_permission_checked_before_post(hass, transport, room_type, enabled):
    requests, replies = transport
    replies.update(type=room_type, enabled=enabled)
    api = ParroApi(hass, {"access_token": "synthetic"}, "1", lambda _: None)
    with pytest.raises(ParroError):
        await api.async_send_reply("42", "Synthetic")
    assert not any(r.method == "POST" for r in requests)
    await api.async_close()


async def test_incomplete_family_fails_closed(hass, transport):
    _, replies = transport
    replies["incomplete"] = True
    api = ParroApi(hass, {"access_token": "synthetic"}, "1", lambda _: None)
    with pytest.raises(ParroError, match="incomplete"):
        await api.async_get_family()
    await api.async_close()


async def test_native_calendar_query_is_bounded(hass, transport):
    from datetime import timedelta

    requests, replies = transport
    replies["calendar_full"] = True
    api = ParroApi(hass, {"access_token": "synthetic"}, "1", lambda _: None)
    now = dt_util.utcnow()
    with pytest.raises(ParroError, match="limit"):
        await api.async_get_child_events(now, now + timedelta(days=365))
    assert len([r for r in requests if r.url.path.endswith("/event")]) == 40
    await api.async_close()
