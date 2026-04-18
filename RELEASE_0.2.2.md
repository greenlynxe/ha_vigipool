# 0.2.2

Schedule decoding update for the Vigipool integration.

## Added

- new decoded `Filter schedule` sensor
- readable filtration slot attributes with:
  - enabled state
  - selected days
  - thermoregulated mode
  - sequence count
  - per-sequence start and end times

## Based on

This decoder was derived from live MQTT captures on the reference controller and currently targets the filtration schedule payload:

- `s128_w/filt_sched/info/reported`
- `s128_w/filt_sched/info/desired`
