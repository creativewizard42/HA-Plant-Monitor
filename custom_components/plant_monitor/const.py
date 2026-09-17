"""Constants for the Plant Monitor integration."""
from __future__ import annotations

DOMAIN = "plant_monitor"

CONF_NAME = "name"
CONF_SPECIES = "species"
CONF_CARE_TIP = "care_tip"
CONF_PHOTO_PATH = "photo_path"  # relative path under www/, e.g. "plant_monitor/<id>.jpg"
CONF_SOIL_MOISTURE_ENTITY = "soil_moisture_entity"
CONF_TEMPERATURE_ENTITY = "temperature_entity"
CONF_HUMIDITY_ENTITY = "humidity_entity"
CONF_BATTERY_ENTITY = "battery_entity"

CONF_DRY_THRESHOLD = "dry_threshold"
CONF_WET_THRESHOLD = "wet_threshold"
CONF_TEMP_HOT = "temp_hot_threshold"
CONF_TEMP_COLD = "temp_cold_threshold"
CONF_HUMIDITY_LOW = "humidity_low_threshold"
CONF_BATTERY_LOW = "battery_low_threshold"
CONF_WATER_JUMP = "water_jump_threshold"

DEFAULT_CARE_TIP = "No species matched - add your own care notes here."
PHOTO_SUBDIR = "plant_monitor"  # under Home Assistant's www/ folder

DEFAULT_DRY_THRESHOLD = 20.0
DEFAULT_WET_THRESHOLD = 70.0
DEFAULT_TEMP_HOT = 28.0
DEFAULT_TEMP_COLD = 15.0
DEFAULT_HUMIDITY_LOW = 40.0
DEFAULT_BATTERY_LOW = 20.0
DEFAULT_WATER_JUMP = 8.0

# Rolling in-memory history used for the drying-rate calculation.
# (No recorder/history queries needed - this is intentionally lightweight.)
HISTORY_MAX_AGE_HOURS = 24
HISTORY_MAX_SAMPLES = 200
MIN_SPAN_MINUTES_FOR_RATE = 30

PLATFORMS = ["sensor", "binary_sensor", "number", "image"]

SIGNAL_UPDATE = f"{DOMAIN}_update"

SERVICE_LOG_WATERING = "log_watering"

