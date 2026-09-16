"""Number platform for Plant Monitor - live-adjustable thresholds.

Changing one of these updates the config entry's options (so the value
survives restarts) and reloads the entry, the same as changing it via the
Options flow.
"""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_DRY_THRESHOLD, CONF_WET_THRESHOLD, DOMAIN
from .plant_data import PlantData
from .sensor import _device_info


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    plant: PlantData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            PlantThresholdNumber(
                entry, plant, CONF_DRY_THRESHOLD, "dry_threshold", "mdi:water-alert"
            ),
            PlantThresholdNumber(
                entry, plant, CONF_WET_THRESHOLD, "wet_threshold", "mdi:water-plus"
            ),
        ]
    )


class PlantThresholdNumber(NumberEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        entry: ConfigEntry,
        plant: PlantData,
        config_key: str,
        translation_key: str,
        icon: str,
    ) -> None:
        self._entry = entry
        self._plant = plant
        self._config_key = config_key
        self._attr_translation_key = translation_key
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{config_key}"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self) -> float:
        return getattr(self._plant, self._config_key)

    async def async_set_native_value(self, value: float) -> None:
        new_options = dict(self._entry.options)
        new_options[self._config_key] = value
        self.hass.config_entries.async_update_entry(self._entry, options=new_options)
