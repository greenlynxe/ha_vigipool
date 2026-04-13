# 0.2.0

First control-oriented release for the Vigipool integration.

## Added

- `Filtration` switch
- `Pool light` light entity
- MQTT command publishing to the first confirmed `.../desired` topics
- optimistic local state updates after commands for a faster Home Assistant UI response

## Command topics used in this release

- `u16_w/filt_state/info/desired`
- `u8_w/light_state/info/desired`

## Notes

The filtration switch uses forced run when turned on and stop when turned off.

Auxiliary relay control is intentionally left for a later release until its writable topic is confirmed.
