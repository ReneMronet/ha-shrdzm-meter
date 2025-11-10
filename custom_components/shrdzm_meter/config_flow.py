# SHRDZM Meter (HTTP JSON)
# Version: 0.1.4
# Date: 2025-11-07
# File: custom_components/shrdzm_meter/config_flow.py
from __future__ import annotations

import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from . import _fetch


class SHRDZMMeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): int,
                }),
            )

        test_entry = DummyEntry(user_input)
        try:
            data = await _fetch(self.hass, test_entry)
        except Exception:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_HOST, default=user_input.get(CONF_HOST, "")): str,
                    vol.Required(CONF_USERNAME, default=user_input.get(CONF_USERNAME, "")): str,
                    vol.Required(CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, "")): str,
                    vol.Optional("scan_interval", default=user_input.get("scan_interval", DEFAULT_SCAN_INTERVAL)): int,
                }),
                errors={"base": "cannot_connect"},
            )

        unique_id = data.get("device_id") or user_input[CONF_HOST]
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"SHRDZM Meter {unique_id}",
            data={"host": user_input[CONF_HOST].strip(), "user": user_input[CONF_USERNAME], "password": user_input[CONF_PASSWORD], "scan_interval": user_input.get("scan_interval", DEFAULT_SCAN_INTERVAL)},
        )


class DummyEntry:
    def __init__(self, data: dict):
        self.data = data
        self.options = {}
