"""End-to-end tests for notifications.py: dry/overwatered transitions
trigger exactly one notify.send_message call each (not a repeat spam every
update), targeted at the configured device, and disabled plants send none."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.plant_monitor.const import DOMAIN


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


async def _create_plant(hass, *, notify_enabled, notify_device_id=None, name="Notify Test Plant"):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": name, "species": "Not A Real Plant"}
    )
    slug = name.lower().replace(" ", "_")
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"soil_moisture_entity": f"sensor.{slug}_soil"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"dry_threshold": 20.0, "wet_threshold": 70.0, "care_tip": "x"}
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})  # skip photo
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "temp_cold_threshold": 15.0, "temp_hot_threshold": 28.0,
            "humidity_low_threshold": 40.0, "battery_low_threshold": 20.0,
            "water_jump_threshold": 8.0,
        },
    )
    notify_data = {"notify_enabled": notify_enabled, "notify_daily_summary_enabled": False}
    if notify_device_id:
        notify_data["notify_device_id"] = notify_device_id
    result = await hass.config_entries.flow.async_configure(result["flow_id"], notify_data)
    assert result["type"] == "create_entry"
    await hass.async_block_till_done()
    return result, f"sensor.{slug}_soil"


async def test_dry_transition_sends_exactly_one_notification(hass):
    owner_entry = MockConfigEntry(domain="mobile_app")
    owner_entry.add_to_hass(hass)
    from homeassistant.helpers import device_registry as dr

    device_registry = dr.async_get(hass)
    phone = device_registry.async_get_or_create(
        config_entry_id=owner_entry.entry_id,
        identifiers={("mobile_app", "dry_test_phone")},
        name="Dry Test Phone",
    )

    calls = []

    async def _fake_send_message(call):
        calls.append({"data": dict(call.data), "target_device_id": call.data.get("device_id")})

    hass.services.async_register("notify", "send_message", _fake_send_message)

    _, soil_entity = await _create_plant(hass, notify_enabled=True, notify_device_id=phone.id)

    # Starts unknown (no state yet) -> going dry should fire exactly once.
    hass.states.async_set(soil_entity, "50")
    await hass.async_block_till_done()
    assert len(calls) == 0, "should not notify while comfortably above the dry threshold"

    hass.states.async_set(soil_entity, "10")  # below dry_threshold=20
    await hass.async_block_till_done()
    assert len(calls) == 1, f"expected exactly one dry notification, got {len(calls)}"
    assert "water nodig" in calls[0]["data"]["title"]

    # Staying dry on subsequent updates must NOT spam another notification.
    hass.states.async_set(soil_entity, "8")
    await hass.async_block_till_done()
    assert len(calls) == 1, "must not repeat the notification while still dry"

    # Recovering then going dry AGAIN should notify a second time.
    hass.states.async_set(soil_entity, "50")
    await hass.async_block_till_done()
    hass.states.async_set(soil_entity, "5")
    await hass.async_block_till_done()
    assert len(calls) == 2, "a fresh dry transition after recovering should notify again"
    print("test_dry_transition_sends_exactly_one_notification: OK ->", len(calls), "calls")


async def test_overwatered_transition_notifies(hass):
    owner_entry = MockConfigEntry(domain="mobile_app")
    owner_entry.add_to_hass(hass)
    from homeassistant.helpers import device_registry as dr

    device_registry = dr.async_get(hass)
    phone = device_registry.async_get_or_create(
        config_entry_id=owner_entry.entry_id,
        identifiers={("mobile_app", "wet_test_phone")},
        name="Wet Test Phone",
    )

    calls = []

    async def _fake_send_message(call):
        calls.append(dict(call.data))

    hass.services.async_register("notify", "send_message", _fake_send_message)

    _, soil_entity = await _create_plant(
        hass, notify_enabled=True, notify_device_id=phone.id, name="Wet Test Plant"
    )
    hass.states.async_set(soil_entity, "90")  # above wet_threshold=70
    await hass.async_block_till_done()
    assert len(calls) == 1
    assert "te nat" in calls[0]["title"]
    print("test_overwatered_transition_notifies: OK")


async def test_notifications_disabled_sends_nothing(hass):
    calls = []

    async def _fake_send_message(call):
        calls.append(dict(call.data))

    hass.services.async_register("notify", "send_message", _fake_send_message)

    _, soil_entity = await _create_plant(hass, notify_enabled=False, name="Disabled Notify Plant")
    hass.states.async_set(soil_entity, "1")  # very dry
    await hass.async_block_till_done()
    assert len(calls) == 0, "notify_enabled=False must never send anything"
    print("test_notifications_disabled_sends_nothing: OK")


async def test_no_device_configured_sends_nothing_even_if_enabled(hass):
    calls = []

    async def _fake_send_message(call):
        calls.append(dict(call.data))

    hass.services.async_register("notify", "send_message", _fake_send_message)

    # notify_enabled=True but no device picked - must not crash, must not send.
    _, soil_entity = await _create_plant(hass, notify_enabled=True, name="No Device Plant")
    hass.states.async_set(soil_entity, "1")
    await hass.async_block_till_done()
    assert len(calls) == 0
    print("test_no_device_configured_sends_nothing_even_if_enabled: OK")
