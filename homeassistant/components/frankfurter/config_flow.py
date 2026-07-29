"""Config flow for the Frankfurter integration."""

import logging
from typing import Any, override

from frankfurter_api import FrankfurterAPI
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_BASE, CONF_TARGET

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class FrankfurterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Frankfurter."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._api = FrankfurterAPI()
        self._currencies: dict[str, str] = {}

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if not self._currencies:
            try:
                data = await self._api.get_currencies()
                self._currencies = {
                    item["iso_code"]: f"{item['name']} ({item['iso_code']})"
                    for item in data
                }
            except Exception:
                _LOGGER.exception("Failed to fetch currencies")
                return self.async_abort(reason="cannot_connect")

        if user_input is not None:
            base = user_input[CONF_BASE]
            target = user_input[CONF_TARGET]

            if base == target:
                errors["base"] = "same_currency"
            else:
                await self.async_set_unique_id(f"{base}_{target}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"{base} to {target}", data=user_input
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE, default="USD"): vol.In(self._currencies),
                vol.Required(CONF_TARGET, default="EUR"): vol.In(self._currencies),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
