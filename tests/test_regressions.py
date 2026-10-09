"""Regression coverage for cold startup, configuration and sensor edge cases."""

import builtins
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import threading

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from custom_components.plant_monitor import species
from custom_components.plant_monitor.config_flow import (
    PlantMonitorConfigFlow,
    _notify_schema,
)
from custom_components.plant_monitor.validation import thresholds_valid
from custom_components.plant_monitor.plant_data import PlantData
from custom_components.plant_monitor.notifications import PlantNotifier
from homeassistant.helpers import config_validation as cv
from homeassistant.core import State


class States:
    def __init__(self, **values):
        self.values = values

    def get(self, entity_id):
        return self.values.get(entity_id)


def plant(states=None, **data):
    hass = SimpleNamespace(states=states or States())
    entry = SimpleNamespace(
        data={"name": "Probe", "soil_moisture_entity": "sensor.soil", **data},
        options={},
        entry_id="probe",
    )
    return PlantData(hass, entry)


@pytest.mark.asyncio
async def test_cold_species_form_performs_no_file_io_on_event_loop(hass):
    flow = PlantMonitorConfigFlow()
    flow.hass = hass
    species.load_species.cache_clear()
    calls = []
    loop_thread = threading.get_ident()
    real_open = builtins.open

    def observe_open(*args, **kwargs):
        if Path(args[0]) == species._DATA_FILE and threading.get_ident() == loop_thread:
            calls.append(str(args[0]))
        return real_open(*args, **kwargs)

    with patch("builtins.open", observe_open):
        await flow.async_step_user()
    assert not calls, f"File opened synchronously in async form: {calls}"


@pytest.mark.asyncio
async def test_cold_entry_startup_performs_no_file_io_on_event_loop(
    hass, enable_custom_integrations
):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain="plant_monitor",
        version=2,
        data={
            "name": "Cold",
            "species": "Monstera",
            "soil_moisture_entity": "sensor.soil",
        },
    )
    entry.add_to_hass(hass)
    species.load_species.cache_clear()
    loop_thread = threading.get_ident()
    reads_on_loop = []
    real_open = builtins.open

    def observe_open(*args, **kwargs):
        if Path(args[0]) == species._DATA_FILE and threading.get_ident() == loop_thread:
            reads_on_loop.append(str(args[0]))
        return real_open(*args, **kwargs)

    with patch("builtins.open", observe_open):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert not reads_on_loop, (
        f"Cold entry setup read species JSON on event loop: {reads_on_loop}"
    )


@pytest.mark.asyncio
async def test_executor_preload_avoids_file_io_in_species_form(hass):
    species.load_species.cache_clear()
    loop_thread = threading.get_ident()
    reads = []
    real_open = builtins.open

    def observe_open(*args, **kwargs):
        if Path(args[0]) == species._DATA_FILE:
            reads.append(threading.get_ident())
        return real_open(*args, **kwargs)

    flow = PlantMonitorConfigFlow()
    flow.hass = hass
    with patch("builtins.open", observe_open):
        await hass.async_add_executor_job(species.load_species)
        await flow.async_step_user()
    assert reads and all(thread_id != loop_thread for thread_id in reads)


def test_unavailable_soil_does_not_claim_healthy():
    p = plant(States(**{"sensor.soil": State("sensor.soil", "unavailable")}))
    p._refresh_from_states()
    p._recompute()
    assert p.health_score is None, (
        f"Unavailable sensor gives score {p.health_score} and advice {p.advice!r}"
    )


def test_advice_state_fits_home_assistant_limit():
    p = plant()
    p.soil_moisture, p.temperature, p.humidity, p.battery = 0, 40, 0, 0
    p._recompute()
    assert len(p.advice) <= 255, f"Advice state is {len(p.advice)} characters"


def test_threshold_schema_rejects_inverted_range():
    assert not thresholds_valid(
        {"dry_threshold": 80, "wet_threshold": 20}, "dry_threshold", "wet_threshold"
    )


def test_nan_reading_is_treated_as_missing():
    p = plant(States(**{"sensor.soil": State("sensor.soil", "nan")}))
    p._refresh_from_states()
    assert p.soil_moisture is None, f"Non-finite reading accepted: {p.soil_moisture}"


