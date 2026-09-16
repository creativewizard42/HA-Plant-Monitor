"""Binary sensor platform for Plant Monitor.

These are computed by this integration rather than relying on the source
hardware to expose its own "dry" sensor - not all soil sensors do.
"""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_UPDATE
from .plant_data import PlantData
from .sensor import _device_info


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    plant: PlantData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [PlantDryBinarySensor(entry, plant), PlantOverwateredBinarySensor(entry, plant)]
    )


class _PlantBinarySensorBase(BinarySensorEntity):
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


class PlantDryBinarySensor(_PlantBinarySensorBase):
    _attr_translation_key = "dry"
    _attr_device_class = BinarySensorDeviceClass.MOISTURE

    def __init__(self, entry: ConfigEntry, plant: PlantData) -> None:
        super().__init__(entry, plant)
        self._attr_unique_id = f"{entry.entry_id}_dry"

    @property
    def is_on(self) -> bool | None:
        if self._plant.soil_moisture is None:
            return None
        return self._plant.soil_moisture < self._plant.dry_threshold


class PlantOverwateredBinarySensor(_PlantBinarySensorBase):
    _attr_translation_key = "overwatered"
    _attr_icon = "mdi:water-alert"

    def __init__(self, entry: ConfigEntry, plant: PlantData) -> None:
        super().__init__(entry, plant)
        self._attr_unique_id = f"{entry.entry_id}_overwatered"

    @property
    def is_on(self) -> bool | None:
        if self._plant.soil_moisture is None:
            return None
        return self._plant.soil_moisture > self._plant.wet_threshold
