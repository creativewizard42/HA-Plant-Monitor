"""Standalone test of PlantData's calculation logic using lightweight stubs
(no full Home Assistant runtime needed - just enough surface for the code
under test to run against)."""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from custom_components.plant_monitor.plant_data import PlantData, _Sample  # noqa: E402


class FakeState:
    def __init__(self, state):
        self.state = str(state)


class FakeStates:
    def __init__(self):
        self._d = {}

    def set(self, entity_id, value):
        self._d[entity_id] = FakeState(value)

    def get(self, entity_id):
        return self._d.get(entity_id)


class FakeHass:
    def __init__(self):
        self.states = FakeStates()


class FakeEntry:
    def __init__(self, data, options=None):
        self.data = data
        self.options = options or {}
        self.entry_id = "test_entry"


def make_plant(data, options=None):
    hass = FakeHass()
    entry = FakeEntry(data, options)
    plant = PlantData(hass, entry)
    return hass, plant


def test_advice_dry():
    hass, plant = make_plant(
        {
            "soil_moisture_entity": "sensor.soil",
            "dry_threshold": 20.0,
            "wet_threshold": 70.0,
        }
    )
    hass.states.set("sensor.soil", 10)
    plant._refresh_from_states()
    plant._recompute()
    assert "Water now" in plant.advice, plant.advice
    assert plant.health_score is not None and plant.health_score < 100
    print("test_advice_dry: OK ->", plant.advice, "| score:", plant.health_score)


def test_advice_overwatered():
    hass, plant = make_plant(
        {
            "soil_moisture_entity": "sensor.soil",
            "dry_threshold": 20.0,
            "wet_threshold": 70.0,
        }
    )
    hass.states.set("sensor.soil", 90)
    plant._refresh_from_states()
    plant._recompute()
    assert "dry out" in plant.advice, plant.advice
    print("test_advice_overwatered: OK ->", plant.advice)


def test_advice_all_good():
    hass, plant = make_plant(
        {
            "soil_moisture_entity": "sensor.soil",
            "temperature_entity": "sensor.temp",
            "humidity_entity": "sensor.hum",
            "battery_entity": "sensor.batt",
            "dry_threshold": 20.0,
            "wet_threshold": 70.0,
        }
    )
    hass.states.set("sensor.soil", 45)
    hass.states.set("sensor.temp", 21)
    hass.states.set("sensor.hum", 55)
    hass.states.set("sensor.batt", 100)
    plant._refresh_from_states()
    plant._recompute()
    assert plant.advice.startswith("\u2705"), plant.advice
    assert plant.health_score == 100, plant.health_score
    print("test_advice_all_good: OK -> score:", plant.health_score)


def test_temp_and_battery_and_humidity_advice():
    hass, plant = make_plant(
        {
            "soil_moisture_entity": "sensor.soil",
            "temperature_entity": "sensor.temp",
            "humidity_entity": "sensor.hum",
            "battery_entity": "sensor.batt",
            "dry_threshold": 20.0,
            "wet_threshold": 70.0,
        }
    )
    hass.states.set("sensor.soil", 45)
    hass.states.set("sensor.temp", 32)  # hot
    hass.states.set("sensor.hum", 20)  # dry air
    hass.states.set("sensor.batt", 5)  # low battery
    plant._refresh_from_states()
    plant._recompute()
    assert "warm" in plant.advice
    assert "dry - mist" in plant.advice
    assert "battery" in plant.advice
    print("test_temp_and_battery_and_humidity_advice: OK ->", repr(plant.advice))


def test_drying_rate_and_prediction():
    hass, plant = make_plant(
        {
            "soil_moisture_entity": "sensor.soil",
            "dry_threshold": 20.0,
            "wet_threshold": 70.0,
        }
    )
    # Manually seed history: dropped from 50% to 40% over 1 hour -> 10 %/h
    now = datetime.now(timezone.utc)
    plant._history.append(_Sample(now - timedelta(hours=1), 50.0))
    plant._history.append(_Sample(now, 40.0))
    hass.states.set("sensor.soil", 40)
    plant.soil_moisture = 40.0
    plant._recompute()
    assert plant.drying_rate == 10.0, plant.drying_rate
    # (40 - 20) / 10 %/h = 2 hours
    assert "2.0 hours" in plant.water_prediction, plant.water_prediction
    print("test_drying_rate_and_prediction: OK -> rate:", plant.drying_rate, "| prediction:", plant.water_prediction)


