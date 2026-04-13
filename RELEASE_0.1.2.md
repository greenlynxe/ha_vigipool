# 0.1.2

Small bugfix release for the first Vigipool integration.

## Fixed

- fixed the `Filter state` entity staying `unknown`
- restored the filtration state mapping by importing the flow topic used by the state resolver

## Result

The filtration entity can now resolve the expected state again from:

- `u16_w/filt_state/info/reported`
- `u8_r/flow_on/value/reported`
