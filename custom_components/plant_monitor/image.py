"""Image platform for Plant Monitor.

Serves the user's own uploaded photo if they added one; otherwise falls
back to the matched species' bundled stock photo (fetched from its
verified external URL - see species_data.json's stock_photo_url / the
generator script's STOCK_PHOTOS for credits). Only a curated subset of
species have a stock photo; most plants show no photo until the user
uploads their own, which always takes priority anyway.
"""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SIGNAL_UPDATE
from .plant_data import PlantData
from .sensor import _device_info

_LOGGER = logging.getLogger(__name__)

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
        self._last_seen_url: str | None = None

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
        # A changed photo (upload via the options flow) only fully takes
        # effect after the entry reloads, since that's when this entity is
        # recreated - this just keeps the entity's own state fresh otherwise.
        self.async_write_ha_state()

    async def async_image(self) -> bytes | None:
        photo_url = self._plant.photo_url
        if not photo_url:
            return None
        if photo_url.startswith("/local/"):
            return await self.hass.async_add_executor_job(self._read_local_file, photo_url)
        if photo_url.startswith("http://") or photo_url.startswith("https://"):
            return await self._fetch_remote(photo_url)
        return None

    def _read_local_file(self, photo_url: str) -> bytes | None:
        relative = photo_url[len("/local/"):]
        path = Path(self.hass.config.path("www", relative))
        if not path.exists():
            return None
        self._note_content_type(path.suffix.lower(), photo_url)
        return path.read_bytes()

    async def _fetch_remote(self, photo_url: str) -> bytes | None:
        try:
            client = get_async_client(self.hass)
            response = await client.get(photo_url, timeout=10, follow_redirects=True)
            response.raise_for_status()
        except Exception:  # noqa: BLE001 - a missing/unreachable stock photo must never crash the entity
            _LOGGER.debug("Could not fetch the stock photo at %s", photo_url, exc_info=True)
            return None
        self._attr_content_type = response.headers.get("content-type", "image/jpeg")
        self._note_content_type(None, photo_url)
        return response.content

    def _note_content_type(self, suffix: str | None, photo_url: str) -> None:
        if suffix:
            self._attr_content_type = _CONTENT_TYPES.get(suffix, "image/jpeg")
        if self._last_seen_url != photo_url:
            self._last_seen_url = photo_url
            self._attr_image_last_updated = dt_util.utcnow()
