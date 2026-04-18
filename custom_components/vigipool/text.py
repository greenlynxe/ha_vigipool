"""Text entities for compact Vigipool schedule editing."""

from __future__ import annotations

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import VigipoolCoordinator
from .entity import VigipoolEntity
from .schedule import format_days_mask, format_slots, parse_days_input, parse_slots_input


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Vigipool text entities."""
    coordinator: VigipoolCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities: list[TextEntity] = []

    for program_index in range(2):
        entities.append(VigipoolProgramDaysText(coordinator, program_index))
        entities.append(VigipoolProgramSlotsText(coordinator, program_index))

    async_add_entities(entities)


class VigipoolScheduleTextEntity(VigipoolEntity, TextEntity):
    """Base class for compact schedule editing text entities."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = TextMode.TEXT

    def __init__(self, coordinator: VigipoolCoordinator, unique_suffix: str) -> None:
        super().__init__(coordinator, unique_suffix)

    @property
    def available(self) -> bool:
        """Return availability for schedule text entities."""
        return self.coordinator.get_filter_schedule() is not None


class VigipoolProgramDaysText(VigipoolScheduleTextEntity):
    """Editable day list for one filtration program."""

    _attr_native_max = 64

    def __init__(self, coordinator: VigipoolCoordinator, program_index: int) -> None:
        super().__init__(coordinator, f"filter_program_{program_index + 1}_days")
        self.program_index = program_index
        self._attr_name = f"Program {program_index + 1} days"
        self._attr_icon = "mdi:calendar-week"

    @property
    def native_value(self) -> str:
        """Return the selected weekdays as a compact string."""
        schedule = self.coordinator.get_filter_schedule()
        if schedule is None:
            return ""
        return format_days_mask(schedule.programs[self.program_index].days_mask)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Expose the accepted input format."""
        return {
            "example": "Mon, Wed, Fri",
            "accepted_keywords": "Every day, Mon, Tue, Wed, Thu, Fri, Sat, Sun",
            "accepted_french": "Lun, Mar, Mer, Jeu, Ven, Sam, Dim, Tous",
        }

    async def async_set_value(self, value: str) -> None:
        """Update the selected weekdays."""
        schedule = self.coordinator.get_filter_schedule()
        if schedule is None:
            return
        try:
            schedule.programs[self.program_index].days_mask = parse_days_input(value)
        except ValueError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_set_filter_schedule(schedule)


class VigipoolProgramSlotsText(VigipoolScheduleTextEntity):
    """Editable slot list for one filtration program."""

    _attr_native_max = 96

    def __init__(self, coordinator: VigipoolCoordinator, program_index: int) -> None:
        super().__init__(coordinator, f"filter_program_{program_index + 1}_slots")
        self.program_index = program_index
        self._attr_name = f"Program {program_index + 1} slots"
        self._attr_icon = "mdi:table-clock"

    @property
    def native_value(self) -> str:
        """Return the current slot list as an editable string."""
        schedule = self.coordinator.get_filter_schedule()
        if schedule is None:
            return ""
        return format_slots(schedule.programs[self.program_index].slots)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Expose the accepted slot format."""
        return {
            "example": "08:00-10:00; 18:30-18:45",
            "notes": "Up to 3 slots, 15-minute steps, empty value clears all slots",
        }

    async def async_set_value(self, value: str) -> None:
        """Update the slot list."""
        schedule = self.coordinator.get_filter_schedule()
        if schedule is None:
            return
        try:
            schedule.programs[self.program_index].slots = parse_slots_input(value)
        except ValueError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_set_filter_schedule(schedule)
