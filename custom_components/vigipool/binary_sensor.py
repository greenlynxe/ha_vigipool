"""Binary sensors for Vigipool."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    TOPIC_AUX_STATE,
    TOPIC_COVER_ON,
    TOPIC_FLOW_ON,
    TOPIC_LIGHT_STATE,
    TOPIC_MQTT_CONNECTED,
    TOPIC_SERVER_ON,
    TOPIC_WINTER_MODE,
)
from .coordinator import VigipoolCoordinator
from .entity import VigipoolEntity


@dataclass(frozen=True, kw_only=True)
class VigipoolBinarySensorDescription(BinarySensorEntityDescription):
    """Description for a Vigipool binary sensor."""

    topic_suffix: str


BINARY_SENSOR_DESCRIPTIONS: tuple[VigipoolBinarySensorDescription, ...] = (
    VigipoolBinarySensorDescription(
        key="flow_on",
        name="Flow on",
        topic_suffix=TOPIC_FLOW_ON,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    VigipoolBinarySensorDescription(
        key="cover_on",
        name="Cover on",
        topic_suffix=TOPIC_COVER_ON,
    ),
    VigipoolBinarySensorDescription(
        key="aux_state",
        name="Aux state",
        topic_suffix=TOPIC_AUX_STATE,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    VigipoolBinarySensorDescription(
        key="light_state",
        name="Light state",
        topic_suffix=TOPIC_LIGHT_STATE,
        device_class=BinarySensorDeviceClass.LIGHT,
    ),
    VigipoolBinarySensorDescription(
        key="mqtt_connected",
        name="MQTT connected",
        topic_suffix=TOPIC_MQTT_CONNECTED,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    VigipoolBinarySensorDescription(
        key="server_on",
        name="Server on",
        topic_suffix=TOPIC_SERVER_ON,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    VigipoolBinarySensorDescription(
        key="winter_mode",
        name="Winter mode",
        topic_suffix=TOPIC_WINTER_MODE,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Vigipool binary sensors."""
    coordinator: VigipoolCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        VigipoolBinaryTopicSensor(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class VigipoolBinaryTopicSensor(VigipoolEntity, BinarySensorEntity):
    """Binary sensor backed by a Vigipool MQTT topic."""

    entity_description: VigipoolBinarySensorDescription

    def __init__(
        self,
        coordinator: VigipoolCoordinator,
        description: VigipoolBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name

    @property
    def available(self) -> bool:
        """Return availability for the topic-backed binary sensor."""
        return self.raw_value(self.entity_description.topic_suffix) is not None

    @property
    def is_on(self) -> bool | None:
        """Return the boolean MQTT state."""
        value = self.int_value(self.entity_description.topic_suffix)
        if value is None:
            return None
        return value != 0
