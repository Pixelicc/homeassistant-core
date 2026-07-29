"""DataUpdateCoordinator for the Frankfurter integration."""

import logging
from typing import override

from frankfurter_api import FrankfurterAPI
from frankfurter_api.client import ExchangeRateResponse

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_BASE, CONF_TARGET
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class FrankfurterDataUpdateCoordinator(DataUpdateCoordinator[ExchangeRateResponse]):
    """Class to manage fetching Frankfurter Currency API data."""

    config_entry: ConfigEntry
    base: str
    target: str

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.base = entry.data[CONF_BASE]
        self.target = entry.data[CONF_TARGET]
        self.api = FrankfurterAPI()

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{self.base}_{self.target}",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

    @override
    async def _async_update_data(self) -> ExchangeRateResponse:
        """Fetch data from the Frankfurter Currency API."""
        try:
            data = await self.api.get_rate(
                base=self.base,
                target=self.target,
            )
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        if "rate" not in data:
            raise UpdateFailed(f"Invalid response from API: {data}")

        return data
