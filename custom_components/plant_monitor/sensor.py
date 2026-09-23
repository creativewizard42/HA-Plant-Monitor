"""Sensor platform for Plant Monitor."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_NAME, CONF_SPECIES, DOMAIN, SIGNAL_UPDATE
from .plant_data import PlantData
from .species import find_species


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    plant: PlantData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            PlantAdviceSensor(entry, plant),
            PlantCareTipSensor(entry, plant),
            PlantSoilMoistureSensor(entry, plant),
            PlantHealthScoreSensor(entry, plant),
            PlantDryingRateSensor(entry, plant),
            PlantWaterPredictionSensor(entry, plant),
            PlantLastWateredSensor(entry, plant),
            PlantWateringsThisWeekSensor(entry, plant),
        ]
    )


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    species_name = entry.data.get(CONF_SPECIES, "")
    match = find_species(species_name)
    # Dutch-first label, e.g. "Malabar Kastanje (Pachira aquatica)" - the
    # card shows this in its "Verzorgingstips - ..." header.
    if match:
        model = match.get("nl_label") or match["display_name"]
    else:
        model = species_name or "Eigen plant"
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.data[CONF_NAME],
        manufacturer="Plant Monitor",
        model=model,
    )


class _PlantSensorBase(SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, plant: PlantData) -> None:
        self._entry = entry
        self._plant = plant
        self._attr_device_info = _device_info(entry)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{SIGNAL_UPDATE}_{self._entry.entry_id}",
                self._handle_update,
            )
        )

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()


class PlantAdviceSensor(_PlantSensorBase):
    _attr_translation_key = "advice"
    _attr_icon = "mdi:comment-text-outline"

    def __init__(self, entry: ConfigEntry, plant: PlantData) -> None:
        super().__init__(entry, plant)
        self._attr_unique_id = f"{entry.entry_id}_advice"

    @property
    def native_value(self) -> str:
        return self._plant.advice


class PlantCareTipSensor(_PlantSensorBase):
    _attr_translation_key = "care_tip"
    _attr_icon = "mdi:book-open-variant"

    def __init__(self, entry: ConfigEntry, plant: PlantData) -> None:
        super().__init__(entry, plant)
        self._attr_unique_id = f"{entry.entry_id}_care_tip"

    @property
    def native_value(self) -> str:
        # Home Assistant sensor states are capped at 255 characters - a
        # full multi-section care guide is routinely 1000+ characters, so
        # it must live in extra_state_attributes (no such cap) instead.
        # The state itself stays short: enough to be useful in the entity
        # list/history without ever needing truncation.
        full = self._plant.care_tip
        return full if len(full) <= 255 else f"{full[:252]}..."

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        return {"full_text": self._plant.care_tip, **self._plant.care_guide_sections}


class PlantSoilMoistureSensor(_PlantSensorBase):
    """Mirrors the linked source sensor's current value under a stable,
    Plant-Monitor-owned entity_id/unique_id, so the recorder keeps its own
    history for this plant regardless of what the underlying hardware
    sensor happens to be - used by the bundled dashboard card's history
    graph and useful on its own for graphing/statistics either way."""

    _attr_translation_key = "soil_moisture"
    _attr_icon = "mdi:water-percent"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, plant: PlantData) -> None:
        super().__init__(entry, plant)
        self._attr_unique_id = f"{entry.entry_id}_soil_moisture"

    @property
    def native_value(self) -> float | None:
        return self._plant.soil_moisture

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        # The card can't assume these live on the same HA "device" as this
        # sensor - Plant Monitor's own entities are on their own device,
        # separate from whatever device the user's original
        # temperature/humidity/battery sensors belong to. Exposing the
        # actual linked entity_ids here lets the card look them up
        # directly instead of guessing via device_class-on-the-same-device
        # (which silently found nothing, since it's the wrong device).
        attrs: dict[str, str] = {}
        if self._plant.temperature_entity_id:
            attrs["temperature_entity_id"] = self._plant.temperature_entity_id
        if self._plant.humidity_entity_id:
            attrs["humidity_entity_id"] = self._plant.humidity_entity_id
        if self._plant.battery_entity_id:
            attrs["battery_entity_id"] = self._plant.battery_entity_id
        return attrs


class PlantHealthScoreSensor(_PlantSensorBase):
    _attr_translation_key = "health_score"
    _attr_icon = "mdi:heart-pulse"
    _attr_native_unit_of_measurement = "pts"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, plant: PlantData) -> None:
        super().__init__(entry, plant)
        self._attr_unique_id = f"{entry.entry_id}_health_score"

    @property
    def native_value(self) -> int | None:
        return self._plant.health_score


class PlantDryingRateSensor(_PlantSensorBase):
    _attr_translation_key = "drying_rate"
    _attr_icon = "mdi:trending-down"
    _attr_native_unit_of_measurement = "%/h"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry, plant: PlantData) -> None:
        super().__init__(entry, plant)
        self._attr_unique_id = f"{entry.entry_id}_drying_rate"

    @property
    def native_value(self) -> float | None:
        return self._plant.drying_rate


class PlantWaterPredictionSensor(_PlantSensorBase):
    _attr_translation_key = "water_prediction"
    _attr_icon = "mdi:clock-alert-outline"

    def __init__(self, entry: ConfigEntry, plant: PlantData) -> None:
        super().__init__(entry, plant)
        self._attr_unique_id = f"{entry.entry_id}_water_prediction"

    @property
    def native_value(self) -> str:
        return self._plant.water_prediction


class PlantLastWateredSensor(_PlantSensorBase):
    _attr_translation_key = "last_watered"
    _attr_icon = "mdi:watering-can"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, entry: ConfigEntry, plant: PlantData) -> None:
        super().__init__(entry, plant)
        self._attr_unique_id = f"{entry.entry_id}_last_watered"

    @property
    def native_value(self):
        return self._plant.last_watered


class PlantWateringsThisWeekSensor(_PlantSensorBase):
    _attr_translation_key = "waterings_this_week"
    _attr_icon = "mdi:counter"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry: ConfigEntry, plant: PlantData) -> None:
        super().__init__(entry, plant)
        self._attr_unique_id = f"{entry.entry_id}_waterings_this_week"

    @property
    def native_value(self) -> int:
        return self._plant.waterings_this_week
