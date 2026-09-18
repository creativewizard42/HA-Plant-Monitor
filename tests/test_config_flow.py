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
    assert result["step_id"] == "notifications"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"notify_enabled": False, "notify_daily_summary_enabled": False},
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
    assert "Geen soort herkend" in tip_field.default()
    print("test_full_flow_unknown_species_gets_generic_defaults: OK")


async def test_care_tip_sensor_state_never_exceeds_ha_limit_but_full_text_survives(hass):
    """Real end-to-end check (not just the PlantData-level unit test): set
    up an actual plant with a long, multi-section Dutch care guide and
    confirm the resulting sensor's HA *state* is a plain, short string
    (never rejected/truncated oddly by HA itself) while the full text is
    intact and readable via extra_state_attributes."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "Care Tip Length Test", "species": "Monstera"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"soil_moisture_entity": "sensor.caretiptest_soil_moisture"}
    )
    long_tip = "Licht: " + ("A" * 200) + "\nWater geven: " + ("B" * 200) + "\nGiftigheid: " + ("C" * 100)
    assert len(long_tip) > 255
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"dry_threshold": 15.0, "wet_threshold": 55.0, "care_tip": long_tip},
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
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
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"notify_enabled": False, "notify_daily_summary_enabled": False},
    )
    assert result["type"] == "create_entry"
    await hass.async_block_till_done()

    state = hass.states.get("sensor.care_tip_length_test_care_tip") or next(
        (s for s in hass.states.async_all() if s.entity_id.endswith("_care_tip")), None
    )
    assert state is not None, "could not find the care_tip sensor's state"
    assert len(state.state) <= 255, f"HA sensor state must be <= 255 chars, got {len(state.state)}"
    assert state.attributes["full_text"] == long_tip, "full, untruncated text must be in extra_state_attributes"
    assert "Licht" in state.attributes
    assert "Water geven" in state.attributes
    print(
        "test_care_tip_sensor_state_never_exceeds_ha_limit_but_full_text_survives: OK -> "
        f"state len={len(state.state)}, full_text len={len(state.attributes['full_text'])}"
    )


async def test_notifications_step_with_and_without_device(hass):
    """The notifications step must accept both 'skip entirely' (no device
    picked, toggles left off) and 'device picked, toggles on' - this is
    exactly the bug caught above (vol.Optional + a None default breaking
    against the DeviceSelector's validator when the field is left empty)."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    owner_entry = MockConfigEntry(domain="mobile_app")
    owner_entry.add_to_hass(hass)
    device_registry = dr.async_get(hass)
    phone = device_registry.async_get_or_create(
        config_entry_id=owner_entry.entry_id,
        identifiers={("mobile_app", "test_phone")},
        name="Test Phone",
    )

    # Case 1: skip notifications entirely (no device, toggles off).
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "No Notify Plant", "species": "Monstera"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"soil_moisture_entity": "sensor.no_notify_soil"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"dry_threshold": 15.0, "wet_threshold": 55.0, "care_tip": "x"}
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["step_id"] == "advanced"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "temp_cold_threshold": 15.0, "temp_hot_threshold": 28.0,
            "humidity_low_threshold": 40.0, "battery_low_threshold": 20.0,
            "water_jump_threshold": 8.0,
        },
    )
    assert result["step_id"] == "notifications"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"notify_enabled": False, "notify_daily_summary_enabled": False}
    )
    assert result["type"] == "create_entry"
    assert result["data"]["notify_enabled"] is False
    assert "notify_device_id" not in result["data"]

    # Case 2: enable both, with a real device picked.
    result2 = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    result2 = await hass.config_entries.flow.async_configure(
        result2["flow_id"], {"name": "Notify Plant", "species": "Monstera"}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result2["flow_id"], {"soil_moisture_entity": "sensor.notify_plant_soil"}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result2["flow_id"], {"dry_threshold": 15.0, "wet_threshold": 55.0, "care_tip": "x"}
    )
    result2 = await hass.config_entries.flow.async_configure(result2["flow_id"], {})
    result2 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {
            "temp_cold_threshold": 15.0, "temp_hot_threshold": 28.0,
            "humidity_low_threshold": 40.0, "battery_low_threshold": 20.0,
            "water_jump_threshold": 8.0,
        },
    )
    result2 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {
            "notify_enabled": True,
            "notify_device_id": phone.id,
            "notify_daily_summary_enabled": True,
        },
    )
    assert result2["type"] == "create_entry"
    assert result2["data"]["notify_enabled"] is True
    assert result2["data"]["notify_device_id"] == phone.id
    assert result2["data"]["notify_daily_summary_enabled"] is True
    print("test_notifications_step_with_and_without_device: OK")


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
