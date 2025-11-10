# SHRDZM Meter (HTTP JSON)
# Version: 0.1.4+options
# File: custom_components/shrdzm_meter/config_flow.py
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from . import _fetch  # verwendet _fetch aus __init__.py


def _schema(defaults: dict | None = None) -> vol.Schema:
    d = defaults or {}
    return vol.Schema({
        vol.Required(CONF_HOST, default=d.get(CONF_HOST, "")): str,
        vol.Required(CONF_USERNAME, default=d.get(CONF_USERNAME, "")): str,
        vol.Required(CONF_PASSWORD, default=d.get(CONF_PASSWORD, "")): str,
        vol.Optional("scan_interval", default=d.get("scan_interval", DEFAULT_SCAN_INTERVAL)): vol.All(int, vol.Range(min=5, max=3600)),
    })


class SHRDZMMeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Ersteinrichtung via UI."""
    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=_schema())

        # Verbindungscheck
        try:
            await _fetch(self.hass, _DummyEntry(user_input))
        except Exception:
            return self.async_show_form(step_id="user", data_schema=_schema(user_input), errors={"base": "cannot_connect"})

        unique_id = user_input[CONF_HOST].strip()
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"SHRDZM Meter {unique_id}",
            data={
                "host": user_input[CONF_HOST].strip(),
                "user": user_input[CONF_USERNAME],
                "password": user_input[CONF_PASSWORD],
                "scan_interval": user_input.get("scan_interval", DEFAULT_SCAN_INTERVAL),
            },
        )


# ---------- Options Flow (Zahnrad) ----------
async def async_get_options_flow(config_entry: config_entries.ConfigEntry):
    return SHRDZMMeterOptionsFlow(config_entry)


class SHRDZMMeterOptionsFlow(config_entries.OptionsFlow):
    """Nachträgliche Einstellungen per Zahnrad."""
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        # Data + Options mergen für Defaults
        merged = {**self.entry.data, **self.entry.options}

        if user_input is not None:
            # In OPTIONS speichern; __init__ liest Optionen priorisiert
            return self.async_create_entry(title="", data={
                "host": user_input[CONF_HOST].strip(),
                "user": user_input[CONF_USERNAME],
                "password": user_input[CONF_PASSWORD],
                "scan_interval": user_input["scan_interval"],
            })

        return self.async_show_form(step_id="init", data_schema=_schema(merged))


# ---------- Hilfsklassen ----------
class _DummyEntry:
    """Minimaler Wrapper, damit _fetch wie bei echtem Entry arbeitet."""
    def __init__(self, data: dict) -> None:
        self.data = data
        self.options = {}
