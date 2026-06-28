"""DataUpdateCoordinator for the Frankfurter integration."""

import logging
from typing import Any, override

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_BASE, CONF_TARGET
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_PATH_RATE, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class FrankfurterDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Frankfurter Currency API data."""

    config_entry: ConfigEntry
    base: str
    target: str

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.base = entry.data[CONF_BASE]
        self.target = entry.data[CONF_TARGET]
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{self.base}_{self.target}",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

    @override
    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Frankfurter Currency API."""
        url = API_PATH_RATE.format(base=self.base, target=self.target)
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                data: dict[str, Any] = await response.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        if "rate" not in data:
            raise UpdateFailed(f"Invalid response from API: {data}")

        return data
