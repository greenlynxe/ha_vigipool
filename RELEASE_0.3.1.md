# 0.3.1

Small usability fix for the Vigipool filtration controls.

## Fixed

- replaced the filtration icon with a stable MDI icon that renders correctly in Home Assistant
- made filtration schedule controls available even before a retained schedule payload has been received

## Result

The filtration switch now shows a proper icon, and the filtration program controls can appear immediately instead of waiting for an existing `filt_sched` payload to be cached first.
