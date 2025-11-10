# SHRDZM Meter (HTTP JSON)
# Version: 0.1.5
# File: custom_components/shrdzm_meter/__init__.py
from __future__ import annotations

import json as _json
import logging
from datetime import timedelta
from urllib.parse import urlencode, urlparse

from homeassistant.components.persistent_notification import async_create as pn_create
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, DEFAULT_TIMEOUT, SENSORS

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]
SERVICE_DUMP_RAW = "dump_raw"


# YAML-Setup erlauben, falls jemand versehentlich einen YAML-Block anlegt
async def async_setup(hass, config):
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = SHRDZMMeterCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"coordinator": coordinator}

    # Migration auf stabile Entity-IDs
    ent_reg = er.async_get(hass)
    devid = (coordinator.data or {}).get("device_id") or "unknown"
    for key, _name, _unit, _dc, _sc, suggested in SENSORS:
        unique = f"{devid}_{key}"
        entity_id = ent_reg.async_get_entity_id("sensor", DOMAIN, unique_id=unique)
        target = f"sensor.{suggested}"
        if entity_id and entity_id != target:
            try:
                ent_reg.async_update_entity(entity_id, new_entity_id=target)
                _LOGGER.info("Renamed %s -> %s", entity_id, target)
            except Exception as e:
                _LOGGER.debug("Skip rename %s -> %s: %s", entity_id, target, e)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_update_listener))

    async def _svc_dump_raw(call: ServiceCall):
        blocks = []
        for eid, store in hass.data.get(DOMAIN, {}).items():
            coord = store["coordinator"]
            raw = (coord.data or {}).get("raw", None)
            devid2 = (coord.data or {}).get("device_id", eid)
            if raw is None:
                blocks.append(f"<b>{devid2}</b>: keine Daten")
            else:
                txt = _json.dumps(raw, ensure_ascii=False, indent=2)
                _LOGGER.info("SHRDZM dump_raw (%s):\n%s", devid2, txt)
                blocks.append(f"<b>{devid2}</b>:<pre>{txt}</pre>")
        html = "<h3>SHRDZM Rohdaten</h3>" + "<hr>".join(blocks)
        pn_create(hass, html, title="SHRDZM Meter", notification_id=f"{DOMAIN}_dump_raw")

    hass.services.async_register(DOMAIN, SERVICE_DUMP_RAW, _svc_dump_raw)
    entry.async_on_unload(lambda: hass.services.async_remove(DOMAIN, SERVICE_DUMP_RAW))
    return True


async def _update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


class SHRDZMMeterCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        scan = entry.options.get("scan_interval", entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL))
        super().__init__(
            hass,
            _LOGGER,
            name="SHRDZM Meter Coordinator",
            update_interval=timedelta(seconds=scan),
        )

    async def _async_update_data(self):
        try:
            return await _fetch(self.hass, self.entry)
        except Exception as err:
            raise UpdateFailed(str(err)) from err


def _build_url(host: str, user: str, password: str) -> str:
    h = host.strip()
    parsed = urlparse(h if "://" in h else "http://" + h.lstrip("/"))
    base = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path or "/getLastData"
    if "getLastData" not in path:
        path = "/getLastData"
    query = urlencode({"user": user, "password": password})
    return f"{base}{path}?{query}"


async def _fetch(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    import aiohttp
    # Optionen priorisieren
    merged = {**entry.data, **entry.options}
    host = merged.get("host") or merged.get(CONF_HOST)
    user = merged.get("user") or merged.get(CONF_USERNAME)
    password = merged.get("password") or merged.get(CONF_PASSWORD)
    if not host or not user or not password:
        raise RuntimeError("missing_credential")
    url = _build_url(host, user, password)
    timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    _LOGGER.debug("SHRDZM request URL: %s", url)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            text = await resp.text()
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status}: {text[:160]}")
            try:
                data = await resp.json(content_type=None)
            except Exception:
                clean = text.lstrip("\ufeff").strip()
                if clean.endswith(";"):
                    clean = clean[:-1]
                data = _json.loads(clean)
    return _normalize(data)


def _parse_uptime_to_seconds(s: str | None) -> int | None:
    if not s:
        return None
    parts = s.split(":")
    try:
        if len(parts) == 4:
            days, hh, mm, ss = map(int, parts)
            return days * 86400 + hh * 3600 + mm * 60 + ss
        if len(parts) == 3:
            hh, mm, ss = map(int, parts)
            return hh * 3600 + mm * 60 + ss
    except Exception:
        return None
    return None


def _auto_kwh(v):
    try:
        fv = float(v)
    except Exception:
        return None
    return fv / 1000.0 if fv >= 100000.0 else fv


def _normalize(d: dict) -> dict:
    def f(v):
        try:
            return float(v)
        except Exception:
            return None

    return {
        "device_id": d.get("id"),
        "timestamp": d.get("timestamp"),
        "utc": d.get("UTC"),
        "uptime_str": d.get("uptime"),
        "uptime_seconds": _parse_uptime_to_seconds(d.get("uptime")),
        "voltage_l1": f(d.get("32.7.0")),
        "voltage_l2": f(d.get("52.7.0")),
        "voltage_l3": f(d.get("72.7.0")),
        "current_l1": f(d.get("31.7.0")),
        "current_l2": f(d.get("51.7.0")),
        "current_l3": f(d.get("71.7.0")),
        "power_import_now": f(d.get("1.7.0")),
        "power_export_now": f(d.get("2.7.0")),
        "apparent_power_now": f(d.get("16.7.0")),
        "energy_import_total_kwh": _auto_kwh(d.get("1.8.0")),
        "energy_export_total_kwh": _auto_kwh(d.get("2.8.0")),
        "energy_reactive_import_kvarh": _auto_kwh(d.get("3.8.0")),
        "energy_reactive_export_kvarh": _auto_kwh(d.get("4.8.0")),
        "raw": d,
    }
