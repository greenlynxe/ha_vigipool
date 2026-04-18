"""MQTT coordinator for Vigipool."""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_DEVICE_NAME,
    CONF_TOPIC_PREFIX,
    DOMAIN,
    TOPIC_FILT_SCHEDULE,
    TOPIC_FILT_SCHEDULE_DESIRED,
)
from .schedule import VigipoolFilterSchedule, decode_filter_schedule_payload, encode_filter_schedule_payload

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class VigipoolState:
    """State cache for one Vigipool controller."""

    topic_prefix: str
    topic_values: dict[str, str]
    last_message: datetime | None = None


class VigipoolCoordinator(DataUpdateCoordinator[VigipoolState]):
    """Subscribe to Vigipool MQTT topics and cache the retained state."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, logger=_LOGGER, name=DOMAIN, update_interval=None)
        self.entry = entry
        self.device_name = entry.options.get(
            CONF_DEVICE_NAME, entry.data[CONF_DEVICE_NAME]
        )
        self.topic_prefix = entry.options.get(
            CONF_TOPIC_PREFIX, entry.data[CONF_TOPIC_PREFIX]
        )
        self._unsubscribe: Any = None
        self.data = VigipoolState(topic_prefix=self.topic_prefix, topic_values={})

    async def async_start(self) -> None:
        """Start MQTT subscription."""
        topic = f"{self.topic_prefix}/#"
        self._unsubscribe = await mqtt.async_subscribe(
            self.hass,
            topic,
            self._message_received,
            qos=0,
            encoding="utf-8",
        )
        self.async_set_updated_data(self.data)

    async def async_stop(self) -> None:
        """Stop MQTT subscription."""
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None

    async def _async_update_data(self) -> VigipoolState:
        """Return current cached state."""
        return self.data

    @callback
    def _message_received(self, msg: mqtt.ReceiveMessage) -> None:
        """Handle one MQTT message."""
        payload = msg.payload
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8", errors="replace")
        suffix = self._strip_prefix(msg.topic)
        if suffix is None:
            return

        values = dict(self.data.topic_values)
        values[suffix] = str(payload)
        self.async_set_updated_data(
            replace(
                self.data,
                topic_values=values,
                last_message=datetime.now(timezone.utc),
            )
        )

    def get(self, topic_suffix: str) -> str | None:
        """Return a raw topic value by suffix."""
        return self.data.topic_values.get(topic_suffix)

    def get_int(self, topic_suffix: str) -> int | None:
        """Return a topic value coerced to int."""
        value = self.get(topic_suffix)
        if value is None or value == "":
            return None
        try:
            return int(value)
        except ValueError:
            return None

    def get_float(self, topic_suffix: str, *, divisor: float = 1.0) -> float | None:
        """Return a topic value coerced to float."""
        value = self.get_int(topic_suffix)
        if value is None:
            return None
        return value / divisor

    def get_filter_schedule(self) -> VigipoolFilterSchedule | None:
        """Return the decoded filtration schedule."""
        payload = self.get(TOPIC_FILT_SCHEDULE)
        if payload is None:
            return None
        return decode_filter_schedule_payload(payload)

    async def async_publish_value(
        self,
        desired_topic_suffix: str,
        payload: str | int,
        *,
        optimistic_reported_suffix: str | None = None,
    ) -> None:
        """Publish a command and optionally update the local cache optimistically."""
        topic = f"{self.topic_prefix}/{desired_topic_suffix}"
        string_payload = str(payload)
        mqtt.async_publish(
            self.hass,
            topic,
            string_payload,
            qos=0,
            retain=False,
            encoding="utf-8",
        )

        if optimistic_reported_suffix is not None:
            self._update_cached_value(optimistic_reported_suffix, string_payload)

    async def async_set_filter_schedule(self, schedule: VigipoolFilterSchedule) -> None:
        """Publish an updated filtration schedule."""
        payload = encode_filter_schedule_payload(schedule)
        await self.async_publish_value(
            TOPIC_FILT_SCHEDULE_DESIRED,
            payload,
            optimistic_reported_suffix=TOPIC_FILT_SCHEDULE,
        )

    def _update_cached_value(self, topic_suffix: str, payload: str) -> None:
        """Merge a local optimistic value into the MQTT cache."""
        values = dict(self.data.topic_values)
        values[topic_suffix] = payload
        self.async_set_updated_data(
            replace(
                self.data,
                topic_values=values,
                last_message=datetime.now(timezone.utc),
            )
        )

    def _strip_prefix(self, topic: str) -> str | None:
        """Strip the device prefix from an MQTT topic."""
        prefix = f"{self.topic_prefix}/"
        if not topic.startswith(prefix):
            return None
        return topic[len(prefix) :]
