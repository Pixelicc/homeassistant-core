"""Sensor platform for the Frankfurter integration."""

from typing import Any, override

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import FrankfurterConfigEntry
from .const import DOMAIN
from .coordinator import FrankfurterDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FrankfurterConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Frankfurter sensor platform."""
    coordinator = entry.runtime_data
    async_add_entities([FrankfurterSensor(coordinator)])


class FrankfurterSensor(
    CoordinatorEntity[FrankfurterDataUpdateCoordinator], SensorEntity
):
    """Representation of a Frankfurter Exchange Rate Sensor."""

    _attr_icon = "mdi:currency-usd"
    _attr_has_entity_name = True

    def __init__(self, coordinator: FrankfurterDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.base}_{coordinator.target}"
        self._attr_name = None

        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._attr_unique_id)},
            "name": f"{coordinator.base} to {coordinator.target}",
            "manufacturer": "Frankfurter Currency API",
            "model": "Exchange Rate Sensor",
        }

    @property
    @override
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get("rate")
        return None

    @property
    @override
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self.coordinator.target

    @property
    @override
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the extra state attributes."""
        if self.coordinator.data:
            return {
                "date": self.coordinator.data.get("date"),
                "base": self.coordinator.base,
                "target": self.coordinator.target,
            }
        return {}
