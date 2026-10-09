"""Optional push notifications for a plant: an alert the moment it becomes
dry or overwatered, and/or a daily status summary - both sent via
the selected device's Mobile App notification action or its notify entities.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.device_automation import (
    DeviceAutomationType,
    async_get_device_automation_platform,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.event import async_track_time_change

from .const import CONF_NAME, DAILY_SUMMARY_HOUR, DAILY_SUMMARY_MINUTE, SIGNAL_UPDATE
from .plant_data import PlantData

_LOGGER = logging.getLogger(__name__)


async def async_notification_device_supported(
    hass: HomeAssistant, device_id: str
) -> bool:
    """Check actual notify entities or the Mobile App device action."""
    if any(
        entry.domain == "notify"
        for entry in er.async_entries_for_device(
            er.async_get(hass), device_id, include_disabled_entities=False
        )
    ):
        return True
    if "mobile_app" not in hass.data:
        return False
    try:
        platform = await async_get_device_automation_platform(
            hass, "mobile_app", DeviceAutomationType.ACTION
        )
        return any(
            action.get("type") == "notify"
            for action in await platform.async_get_actions(hass, device_id)
        )
    except HomeAssistantError:
        return False


class PlantNotifier:
    """Watches one plant's dry/overwatered state and sends notifications.

    Fully optional and off by default - configured via the options flow's
    "Notifications" step (pick a device, flip a toggle). Never touches
    anything if notify_enabled/notify_daily_summary_enabled are False or no
    device is set.
    """

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, plant: PlantData
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.plant = plant
        self._unsub: list = []
        self._was_dry = False
        self._was_overwatered = False

    async def async_setup(self) -> None:
        # Prime the "previous" state so we only notify on a fresh
        # dry/overwatered transition, not immediately on startup for a
        # plant that already happens to be dry.
        self._was_dry = self._is_dry()
        self._was_overwatered = self._is_overwatered()

        self._unsub.append(
            async_dispatcher_connect(
                self.hass, f"{SIGNAL_UPDATE}_{self.entry.entry_id}", self._handle_update
            )
        )
        self._unsub.append(
            async_track_time_change(
                self.hass,
                self._handle_daily_summary,
                hour=DAILY_SUMMARY_HOUR,
                minute=DAILY_SUMMARY_MINUTE,
                second=0,
            )
        )

    async def async_unload(self) -> None:
        for unsub in self._unsub:
            unsub()
        self._unsub.clear()

    def _is_dry(self) -> bool:
        soil = self.plant.soil_moisture
        return soil is not None and soil < self.plant.dry_threshold

    def _is_overwatered(self) -> bool:
        soil = self.plant.soil_moisture
        return soil is not None and soil > self.plant.wet_threshold

    def _plant_name(self) -> str:
        return self.entry.data.get(CONF_NAME, "Je plant")

    @callback
    def _handle_update(self) -> None:
        is_dry = self._is_dry()
        is_overwatered = self._is_overwatered()

        if self.plant.notify_enabled and self.plant.notify_device_id:
            if is_dry and not self._was_dry:
                self.hass.async_create_task(
                    self._send(
                        f"\U0001f331 {self._plant_name()} heeft water nodig",
                        f"Bodemvocht is {self.plant.soil_moisture}% - onder de "
                        f"droogte-drempel van {self.plant.dry_threshold}%.",
                    )
                )
            if is_overwatered and not self._was_overwatered:
                self.hass.async_create_task(
                    self._send(
                        f"\U0001f4a7 {self._plant_name()} staat te nat",
                        f"Bodemvocht is {self.plant.soil_moisture}% - boven de "
                        f"overwater-drempel van {self.plant.wet_threshold}%.",
                    )
                )

        self._was_dry = is_dry
        self._was_overwatered = is_overwatered

    async def _handle_daily_summary(self, _now) -> None:
        if not (
            self.plant.notify_daily_summary_enabled and self.plant.notify_device_id
        ):
            return
        await self._send(
            f"\U0001f33f Dagelijkse update - {self._plant_name()}",
            self.plant.advice,
        )

    async def _send(self, title: str, message: str) -> None:
        try:
            device_id = self.plant.notify_device_id
            device = dr.async_get(self.hass).async_get(device_id) if device_id else None
            if device is None:
                raise HomeAssistantError("Notification device is missing")
            is_mobile_app = any(
                entry is not None and entry.domain == "mobile_app"
                for entry in (
                    self.hass.config_entries.async_get_entry(entry_id)
                    for entry_id in device.config_entries
                )
            )
            if is_mobile_app and "mobile_app" in self.hass.data:
                platform = await async_get_device_automation_platform(
                    self.hass, "mobile_app", DeviceAutomationType.ACTION
                )
                actions = await platform.async_get_actions(self.hass, device_id)
                action = next(
                    (item for item in actions if item.get("type") == "notify"), None
                )
                if action is not None:
                    config = platform.ACTION_SCHEMA(
                        {**action, "title": "{{ title }}", "message": "{{ message }}"}
                    )
                    config["title"].hass = self.hass
                    config["message"].hass = self.hass
                    await platform.async_call_action_from_config(
                        self.hass, config, {"title": title, "message": message}, None
                    )
                    return
            entities = [
                entry.entity_id
                for entry in er.async_entries_for_device(
                    er.async_get(self.hass), device_id, include_disabled_entities=False
                )
                if entry.domain == "notify"
            ]
            if not entities:
                raise HomeAssistantError(
                    "Selected device has no supported notification action or notify entity"
                )
            await self.hass.services.async_call(
                "notify",
                "send_message",
                {"title": title, "message": message},
                target={"entity_id": entities},
                blocking=True,
            )
        except Exception:  # noqa: BLE001 - a failed notification must never break the integration
            _LOGGER.warning(
                "Could not send a notification for %s",
                self._plant_name(),
                exc_info=True,
            )
