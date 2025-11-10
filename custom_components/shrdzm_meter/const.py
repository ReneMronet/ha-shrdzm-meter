# SHRDZM Meter (HTTP JSON)
# Version: 0.1.4
# Date: 2025-11-07
# File: custom_components/shrdzm_meter/const.py

DOMAIN = "shrdzm_meter"
DEFAULT_SCAN_INTERVAL = 15  # seconds
DEFAULT_TIMEOUT = 8  # seconds total

SENSORS = [
    ("voltage_l1",            "Voltage L1",                   "V",    "voltage",  None,                "shrdzm_voltage_l1"),
    ("voltage_l2",            "Voltage L2",                   "V",    "voltage",  None,                "shrdzm_voltage_l2"),
    ("voltage_l3",            "Voltage L3",                   "V",    "voltage",  None,                "shrdzm_voltage_l3"),
    ("current_l1",            "Current L1",                   "A",    "current",  None,                "shrdzm_current_l1"),
    ("current_l2",            "Current L2",                   "A",    "current",  None,                "shrdzm_current_l2"),
    ("current_l3",            "Current L3",                   "A",    "current",  None,                "shrdzm_current_l3"),
    ("power_import_now",      "Active power import",          "kW",   "power",    "measurement",       "shrdzm_power_import_now"),
    ("power_export_now",      "Active power export",          "kW",   "power",    "measurement",       "shrdzm_power_export_now"),
    ("apparent_power_now",    "Apparent power",               "kVA",  None,       "measurement",       "shrdzm_apparent_power_now"),
    ("energy_import_total_kwh","Energy import total",         "kWh",  "energy",   "total_increasing",  "shrdzm_energy_import_total_kwh"),
    ("energy_export_total_kwh","Energy export total",         "kWh",  "energy",   "total_increasing",  "shrdzm_energy_export_total_kwh"),
    ("energy_reactive_import_kvarh","Reactive energy import", "kvarh",None,       "total_increasing",  "shrdzm_energy_reactive_import_kvarh"),
    ("energy_reactive_export_kvarh","Reactive energy export", "kvarh",None,       "total_increasing",  "shrdzm_energy_reactive_export_kvarh"),
    ("uptime_seconds",        "Device uptime seconds",        "s",    "duration", "measurement",       "shrdzm_uptime_seconds"),
    ("timestamp",             "Device timestamp",             None,   None,       None,                "shrdzm_timestamp"),
    ("utc",                   "Device UTC",                   None,   None,       None,                "shrdzm_utc"),
    ("uptime_str",            "Device uptime",                None,   None,       None,                "shrdzm_uptime_str"),
]
