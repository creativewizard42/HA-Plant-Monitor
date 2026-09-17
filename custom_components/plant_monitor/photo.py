"""Helpers for turning a config-flow FileSelector upload into a permanent,
dashboard-servable photo under Home Assistant's www/ folder."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from homeassistant.components.file_upload import process_uploaded_file
from homeassistant.core import HomeAssistant

from .const import PHOTO_SUBDIR


async def async_save_uploaded_photo(hass: HomeAssistant, file_id: str) -> str:
    """Copy an uploaded file into www/plant_monitor/ and return its /local/ URL."""

    def _copy() -> str:
        www_dir = Path(hass.config.path("www", PHOTO_SUBDIR))
        www_dir.mkdir(parents=True, exist_ok=True)
        with process_uploaded_file(hass, file_id) as src_path:
            suffix = src_path.suffix or ".jpg"
            dest_name = f"{uuid.uuid4().hex}{suffix}"
            dest = www_dir / dest_name
            shutil.copy(src_path, dest)
        return f"/local/{PHOTO_SUBDIR}/{dest_name}"

    return await hass.async_add_executor_job(_copy)


def async_delete_photo(hass: HomeAssistant, photo_path: str) -> None:
    """Best-effort delete of a previously saved photo (fire-and-forget)."""
    prefix = f"/local/{PHOTO_SUBDIR}/"
    if not photo_path or not photo_path.startswith(prefix):
        return
    filename = photo_path[len(prefix):]
    full_path = Path(hass.config.path("www", PHOTO_SUBDIR, filename))

    def _delete() -> None:
        full_path.unlink(missing_ok=True)

    hass.async_create_task(hass.async_add_executor_job(_delete))
