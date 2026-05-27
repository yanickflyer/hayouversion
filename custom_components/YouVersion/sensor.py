from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEFAULT_NAME


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the YouVersion sensor from a config entry using the coordinator."""
    entry_data = hass.data[DOMAIN].get(entry.entry_id)
    if not entry_data:
        return

    coordinator = entry_data.get("coordinator")
    if not coordinator:
        return

    async_add_entities([YouVersionVerseSensor(coordinator)], True)


class YouVersionVerseSensor(CoordinatorEntity, SensorEntity):
    """Sensor that provides the YouVersion Verse of the Day using a DataUpdateCoordinator."""

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = DEFAULT_NAME

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data:
            return None
        return data.get("reference")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}
        return {"passage": data.get("content")}
