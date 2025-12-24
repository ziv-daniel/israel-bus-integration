"""Sensor platform for Silent Bus integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_ATTRIBUTION,
    ATTR_DIRECTION,
    ATTR_LAST_UPDATE,
    ATTR_LINE_NUMBER,
    ATTR_NEXT_ARRIVAL,
    ATTR_REAL_TIME,
    ATTR_STATION_ID,
    ATTR_STATION_NAME,
    ATTR_UPCOMING_ARRIVALS,
    ATTRIBUTION,
    CONF_BUS_LINES,
    CONF_STATION_ID,
    CONF_STATION_NAME,
    DOMAIN,
)
from .coordinator import SilentBusCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Silent Bus sensors based on a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry
        async_add_entities: Callback to add entities
    """
    coordinator: SilentBusCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    station_id = entry.data[CONF_STATION_ID]
    station_name = entry.data[CONF_STATION_NAME]
    bus_lines = entry.data[CONF_BUS_LINES]

    # Create a sensor for each bus line
    entities = [
        SilentBusSensor(coordinator, station_id, station_name, line_number)
        for line_number in bus_lines
    ]

    async_add_entities(entities, True)

    _LOGGER.info(
        "Set up %s Silent Bus sensors for station %s",
        len(entities),
        station_id,
    )


class SilentBusSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Silent Bus sensor."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:bus"

    def __init__(
        self,
        coordinator: SilentBusCoordinator,
        station_id: str,
        station_name: str,
        line_number: str,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: Data update coordinator
            station_id: Station ID
            station_name: Station name
            line_number: Bus line number
        """
        super().__init__(coordinator)

        self._station_id = station_id
        self._station_name = station_name
        self._line_number = line_number

        # Set unique ID
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{line_number}"

        # Set device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{station_id}")},
            "name": f"Bus Station {station_name}",
            "manufacturer": "Silent Bus",
            "model": "Bus Stop",
        }

        # Set entity name
        self._attr_name = f"Line {line_number}"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor.

        Returns:
            Minutes until next arrival, or status string
        """
        next_arrival = self.coordinator.get_next_arrival(self._line_number)

        if next_arrival is None:
            return "No data"

        minutes = next_arrival["minutes_until"]

        if minutes == 0:
            return "Arrived"

        return str(minutes)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement.

        Returns:
            Unit string
        """
        if self.native_value in ("No data", "Arrived"):
            return None
        return "min"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes.

        Returns:
            Dictionary of attributes
        """
        next_arrival = self.coordinator.get_next_arrival(self._line_number)
        all_arrivals = self.coordinator.get_line_data(self._line_number)

        attributes = {
            ATTR_LINE_NUMBER: self._line_number,
            ATTR_STATION_ID: self._station_id,
            ATTR_STATION_NAME: self._station_name,
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_LAST_UPDATE: datetime.now().isoformat(),
        }

        if next_arrival:
            attributes[ATTR_NEXT_ARRIVAL] = next_arrival["arrival_time"]
            attributes[ATTR_REAL_TIME] = next_arrival["is_realtime"]
            attributes[ATTR_DIRECTION] = next_arrival["direction"]

        if all_arrivals:
            attributes[ATTR_UPCOMING_ARRIVALS] = all_arrivals

        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available.

        Returns:
            True if coordinator has data
        """
        # Entity is available if coordinator is available
        return self.coordinator.last_update_success

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if entity should be enabled by default.

        Returns:
            True to enable by default
        """
        return True
