"""Image platform for Plant Monitor - serves the species stock photo or the
user's own uploaded photo as a proper image entity."""
from __future__ import annotations

from pathlib import Path

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SIGNAL_UPDATE
from .plant_data import PlantData
from .sensor import _device_info

_CONTENT_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    plant: PlantData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PlantPhotoImage(hass, entry, plant)])


class PlantPhotoImage(ImageEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "photo"
    _attr_icon = "mdi:flower"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, plant: PlantData) -> None:
        super().__init__(hass)
        self.hass = hass
        self._entry = entry
        self._plant = plant
        self._attr_unique_id = f"{entry.entry_id}_photo"
        self._attr_device_info = _device_info(entry)
        self._last_seen_path: str | None = None

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
        # A changed photo (via the options flow) only takes effect after the
        # entry reloads, since that's when this entity is recreated with the
        # new path - this just keeps the entity's own state fresh otherwise.
        self.async_write_ha_state()

    def image(self) -> bytes | None:
        path = self._local_file_path()
        if path is None or not path.exists():
            return None
        suffix = path.suffix.lower()
        self._attr_content_type = _CONTENT_TYPES.get(suffix, "image/jpeg")
        if self._last_seen_path != str(path):
            self._last_seen_path = str(path)
            self._attr_image_last_updated = dt_util.utcnow()
        return path.read_bytes()

    def _local_file_path(self) -> Path | None:
        photo_path = self._plant.photo_path  # e.g. "/local/plant_monitor/<id>.jpg"
        if not photo_path or not photo_path.startswith("/local/"):
            return None
        relative = photo_path[len("/local/"):]
        return Path(self.hass.config.path("www", relative))
