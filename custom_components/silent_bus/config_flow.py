"""Config flow for Silent Bus integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .api import (
    ApiConnectionError,
    BusNearbyApiClient,
    StationNotFoundError,
)
from .const import (
    CONF_BUS_LINES,
    CONF_MAX_ARRIVALS,
    CONF_STATION_ID,
    CONF_STATION_NAME,
    CONF_UPDATE_INTERVAL,
    DEFAULT_MAX_ARRIVALS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    ERROR_CANNOT_CONNECT,
    ERROR_STATION_NOT_FOUND,
    ERROR_UNKNOWN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class SilentBusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Silent Bus."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._station_id: str | None = None
        self._station_name: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - station selection.

        Args:
            user_input: User input data

        Returns:
            Flow result
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            station_id = user_input[CONF_STATION_ID].strip()

            # Validate station ID
            try:
                async with aiohttp.ClientSession() as session:
                    api_client = BusNearbyApiClient(session)

                    # Try to validate the station
                    is_valid = await api_client.validate_station(station_id)

                    if not is_valid:
                        errors["base"] = ERROR_STATION_NOT_FOUND
                    else:
                        # Try to get station name
                        try:
                            stations = await api_client.search_station(station_id)
                            if stations:
                                self._station_name = stations[0].get("name", f"Station {station_id}")
                            else:
                                self._station_name = f"Station {station_id}"
                        except Exception:
                            self._station_name = f"Station {station_id}"

                        self._station_id = station_id

                        # Move to next step
                        return await self.async_step_bus_lines()

            except ApiConnectionError:
                errors["base"] = ERROR_CANNOT_CONNECT
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = ERROR_UNKNOWN

        # Show form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_STATION_ID): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "station_help": "Enter the station number (e.g., 24068). "
                "You can find station numbers at https://www.bus.co.il"
            },
        )

    async def async_step_bus_lines(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle bus lines selection step.

        Args:
            user_input: User input data

        Returns:
            Flow result
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            bus_lines_input = user_input[CONF_BUS_LINES].strip()

            # Parse bus lines (comma-separated)
            bus_lines = [
                line.strip()
                for line in bus_lines_input.split(",")
                if line.strip()
            ]

            if not bus_lines:
                errors["base"] = "no_lines"
            else:
                # Create the config entry
                await self.async_set_unique_id(f"{self._station_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"{self._station_name}",
                    data={
                        CONF_STATION_ID: self._station_id,
                        CONF_STATION_NAME: self._station_name,
                        CONF_BUS_LINES: bus_lines,
                        CONF_UPDATE_INTERVAL: DEFAULT_SCAN_INTERVAL.total_seconds(),
                        CONF_MAX_ARRIVALS: DEFAULT_MAX_ARRIVALS,
                    },
                )

        # Show form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_BUS_LINES): str,
            }
        )

        return self.async_show_form(
            step_id="bus_lines",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "station_name": self._station_name or "Unknown",
                "lines_help": "Enter bus line numbers separated by commas (e.g., 249, 40, 605)",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SilentBusOptionsFlow:
        """Get the options flow for this handler.

        Args:
            config_entry: Config entry

        Returns:
            Options flow handler
        """
        return SilentBusOptionsFlow(config_entry)


class SilentBusOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Silent Bus."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow.

        Args:
            config_entry: Config entry
        """
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options.

        Args:
            user_input: User input data

        Returns:
            Flow result
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # Parse bus lines
            bus_lines_input = user_input[CONF_BUS_LINES].strip()
            bus_lines = [
                line.strip()
                for line in bus_lines_input.split(",")
                if line.strip()
            ]

            if not bus_lines:
                errors["base"] = "no_lines"
            else:
                # Update the config entry
                new_data = {
                    **self.config_entry.data,
                    CONF_BUS_LINES: bus_lines,
                    CONF_UPDATE_INTERVAL: user_input[CONF_UPDATE_INTERVAL],
                    CONF_MAX_ARRIVALS: user_input[CONF_MAX_ARRIVALS],
                }

                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data=new_data,
                )

                return self.async_create_entry(title="", data={})

        # Get current values
        current_lines = self.config_entry.data.get(CONF_BUS_LINES, [])
        current_interval = self.config_entry.data.get(
            CONF_UPDATE_INTERVAL,
            DEFAULT_SCAN_INTERVAL.total_seconds(),
        )
        current_max_arrivals = self.config_entry.data.get(
            CONF_MAX_ARRIVALS,
            DEFAULT_MAX_ARRIVALS,
        )

        # Show form
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_BUS_LINES,
                    default=", ".join(current_lines),
                ): str,
                vol.Required(
                    CONF_UPDATE_INTERVAL,
                    default=current_interval,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(
                        min=MIN_SCAN_INTERVAL.total_seconds(),
                        max=MAX_SCAN_INTERVAL.total_seconds(),
                    ),
                ),
                vol.Required(
                    CONF_MAX_ARRIVALS,
                    default=current_max_arrivals,
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "station_name": self.config_entry.data.get(CONF_STATION_NAME, "Unknown"),
            },
        )