def test_fahrenheit_sensor_is_converted_for_celsius_thresholds():
    p = plant(
        States(
            **{
                "sensor.soil": State("sensor.soil", "50"),
                "sensor.temp": State(
                    "sensor.temp", "68", {"unit_of_measurement": "°F"}
                ),
            }
        ),
        temperature_entity="sensor.temp",
    )
    p._refresh_from_states()
    assert p.temperature == 20, f"68°F treated as {p.temperature}°C"


def test_weekly_counter_resets_when_week_changes_without_watering():
    p = plant(States(**{"sensor.soil": State("sensor.soil", "50")}))
    p._bump_weekly_counter(datetime(2026, 10, 4, 12, tzinfo=timezone.utc))
    with patch(
        "custom_components.plant_monitor.plant_data.dt_util.utcnow",
        return_value=datetime(2026, 10, 5, 12, tzinfo=timezone.utc),
    ):
        p._refresh_from_states()
        p._recompute()
    assert p.waterings_this_week == 0, (
        f"Last week count remains {p.waterings_this_week}"
    )


@pytest.mark.asyncio
async def test_daily_summary_title_is_valid_unicode():
    p = plant(notify_daily_summary_enabled=True, notify_device_id="phone")
    notifier = PlantNotifier(p.hass, p.entry, p)
    titles = []

    async def capture(title, message):
        titles.append(title)

    notifier._send = capture
    await notifier._handle_daily_summary(None)
    titles[0].encode("utf-8")


@pytest.mark.asyncio
async def test_blueprint_accepts_action_selector_list(hass):
    import yaml

    class Loader(yaml.SafeLoader):
        pass

    inputs = {
        "dry_sensor": "binary_sensor.dry",
        "overwatered_sensor": "binary_sensor.wet",
        "overwatered_delay": {"hours": 1},
        "notify_action": [
            {
                "action": "notify.mobile_app_phone",
                "data": {"message": "{{ plant_message }}"},
            }
        ],
    }
    Loader.add_constructor(
        "!input", lambda loader, node: inputs[loader.construct_scalar(node)]
    )
    blueprint = yaml.load(
        (
            Path(__file__).parent.parent
            / "blueprints/automation/plant_monitor/plant_needs_attention.yaml"
        ).read_text(),
        Loader=Loader,
    )
    cv.SCRIPT_SCHEMA(blueprint["actions"])


@pytest.mark.asyncio
async def test_version_one_entry_can_be_loaded(hass, enable_custom_integrations):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain="plant_monitor",
        version=1,
        data={
            "name": "Legacy",
            "species": "custom",
            "soil_moisture_entity": "sensor.soil",
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id), (
        f"Legacy entry state: {entry.state}"
    )
    assert entry.version == 2
    assert entry.data["soil_moisture_entity"] == "sensor.soil"


@pytest.mark.asyncio
async def test_mobile_app_legacy_service_receives_notification(hass):
    from homeassistant.setup import async_setup_component
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from homeassistant.helpers import device_registry as dr

    await async_setup_component(hass, "notify", {})
    owner = MockConfigEntry(domain="mobile_app")
    owner.add_to_hass(hass)
    phone = dr.async_get(hass).async_get_or_create(
        config_entry_id=owner.entry_id, identifiers={("mobile_app", "probe_phone")}
    )
    delivered = []

    async def legacy_mobile_app_service(call):
        delivered.append(dict(call.data))

    hass.services.async_register(
        "notify", "mobile_app_probe_phone", legacy_mobile_app_service
    )
    hass.data["mobile_app"] = {
        "devices": {"webhook": phone},
        "config_entries": {
            "webhook": SimpleNamespace(
                data={
                    "app_data": {
                        "push_token": "test",
                        "push_url": "https://example.invalid",
                    }
                }
            )
        },
        "notify": SimpleNamespace(
            registered_targets={"mobile_app_probe_phone": "webhook"}
        ),
    }
    entry = SimpleNamespace(
        data={"name": "Probe", "notify_enabled": True, "notify_device_id": phone.id},
        options={},
        entry_id="probe",
    )
    p = PlantData(hass, entry)
    await PlantNotifier(hass, entry, p)._send("Water needed", "Dry soil")
    assert (
        delivered
        and delivered[0]["message"] == "Dry soil"
        and delivered[0]["title"] == "Water needed"
    )


