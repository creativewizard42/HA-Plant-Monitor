"""Constants for the Plant Monitor integration."""
from __future__ import annotations

DOMAIN = "plant_monitor"

CONF_NAME = "name"
CONF_SPECIES = "species"
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

PLATFORMS = ["sensor", "binary_sensor", "number"]

SIGNAL_UPDATE = f"{DOMAIN}_update"

SERVICE_LOG_WATERING = "log_watering"

# Sensible starting thresholds per species. Users can override every value
# in the config flow and change them later from the plant's device page.
SPECIES_PRESETS: dict[str, dict[str, float | str]] = {
    "strelitzia": {
        "label": "Strelitzia (Bird of Paradise)",
        CONF_DRY_THRESHOLD: 15.0,
        CONF_WET_THRESHOLD: 65.0,
    },
    "monstera": {
        "label": "Monstera (Swiss Cheese Plant)",
        CONF_DRY_THRESHOLD: 15.0,
        CONF_WET_THRESHOLD: 55.0,
    },
    "calathea": {
        "label": "Calathea",
        CONF_DRY_THRESHOLD: 35.0,
        CONF_WET_THRESHOLD: 70.0,
    },
    "asplenium": {
        "label": "Asplenium (Bird's Nest Fern)",
        CONF_DRY_THRESHOLD: 30.0,
        CONF_WET_THRESHOLD: 75.0,
    },
    "custom": {
        "label": "Custom / other",
        CONF_DRY_THRESHOLD: DEFAULT_DRY_THRESHOLD,
        CONF_WET_THRESHOLD: DEFAULT_WET_THRESHOLD,
    },
}
