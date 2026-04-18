"""Button entities for Vigipool."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import VigipoolCoordinator
from .entity import VigipoolEntity
from .schedule import clear_slot


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Vigipool buttons."""
    coordinator: VigipoolCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities: list[ButtonEntity] = []
    for program_index in range(2):
        for slot_index in range(3):
            entities.append(
                VigipoolClearSlotButton(
                    coordinator,
                    program_index=program_index,
                    slot_index=slot_index,
                )
            )
    async_add_entities(entities)


class VigipoolClearSlotButton(VigipoolEntity, ButtonEntity):
    """Button to remove one filtration slot."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: VigipoolCoordinator,
        *,
        program_index: int,
        slot_index: int,
    ) -> None:
        super().__init__(
            coordinator,
            f"filter_program_{program_index + 1}_slot_{slot_index + 1}_clear",
        )
        self.program_index = program_index
        self.slot_index = slot_index
        self._attr_name = f"Clear program {program_index + 1} slot {slot_index + 1}"
        self._attr_icon = "mdi:delete-outline"

    @property
    def available(self) -> bool:
        """Return availability for the clear button."""
        schedule = self.coordinator.get_filter_schedule()
        if schedule is None:
            return False
        return schedule.programs[self.program_index].slots[self.slot_index] is not None

    async def async_press(self) -> None:
        """Clear the selected slot."""
        schedule = self.coordinator.get_filter_schedule()
        if schedule is None:
            return
        clear_slot(
            schedule,
            program_index=self.program_index,
            slot_index=self.slot_index,
        )
        await self.coordinator.async_set_filter_schedule(schedule)
