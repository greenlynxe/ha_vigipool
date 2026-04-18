# Vigipool for Home Assistant

Custom Home Assistant integration for `Vigipool` controllers already publishing their state on a local MQTT broker.

This project currently targets a controller visible under the MQTT prefix:

`tild_30C9229A50C4`

## Current status

`0.2.2` is the current release and adds first MQTT controls plus a decoded filtration schedule.

Included today:

- UI setup through a Home Assistant `config flow`
- native subscription through Home Assistant's built-in `mqtt` integration
- automatic tracking of `.../reported` topics under a configurable device prefix
- main sensors for temperature, setpoint and diagnostics
- a decoded filtration schedule sensor with readable slot attributes
- binary sensors for flow, light, auxiliary relay, cover and connectivity
- a filtration switch using the Vigipool command topic
- a pool light entity using the Vigipool command topic
- one raw diagnostic entity exposing every MQTT topic received for the device

Not included yet:

- decoded schedules
- auxiliary relay control
- dedicated `climate` or `select` entities
- full `pH / Redox` support

## What this integration currently covers

- pool temperature
- temperature setpoint
- filtration state codes
- pool light state and related parameters
- auxiliary relay state and configuration
- winter / frost-free related flags
- simple connectivity and error diagnostics
- raw filtration, light and auxiliary schedules

## Installation

### Prerequisites

- Home Assistant with the native `mqtt` integration already configured
- access to the local Vigipool MQTT topics

### HACS

1. Open `HACS > Integrations > Custom repositories`.
2. Add `https://github.com/greenlynxe/ha_vigipool` as an `Integration`.
3. Install `Vigipool`.
4. Restart Home Assistant.
5. Go to `Settings > Devices & services > Add integration`.
6. Search for `Vigipool`.

### Manual installation

1. Copy `custom_components/vigipool` into your Home Assistant `custom_components` folder.
2. Restart Home Assistant.
3. Add the integration from `Settings > Devices & services`.

## Configuration

The config flow asks for:

- `Device name`
- `MQTT topic prefix`

Example:

`tild_30C9229A50C4`

The integration then subscribes to:

`<topic_prefix>/#`

## Exposed entities

### Sensors

- `Pool temperature`
- `Temperature setpoint`
- `Filter state code`
- `Error code`
- `State bitmask`
- `Wi-Fi RSSI`
- `Model ID`
- `Hardware version`
- `Software version`
- `Action code`
- `Filter service interval`
- `Light type`
- `Light code`
- `Light brightness`
- `Light speed`
- `Aux type`
- `Aux config`
- `Aux minimum temperature`
- `Aux temperature hysteresis`
- `Frost free mode`
- `Backwash code`
- `Filter schedule raw`
- `Filter schedule`
- `Light schedule raw`
- `Aux schedule raw`
- `Serial number raw`
- `Device ID`
- `Raw MQTT topics`

### Binary sensors

- `Flow on`
- `Cover on`
- `Aux state`
- `Light state`
- `MQTT connected`
- `Server on`
- `Winter mode`

### Controls

- `Filtration` switch
- `Pool light` light entity

## MQTT model currently assumed

The controller appears to publish topics with a shape close to:

`<device_prefix>/<type>_<direction>/<feature>/<channel>/reported`

Useful examples already observed:

- `u16_r/value_temp/value/reported`
- `u16_w/consigne_temp/consigne/reported`
- `u16_w/filt_state/info/reported`
- `s128_w/filt_sched/info/reported`
- `u8_w/light_state/info/reported`
- `s44_w/light_sched/info/reported`
- `u8_r/aux_state/info/reported`
- `s44_w/aux_sched/info/reported`
- `u32_r/error/info/reported`

The first writable topics now used by the integration are:

- `u16_w/filt_state/info/desired`
- `u8_w/light_state/info/desired`

Observed filtration values on the reference controller:

- `1` for forced filtration on
- `0` for filtration off

## Known limitations

- auxiliary relay control is not enabled yet
- schedules are still exposed as raw strings
- no full support for the separate chemistry module

## Short roadmap

- confirm auxiliary writable MQTT topics
- add auxiliary relay control
- decode schedules into readable attributes

## Project layout

The Home Assistant integration lives in `custom_components/vigipool`.
