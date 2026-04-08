"""Sensor entities for Vigipool."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    TOPIC_ACTION,
    TOPIC_AUX_CONFIG,
    TOPIC_AUX_MIN_TEMP,
    TOPIC_AUX_SCHEDULE,
    TOPIC_AUX_TEMP_HYST,
    TOPIC_AUX_TYPE,
    TOPIC_BACKWASH,
    TOPIC_DEVICE_ID,
    TOPIC_ERROR_CODE,
    TOPIC_FILT_SCHEDULE,
    TOPIC_FILT_SERVICE_INTERVAL,
    TOPIC_FILT_STATE,
    TOPIC_FROST_FREE,
    TOPIC_HW_VERSION,
    TOPIC_LIGHT_BRIGHTNESS,
    TOPIC_LIGHT_CODE,
    TOPIC_LIGHT_SCHEDULE,
    TOPIC_LIGHT_SPEED,
    TOPIC_LIGHT_TYPE,
    TOPIC_MODEL_ID,
    TOPIC_POOL_TEMPERATURE,
    TOPIC_RSSI,
    TOPIC_SERIAL,
    TOPIC_STATE_BITS,
    TOPIC_SW_VERSION,
    TOPIC_TEMPERATURE_SETPOINT,
)
from .coordinator import VigipoolCoordinator
from .entity import VigipoolEntity


@dataclass(frozen=True, kw_only=True)
class VigipoolSensorDescription(SensorEntityDescription):
    """Description for a Vigipool topic sensor."""

    topic_suffix: str
    divisor: float = 1.0
    value_type: str = "int"


@dataclass(frozen=True, kw_only=True)
class VigipoolMappedSensorDescription(SensorEntityDescription):
    """Description for a computed Vigipool text sensor."""

    value_fn: Callable[[VigipoolCoordinator], str | None]
    raw_topic_suffix: str | None = None


NUMERIC_SENSOR_DESCRIPTIONS: tuple[VigipoolSensorDescription, ...] = (
    VigipoolSensorDescription(
        key="pool_temperature",
        name="Pool temperature",
        topic_suffix=TOPIC_POOL_TEMPERATURE,
        divisor=10.0,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    VigipoolSensorDescription(
        key="temperature_setpoint",
        name="Temperature setpoint",
        topic_suffix=TOPIC_TEMPERATURE_SETPOINT,
        divisor=10.0,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=1,
    ),
    VigipoolSensorDescription(
        key="filter_state_code",
        name="Filter state code",
        topic_suffix=TOPIC_FILT_STATE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="error_code",
        name="Error code",
        topic_suffix=TOPIC_ERROR_CODE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="state_bits",
        name="State bitmask",
        topic_suffix=TOPIC_STATE_BITS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="rssi",
        name="Wi-Fi RSSI",
        topic_suffix=TOPIC_RSSI,
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="model_id",
        name="Model ID",
        topic_suffix=TOPIC_MODEL_ID,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="hardware_version",
        name="Hardware version",
        topic_suffix=TOPIC_HW_VERSION,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="software_version",
        name="Software version",
        topic_suffix=TOPIC_SW_VERSION,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="action_code",
        name="Action code",
        topic_suffix=TOPIC_ACTION,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="filter_service_interval",
        name="Filter service interval",
        topic_suffix=TOPIC_FILT_SERVICE_INTERVAL,
        native_unit_of_measurement=UnitOfTime.HOURS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="light_type",
        name="Light type",
        topic_suffix=TOPIC_LIGHT_TYPE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="light_code",
        name="Light code",
        topic_suffix=TOPIC_LIGHT_CODE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="light_brightness",
        name="Light brightness",
        topic_suffix=TOPIC_LIGHT_BRIGHTNESS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="light_speed",
        name="Light speed",
        topic_suffix=TOPIC_LIGHT_SPEED,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="aux_type",
        name="Aux type",
        topic_suffix=TOPIC_AUX_TYPE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="aux_config",
        name="Aux config",
        topic_suffix=TOPIC_AUX_CONFIG,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="aux_minimum_temperature",
        name="Aux minimum temperature",
        topic_suffix=TOPIC_AUX_MIN_TEMP,
        divisor=10.0,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="aux_temperature_hysteresis",
        name="Aux temperature hysteresis",
        topic_suffix=TOPIC_AUX_TEMP_HYST,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="frost_free_mode",
        name="Frost free mode",
        topic_suffix=TOPIC_FROST_FREE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="backwash_code",
        name="Backwash code",
        topic_suffix=TOPIC_BACKWASH,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

TEXT_SENSOR_DESCRIPTIONS: tuple[VigipoolSensorDescription, ...] = (
    VigipoolSensorDescription(
        key="filter_schedule_raw",
        name="Filter schedule raw",
        topic_suffix=TOPIC_FILT_SCHEDULE,
        value_type="str",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="light_schedule_raw",
        name="Light schedule raw",
        topic_suffix=TOPIC_LIGHT_SCHEDULE,
        value_type="str",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="aux_schedule_raw",
        name="Aux schedule raw",
        topic_suffix=TOPIC_AUX_SCHEDULE,
        value_type="str",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="serial_number_raw",
        name="Serial number raw",
        topic_suffix=TOPIC_SERIAL,
        value_type="str",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolSensorDescription(
        key="device_id",
        name="Device ID",
        topic_suffix=TOPIC_DEVICE_ID,
        value_type="str",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

MAPPED_SENSOR_DESCRIPTIONS: tuple[VigipoolMappedSensorDescription, ...] = (
    VigipoolMappedSensorDescription(
        key="filter_state",
        name="Filter state",
        value_fn=lambda coordinator: _describe_filter_state(coordinator),
        raw_topic_suffix=TOPIC_FILT_STATE,
    ),
    VigipoolMappedSensorDescription(
        key="action",
        name="Action",
        value_fn=lambda coordinator: _describe_action(coordinator),
        raw_topic_suffix=TOPIC_ACTION,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    VigipoolMappedSensorDescription(
        key="aux_type_name",
        name="Aux mode",
        value_fn=lambda coordinator: _describe_aux_type(coordinator),
        raw_topic_suffix=TOPIC_AUX_TYPE,
    ),
    VigipoolMappedSensorDescription(
        key="frost_free_status",
        name="Frost free status",
        value_fn=lambda coordinator: _describe_frost_free(coordinator),
        raw_topic_suffix=TOPIC_FROST_FREE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Vigipool sensors."""
    coordinator: VigipoolCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities: list[SensorEntity] = [
        VigipoolTopicSensor(coordinator, description)
        for description in NUMERIC_SENSOR_DESCRIPTIONS + TEXT_SENSOR_DESCRIPTIONS
    ]
    entities.extend(
        VigipoolMappedSensor(coordinator, description)
        for description in MAPPED_SENSOR_DESCRIPTIONS
    )
    entities.append(VigipoolRawTopicsSensor(coordinator))
    async_add_entities(entities)


