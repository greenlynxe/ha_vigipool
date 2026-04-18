"""Helpers to decode and encode Vigipool filtration schedules."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
import re

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

DAY_LABELS: dict[int, str] = {
    DAY_BIT_MONDAY: "Mon",
    DAY_BIT_TUESDAY: "Tue",
    DAY_BIT_WEDNESDAY: "Wed",
    DAY_BIT_THURSDAY: "Thu",
    DAY_BIT_FRIDAY: "Fri",
    DAY_BIT_SATURDAY: "Sat",
    DAY_BIT_SUNDAY: "Sun",
}

DAY_ALIASES: dict[str, int] = {
    "mon": DAY_BIT_MONDAY,
    "monday": DAY_BIT_MONDAY,
    "lun": DAY_BIT_MONDAY,
    "lundi": DAY_BIT_MONDAY,
    "tue": DAY_BIT_TUESDAY,
    "tues": DAY_BIT_TUESDAY,
    "tuesday": DAY_BIT_TUESDAY,
    "mar": DAY_BIT_TUESDAY,
    "mardi": DAY_BIT_TUESDAY,
    "wed": DAY_BIT_WEDNESDAY,
    "wednesday": DAY_BIT_WEDNESDAY,
    "mer": DAY_BIT_WEDNESDAY,
    "mercredi": DAY_BIT_WEDNESDAY,
    "thu": DAY_BIT_THURSDAY,
    "thur": DAY_BIT_THURSDAY,
    "thursday": DAY_BIT_THURSDAY,
    "jeu": DAY_BIT_THURSDAY,
    "jeudi": DAY_BIT_THURSDAY,
    "fri": DAY_BIT_FRIDAY,
    "friday": DAY_BIT_FRIDAY,
    "ven": DAY_BIT_FRIDAY,
    "vendredi": DAY_BIT_FRIDAY,
    "sat": DAY_BIT_SATURDAY,
    "saturday": DAY_BIT_SATURDAY,
    "sam": DAY_BIT_SATURDAY,
    "samedi": DAY_BIT_SATURDAY,
    "sun": DAY_BIT_SUNDAY,
    "sunday": DAY_BIT_SUNDAY,
    "dim": DAY_BIT_SUNDAY,
    "dimanche": DAY_BIT_SUNDAY,
}

ALL_DAYS_ALIASES = {
    "all",
    "everyday",
    "daily",
    "tous",
    "touslesjours",
    "7/7",
}


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


def format_days_mask(mask: int) -> str:
    """Format a day mask as a compact human-readable string."""
    if mask == 0:
        return ""
    if mask == (
        DAY_BIT_MONDAY
        | DAY_BIT_TUESDAY
        | DAY_BIT_WEDNESDAY
        | DAY_BIT_THURSDAY
        | DAY_BIT_FRIDAY
        | DAY_BIT_SATURDAY
        | DAY_BIT_SUNDAY
    ):
        return "Every day"

    return ", ".join(
        DAY_LABELS[bit] for bit, _, _ in DAY_SWITCHES if mask & bit
    )


def parse_days_input(value: str) -> int:
    """Parse a day list entered by the user."""
    cleaned = value.strip().lower()
    if not cleaned:
        return 0

    normalized = re.sub(r"[^a-z0-9]+", "", cleaned)
    if normalized in ALL_DAYS_ALIASES:
        return (
            DAY_BIT_MONDAY
            | DAY_BIT_TUESDAY
            | DAY_BIT_WEDNESDAY
            | DAY_BIT_THURSDAY
            | DAY_BIT_FRIDAY
            | DAY_BIT_SATURDAY
            | DAY_BIT_SUNDAY
        )

    tokens = [
        token
        for token in re.split(r"[,\s;/]+", cleaned)
        if token
    ]
    if not tokens:
        raise ValueError("No valid day provided")

    mask = 0
    for token in tokens:
        day_bit = DAY_ALIASES.get(token)
        if day_bit is None:
            raise ValueError(f"Unknown day token: {token}")
        mask |= day_bit

    return mask


def format_slots(slots: list[VigipoolFilterSlot | None]) -> str:
    """Format schedule slots as a compact editable string."""
    return "; ".join(
        f"{format_slot_index(slot.start_index)}-{format_slot_index(slot.end_index)}"
        for slot in slots
        if slot is not None
    )


def parse_slots_input(value: str) -> list[VigipoolFilterSlot | None]:
    """Parse a semicolon-separated slot list."""
    cleaned = value.strip()
    if not cleaned:
        return [None] * SCHEDULE_MAX_SLOTS

    raw_slots = [part.strip() for part in cleaned.split(";") if part.strip()]
    if len(raw_slots) > SCHEDULE_MAX_SLOTS:
        raise ValueError(f"At most {SCHEDULE_MAX_SLOTS} slots are supported")

    parsed: list[VigipoolFilterSlot] = []
    for raw_slot in raw_slots:
        if "-" not in raw_slot:
            raise ValueError(f"Invalid slot format: {raw_slot}")

        start_raw, end_raw = [part.strip() for part in raw_slot.split("-", 1)]
        start_time = _parse_time_string(start_raw)
        end_time = _parse_time_string(end_raw)
        start_index = time_to_slot_index(start_time)
        end_index = time_to_slot_index(end_time)

        if start_index == end_index:
            raise ValueError("Start and end cannot be identical")
        if end_index <= start_index:
            raise ValueError("End time must be after start time")

        parsed.append(
            VigipoolFilterSlot(
                start_index=start_index,
                end_index=end_index,
            )
        )

    parsed.sort(key=lambda slot: slot.start_index)
    return compact_slots(parsed)


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


def _parse_time_string(value: str) -> time:
    """Parse a strict HH:MM time aligned to quarter hours."""
    try:
        hours_raw, minutes_raw = value.split(":", 1)
        parsed = time(hour=int(hours_raw), minute=int(minutes_raw))
    except (TypeError, ValueError) as err:
        raise ValueError(f"Invalid time: {value}") from err

    if parsed.minute not in {0, 15, 30, 45}:
        raise ValueError("Only 15-minute increments are supported")

    return parsed
