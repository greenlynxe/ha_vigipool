"""Light entities for Vigipool."""

from __future__ import annotations

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    LIGHT_STATE_OFF,
    LIGHT_STATE_ON,
    TOPIC_LIGHT_STATE,
    TOPIC_LIGHT_STATE_DESIRED,
)
from .coordinator import VigipoolCoordinator
from .entity import VigipoolEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Vigipool lights."""
    coordinator: VigipoolCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([VigipoolPoolLight(coordinator)])


class VigipoolPoolLight(VigipoolEntity, LightEntity):
    """Pool light controlled through the Vigipool MQTT bridge."""

    _attr_name = "Pool light"
    _attr_icon = "mdi:lightbulb"
    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(self, coordinator: VigipoolCoordinator) -> None:
        super().__init__(coordinator, "pool_light")

    @property
    def available(self) -> bool:
        """Return availability for the pool light."""
        return self.raw_value(TOPIC_LIGHT_STATE) is not None

    @property
    def is_on(self) -> bool | None:
        """Return whether the pool light is on."""
        value = self.int_value(TOPIC_LIGHT_STATE)
        if value is None:
            return None
        return value != LIGHT_STATE_OFF

    @property
    def color_mode(self) -> ColorMode | None:
        """Expose the supported color mode."""
        if self.is_on is None:
            return None
        return ColorMode.ONOFF

    @property
    def extra_state_attributes(self) -> dict[str, str | int | None]:
        """Expose the command topic used by the light."""
        return {
            "light_state_code": self.int_value(TOPIC_LIGHT_STATE),
            "command_topic": f"{self.coordinator.topic_prefix}/{TOPIC_LIGHT_STATE_DESIRED}",
        }

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the pool light on."""
        await self.coordinator.async_publish_value(
            TOPIC_LIGHT_STATE_DESIRED,
            LIGHT_STATE_ON,
            optimistic_reported_suffix=TOPIC_LIGHT_STATE,
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the pool light off."""
        await self.coordinator.async_publish_value(
            TOPIC_LIGHT_STATE_DESIRED,
            LIGHT_STATE_OFF,
            optimistic_reported_suffix=TOPIC_LIGHT_STATE,
        )