@pytest.mark.asyncio
async def test_threshold_forms_show_errors_without_saving(hass):
    flow = PlantMonitorConfigFlow()
    flow.hass = hass
    care = await flow.async_step_care(
        {"dry_threshold": 80, "wet_threshold": 20, "care_tip": "x"}
    )
    assert care["errors"] == {"base": "invalid_thresholds"}
    assert "dry_threshold" not in flow._data
    advanced = await flow.async_step_advanced(
        {"temp_cold_threshold": 30, "temp_hot_threshold": 10}
    )
    assert advanced["errors"] == {"base": "invalid_temperature_thresholds"}
    assert "temp_cold_threshold" not in flow._data


def test_notification_device_prefill_can_be_cleared():
    validated = _notify_schema({"notify_device_id": "old"})(
        {"notify_enabled": False, "notify_daily_summary_enabled": False}
    )
    assert "notify_device_id" not in validated


@pytest.mark.asyncio
async def test_threshold_number_rejects_invalid_pair(hass, enable_custom_integrations):
    from pytest_homeassistant_custom_component.common import MockConfigEntry
    from homeassistant.helpers import entity_registry as er
    from homeassistant.exceptions import ServiceValidationError

    entry = MockConfigEntry(
        domain="plant_monitor",
        version=2,
        data={
            "name": "Threshold",
            "species": "Custom",
            "soil_moisture_entity": "sensor.soil",
            "dry_threshold": 20,
            "wet_threshold": 70,
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    dry = next(
        e
        for e in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
        if e.unique_id.endswith("_dry_threshold")
    )
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": dry.entity_id, "value": 80},
            blocking=True,
        )
    assert "dry_threshold" not in entry.options


@pytest.mark.asyncio
async def test_legacy_migration_preserves_custom_settings(
    hass, enable_custom_integrations
):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain="plant_monitor",
        version=1,
        data={
            "name": "Legacy",
            "species": "strelitzia",
            "soil_moisture_entity": "sensor.soil",
            "dry_threshold": 17,
        },
        options={"wet_threshold": 66, "care_tip": "My own guide"},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    assert entry.data["species"] == "Bird of Paradise"
    assert entry.data["dry_threshold"] == 17
    assert entry.options == {"wet_threshold": 66, "care_tip": "My own guide"}


def test_unrelated_sensor_updates_do_not_evict_soil_history():
    p = plant(States(**{"sensor.soil": State("sensor.soil", "50")}))
    p._refresh_from_states()
    for _ in range(300):
        p._refresh_from_states(sample_soil=False)
    assert len(p._history) == 1


def test_unknown_temperature_unit_is_missing_instead_of_crashing():
    p = plant(
        States(
            **{
                "sensor.temp": State(
                    "sensor.temp", "5", {"unit_of_measurement": "bananas"}
                )
            }
        ),
        temperature_entity="sensor.temp",
    )
    p._refresh_from_states()
    assert p.temperature is None


def test_database_failure_is_not_cached_as_empty():
    species.load_species.cache_clear()
    with patch("builtins.open", side_effect=OSError("probe")):
        with pytest.raises(OSError):
            species.load_species()
    assert species.load_species()


@pytest.mark.asyncio
async def test_unsupported_notification_device_gets_form_error(hass):
    from homeassistant.helpers import device_registry as dr
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    owner = MockConfigEntry(domain="test")
    owner.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=owner.entry_id, identifiers={("test", "not_notify")}
    )
    flow = PlantMonitorConfigFlow()
    flow.hass = hass
    result = await flow.async_step_notifications(
        {
            "notify_enabled": True,
            "notify_daily_summary_enabled": False,
            "notify_device_id": device.id,
        }
    )
    assert result["errors"] == {"base": "unsupported_notification_device"}
