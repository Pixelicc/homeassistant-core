"""Test the Frankfurter config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.components.frankfurter.const import DOMAIN
from homeassistant.const import CONF_BASE, CONF_TARGET
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_form(hass: HomeAssistant) -> None:
    """Test integration form."""
    with (
        patch(
            "homeassistant.components.frankfurter.config_flow.FrankfurterAPI.get_currencies",
            new=AsyncMock(
                return_value=[
                    {"iso_code": "EUR", "name": "Euro"},
                    {"iso_code": "USD", "name": "United States Dollar"},
                ]
            ),
        ),
        patch(
            "homeassistant.components.frankfurter.async_setup_entry",
            return_value=True,
        ) as mock_setup_entry,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {}

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_BASE: "EUR",
                CONF_TARGET: "USD",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "EUR to USD"
    assert result["data"] == {
        CONF_BASE: "EUR",
        CONF_TARGET: "USD",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test handling of connection errors."""
    with patch(
        "homeassistant.components.frankfurter.config_flow.FrankfurterAPI.get_currencies",
        new=AsyncMock(side_effect=Exception("HTTP Error 500")),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "cannot_connect"


async def test_form_same_currency(hass: HomeAssistant) -> None:
    """Test handling of same currency error."""
    with patch(
        "homeassistant.components.frankfurter.config_flow.FrankfurterAPI.get_currencies",
        new=AsyncMock(
            return_value=[
                {"iso_code": "EUR", "name": "Euro"},
                {"iso_code": "USD", "name": "United States Dollar"},
            ]
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
    assert result["type"] is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_BASE: "EUR",
            CONF_TARGET: "EUR",
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "same_currency"}


async def test_form_exception(hass: HomeAssistant) -> None:
    """Test handling of exceptions."""
    with patch(
        "homeassistant.components.frankfurter.config_flow.FrankfurterAPI.get_currencies",
        new=AsyncMock(side_effect=Exception),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "cannot_connect"
