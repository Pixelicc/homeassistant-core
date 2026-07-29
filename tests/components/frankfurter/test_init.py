"""Test the Frankfurter integration."""

from unittest.mock import AsyncMock, patch

from homeassistant.components.frankfurter.const import DOMAIN
from homeassistant.const import CONF_BASE, CONF_TARGET, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry


async def test_setup_unload_entry(hass: HomeAssistant) -> None:
    """Test setting up and unloading a config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_BASE: "EUR",
            CONF_TARGET: "USD",
        },
        unique_id="EUR_USD",
    )
    entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.frankfurter.coordinator.FrankfurterAPI.get_rate",
        new=AsyncMock(
            return_value={
                "date": "2026-06-28",
                "base": "EUR",
                "quote": "USD",
                "rate": 1.1393,
            }
        ),
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        assert len(hass.config_entries.async_entries(DOMAIN)) == 1
        assert hass.states.get("sensor.eur_to_usd")

        assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()

        assert hass.states.get("sensor.eur_to_usd").state == STATE_UNAVAILABLE
        assert len(hass.config_entries.async_entries(DOMAIN)) == 1
