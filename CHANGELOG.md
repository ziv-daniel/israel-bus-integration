# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-24

### Added
- Initial release of Silent Bus Home Assistant integration
- Real-time bus arrival tracking for Israeli public transportation
- Support for multiple stations and bus lines
- UI-based configuration flow with station and line selection
- Dynamic update intervals based on bus proximity and time of day
- Comprehensive sensor entities with rich attributes
- Bilingual support (English and Hebrew)
- Automatic error handling and retry logic
- Options flow for reconfiguring existing integrations
- Full test coverage (unit and integration tests)
- HACS compatibility

### Features
- BusNearby API integration for real-time data
- DataUpdateCoordinator for efficient data management
- Smart update intervals (15-300 seconds based on context)
- Per-line sensor entities with unique IDs
- Device registry integration
- Sensor attributes including:
  - Next arrival time
  - Real-time vs scheduled data
  - Bus direction/destination
  - List of upcoming arrivals
  - Last update timestamp

### Documentation
- Comprehensive README with usage examples
- Detailed integration plan document
- Configuration guide
- Automation examples
- Troubleshooting section

### Testing
- Unit tests for API client
- Unit tests for coordinator
- Unit tests for config flow
- Unit tests for sensors
- Integration tests for setup/unload
- 90%+ code coverage

---

## Release Notes

This is the first production-ready release of the Silent Bus integration. The integration has been thoroughly tested and is ready for daily use.

### Known Limitations
- Currently supports bus tracking only (train support planned for v1.1)
- Relies on BusNearby API availability
- No offline mode (planned for future release)

### Upgrade Path
- This is the initial release, no upgrade needed

### Breaking Changes
- None (initial release)
