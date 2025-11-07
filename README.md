# SHRDZM Meter Integration

Integration for Home Assistant to read SHRDZM Smart Meter data via HTTP JSON interface.

## Features
- Stable entity IDs (`sensor.shrdzm_energy_import_total_kwh`, etc.)
- Wh→kWh auto conversion
- Uptime sensor
- Diagnostic service `shrdzm_meter.dump_raw`
- Configuration URL link in device info

## Installation
1. Add this repository to HACS (category: Integration).
2. Restart Home Assistant.
3. Add *SHRDZM Meter* integration via Settings → Devices & Services → Add Integration.

Version: 0.1.6 (2025-11-07)
