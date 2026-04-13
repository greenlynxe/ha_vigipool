"""Switch entities for Vigipool."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    FILTER_STATE_BACKWASH,
    FILTER_STATE_FORCED,
    FILTER_STATE_OFF,
    FILTER_STATE_RINSE,
    TOPIC_FILT_STATE,
    TOPIC_FILT_STATE_DESIRED,
    TOPIC_FLOW_ON,
)
from .coordinator import VigipoolCoordinator
from .entity import VigipoolEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Vigipool switches."""
    coordinator: VigipoolCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([VigipoolFiltrationSwitch(coordinator)])


class VigipoolFiltrationSwitch(VigipoolEntity, SwitchEntity):
    """Switch to force filtration on or stop it."""

    _attr_name = "Filtration"
    _attr_icon = "mdi:pool-pump"

    def __init__(self, coordinator: VigipoolCoordinator) -> None:
        super().__init__(coordinator, "filtration_switch")

    @property
    def available(self) -> bool:
        """Return availability for the filtration switch."""
        return (
            self.raw_value(TOPIC_FILT_STATE) is not None
            or self.raw_value(TOPIC_FLOW_ON) is not None
        )

    @property
    def is_on(self) -> bool | None:
        """Return the current filtration state."""
        flow_on = self.int_value(TOPIC_FLOW_ON)
        if flow_on is not None and flow_on != 0:
            return True

        filter_state = self.int_value(TOPIC_FILT_STATE)
        if filter_state is None:
            return None

        return filter_state in {
            FILTER_STATE_FORCED,
            FILTER_STATE_BACKWASH,
            FILTER_STATE_RINSE,
        }

    @property
    def extra_state_attributes(self) -> dict[str, int | None]:
        """Expose the raw state used for the switch."""
        return {
            "filter_state_code": self.int_value(TOPIC_FILT_STATE),
            "flow_on": self.int_value(TOPIC_FLOW_ON),
            "command_topic": f"{self.coordinator.topic_prefix}/{TOPIC_FILT_STATE_DESIRED}",
        }

    async def async_turn_on(self, **kwargs) -> None:
        """Force filtration on."""
        await self.coordinator.async_publish_value(
            TOPIC_FILT_STATE_DESIRED,
            FILTER_STATE_FORCED,
            optimistic_reported_suffix=TOPIC_FILT_STATE,
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Stop filtration."""
        await self.coordinator.async_publish_value(
            TOPIC_FILT_STATE_DESIRED,
            FILTER_STATE_OFF,
            optimistic_reported_suffix=TOPIC_FILT_STATE,
        )