def test_watering_detection_and_weekly_counter():
    hass, plant = make_plant(
        {
            "soil_moisture_entity": "sensor.soil",
            "dry_threshold": 20.0,
            "wet_threshold": 70.0,
            "water_jump_threshold": 8.0,
        }
    )
    hass.states.set("sensor.soil", 15)
    plant._refresh_from_states()  # prev=None -> no watering event yet
    assert plant.last_watered is None
    assert plant.waterings_this_week == 0

    hass.states.set("sensor.soil", 35)  # jump of 20 >= 8 -> counts as watering
    plant._refresh_from_states()
    assert plant.last_watered is not None
    assert plant.waterings_this_week == 1
    print("test_watering_detection_and_weekly_counter: OK -> waterings:", plant.waterings_this_week)


def test_dry_binary_sensor_logic_via_thresholds():
    # Mirrors what binary_sensor.py checks (soil vs thresholds), tested here
    # directly on PlantData since that's where the source values live.
    hass, plant = make_plant(
        {"soil_moisture_entity": "sensor.soil", "dry_threshold": 20.0, "wet_threshold": 70.0}
    )
    hass.states.set("sensor.soil", 10)
    plant._refresh_from_states()
    assert plant.soil_moisture < plant.dry_threshold
    hass.states.set("sensor.soil", 80)
    plant._refresh_from_states()
    assert plant.soil_moisture > plant.wet_threshold
    print("test_dry_binary_sensor_logic_via_thresholds: OK")


def test_options_override_data():
    hass, plant = make_plant(
        {"soil_moisture_entity": "sensor.soil", "dry_threshold": 20.0, "wet_threshold": 70.0},
        options={"dry_threshold": 30.0},
    )
    assert plant.dry_threshold == 30.0  # options win over data
    assert plant.wet_threshold == 70.0  # falls back to data
    print("test_options_override_data: OK")


def test_care_tip_and_photo_path():
    # No care_tip/photo set at all -> generic fallback text, no photo.
    hass, plant = make_plant({"soil_moisture_entity": "sensor.soil"})
    assert "Geen soort herkend" in plant.care_tip
    assert plant.photo_path is None

    # Set via data (as the initial config flow would).
    hass, plant = make_plant(
        {"soil_moisture_entity": "sensor.soil", "care_tip": "Bright light, water weekly.",
         "photo_path": "/local/plant_monitor/abc123.jpg"}
    )
    assert plant.care_tip == "Bright light, water weekly."
    assert plant.photo_path == "/local/plant_monitor/abc123.jpg"

    # Options override data (as the options flow re-upload/edit would).
    hass, plant = make_plant(
        {"soil_moisture_entity": "sensor.soil", "care_tip": "Old tip", "photo_path": "/local/plant_monitor/old.jpg"},
        options={"care_tip": "New tip", "photo_path": "/local/plant_monitor/new.jpg"},
    )
    assert plant.care_tip == "New tip"
    assert plant.photo_path == "/local/plant_monitor/new.jpg"
    print("test_care_tip_and_photo_path: OK")


def test_photo_url_fallback_chain():
    # No upload, no species match -> nothing to show.
    hass, plant = make_plant({"soil_moisture_entity": "sensor.soil", "species": "Not A Real Plant"})
    assert plant.photo_url is None

    # No upload, but species matched and has a stock photo -> use it.
    hass, plant = make_plant({"soil_moisture_entity": "sensor.soil", "species": "Monstera"})
    assert plant.photo_url is not None
    assert plant.photo_url.startswith("https://")

    # No upload, species matched but that species has NO stock photo -> None.
    hass, plant = make_plant({"soil_moisture_entity": "sensor.soil", "species": "Fatsia"})
    assert plant.photo_url is None

    # A user upload always wins over any stock photo, even for a species that has one.
    hass, plant = make_plant(
        {"soil_moisture_entity": "sensor.soil", "species": "Monstera", "photo_path": "/local/plant_monitor/mine.jpg"}
    )
    assert plant.photo_url == "/local/plant_monitor/mine.jpg"
    print("test_photo_url_fallback_chain: OK")


if __name__ == "__main__":
    tests = [
        test_advice_dry,
        test_advice_overwatered,
        test_advice_all_good,
        test_temp_and_battery_and_humidity_advice,
        test_drying_rate_and_prediction,
        test_watering_detection_and_weekly_counter,
        test_dry_binary_sensor_logic_via_thresholds,
        test_options_override_data,
        test_care_tip_and_photo_path,
        test_photo_url_fallback_chain,
    ]
    failures = 0
    for t in tests:
        try:
            t()
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"{t.__name__}: FAILED -> {exc!r}")
    print()
    if failures:
        print(f"{failures} test(s) FAILED")
        sys.exit(1)
    print(f"All {len(tests)} tests passed.")
