from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DEFAULT_NAME


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    # Ensure we have recent data before adding entity
    await coordinator.async_request_refresh()
    async_add_entities([YouVersionVOTDSensor(coordinator, entry)])


class YouVersionVOTDSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = DEFAULT_NAME
        self._attr_unique_id = f"{entry.entry_id}_votd"

    @property
    def state(self):
        data = self.coordinator.data or {}
        return data.get("text")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return {
            "reference": data.get("reference"),
            "passage_id": data.get("passage_id"),
            "day": data.get("day"),
        }
