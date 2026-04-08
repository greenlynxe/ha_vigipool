"""Config flow for Vigipool."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_DEVICE_NAME,
    CONF_TOPIC_PREFIX,
    DEFAULT_DEVICE_NAME,
    DEFAULT_TOPIC_PREFIX,
    DOMAIN,
)


class VigipoolConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle Vigipool configuration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure the topic prefix."""
        if user_input is not None:
            topic_prefix = user_input[CONF_TOPIC_PREFIX].strip()
            await self.async_set_unique_id(topic_prefix)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_DEVICE_NAME].strip(),
                data={
                    CONF_DEVICE_NAME: user_input[CONF_DEVICE_NAME].strip(),
                    CONF_TOPIC_PREFIX: topic_prefix,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_NAME, default=DEFAULT_DEVICE_NAME): str,
                    vol.Required(CONF_TOPIC_PREFIX, default=DEFAULT_TOPIC_PREFIX): str,
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow."""
        return VigipoolOptionsFlow(config_entry)


class VigipoolOptionsFlow(config_entries.OptionsFlow):
    """Manage Vigipool options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_name = self.config_entry.options.get(
            CONF_DEVICE_NAME,
            self.config_entry.data.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME),
        )
        current_prefix = self.config_entry.options.get(
            CONF_TOPIC_PREFIX,
            self.config_entry.data.get(CONF_TOPIC_PREFIX, DEFAULT_TOPIC_PREFIX),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_NAME, default=current_name): str,
                    vol.Required(CONF_TOPIC_PREFIX, default=current_prefix): str,
                }
            ),
        )

