"""Constants for the Silent Bus integration."""
from datetime import timedelta
from typing import Final

# Integration domain
DOMAIN: Final = "silent_bus"

# Configuration and options
CONF_STATION_ID: Final = "station_id"
CONF_STATION_NAME: Final = "station_name"
CONF_BUS_LINES: Final = "bus_lines"
CONF_UPDATE_INTERVAL: Final = "update_interval"
CONF_MAX_ARRIVALS: Final = "max_arrivals"

# Default values
DEFAULT_SCAN_INTERVAL: Final = timedelta(seconds=30)
DEFAULT_MAX_ARRIVALS: Final = 3
MIN_SCAN_INTERVAL: Final = timedelta(seconds=15)
MAX_SCAN_INTERVAL: Final = timedelta(minutes=10)

# API configuration
API_BASE_URL: Final = "https://api.busnearby.co.il"
API_SEARCH_URL: Final = "https://app.busnearby.co.il/stopSearch"
API_TIMEOUT: Final = 10
MAX_RETRIES: Final = 3
RETRY_DELAY: Final = 2

# Time thresholds (in minutes)
APPROACHING_THRESHOLD: Final = 10
FAR_AWAY_THRESHOLD: Final = 60
NIGHT_HOUR_START: Final = 22
NIGHT_HOUR_END: Final = 6

# Sensor configuration
ATTR_LINE_NUMBER: Final = "line_number"
ATTR_STATION_ID: Final = "station_id"
ATTR_STATION_NAME: Final = "station_name"
ATTR_NEXT_ARRIVAL: Final = "next_arrival"
ATTR_REAL_TIME: Final = "real_time"
ATTR_DIRECTION: Final = "direction"
ATTR_UPCOMING_ARRIVALS: Final = "upcoming_arrivals"
ATTR_LAST_UPDATE: Final = "last_update"
ATTR_ATTRIBUTION: Final = "attribution"

# Attribution
ATTRIBUTION: Final = "Data provided by BusNearby"

# Error messages
ERROR_STATION_NOT_FOUND: Final = "station_not_found"
ERROR_NO_LINES_CONFIGURED: Final = "no_lines_configured"
ERROR_API_UNAVAILABLE: Final = "api_unavailable"
ERROR_INVALID_RESPONSE: Final = "invalid_response"
ERROR_NETWORK_ERROR: Final = "network_error"
ERROR_TIMEOUT: Final = "timeout"
ERROR_CANNOT_CONNECT: Final = "cannot_connect"
ERROR_UNKNOWN: Final = "unknown"

# User agent for API requests
USER_AGENT: Final = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
