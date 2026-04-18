# 0.4.0

Major filtration schedule UX cleanup.

## Added

- compact `Program N days` text editors
- compact `Program N slots` text editors
- readable `Program N schedule` summary sensors

## Changed

- removed the noisy per-day switches from the default schedule editor
- removed the separate start/end slot time entities from the default schedule editor
- removed the clear-slot buttons from the default schedule editor
- cleaned up legacy detailed schedule entities from the registry during setup

## Result

The device page stays much cleaner while still allowing full schedule editing:

- enable or disable each program
- toggle thermoregulated mode
- edit weekdays in one field
- edit up to 3 time ranges in one field

## Input examples

- `Program 1 days`: `Mon, Wed, Fri`
- `Program 1 slots`: `08:00-10:00; 18:30-18:45`

French day names and aliases are accepted as well, and an empty `slots` field clears all slots.
