"""Serves the bundled Plant Monitor Lovelace card and, where possible,
registers it as a dashboard resource automatically.

Auto-registration only works for storage-mode Lovelace (the default for
most installs). YAML-mode dashboards can't be modified this way, so in
that case - or if anything about this ever goes wrong - we fall back to a
repair/issue with the one manual step instead of failing loudly.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace import resources as lovelace_resources
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CARD_FILENAME = "plant-monitor-card.js"
STATIC_URL_PATH = f"/plant_monitor_files/{CARD_FILENAME}"
ISSUE_ADD_RESOURCE_MANUALLY = "add_lovelace_resource_manually"


def _integration_version() -> str:
    try:
        manifest = json.loads((Path(__file__).parent / "manifest.json").read_text(encoding="utf-8"))
        return str(manifest.get("version", "0"))
    except (OSError, ValueError):
        return "0"


# The resource URL carries the integration version so browsers (and the HA
# frontend's cache) fetch the new card after every update, instead of
# silently keeping the previous release's JavaScript.
RESOURCE_URL = f"{STATIC_URL_PATH}?v={_integration_version()}"


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Serve the card's JS and try to auto-register it as a resource.

    Safe to call on every startup: HA's static-path registration is
    idempotent, and the resource-add step checks for an existing entry
    with the same URL before adding a new one. This function must never
    raise - a dashboard nicety failing should never stop the integration
    (which owns real plant data) from loading.
    """
    try:
        www_dir = Path(__file__).parent / "www"
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL_PATH, str(www_dir / CARD_FILENAME), False)]
        )
    except Exception:  # noqa: BLE001
        _LOGGER.warning(
            "Could not serve the Plant Monitor card's JavaScript file; "
            "the plant-monitor-card will not be available on dashboards.",
            exc_info=True,
        )
        return

    if await _try_auto_register_resource(hass):
        ir.async_delete_issue(hass, DOMAIN, ISSUE_ADD_RESOURCE_MANUALLY)
        return

    ir.async_create_issue(
        hass,
        DOMAIN,
        ISSUE_ADD_RESOURCE_MANUALLY,
        is_fixable=False,
        is_persistent=True,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_ADD_RESOURCE_MANUALLY,
        translation_placeholders={"url": RESOURCE_URL},
    )


async def _try_auto_register_resource(hass: HomeAssistant) -> bool:
    """Return True if the resource is registered (already was, or just got
    added). Return False - never raise - if it can't be done automatically."""
    try:
        lovelace_data = hass.data.get("lovelace")
        if not lovelace_data:
            return False

        # HA 2025.2+ stores a LovelaceData dataclass; older versions a dict.
        if isinstance(lovelace_data, dict):
            resource_collection = lovelace_data.get("resources")
        else:
            resource_collection = getattr(lovelace_data, "resources", None)
        if not isinstance(resource_collection, lovelace_resources.ResourceStorageCollection):
            return False  # YAML-mode dashboards - not programmatically editable

        if not resource_collection.loaded:
            await resource_collection.async_load()
            resource_collection.loaded = True

        existing = next(
            (
                item
                for item in resource_collection.async_items()
                if item.get("url", "").split("?", 1)[0] == STATIC_URL_PATH
            ),
            None,
        )
        if existing is not None:
            if existing.get("url") != RESOURCE_URL:
                # Older release (or no version at all): bump the URL so
                # browsers drop the cached copy of the previous card.
                await resource_collection.async_update_item(
                    existing["id"], {"res_type": "module", "url": RESOURCE_URL}
                )
                _LOGGER.info("Updated Lovelace resource to %s", RESOURCE_URL)
            return True

        await resource_collection.async_create_item(
            {"res_type": "module", "url": RESOURCE_URL}
        )
        _LOGGER.info("Registered %s as a Lovelace resource automatically", RESOURCE_URL)
        return True
    except Exception:  # noqa: BLE001 - a frontend nicety must never break setup
        _LOGGER.debug(
            "Could not auto-register the Plant Monitor card as a Lovelace "
            "resource; the user will need to add it manually.",
            exc_info=True,
        )
        return False
