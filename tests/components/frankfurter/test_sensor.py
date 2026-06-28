"""Test the Frankfurter sensor platform."""

from homeassistant.components.frankfurter.const import DOMAIN
from homeassistant.components.frankfurter.coordinator import (
    FrankfurterDataUpdateCoordinator,
)
from homeassistant.components.frankfurter.sensor import FrankfurterSensor
from homeassistant.const import CONF_BASE, CONF_TARGET
from homeassistant.core import HomeAssistant

from tests.common import MockConfigEntry
from tests.test_util.aiohttp import AiohttpClientMocker


async def test_sensor(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    """Test the Exchange Rate Sensor."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_BASE: "EUR",
            CONF_TARGET: "USD",
        },
        unique_id="EUR_USD",
    )
    entry.add_to_hass(hass)

    aioclient_mock.get(
        "https://api.frankfurter.dev/v2/rate/EUR/USD",
        json={
            "date": "2026-06-28",
            "base": "EUR",
            "quote": "USD",
            "rate": 1.1393,
        },
    )

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.eur_to_usd")
    assert state
    assert state.state == "1.1393"
    assert state.attributes["unit_of_measurement"] == "USD"
    assert state.attributes["base"] == "EUR"
    assert state.attributes["target"] == "USD"


async def test_sensor_update_failed(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Test the Exchange Rate Sensor against a failed update."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_BASE: "EUR",
            CONF_TARGET: "USD",
        },
        unique_id="EUR_USD",
    )
    entry.add_to_hass(hass)

    # Mock successful response
    aioclient_mock.get(
        "https://api.frankfurter.dev/v2/rate/EUR/USD",
        json={
            "date": "2026-06-28",
            "base": "EUR",
            "quote": "USD",
            "rate": 1.1393,
        },
    )

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.eur_to_usd")
    assert state.state == "1.1393"

    #  Mock a failed request
    aioclient_mock.clear_requests()
    aioclient_mock.get(
        "https://api.frankfurter.dev/v2/rate/EUR/USD",
        status=500,
    )

    coordinator: FrankfurterDataUpdateCoordinator = entry.runtime_data
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    state = hass.states.get("sensor.eur_to_usd")
    assert state.state == "unavailable"


async def test_sensor_no_data(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Test the Exchange Rate Sensor with no data."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_BASE: "EUR",
            CONF_TARGET: "USD",
        },
        unique_id="EUR_USD",
    )
    entry.add_to_hass(hass)

    aioclient_mock.get(
        "https://api.frankfurter.dev/v2/rate/EUR/USD",
        json={
            "date": "2026-06-28",
            "base": "EUR",
            "quote": "USD",
            "rate": 1.1393,
        },
    )

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    coordinator: FrankfurterDataUpdateCoordinator = entry.runtime_data
    sensor = FrankfurterSensor(coordinator)

    # Test properties when data is present
    assert sensor.native_value == 1.1393
    assert sensor.extra_state_attributes["date"] == "2026-06-28"

    # Test properties when data is missing
    coordinator.data = None
    assert sensor.native_value is None
    assert sensor.extra_state_attributes == {}


async def test_sensor_invalid_response(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """Test the Exchange Rate Sensor against an invalid response."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_BASE: "EUR",
            CONF_TARGET: "USD",
        },
        unique_id="EUR_USD",
    )
    entry.add_to_hass(hass)

    # Mock returning valid data
    aioclient_mock.get(
        "https://api.frankfurter.dev/v2/rate/EUR/USD",
        json={
            "date": "2026-06-28",
            "base": "EUR",
            "quote": "USD",
            "rate": 1.1393,
        },
    )

    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.eur_to_usd")
    assert state.state == "1.1393"

    # Mock returning invalid data
    aioclient_mock.clear_requests()
    aioclient_mock.get(
        "https://api.frankfurter.dev/v2/rate/EUR/USD",
        json={"something": "else"},
    )

    coordinator: FrankfurterDataUpdateCoordinator = entry.runtime_data
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    state = hass.states.get("sensor.eur_to_usd")
    assert state.state == "unavailable"
