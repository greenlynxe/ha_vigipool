# 0.3.0

First filtration scheduling release for the Vigipool integration.

## Added

- program enable switches for filtration programs 1 and 2
- thermoregulated mode switches for both filtration programs
- weekday switches for both filtration programs
- start/end time entities for the 3 available slots of each filtration program
- clear-slot buttons for every filtration slot
- shared schedule encoder/decoder used by both sensors and controls

## Result

Home Assistant can now:

- activate or deactivate filtration programs 1 and 2
- choose the weekdays for each program
- toggle thermoregulated mode
- define or clear up to 3 time slots per program

## Scope

This release targets the filtration schedule payload:

- `s128_w/filt_sched/info/reported`
- `s128_w/filt_sched/info/desired`