class VigipoolTopicSensor(VigipoolEntity, SensorEntity):
    """Sensor backed by a single Vigipool MQTT topic."""

    entity_description: VigipoolSensorDescription

    def __init__(
        self, coordinator: VigipoolCoordinator, description: VigipoolSensorDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name

    @property
    def available(self) -> bool:
        """Return availability for the topic-backed sensor."""
        return self.raw_value(self.entity_description.topic_suffix) is not None

    @property
    def native_value(self) -> str | int | float | None:
        """Return the parsed MQTT value."""
        if self.entity_description.value_type == "str":
            return self.raw_value(self.entity_description.topic_suffix)

        if self.entity_description.divisor != 1.0:
            return self.float_value(
                self.entity_description.topic_suffix,
                divisor=self.entity_description.divisor,
            )

        return self.int_value(self.entity_description.topic_suffix)


class VigipoolRawTopicsSensor(VigipoolEntity, SensorEntity):
    """Diagnostic sensor exposing all cached Vigipool MQTT topics."""

    _attr_name = "Raw MQTT topics"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: VigipoolCoordinator) -> None:
        super().__init__(coordinator, "raw_topics")

    @property
    def native_value(self) -> int | None:
        """Return the number of cached topics."""
        if self.coordinator.data is None:
            return None
        return len(self.coordinator.data.topic_values)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Expose all cached topic values."""
        if self.coordinator.data is None:
            return None
        return {
            "topic_prefix": self.coordinator.topic_prefix,
            "last_message": _as_iso(self.coordinator.data.last_message),
            "topics": dict(sorted(self.coordinator.data.topic_values.items())),
        }


class VigipoolMappedSensor(VigipoolEntity, SensorEntity):
    """Sensor exposing a human-readable Vigipool state."""

    entity_description: VigipoolMappedSensorDescription

    def __init__(
        self,
        coordinator: VigipoolCoordinator,
        description: VigipoolMappedSensorDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name

    @property
    def available(self) -> bool:
        """Return availability for the computed sensor."""
        return self.native_value is not None

    @property
    def native_value(self) -> str | None:
        """Return the computed human-readable value."""
        return self.entity_description.value_fn(self.coordinator)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Expose the underlying numeric code when available."""
        raw_topic_suffix = self.entity_description.raw_topic_suffix
        if raw_topic_suffix is None:
            return None

        raw_value = self.raw_value(raw_topic_suffix)
        if raw_value is None:
            return None

        return {"raw_code": raw_value}


def _as_iso(value: datetime | None) -> str | None:
    """Serialize datetimes for HA attributes."""
    if value is None:
        return None
    return value.isoformat()


def _describe_filter_state(coordinator: VigipoolCoordinator) -> str | None:
    """Return a human-readable filtration state."""
    code = coordinator.get_int(TOPIC_FILT_STATE)
    if code is None:
        return None

    flow_on = coordinator.get_int(TOPIC_FLOW_ON)
    if code == 0:
        return "Running" if flow_on else "Stopped"

    if code == 1:
        return "Scheduled"
    if code == 2:
        return "Forced"
    if code == 3:
        return "Backwash"
    if code == 4:
        return "Rinse"

    return f"State {code}"


def _describe_action(coordinator: VigipoolCoordinator) -> str | None:
    """Return a human-readable action state."""
    code = coordinator.get_int(TOPIC_ACTION)
    if code is None:
        return None
    if code == 0:
        return "Idle"
    return f"Action {code}"


def _describe_aux_type(coordinator: VigipoolCoordinator) -> str | None:
    """Return a best-effort auxiliary type label."""
    code = coordinator.get_int(TOPIC_AUX_TYPE)
    if code is None:
        return None
    if code == 0:
        return "Disabled"
    if code == 1:
        return "Relay"
    if code == 2:
        return "Temperature relay"
    return f"Type {code}"


def _describe_frost_free(coordinator: VigipoolCoordinator) -> str | None:
    """Return a best-effort frost protection label."""
    code = coordinator.get_int(TOPIC_FROST_FREE)
    if code is None:
        return None
    if code == 0:
        return "Disabled"
    if code == 1:
        return "Enabled"
    if code == 2:
        return "Automatic"
    return f"Mode {code}"
