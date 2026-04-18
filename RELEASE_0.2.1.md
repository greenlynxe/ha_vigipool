# 0.2.1

Bugfix release for the first control-enabled Vigipool version.

## Fixed

- corrected the filtration command value after live MQTT sniffing
- aligned the `Filter state` sensor with the actual observed Vigipool values

## Confirmed live on the reference controller

- `u16_w/filt_state/info/desired = 1` for forced filtration on
- `u16_w/filt_state/info/desired = 0` for filtration off
- `u16_w/filt_state/info/reported` mirrors the same values
