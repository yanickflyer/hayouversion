"""The YouVersion Verse of the Day Integration"""

from datetime import timedelta
from pathlib import Path
import shutil
import time

from homeassistant.components.lovelace import DOMAIN as LL_DOMAIN
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, CONF_API_KEY
from .verse import get_verse_day

CARD_JS = "youversion-verseoftheday.js"
CARD_BASE_PATH = f"/local/{DOMAIN}/{CARD_JS}"


async def async_setup(hass, config):
    """Set up the YouVersion integration and register the Lovelace resource."""
    hass.data.setdefault(DOMAIN, {})

    www_dir = Path(hass.config.path()) / "www" / DOMAIN
    src = Path(__file__).parent / "www" / CARD_JS
    dest = www_dir / CARD_JS

    def _copy_card():
        www_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dest))

    await hass.async_add_executor_job(_copy_card)

    async def _deferred_register(_event):
        await _register_lovelace_resource(hass, CARD_BASE_PATH, CARD_JS)

    hass.bus.async_listen_once("homeassistant_started", _deferred_register)

    return True


async def _register_lovelace_resource(hass, card_base_path, card_js):
    """Register the card JS file with Home Assistant Lovelace resources."""
    if LL_DOMAIN not in hass.data:
        LOGGER.debug("Lovelace unavailable when registering resource %s", card_base_path)
        return

    ll_data = hass.data[LL_DOMAIN]
    resources = getattr(ll_data, "resources", None)
    if resources is None or not isinstance(resources, ResourceStorageCollection):
        LOGGER.info(
            "Lovelace resources unavailable; add manually: url: %s, type: module",
            card_base_path,
        )
        return

    if not resources.loaded:
        await resources.async_load()

    www_path = Path(hass.config.path()) / "www" / DOMAIN / card_js
    try:
        mtime = int(www_path.stat().st_mtime * 10)
    except OSError:
        mtime = int(time.time() * 10)

    card_url = f"{card_base_path}?v={mtime}"

    for item in resources.async_items():
        url = item.get("url", "")
        if card_base_path in url:
            if url != card_url:
                await resources.async_update_item(
                    item["id"], {"res_type": "module", "url": card_url}
                )
                LOGGER.info("Updated lovelace resource: %s", card_url)
            else:
                LOGGER.debug("Lovelace resource already current: %s", card_base_path)
            return

    await resources.async_create_item({"res_type": "module", "url": card_url})
    LOGGER.info("Registered lovelace resource: %s", card_url)


async def async_setup_entry(hass, entry):
    """Set up YouVersion Verse of the Day from a config entry and create coordinator."""
    api_key = entry.data.get(CONF_API_KEY)
    if not api_key:
        LOGGER.error("API key is missing in the configuration.")
        return False

    # Store the api_key and coordinator container for this entry
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {CONF_API_KEY: api_key}

    async def async_update_data():
        result = await hass.async_add_executor_job(get_verse_day, api_key)
        if not result:
            raise UpdateFailed("Failed to fetch verse from YouVersion API")
        content, reference = result
        return {"content": content, "reference": reference}

    coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=f"{DOMAIN}_{entry.entry_id}",
        update_method=async_update_data,
        update_interval=timedelta(hours=1),
    )

    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

    # Perform first refresh so data is available when platforms are set up
    await coordinator.async_config_entry_first_refresh()

    # Forward setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok