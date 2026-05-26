from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryNotReady

from datetime import datetime, timezone

from .const import DOMAIN, CONF_API_KEY, API_VOTD_CALENDAR, API_PASSAGES, CONF_BIBLE_ID, DEFAULT_BIBLE_ID

_LOGGER = logging.getLogger(__name__)


def _parse_votd(data: dict) -> dict:
    """Best-effort parse verse-of-the-day payload into text and reference."""
    text = ""
    reference = ""
    if not isinstance(data, dict):
        return {"text": text, "reference": reference}

    candidates = [data.get("text"), data.get("content"), data.get("verse")]
    verse_obj = data.get("verse")
    if isinstance(verse_obj, dict):
        candidates.append(verse_obj.get("text"))
        reference = reference or verse_obj.get("reference") or reference
    data_obj = data.get("data")
    if isinstance(data_obj, dict):
        candidates.append(data_obj.get("text"))
        reference = reference or data_obj.get("reference") or reference

    for c in candidates:
        if c:
            text = c
            break

    if not reference:
        reference = data.get("reference") or data.get("verses") or ""

    return {"text": text, "reference": reference}


class YouVersionClient:
    def __init__(self, session, api_key: str, bible_id: int | None = None):
        self._session = session
        self._api_key = api_key
        self._bible_id = bible_id or DEFAULT_BIBLE_ID

    async def _fetch_json(self, url: str, headers: dict, params: dict | None = None) -> dict | None:
        try:
            resp = await self._session.get(url, headers=headers, params=params, timeout=10)
        except Exception:
            _LOGGER.debug("Request failed for %s with headers %s", url, headers, exc_info=True)
            return None

        if resp.status != 200:
            await resp.read()
            return None

        try:
            return await resp.json()
        except Exception:
            _LOGGER.debug("Invalid JSON from %s", url, exc_info=True)
            return None

    async def async_get_votd(self, day: int | None = None):
        """Retrieve the verse of the day content for the given day (or today).

        Returns a dict with keys: text, reference, passage_id, day
        """
        if day is None:
            day = datetime.now(timezone.utc).timetuple().tm_yday

        # Try common header formats until one works
        header_variants = [
            {"Authorization": f"Bearer {self._api_key}"},
            {"x-yvp-app-key": self._api_key},
            {"X-YouVersion-Developer-Token": self._api_key},
        ]

        passage_id = await self._get_passage_id(day, header_variants)
        if not passage_id:
            raise ConfigEntryNotReady("Unable to retrieve Verse of the Day - check API key and endpoint")

        content = await self._get_passage_content(passage_id, header_variants)
        if not content:
            raise ConfigEntryNotReady("Unable to retrieve passage content - check Bible id and API key")

        content.update({"passage_id": passage_id, "day": day})
        return content

    async def _get_passage_id(self, day: int, header_variants: list[dict]) -> str | None:
        votd_url = f"{API_VOTD_CALENDAR}/{day}"
        for headers in header_variants:
            data = await self._fetch_json(votd_url, headers)
            if not data:
                continue
            if isinstance(data, dict):
                passage_id = data.get("passage_id") or (data.get("data") and data["data"].get("passage_id"))
                if passage_id:
                    return passage_id
        return None

    async def _get_passage_content(self, passage_id: str, header_variants: list[dict]) -> dict | None:
        passage_url = API_PASSAGES.format(bible_id=self._bible_id, passage_id=passage_id)
        params = {"format": "text"}
        for headers in header_variants:
            p = await self._fetch_json(passage_url, headers, params=params)
            if not p or not isinstance(p, dict):
                continue
            text = p.get("content") or p.get("text") or ""
            reference = p.get("reference") or ""
            return {"text": text, "reference": reference}
        return None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    api_key = entry.data.get(CONF_API_KEY)
    bible_id = entry.data.get(CONF_BIBLE_ID, DEFAULT_BIBLE_ID)
    client = YouVersionClient(session, api_key, bible_id=bible_id)

    async def async_update_data():
        return await client.async_get_votd()

    coordinator = DataUpdateCoordinator(hass, _LOGGER, name=DOMAIN, update_method=async_update_data, update_interval=None)

    # Do initial refresh and check
    await coordinator.async_refresh()

    hass.data[DOMAIN][entry.entry_id] = {"client": client, "coordinator": coordinator}

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
