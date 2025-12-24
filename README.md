# Silent Bus - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/ziv-daniel/Silent-bus-integration.svg)](https://github.com/ziv-daniel/Silent-bus-integration/releases)
[![License](https://img.shields.io/github/license/ziv-daniel/Silent-bus-integration.svg)](LICENSE)

A comprehensive Home Assistant integration for monitoring Israeli public transportation in real-time. Track bus arrival times at your favorite stations and get notified when your bus is approaching.

## Features

- 🚌 **Real-time Bus Tracking** - Get live arrival times for Israeli buses
- 🎯 **Multi-Station Support** - Monitor multiple stations simultaneously
- 🔄 **Automatic Updates** - Smart polling with dynamic update intervals
- 🌍 **Bilingual** - Full support for Hebrew and English
- 📊 **Rich Sensor Data** - Detailed attributes including direction, real-time status, and upcoming arrivals
- ⚙️ **Easy Configuration** - User-friendly UI configuration flow
- 🔔 **Automation Ready** - Perfect for creating arrival notifications and automations

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/ziv-daniel/Silent-bus-integration`
6. Select category: "Integration"
7. Click "Add"
8. Find "Silent Bus" in the integrations list
9. Click "Download"
10. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/ziv-daniel/Silent-bus-integration/releases)
2. Extract the `custom_components/silent_bus` folder
3. Copy it to your Home Assistant `custom_components` directory
4. Restart Home Assistant

## Configuration

### Adding the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Silent Bus**
4. Follow the configuration steps:
   - **Step 1**: Enter your station number (e.g., `24068`)
   - **Step 2**: Enter bus line numbers separated by commas (e.g., `249, 40, 605`)

### Finding Station Numbers

You can find station numbers at:
- [bus.co.il](https://www.bus.co.il) - Official Israeli bus information site
- [BusNearby](https://app.busnearby.co.il) - Real-time bus tracking app

Simply search for your station and note the station number.

### Configuration Options

After setup, you can modify settings by clicking **Configure** on the integration:

- **Bus Lines**: Comma-separated list of bus line numbers to track
- **Update Interval**: How often to fetch data (15-600 seconds, default: 30)
- **Maximum Arrivals**: Number of upcoming arrivals to track per line (1-10, default: 3)

## Sensors

The integration creates one sensor per bus line with the following format:

**Entity ID**: `sensor.bus_{station_id}_line_{line_number}`

**Example**: `sensor.bus_24068_line_249`

### Sensor State

The sensor state shows minutes until the next bus arrival:
- `5` - Bus arriving in 5 minutes
- `Arrived` - Bus is at the station
- `No data` - No upcoming arrivals
- `Unavailable` - API connection error

### Sensor Attributes

Each sensor provides rich attributes:

```yaml
line_number: "249"
station_id: "24068"
station_name: "Arlozorov Terminal"
next_arrival: "2025-12-24T14:35:00+02:00"
real_time: true
direction: "Tel Aviv - Jerusalem"
upcoming_arrivals:
  - arrival_time: "2025-12-24T14:35:00+02:00"
    minutes_until: 5
    is_realtime: true
    direction: "Tel Aviv - Jerusalem"
  - arrival_time: "2025-12-24T14:50:00+02:00"
    minutes_until: 20
    is_realtime: false
    direction: "Tel Aviv - Jerusalem"
last_update: "2025-12-24T14:30:15+02:00"
attribution: "Data provided by BusNearby"
```

## Usage Examples

### Dashboard Card

Display bus times using the built-in entities card:

```yaml
type: entities
title: Bus Times - Home
entities:
  - entity: sensor.bus_24068_line_249
    name: Line 249
    icon: mdi:bus
  - entity: sensor.bus_24068_line_40
    name: Line 40
    icon: mdi:bus
  - entity: sensor.bus_24068_line_605
    name: Line 605
    icon: mdi:bus
```

### Automation: Notify When Bus Approaching

Get notified when your bus is 10 minutes away:

```yaml
automation:
  - alias: "Bus 249 Approaching"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bus_24068_line_249
        below: 10
    condition:
      - condition: numeric_state
        entity_id: sensor.bus_24068_line_249
        above: 0
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Bus 249 Approaching"
          message: "Bus arrives in {{ states('sensor.bus_24068_line_249') }} minutes"
```

### Automation: Turn On Lights When Bus is Near

Prepare to leave when bus is 5 minutes away:

```yaml
automation:
  - alias: "Prepare to Leave - Bus Approaching"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bus_24068_line_249
        below: 5
    action:
      - service: light.turn_on
        target:
          entity_id: light.hallway
      - service: notify.mobile_app_your_phone
        data:
          message: "Time to leave! Bus 249 in {{ states('sensor.bus_24068_line_249') }} min"
```

### Template Sensor: Next Bus Across Multiple Lines

Create a sensor showing the soonest bus from multiple lines:

```yaml
template:
  - sensor:
      - name: "Next Bus Home"
        state: >
          {% set lines = [
            states('sensor.bus_24068_line_249'),
            states('sensor.bus_24068_line_40'),
            states('sensor.bus_24068_line_605')
          ] %}
          {% set times = lines | reject('in', ['No data', 'Arrived', 'unavailable']) | map('int') | list %}
          {% if times | length > 0 %}
            {{ times | min }}
          {% else %}
            No data
          {% endif %}
        unit_of_measurement: "min"
        icon: mdi:bus-clock
```

## Smart Features

### Dynamic Update Intervals

The integration automatically adjusts update frequency based on context:

- **Bus approaching** (<10 min): Updates every 15 seconds
- **Normal hours** (6:00-22:00): Updates every 30 seconds (default)
- **Night hours** (22:00-6:00): Updates every 5 minutes
- **No upcoming buses** (>60 min): Updates every 5 minutes

This optimizes API usage while ensuring timely updates when you need them most.

### Error Handling

The integration includes robust error handling:

- **Automatic retries** with exponential backoff for network errors
- **Graceful degradation** when API is unavailable
- **Clear error messages** in the UI
- **Sensor availability tracking** - sensors marked unavailable during errors

## Data Source

This integration uses the [BusNearby API](https://app.busnearby.co.il), which provides real-time Israeli public transportation data. The API does not require authentication and is free to use.

## Troubleshooting

### Sensors Not Updating

1. Check your internet connection
2. Verify the station ID is correct
3. Ensure the bus lines serve that station
4. Check Home Assistant logs for errors: `Configuration` → `Logs`

### Station Not Found During Setup

- Double-check the station number at [bus.co.il](https://www.bus.co.il)
- Try entering the station number without any prefix
- Some stations may not be available in the API

### No Data for Specific Line

- Verify the line number is correct
- Check if the line serves this station
- The line may not be operating at the current time

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements_test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=custom_components.silent_bus --cov-report=html

# Run specific test file
pytest tests/unit/test_api.py
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- Integration developed by [@ziv-daniel](https://github.com/ziv-daniel)
- Data provided by [BusNearby](https://app.busnearby.co.il)
- Inspired by the original [silent-bus](https://github.com/silentbil/silent-bus) Lovelace card

## Support

- 🐛 **Report bugs**: [GitHub Issues](https://github.com/ziv-daniel/Silent-bus-integration/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ziv-daniel/Silent-bus-integration/discussions)
- 📖 **Documentation**: [Integration Plan](INTEGRATION_PLAN.md)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

---

**Disclaimer**: This is an unofficial integration and is not affiliated with or endorsed by the Israeli Ministry of Transportation or BusNearby.
