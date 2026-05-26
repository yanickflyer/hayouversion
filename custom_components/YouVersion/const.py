DOMAIN = "youversion"
PLATFORMS = ["sensor"]
CONF_API_KEY = "api_key"
DEFAULT_NAME = "YouVersion Verse of the Day"

# Base API
API_BASE = "https://api.youversion.com/v1"
API_VOTD_CALENDAR = f"{API_BASE}/verse_of_the_days"
API_PASSAGES = f"{API_BASE}/bibles/{{bible_id}}/passages/{{passage_id}}"

# Optional default Bible id (user can override in config). Common public ids vary by region.
CONF_BIBLE_ID = "bible_id"
DEFAULT_BIBLE_ID = 3034
