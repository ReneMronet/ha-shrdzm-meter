# SHRDZM Meter (HTTP JSON)
# Version: 0.1.4
# File: custom_components/shrdzm_meter/sensor.py
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfElectricPotential, UnitOfElectricCurrent, UnitOfPower, UnitOfEnergy, UnitOfApparentPower, UnitOfTime
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SHRDZMMeterCoordinator
from .const import DOMAIN, SENSORS

UNIT_MAP = {
    "V": UnitOfElectricPotential.VOLT,
    "A": UnitOfElectricCurrent.AMPERE,
    "kW": UnitOfPower.KILO_WATT,
    "kWh": UnitOfEnergy.KILO_WATT_HOUR,
    "kVA": UnitOfApparentPower.KILO_VOLT_AMPERE,
    "s": UnitOfTime.SECONDS,
}

DEVICE_CLASS_MAP = {
    "voltage": SensorDeviceClass.VOLTAGE,
    "current": SensorDeviceClass.CURRENT,
    "power": SensorDeviceClass.POWER,
    "energy": SensorDeviceClass.ENERGY,
    "duration": SensorDeviceClass.DURATION,
}


class BaseEntity(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = False  # use suggested_object_id for stable entity_id

    def __init__(self, coordinator: SHRDZMMeterCoordinator, key: str, name: str, suggested_object_id: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_suggested_object_id = suggested_object_id

    @property
    def device_info(self):
        d = self.coordinator.data or {}
        devid = d.get("device_id") or "shrdzm_meter"
        return {
            "identifiers": {(DOMAIN, devid)},
            "manufacturer": "SHRDZM",
            "model": "Meter",
            "name": f"SHRDZM Meter {devid}",
        }

    @property
    def unique_id(self) -> str:
        d = self.coordinator.data or {}
        devid = d.get("device_id") or "unknown"
        return f"{devid}_{self._key}"


class MeterNumber(BaseEntity):
    def __init__(self, coordinator, key, name, unit_symbol, device_class_key, state_class, suggested_object_id) -> None:
        super().__init__(coordinator, key, name, suggested_object_id)
        unit = UNIT_MAP.get(unit_symbol)
        if unit:
            self._attr_native_unit_of_measurement = unit
        dc = DEVICE_CLASS_MAP.get(device_class_key)
        if dc:
            self._attr_device_class = dc
        if state_class:
            self._attr_state_class = state_class

    @property
    def native_value(self):
        d = self.coordinator.data or {}
        return d.get(self._key)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add_entities: AddEntitiesCallback) -> None:
    coord: SHRDZMMeterCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities: list[SensorEntity] = []
    for key, name, unit, dc, sc, sid in SENSORS:
        entities.append(MeterNumber(coord, key, name, unit, dc, sc, sid))
    add_entities(entities)
