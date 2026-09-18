"""Config flow for Plant Monitor.

Deliberately hardware-agnostic: the user can point this at a whole device
(e.g. a Zigbee2MQTT plant sensor) to auto-map its entities, or pick entities
individually - either way every value stays editable afterwards.
"""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, selector

from .const import (
    CONF_BATTERY_ENTITY,
    CONF_BATTERY_LOW,
    CONF_CARE_TIP,
    CONF_DRY_THRESHOLD,
    CONF_HUMIDITY_ENTITY,
    CONF_HUMIDITY_LOW,
    CONF_NAME,
    CONF_NOTIFY_DAILY_SUMMARY_ENABLED,
    CONF_NOTIFY_DEVICE_ID,
    CONF_NOTIFY_ENABLED,
    CONF_PHOTO_PATH,
    CONF_SOIL_MOISTURE_ENTITY,
    CONF_SPECIES,
    CONF_TEMP_COLD,
    CONF_TEMP_HOT,
    CONF_TEMPERATURE_ENTITY,
    CONF_WATER_JUMP,
    CONF_WET_THRESHOLD,
    DEFAULT_BATTERY_LOW,
    DEFAULT_CARE_TIP,
    DEFAULT_DRY_THRESHOLD,
    DEFAULT_HUMIDITY_LOW,
    DEFAULT_TEMP_COLD,
    DEFAULT_TEMP_HOT,
    DEFAULT_WATER_JUMP,
    DEFAULT_WET_THRESHOLD,
    DOMAIN,
)
from .photo import async_delete_photo, async_save_uploaded_photo
from .species import find_species, species_select_options

CONF_DEVICE = "device_id"
CONF_PHOTO_UPLOAD = "photo_upload"


# ---- shared schema builders (used by both the config flow and options flow) ----


def _entity_selector() -> selector.EntitySelector:
    return selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor"))


def _percent_selector() -> selector.NumberSelector:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=0, max=100, step=1, unit_of_measurement="%",
            mode=selector.NumberSelectorMode.SLIDER,
        )
    )


def _entities_schema(guesses: dict[str, str]) -> vol.Schema:
    schema: dict[Any, Any] = {}
    if CONF_SOIL_MOISTURE_ENTITY in guesses:
        schema[vol.Required(CONF_SOIL_MOISTURE_ENTITY, default=guesses[CONF_SOIL_MOISTURE_ENTITY])] = _entity_selector()
    else:
        schema[vol.Required(CONF_SOIL_MOISTURE_ENTITY)] = _entity_selector()
    for key in (CONF_TEMPERATURE_ENTITY, CONF_HUMIDITY_ENTITY, CONF_BATTERY_ENTITY):
        if key in guesses:
            schema[vol.Optional(key, default=guesses[key])] = _entity_selector()
        else:
            schema[vol.Optional(key)] = _entity_selector()
    return vol.Schema(schema)


def _care_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_DRY_THRESHOLD, default=defaults.get(CONF_DRY_THRESHOLD, DEFAULT_DRY_THRESHOLD)
            ): _percent_selector(),
            vol.Required(
                CONF_WET_THRESHOLD, default=defaults.get(CONF_WET_THRESHOLD, DEFAULT_WET_THRESHOLD)
            ): _percent_selector(),
            vol.Required(
                CONF_CARE_TIP, default=defaults.get(CONF_CARE_TIP, DEFAULT_CARE_TIP)
            ): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
        }
    )


def _photo_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(CONF_PHOTO_UPLOAD): selector.FileSelector(
                selector.FileSelectorConfig(accept="image/*")
            ),
        }
    )


def _notify_schema(defaults: dict[str, Any]) -> vol.Schema:
    schema: dict[Any, Any] = {
        vol.Required(
            CONF_NOTIFY_ENABLED, default=defaults.get(CONF_NOTIFY_ENABLED, False)
        ): selector.BooleanSelector(),
    }
    if defaults.get(CONF_NOTIFY_DEVICE_ID):
        schema[vol.Optional(CONF_NOTIFY_DEVICE_ID, default=defaults[CONF_NOTIFY_DEVICE_ID])] = (
            selector.DeviceSelector()
        )
    else:
        schema[vol.Optional(CONF_NOTIFY_DEVICE_ID)] = selector.DeviceSelector()
    schema[
        vol.Required(
            CONF_NOTIFY_DAILY_SUMMARY_ENABLED,
            default=defaults.get(CONF_NOTIFY_DAILY_SUMMARY_ENABLED, False),
        )
    ] = selector.BooleanSelector()
    return vol.Schema(schema)


def _advanced_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_TEMP_COLD, default=defaults.get(CONF_TEMP_COLD, DEFAULT_TEMP_COLD)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=-10, max=40, step=0.5, unit_of_measurement="\u00b0C")
            ),
            vol.Required(
                CONF_TEMP_HOT, default=defaults.get(CONF_TEMP_HOT, DEFAULT_TEMP_HOT)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=50, step=0.5, unit_of_measurement="\u00b0C")
            ),
            vol.Required(
                CONF_HUMIDITY_LOW, default=defaults.get(CONF_HUMIDITY_LOW, DEFAULT_HUMIDITY_LOW)
            ): _percent_selector(),
            vol.Required(
                CONF_BATTERY_LOW, default=defaults.get(CONF_BATTERY_LOW, DEFAULT_BATTERY_LOW)
            ): _percent_selector(),
            vol.Required(
                CONF_WATER_JUMP, default=defaults.get(CONF_WATER_JUMP, DEFAULT_WATER_JUMP)
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=50, step=1, unit_of_measurement="%")
            ),
        }
    )


def _guess_entities_for_device(hass: HomeAssistant, device_id: str) -> dict[str, str]:
    """Best-effort mapping of a device's sensor entities to their roles.

    Matches by device_class first (temperature/humidity/battery), and by an
    entity_id/unique_id substring for soil moisture (which has no dedicated
    HA device_class). Always adjustable afterwards - this only fills in
    sensible defaults.
    """
    entity_registry = er.async_get(hass)
    entries = er.async_entries_for_device(entity_registry, device_id, include_disabled_entities=False)

    guesses: dict[str, str] = {}
    for entry in entries:
        if entry.domain != "sensor":
            continue
        haystack = f"{entry.entity_id} {entry.unique_id or ''}".lower()
        state = hass.states.get(entry.entity_id)
        device_class = state.attributes.get("device_class") if state else None

        if CONF_SOIL_MOISTURE_ENTITY not in guesses and "soil" in haystack and (
            "moist" in haystack or "vocht" in haystack
        ):
            guesses[CONF_SOIL_MOISTURE_ENTITY] = entry.entity_id
        elif CONF_BATTERY_ENTITY not in guesses and device_class == "battery":
            guesses[CONF_BATTERY_ENTITY] = entry.entity_id
        elif CONF_TEMPERATURE_ENTITY not in guesses and device_class == "temperature":
            guesses[CONF_TEMPERATURE_ENTITY] = entry.entity_id
        elif (
            CONF_HUMIDITY_ENTITY not in guesses
            and device_class == "humidity"
            and "soil" not in haystack
        ):
            guesses[CONF_HUMIDITY_ENTITY] = entry.entity_id
    return guesses


class PlantMonitorConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Plant Monitor. One entry = one plant."""

    VERSION = 2

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._entity_guesses: dict[str, str] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> Any:
        if user_input is not None:
            device_id = user_input.pop(CONF_DEVICE, None)
            self._data.update(user_input)
            if device_id:
                self._entity_guesses = _guess_entities_for_device(self.hass, device_id)
            return await self.async_step_entities()

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): selector.TextSelector(),
                vol.Required(CONF_SPECIES): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=species_select_options(),
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        custom_value=True,
                    )
                ),
                vol.Optional(CONF_DEVICE): selector.DeviceSelector(),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_entities(self, user_input: dict[str, Any] | None = None) -> Any:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_care()
        return self.async_show_form(
            step_id="entities", data_schema=_entities_schema(self._entity_guesses)
        )

    async def async_step_care(self, user_input: dict[str, Any] | None = None) -> Any:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_photo()

        match = find_species(self._data.get(CONF_SPECIES, ""))
        if match:
            defaults = {
                CONF_DRY_THRESHOLD: match["dry_threshold"],
                CONF_WET_THRESHOLD: match["wet_threshold"],
                CONF_CARE_TIP: match["care_tip"],
            }
        else:
            defaults = {}
        return self.async_show_form(step_id="care", data_schema=_care_schema(defaults))

    async def async_step_photo(self, user_input: dict[str, Any] | None = None) -> Any:
        if user_input is not None:
            file_id = user_input.get(CONF_PHOTO_UPLOAD)
            if file_id:
                self._data[CONF_PHOTO_PATH] = await async_save_uploaded_photo(self.hass, file_id)
            return await self.async_step_advanced()
        return self.async_show_form(step_id="photo", data_schema=_photo_schema())

    async def async_step_advanced(self, user_input: dict[str, Any] | None = None) -> Any:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_notifications()
        return self.async_show_form(step_id="advanced", data_schema=_advanced_schema({}))

    async def async_step_notifications(self, user_input: dict[str, Any] | None = None) -> Any:
        if user_input is not None:
            self._data.update(user_input)
            await self.async_set_unique_id(
                f"{self._data[CONF_NAME]}_{self._data[CONF_SOIL_MOISTURE_ENTITY]}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=self._data[CONF_NAME], data=self._data)
        return self.async_show_form(step_id="notifications", data_schema=_notify_schema({}))

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return PlantMonitorOptionsFlow()


class PlantMonitorOptionsFlow(OptionsFlow):
    """Let the user change anything after setup, grouped into a menu."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> Any:
        return self.async_show_menu(
            step_id="init",
            menu_options=["entities", "care", "photo", "notifications", "advanced"],
        )

    def _current(self) -> dict[str, Any]:
        return {**self.config_entry.data, **self.config_entry.options}

    async def async_step_entities(self, user_input: dict[str, Any] | None = None) -> Any:
        if user_input is not None:
            new_options = dict(self.config_entry.options)
            new_options.update(user_input)
            return self.async_create_entry(title="", data=new_options)
        current = self._current()
        guesses = {
            k: current[k]
            for k in (
                CONF_SOIL_MOISTURE_ENTITY,
                CONF_TEMPERATURE_ENTITY,
                CONF_HUMIDITY_ENTITY,
                CONF_BATTERY_ENTITY,
            )
            if current.get(k)
        }
        return self.async_show_form(step_id="entities", data_schema=_entities_schema(guesses))

    async def async_step_care(self, user_input: dict[str, Any] | None = None) -> Any:
        if user_input is not None:
            new_options = dict(self.config_entry.options)
            new_options.update(user_input)
            return self.async_create_entry(title="", data=new_options)
        return self.async_show_form(step_id="care", data_schema=_care_schema(self._current()))

    async def async_step_photo(self, user_input: dict[str, Any] | None = None) -> Any:
        if user_input is not None:
            file_id = user_input.get(CONF_PHOTO_UPLOAD)
            new_options = dict(self.config_entry.options)
            if file_id:
                old_photo = self._current().get(CONF_PHOTO_PATH)
                new_options[CONF_PHOTO_PATH] = await async_save_uploaded_photo(self.hass, file_id)
                if old_photo:
                    async_delete_photo(self.hass, old_photo)
            return self.async_create_entry(title="", data=new_options)
        return self.async_show_form(step_id="photo", data_schema=_photo_schema())

    async def async_step_notifications(self, user_input: dict[str, Any] | None = None) -> Any:
        if user_input is not None:
            new_options = dict(self.config_entry.options)
            new_options.update(user_input)
            return self.async_create_entry(title="", data=new_options)
        return self.async_show_form(
            step_id="notifications", data_schema=_notify_schema(self._current())
        )

    async def async_step_advanced(self, user_input: dict[str, Any] | None = None) -> Any:
        if user_input is not None:
            new_options = dict(self.config_entry.options)
            new_options.update(user_input)
            return self.async_create_entry(title="", data=new_options)
        return self.async_show_form(
            step_id="advanced", data_schema=_advanced_schema(self._current())
        )
