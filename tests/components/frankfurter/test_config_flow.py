"""Test the Frankfurter config flow."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.components.frankfurter.const import DOMAIN
from homeassistant.const import CONF_BASE, CONF_TARGET
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.test_util.aiohttp import AiohttpClientMocker


async def test_form(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    """Test integration form."""
    aioclient_mock.get(
        "https://api.frankfurter.dev/v2/currencies",
        json=[
            {"iso_code": "EUR", "name": "Euro"},
            {"iso_code": "USD", "name": "US Dollar"},
        ],
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "homeassistant.components.frankfurter.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
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


async def test_form_cannot_connect(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Test handling of connection errors."""
    aioclient_mock.get(
        "https://api.frankfurter.dev/v2/currencies",
        status=500,
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "cannot_connect"


async def test_form_same_currency(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Test handling of same currency error."""
    aioclient_mock.get(
        "https://api.frankfurter.dev/v2/currencies",
        json=[
            {"iso_code": "EUR", "name": "Euro"},
            {"iso_code": "USD", "name": "US Dollar"},
        ],
    )

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


async def test_form_exception(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Test handling of exceptions."""
    aioclient_mock.get(
        "https://api.frankfurter.dev/v2/currencies",
        exc=Exception,
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "cannot_connect"
