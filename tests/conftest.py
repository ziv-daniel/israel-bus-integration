"""Fixtures for Silent Bus tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.silent_bus.const import (
    CONF_BUS_LINES,
    CONF_MAX_ARRIVALS,
    CONF_STATION_ID,
    CONF_STATION_NAME,
    CONF_UPDATE_INTERVAL,
    DEFAULT_MAX_ARRIVALS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


@pytest.fixture(autouse=True)
async def auto_enable_custom_integrations(hass: HomeAssistant):
    """Enable custom integrations for all tests."""
    await async_setup_component(hass, DOMAIN, {})


@pytest.fixture
def mock_api_client():
    """Mock BusNearbyApiClient."""
    with patch("custom_components.silent_bus.api.BusNearbyApiClient") as mock:
        client = mock.return_value
        client.validate_station = AsyncMock(return_value=True)
        client.search_station = AsyncMock(
            return_value=[
                {
                    "stop_id": "24068",
                    "name": "Arlozorov Terminal",
                    "city": "Tel Aviv",
                    "lat": 32.0853,
                    "lon": 34.7818,
                }
            ]
        )
        client.get_stop_times = AsyncMock(
            return_value=[
                {
                    "routeShortName": "249",
                    "serviceDay": 1640000000,
                    "realtimeArrival": 1000,
                    "scheduledArrival": 1000,
                    "realtime": True,
                    "headsign": "Tel Aviv - Jerusalem",
                },
                {
                    "routeShortName": "40",
                    "serviceDay": 1640000000,
                    "realtimeArrival": 2000,
                    "scheduledArrival": 2000,
                    "realtime": True,
                    "headsign": "Tel Aviv - Ramat Gan",
                },
            ]
        )
        client.close = AsyncMock()
        yield client


@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_STATION_ID: "24068",
            CONF_STATION_NAME: "Arlozorov Terminal",
            CONF_BUS_LINES: ["249", "40", "605"],
            CONF_UPDATE_INTERVAL: DEFAULT_SCAN_INTERVAL.total_seconds(),
            CONF_MAX_ARRIVALS: DEFAULT_MAX_ARRIVALS,
        },
        options={},
    )


@pytest.fixture
async def setup_integration(hass: HomeAssistant, mock_config_entry, mock_api_client):
    """Set up the Silent Bus integration."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.silent_bus.BusNearbyApiClient",
        return_value=mock_api_client,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    return mock_config_entry
