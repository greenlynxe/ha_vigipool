"""Switch entities for Vigipool."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
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
from .schedule import DAY_SWITCHES, VigipoolFilterSchedule


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Vigipool switches."""
    coordinator: VigipoolCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities: list[SwitchEntity] = [VigipoolFiltrationSwitch(coordinator)]

    for program_index in range(2):
        entities.append(VigipoolProgramEnabledSwitch(coordinator, program_index))
        entities.append(VigipoolProgramThermoregulatedSwitch(coordinator, program_index))
        for bit, key, label in DAY_SWITCHES:
            entities.append(
                VigipoolProgramDaySwitch(
                    coordinator,
                    program_index,
                    bit=bit,
                    day_key=key,
                    day_label=label,
                )
            )

    async_add_entities(entities)


class VigipoolScheduleSwitch(VigipoolEntity, SwitchEntity):
    """Base class for switches mutating the filtration schedule."""

    _attr_entity_category = EntityCategory.CONFIG

    def _get_schedule(self) -> VigipoolFilterSchedule | None:
        return self.coordinator.get_filter_schedule()

    @property
    def available(self) -> bool:
        """Return availability for schedule switches."""
        return self._get_schedule() is not None


class VigipoolFiltrationSwitch(VigipoolEntity, SwitchEntity):
    """Switch to force filtration on or stop it."""

    _attr_name = "Filtration"
    _attr_icon = "mdi:pump"

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
    def extra_state_attributes(self) -> dict[str, int | str | None]:
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


class VigipoolProgramEnabledSwitch(VigipoolScheduleSwitch):
    """Enable or disable one filtration program."""

    def __init__(self, coordinator: VigipoolCoordinator, program_index: int) -> None:
        super().__init__(coordinator, f"filter_program_{program_index + 1}_enabled")
        self.program_index = program_index
        self._attr_name = f"Program {program_index + 1} enabled"
        self._attr_icon = "mdi:calendar-check"

    @property
    def is_on(self) -> bool | None:
        """Return whether the program is enabled."""
        schedule = self._get_schedule()
        if schedule is None:
            return None
        return schedule.programs[self.program_index].enabled

    async def async_turn_on(self, **kwargs) -> None:
        """Enable the program."""
        schedule = self._get_schedule()
        if schedule is None:
            return
        schedule.programs[self.program_index].enabled = True
        await self.coordinator.async_set_filter_schedule(schedule)

    async def async_turn_off(self, **kwargs) -> None:
        """Disable the program."""
        schedule = self._get_schedule()
        if schedule is None:
            return
        schedule.programs[self.program_index].enabled = False
        await self.coordinator.async_set_filter_schedule(schedule)


class VigipoolProgramThermoregulatedSwitch(VigipoolScheduleSwitch):
    """Toggle thermoregulated mode for one filtration program."""

    def __init__(self, coordinator: VigipoolCoordinator, program_index: int) -> None:
        super().__init__(
            coordinator, f"filter_program_{program_index + 1}_thermoregulated"
        )
        self.program_index = program_index
        self._attr_name = f"Program {program_index + 1} thermoregulated"
        self._attr_icon = "mdi:thermometer-auto"

    @property
    def is_on(self) -> bool | None:
        """Return whether thermoregulated mode is enabled."""
        schedule = self._get_schedule()
        if schedule is None:
            return None
        return schedule.programs[self.program_index].thermoregulated

    async def async_turn_on(self, **kwargs) -> None:
        """Enable thermoregulated mode."""
        schedule = self._get_schedule()
        if schedule is None:
            return
        schedule.programs[self.program_index].thermoregulated = True
        await self.coordinator.async_set_filter_schedule(schedule)

    async def async_turn_off(self, **kwargs) -> None:
        """Disable thermoregulated mode."""
        schedule = self._get_schedule()
        if schedule is None:
            return
        schedule.programs[self.program_index].thermoregulated = False
        await self.coordinator.async_set_filter_schedule(schedule)


class VigipoolProgramDaySwitch(VigipoolScheduleSwitch):
    """Toggle one weekday for one filtration program."""

    def __init__(
        self,
        coordinator: VigipoolCoordinator,
        program_index: int,
        *,
        bit: int,
        day_key: str,
        day_label: str,
    ) -> None:
        super().__init__(
            coordinator, f"filter_program_{program_index + 1}_{day_key}"
        )
        self.program_index = program_index
        self.day_bit = bit
        self._attr_name = f"Program {program_index + 1} {day_label}"
        self._attr_icon = "mdi:calendar"

    @property
    def is_on(self) -> bool | None:
        """Return whether the weekday is selected."""
        schedule = self._get_schedule()
        if schedule is None:
            return None
        return bool(schedule.programs[self.program_index].days_mask & self.day_bit)

    async def async_turn_on(self, **kwargs) -> None:
        """Enable the weekday for this program."""
        schedule = self._get_schedule()
        if schedule is None:
            return
        program = schedule.programs[self.program_index]
        program.days_mask |= self.day_bit
        await self.coordinator.async_set_filter_schedule(schedule)

    async def async_turn_off(self, **kwargs) -> None:
        """Disable the weekday for this program."""
        schedule = self._get_schedule()
        if schedule is None:
            return
        program = schedule.programs[self.program_index]
        program.days_mask &= ~self.day_bit
        await self.coordinator.async_set_filter_schedule(schedule)
