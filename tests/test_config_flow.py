"""End-to-end tests of the config flow, driven through a real (test) hass
instance via pytest-homeassistant-custom-component - not just schema checks."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from homeassistant.helpers import device_registry as dr, entity_registry as er

from custom_components.plant_monitor.const import DOMAIN

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


async def test_full_flow_manual_species_match(hass):
    """A recognised species should pre-fill thresholds and a care tip."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] == "form"
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "My Monstera", "species": "Monstera"}
    )
    assert result["step_id"] == "entities"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"soil_moisture_entity": "sensor.test_soil_moisture"}
    )
    assert result["step_id"] == "care"
    # The species matched, so the form's own defaults should already reflect
    # the database values - check via the schema's defaults.
    schema = result["data_schema"].schema
    dry_field = next(k for k in schema if str(k) == "dry_threshold")
    assert dry_field.default() == 15.0

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"dry_threshold": 15.0, "wet_threshold": 55.0, "care_tip": "Custom tip text"},
    )
    assert result["step_id"] == "photo"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["step_id"] == "advanced"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "temp_cold_threshold": 15.0,
            "temp_hot_threshold": 28.0,
            "humidity_low_threshold": 40.0,
            "battery_low_threshold": 20.0,
            "water_jump_threshold": 8.0,
        },
    )
    assert result["type"] == "create_entry"
    assert result["title"] == "My Monstera"
    assert result["data"]["care_tip"] == "Custom tip text"
    assert result["data"]["dry_threshold"] == 15.0
    print("test_full_flow_manual_species_match: OK")


async def test_full_flow_unknown_species_gets_generic_defaults(hass):
    """A made-up plant name should fall back to generic defaults, not crash."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "Bob", "species": "Totally Not A Real Plant Xyz"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"soil_moisture_entity": "sensor.bob_soil_moisture"}
    )
    assert result["step_id"] == "care"
    schema = result["data_schema"].schema
    dry_field = next(k for k in schema if str(k) == "dry_threshold")
    tip_field = next(k for k in schema if str(k) == "care_tip")
    assert dry_field.default() == 20.0  # generic default, not a species match
    assert "No species matched" in tip_field.default()
    print("test_full_flow_unknown_species_gets_generic_defaults: OK")


async def test_device_based_entity_auto_mapping(hass):
    """Registering a device with 4 typical sensor entities should auto-map
    all four roles correctly."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    owner_entry = MockConfigEntry(domain="mqtt")
    owner_entry.add_to_hass(hass)

    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    device = device_registry.async_get_or_create(
        config_entry_id=owner_entry.entry_id,
        identifiers={("mqtt", "0xTESTDEVICE")},
        name="Test Plant Sensor",
    )

    soil = entity_registry.async_get_or_create(
        "sensor", "mqtt", "0xTESTDEVICE_soil_moisture",
        device_id=device.id, config_entry=owner_entry,
    )
    temp = entity_registry.async_get_or_create(
        "sensor", "mqtt", "0xTESTDEVICE_temperature",
        device_id=device.id, config_entry=owner_entry,
    )
    hum = entity_registry.async_get_or_create(
        "sensor", "mqtt", "0xTESTDEVICE_humidity",
        device_id=device.id, config_entry=owner_entry,
    )
    batt = entity_registry.async_get_or_create(
        "sensor", "mqtt", "0xTESTDEVICE_battery",
        device_id=device.id, config_entry=owner_entry,
    )

    hass.states.async_set(temp.entity_id, "21.0", {"device_class": "temperature"})
    hass.states.async_set(hum.entity_id, "55", {"device_class": "humidity"})
    hass.states.async_set(batt.entity_id, "90", {"device_class": "battery"})
    hass.states.async_set(soil.entity_id, "40", {})  # no device_class, matched by name

    from custom_components.plant_monitor.config_flow import _guess_entities_for_device

    guesses = _guess_entities_for_device(hass, device.id)
    assert guesses["soil_moisture_entity"] == soil.entity_id
    assert guesses["temperature_entity"] == temp.entity_id
    assert guesses["humidity_entity"] == hum.entity_id
    assert guesses["battery_entity"] == batt.entity_id
    print("test_device_based_entity_auto_mapping: OK ->", guesses)
