"""Helpers to decode and encode Vigipool filtration schedules."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time

SCHEDULE_PROGRAM_COUNT = 2
SCHEDULE_MAX_SLOTS = 3

DAY_BIT_SUNDAY = 0x01
DAY_BIT_MONDAY = 0x02
DAY_BIT_TUESDAY = 0x04
DAY_BIT_WEDNESDAY = 0x08
DAY_BIT_THURSDAY = 0x10
DAY_BIT_FRIDAY = 0x20
DAY_BIT_SATURDAY = 0x40
DAY_ENABLE_BIT = 0x80

DAY_SWITCHES: tuple[tuple[int, str, str], ...] = (
    (DAY_BIT_MONDAY, "monday", "Monday"),
    (DAY_BIT_TUESDAY, "tuesday", "Tuesday"),
    (DAY_BIT_WEDNESDAY, "wednesday", "Wednesday"),
    (DAY_BIT_THURSDAY, "thursday", "Thursday"),
    (DAY_BIT_FRIDAY, "friday", "Friday"),
    (DAY_BIT_SATURDAY, "saturday", "Saturday"),
    (DAY_BIT_SUNDAY, "sunday", "Sunday"),
)


@dataclass(slots=True)
class VigipoolFilterSlot:
    """One filtration slot."""

    start_index: int
    end_index: int


@dataclass(slots=True)
class VigipoolFilterProgram:
    """One filtration program."""

    enabled: bool = False
    days_mask: int = 0
    thermoregulated: bool = False
    slots: list[VigipoolFilterSlot | None] = field(
        default_factory=lambda: [None] * SCHEDULE_MAX_SLOTS
    )


@dataclass(slots=True)
class VigipoolFilterSchedule:
    """Decoded filtration schedule."""

    programs: list[VigipoolFilterProgram]
    raw_payload: str | None = None
    remaining_hex: str = ""


def decode_filter_schedule_payload(payload: str) -> VigipoolFilterSchedule | None:
    """Decode a filtration schedule payload."""
    try:
        raw = bytes.fromhex(payload)
    except ValueError:
        return None

    if not raw:
        return None

    slot_count = raw[0]
    cursor = 1
    programs: list[VigipoolFilterProgram] = []

    for _ in range(slot_count):
        if cursor + 4 > len(raw):
            break

        day_mask = raw[cursor]
        thermoregulated_flag = raw[cursor + 1]
        sequence_count = int.from_bytes(raw[cursor + 2 : cursor + 4], "big")
        cursor += 4

        slots: list[VigipoolFilterSlot | None] = [None] * SCHEDULE_MAX_SLOTS
        for sequence_index in range(sequence_count):
            if cursor + 2 > len(raw):
                cursor = len(raw)
                break

            start_index = raw[cursor]
            end_index = raw[cursor + 1]
            cursor += 2
            if sequence_index < SCHEDULE_MAX_SLOTS:
                slots[sequence_index] = VigipoolFilterSlot(
                    start_index=start_index,
                    end_index=end_index,
                )

        programs.append(
            VigipoolFilterProgram(
                enabled=bool(day_mask & DAY_ENABLE_BIT),
                days_mask=day_mask & 0x7F,
                thermoregulated=thermoregulated_flag == 1,
                slots=slots,
            )
        )

    while len(programs) < SCHEDULE_PROGRAM_COUNT:
        programs.append(VigipoolFilterProgram())

    return VigipoolFilterSchedule(
        programs=programs[:SCHEDULE_PROGRAM_COUNT],
        raw_payload=payload,
        remaining_hex=raw[cursor:].hex().upper(),
    )


def encode_filter_schedule_payload(schedule: VigipoolFilterSchedule) -> str:
    """Encode a filtration schedule payload."""
    programs = _normalize_programs(schedule.programs)
    payload = bytearray([len(programs)])

    for program in programs:
        day_mask = program.days_mask & 0x7F
        if program.enabled:
            day_mask |= DAY_ENABLE_BIT

        compact_slots = [slot for slot in program.slots if slot is not None]
        payload.append(day_mask)
        payload.append(1 if program.thermoregulated else 0)
        payload.extend(len(compact_slots).to_bytes(2, "big"))

        for slot in compact_slots:
            payload.append(max(0, min(95, slot.start_index)))
            payload.append(max(0, min(95, slot.end_index)))

    return payload.hex().upper()


def slot_index_to_time(value: int) -> time:
    """Convert a quarter-hour slot index to a time."""
    total_minutes = max(0, min(95, value)) * 15
    return time(hour=total_minutes // 60, minute=total_minutes % 60)


def time_to_slot_index(value: time) -> int:
    """Convert a time to the closest quarter-hour slot index."""
    total_minutes = value.hour * 60 + value.minute
    rounded = int(round(total_minutes / 15))
    return max(0, min(95, rounded))


def format_slot_index(value: int) -> str:
    """Format a quarter-hour slot index as HH:MM."""
    slot_time = slot_index_to_time(value)
    return slot_time.strftime("%H:%M")


def decode_days(mask: int) -> list[str]:
    """Decode the day bitmask used by Vigipool schedules."""
    return [label for bit, _, label in DAY_SWITCHES if mask & bit]


def compact_slots(slots: list[VigipoolFilterSlot | None]) -> list[VigipoolFilterSlot | None]:
    """Compact slot holes while preserving order."""
    compact = [slot for slot in slots if slot is not None]
    return compact + [None] * (SCHEDULE_MAX_SLOTS - len(compact))


def set_slot_time(
    schedule: VigipoolFilterSchedule,
    *,
    program_index: int,
    slot_index: int,
    is_start: bool,
    value: time,
) -> VigipoolFilterSchedule:
    """Update one slot boundary and return the mutated schedule."""
    program = schedule.programs[program_index]
    slots = list(program.slots)
    current_slot = slots[slot_index]
    new_index = time_to_slot_index(value)

    if current_slot is None:
        if is_start:
            current_slot = VigipoolFilterSlot(
                start_index=new_index,
                end_index=min(95, new_index + 1),
            )
        else:
            current_slot = VigipoolFilterSlot(
                start_index=max(0, new_index - 1),
                end_index=new_index,
            )

    if is_start:
        current_slot.start_index = new_index
    else:
        current_slot.end_index = new_index

    if current_slot.end_index <= current_slot.start_index:
        if is_start:
            current_slot.end_index = min(95, current_slot.start_index + 1)
        else:
            current_slot.start_index = max(0, current_slot.end_index - 1)

    slots[slot_index] = current_slot
    program.slots = compact_slots(slots)
    return schedule


def clear_slot(
    schedule: VigipoolFilterSchedule,
    *,
    program_index: int,
    slot_index: int,
) -> VigipoolFilterSchedule:
    """Delete one slot and compact the remaining ones."""
    program = schedule.programs[program_index]
    slots = list(program.slots)
    slots[slot_index] = None
    program.slots = compact_slots(slots)
    return schedule


def _normalize_programs(
    programs: list[VigipoolFilterProgram],
) -> list[VigipoolFilterProgram]:
    """Normalize to the fixed number of supported programs."""
    normalized = list(programs[:SCHEDULE_PROGRAM_COUNT])
    while len(normalized) < SCHEDULE_PROGRAM_COUNT:
        normalized.append(VigipoolFilterProgram())

    for program in normalized:
        slots = list(program.slots[:SCHEDULE_MAX_SLOTS])
        while len(slots) < SCHEDULE_MAX_SLOTS:
            slots.append(None)
        program.slots = compact_slots(slots)

    return normalized
