"""Constants for the unofficial Parro integration."""

DOMAIN = "parro"
CONF_ACCOUNT_ID = "account_id"
CONF_TOKENS = "tokens"
CONF_POLL_INTERVAL = "poll_interval"
CONF_DASHBOARD_VIEWERS = "dashboard_viewers"
CONF_CHAT_VIEWERS = "chat_viewers"
CARD_VERSION = "0.4.3"
CARD_PATH = "/parro_static/parro-card.js"
DEFAULT_FEED_LIMIT = 5
MAX_FEED_LIMIT = 20
DEFAULT_POLL_INTERVAL = 30
MIN_POLL_INTERVAL = 15
MAX_POLL_INTERVAL = 240
DEFAULT_LIMIT = 20
MAX_LIMIT = 50

CONF_CHILD_ENTITIES = "child_entities"
CONF_PHOTO_ENTITIES = "photo_entities"
CONF_ACTIVITY_EVENTS = "activity_events"
CONF_ALLOW_REPLIES = "allow_replies"
CONF_REPLY_ROOMS = "reply_rooms"
FEATURE_OPTIONS = (CONF_CHILD_ENTITIES, CONF_PHOTO_ENTITIES, CONF_ACTIVITY_EVENTS)
