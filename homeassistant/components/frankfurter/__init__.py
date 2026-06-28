"""The Frankfurter integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import FrankfurterDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

type FrankfurterConfigEntry = ConfigEntry[FrankfurterDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: FrankfurterConfigEntry) -> bool:
    """Set up Frankfurter from a config entry."""

    coordinator = FrankfurterDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: FrankfurterConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
