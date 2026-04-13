"""Constants for the Vigipool integration."""

from __future__ import annotations

DOMAIN = "vigipool"

CONF_TOPIC_PREFIX = "topic_prefix"
CONF_DEVICE_NAME = "device_name"

DEFAULT_DEVICE_NAME = "Vigipool"
DEFAULT_TOPIC_PREFIX = "tild_30C9229A50C4"

FILTER_STATE_OFF = 0
FILTER_STATE_SCHEDULED = 1
FILTER_STATE_FORCED = 2
FILTER_STATE_BACKWASH = 3
FILTER_STATE_RINSE = 4

LIGHT_STATE_OFF = 0
LIGHT_STATE_ON = 1

TOPIC_POOL_TEMPERATURE = "u16_r/value_temp/value/reported"
TOPIC_TEMPERATURE_SETPOINT = "u16_w/consigne_temp/consigne/reported"
TOPIC_FLOW_ON = "u8_r/flow_on/value/reported"
TOPIC_COVER_ON = "u8_r/couv_on/value/reported"
TOPIC_AUX_STATE = "u8_r/aux_state/info/reported"
TOPIC_LIGHT_STATE = "u8_w/light_state/info/reported"
TOPIC_MQTT_CONNECTED = "u8_r/mqtt_connected/info/reported"
TOPIC_SERVER_ON = "u8_r/server_on/info/reported"
TOPIC_ERROR_CODE = "u32_r/error/info/reported"
TOPIC_STATE_BITS = "u32_r/state/info/reported"
TOPIC_RSSI = "i8_r/rssi/info/reported"
TOPIC_MODEL_ID = "u8_r/model_id/info/reported"
TOPIC_HW_VERSION = "u8_r/hw_vers/info/reported"
TOPIC_SW_VERSION = "u16_r/sw_vers/info/reported"
TOPIC_ACTION = "u8_w/action/info/reported"
TOPIC_FILT_STATE = "u16_w/filt_state/info/reported"
TOPIC_FILT_SERVICE_INTERVAL = "u16_w/filt_serv_inter/info/reported"
TOPIC_FILT_SCHEDULE = "s128_w/filt_sched/info/reported"
TOPIC_LIGHT_TYPE = "u8_w/light_type/info/reported"
TOPIC_LIGHT_CODE = "u8_w/light_code/info/reported"
TOPIC_LIGHT_BRIGHTNESS = "u8_w/light_bright/info/reported"
TOPIC_LIGHT_SPEED = "u8_w/light_speed/info/reported"
TOPIC_LIGHT_SCHEDULE = "s44_w/light_sched/info/reported"
TOPIC_AUX_TYPE = "u8_w/aux_type/info/reported"
TOPIC_AUX_CONFIG = "u16_w/aux_conf/info/reported"
TOPIC_AUX_MIN_TEMP = "u16_w/aux_min_temp/info/reported"
TOPIC_AUX_TEMP_HYST = "u8_w/aux_temp_hyst/info/reported"
TOPIC_AUX_SCHEDULE = "s44_w/aux_sched/info/reported"
TOPIC_WINTER_MODE = "u8_w/winter_mode/info/reported"
TOPIC_FROST_FREE = "u8_w/frost_free/info/reported"
TOPIC_BACKWASH = "u8_w/backwash/info/reported"
TOPIC_SERIAL = "s33_r/serial_num/info/reported"
TOPIC_DEVICE_ID = "s44_r/device_id/info/reported"

TOPIC_FILT_STATE_DESIRED = "u16_w/filt_state/info/desired"
TOPIC_LIGHT_STATE_DESIRED = "u8_w/light_state/info/desired"
