"""Time entities for Vigipool filtration schedules."""

from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import VigipoolCoordinator
from .entity import VigipoolEntity
from .schedule import (
    format_slot_index,
    set_slot_time,
    slot_index_to_time,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Vigipool schedule time entities."""
    coordinator: VigipoolCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities: list[TimeEntity] = []
    for program_index in range(2):
        for slot_index in range(3):
            entities.append(
                VigipoolProgramSlotTimeEntity(
                    coordinator,
                    program_index=program_index,
                    slot_index=slot_index,
                    is_start=True,
                )
            )
            entities.append(
                VigipoolProgramSlotTimeEntity(
                    coordinator,
                    program_index=program_index,
                    slot_index=slot_index,
                    is_start=False,
                )
            )
    async_add_entities(entities)


class VigipoolProgramSlotTimeEntity(VigipoolEntity, TimeEntity):
    """One slot boundary in the filtration schedule."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: VigipoolCoordinator,
        *,
        program_index: int,
        slot_index: int,
        is_start: bool,
    ) -> None:
        suffix = "start" if is_start else "end"
        super().__init__(
            coordinator,
            f"filter_program_{program_index + 1}_slot_{slot_index + 1}_{suffix}",
        )
        self.program_index = program_index
        self.slot_index = slot_index
        self.is_start = is_start
        self._attr_name = (
            f"Program {program_index + 1} slot {slot_index + 1} {suffix}"
        )
        self._attr_icon = "mdi:clock-outline"

    @property
    def available(self) -> bool:
        """Return availability for the slot boundary."""
        schedule = self.coordinator.get_filter_schedule()
        if schedule is None:
            return False

        slots = schedule.programs[self.program_index].slots
        if slots[self.slot_index] is not None:
            return True

        try:
            next_empty = slots.index(None)
        except ValueError:
            return False

        return self.slot_index == next_empty

    @property
    def native_value(self) -> time:
        """Return the current slot boundary."""
        schedule = self.coordinator.get_filter_schedule()
        if schedule is None:
            return time(hour=0, minute=0)

        slot = schedule.programs[self.program_index].slots[self.slot_index]
        if slot is None:
            return time(hour=0, minute=0)

        boundary = slot.start_index if self.is_start else slot.end_index
        return slot_index_to_time(boundary)

    @property
    def extra_state_attributes(self) -> dict[str, bool | str]:
        """Expose current slot metadata."""
        schedule = self.coordinator.get_filter_schedule()
        if schedule is None:
            return {"slot_active": False}

        slot = schedule.programs[self.program_index].slots[self.slot_index]
        if slot is None:
            return {"slot_active": False}

        return {
            "slot_active": True,
            "start": format_slot_index(slot.start_index),
            "end": format_slot_index(slot.end_index),
        }

    async def async_set_value(self, value: time) -> None:
        """Update the slot boundary."""
        schedule = self.coordinator.get_filter_schedule()
        if schedule is None:
            return
        set_slot_time(
            schedule,
            program_index=self.program_index,
            slot_index=self.slot_index,
            is_start=self.is_start,
            value=value,
        )
        await self.coordinator.async_set_filter_schedule(schedule)
