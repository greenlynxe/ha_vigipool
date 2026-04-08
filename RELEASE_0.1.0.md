# 0.1.0

First public release of the `Vigipool` custom integration for Home Assistant.

## Highlights

- native Home Assistant integration using the built-in `mqtt` dependency
- UI-based setup through a `config flow`
- configurable MQTT topic prefix, designed around `tild_30C9229A50C4`
- read-only sensors for temperature, setpoint and device diagnostics
- binary sensors for flow, light, auxiliary relay and connectivity
- raw diagnostic entity exposing all MQTT topics received for the device

## Scope of this first release

This version is intentionally focused on reading retained and live `.../reported` MQTT states from a Vigipool controller.

It is intended as a clean base for the next iterations:

- filtration control
- lighting control
- auxiliary relay control
- schedule decoding

## Current limitations

- no MQTT writes yet
- no decoded schedules yet
- no dedicated `switch`, `light`, `climate` or `select` entities yet
- no complete support for the separate chemistry module yet
