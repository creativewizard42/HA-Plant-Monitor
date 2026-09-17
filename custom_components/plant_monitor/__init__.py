"""The Plant Monitor integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, device_registry as dr

from .const import CONF_PHOTO_PATH, DOMAIN, PLATFORMS, SERVICE_LOG_WATERING
from .photo import async_delete_photo
from .plant_data import PlantData

LOG_WATERING_SCHEMA = vol.Schema(
    {vol.Required("device_id"): vol.All(cv.ensure_list, [cv.string])}
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register services once, regardless of how many plants get added."""

    async def _handle_log_watering(call: ServiceCall) -> None:
        device_registry = dr.async_get(hass)
        for device_id in call.data["device_id"]:
            device = device_registry.async_get(device_id)
            if device is None:
                continue
            for entry_id in device.config_entries:
                plant = hass.data.get(DOMAIN, {}).get(entry_id)
                if plant is not None:
                    plant.log_manual_watering()

    if not hass.services.has_service(DOMAIN, SERVICE_LOG_WATERING):
        hass.services.async_register(
            DOMAIN,
            SERVICE_LOG_WATERING,
            _handle_log_watering,
            schema=LOG_WATERING_SCHEMA,
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Plant Monitor from a config entry (one plant)."""
    hass.data.setdefault(DOMAIN, {})

    plant = PlantData(hass, entry)
    await plant.async_setup()
    hass.data[DOMAIN][entry.entry_id] = plant

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        plant: PlantData = hass.data[DOMAIN].pop(entry.entry_id)
        await plant.async_unload()
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry whenever its options change (threshold edits)."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Clean up a plant's saved photo file when it's removed entirely."""
    photo_path = entry.options.get(CONF_PHOTO_PATH, entry.data.get(CONF_PHOTO_PATH))
    if photo_path:
        async_delete_photo(hass, photo_path)
