"""Shared entity helpers for Vigipool."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, TOPIC_MODEL_ID, TOPIC_SERIAL, TOPIC_SW_VERSION
from .coordinator import VigipoolCoordinator


class VigipoolEntity(CoordinatorEntity[VigipoolCoordinator]):
    """Common base entity for Vigipool."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: VigipoolCoordinator, unique_suffix: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.topic_prefix}_{unique_suffix}"

    @property
    def available(self) -> bool:
        """Return True once at least one MQTT state has been received."""
        return bool(self.coordinator.data.topic_values)

    @property
    def device_info(self) -> DeviceInfo:
        """Return the Vigipool device info."""
        serial = self.coordinator.get(TOPIC_SERIAL)
        model_id = self.coordinator.get(TOPIC_MODEL_ID)
        sw_version = self.coordinator.get(TOPIC_SW_VERSION)
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.topic_prefix)},
            manufacturer="Vigipool",
            model=f"Controller {model_id}" if model_id is not None else "Pool Controller",
            name=self.coordinator.device_name,
            serial_number=serial,
            sw_version=sw_version,
        )

    def raw_value(self, topic_suffix: str) -> str | None:
        """Return a raw MQTT value."""
        return self.coordinator.get(topic_suffix)

    def int_value(self, topic_suffix: str) -> int | None:
        """Return an integer MQTT value."""
        return self.coordinator.get_int(topic_suffix)

    def float_value(self, topic_suffix: str, *, divisor: float = 1.0) -> float | None:
        """Return a float MQTT value."""
        return self.coordinator.get_float(topic_suffix, divisor=divisor)
