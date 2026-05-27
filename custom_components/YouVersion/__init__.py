"""The YouVersion Verse of the Day Integration"""

from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, CONF_API_KEY
from .verse import get_verse_day


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
        update_interval=timedelta(days=1),
    )

    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

    # Perform first refresh so data is available when platforms are set up
    await coordinator.async_config_entry_first_refresh()

    # Forward setup to the sensor platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok