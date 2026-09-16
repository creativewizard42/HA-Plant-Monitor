"""Config flow for Plant Monitor.

Deliberately hardware-agnostic: the user points this at whatever soil
moisture (and optionally temperature / humidity / battery) sensor entities
they already have, regardless of which integration created them.
"""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.helpers import selector

from .const import (
    CONF_BATTERY_ENTITY,
    CONF_BATTERY_LOW,
    CONF_DRY_THRESHOLD,
    CONF_HUMIDITY_ENTITY,
    CONF_HUMIDITY_LOW,
    CONF_NAME,
    CONF_SOIL_MOISTURE_ENTITY,
    CONF_SPECIES,
    CONF_TEMP_COLD,
    CONF_TEMP_HOT,
    CONF_TEMPERATURE_ENTITY,
    CONF_WATER_JUMP,
    CONF_WET_THRESHOLD,
    DEFAULT_BATTERY_LOW,
    DEFAULT_DRY_THRESHOLD,
    DEFAULT_HUMIDITY_LOW,
    DEFAULT_TEMP_COLD,
    DEFAULT_TEMP_HOT,
    DEFAULT_WATER_JUMP,
    DEFAULT_WET_THRESHOLD,
    DOMAIN,
    SPECIES_PRESETS,
)


def _entity_selector() -> selector.EntitySelector:
    return selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor"))


def _species_options() -> list[selector.SelectOptionDict]:
    return [
        selector.SelectOptionDict(value=key, label=str(preset["label"]))
        for key, preset in SPECIES_PRESETS.items()
    ]


def _percent_selector(default: float) -> selector.NumberSelector:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=0,
            max=100,
            step=1,
            unit_of_measurement="%",
            mode=selector.NumberSelectorMode.SLIDER,
        )
    )


def _threshold_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_DRY_THRESHOLD,
                default=defaults.get(CONF_DRY_THRESHOLD, DEFAULT_DRY_THRESHOLD),
            ): _percent_selector(DEFAULT_DRY_THRESHOLD),
            vol.Required(
                CONF_WET_THRESHOLD,
                default=defaults.get(CONF_WET_THRESHOLD, DEFAULT_WET_THRESHOLD),
            ): _percent_selector(DEFAULT_WET_THRESHOLD),
            vol.Required(
                CONF_TEMP_COLD,
                default=defaults.get(CONF_TEMP_COLD, DEFAULT_TEMP_COLD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=-10, max=40, step=0.5, unit_of_measurement="\u00b0C")
            ),
            vol.Required(
                CONF_TEMP_HOT,
                default=defaults.get(CONF_TEMP_HOT, DEFAULT_TEMP_HOT),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=50, step=0.5, unit_of_measurement="\u00b0C")
            ),
            vol.Required(
                CONF_HUMIDITY_LOW,
                default=defaults.get(CONF_HUMIDITY_LOW, DEFAULT_HUMIDITY_LOW),
            ): _percent_selector(DEFAULT_HUMIDITY_LOW),
            vol.Required(
                CONF_BATTERY_LOW,
                default=defaults.get(CONF_BATTERY_LOW, DEFAULT_BATTERY_LOW),
            ): _percent_selector(DEFAULT_BATTERY_LOW),
            vol.Required(
                CONF_WATER_JUMP,
                default=defaults.get(CONF_WATER_JUMP, DEFAULT_WATER_JUMP),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, max=50, step=1, unit_of_measurement="%")
            ),
        }
    )


class PlantMonitorConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Plant Monitor. One entry = one plant."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_thresholds()

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): selector.TextSelector(),
                vol.Required(CONF_SPECIES, default="custom"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=_species_options(),
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_SOIL_MOISTURE_ENTITY): _entity_selector(),
                vol.Optional(CONF_TEMPERATURE_ENTITY): _entity_selector(),
                vol.Optional(CONF_HUMIDITY_ENTITY): _entity_selector(),
                vol.Optional(CONF_BATTERY_ENTITY): _entity_selector(),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_thresholds(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        if user_input is not None:
            self._data.update(user_input)
            await self.async_set_unique_id(
                f"{self._data[CONF_NAME]}_{self._data[CONF_SOIL_MOISTURE_ENTITY]}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=self._data[CONF_NAME], data=self._data)

        preset = SPECIES_PRESETS.get(
            self._data.get(CONF_SPECIES, "custom"), SPECIES_PRESETS["custom"]
        )
        return self.async_show_form(
            step_id="thresholds", data_schema=_threshold_schema(preset)
        )

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return PlantMonitorOptionsFlow()


class PlantMonitorOptionsFlow(OptionsFlow):
    """Let the user change thresholds after setup, without redoing the wizard."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init", data_schema=_threshold_schema(current)
        )
