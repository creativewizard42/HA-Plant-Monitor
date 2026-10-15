"""Catalogue corrections, safe advice and offline photo regressions."""

import json
from pathlib import Path
import struct
import sys
import threading
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from custom_components.plant_monitor.binary_sensor import PlantOverwateredBinarySensor
from custom_components.plant_monitor.config_flow import PlantMonitorConfigFlow
from custom_components.plant_monitor.image import PlantPhotoImage
from custom_components.plant_monitor.notifications import PlantNotifier
from custom_components.plant_monitor.plant_data import PlantData
from custom_components.plant_monitor.species import find_species, load_species

ROOT = Path(__file__).resolve().parent.parent


def make_plant(hass=None, species="Monstera", **data):
    entry = SimpleNamespace(
        entry_id="review", title="Review plant",
        data={"name": "Review plant", "species": species, **data}, options={},
    )
    return PlantData(hass or SimpleNamespace(), entry)


def test_generator_reproduces_complete_catalogue():
    sys.path.insert(0, str(ROOT / "scripts"))
    import generate_species_data

    expected = json.loads((ROOT / "custom_components/plant_monitor/species_data.json").read_text())
    assert generate_species_data.build() == expected
    assert len(expected) == 203
    for plant in expected:
        assert 0 <= plant["dry_threshold"] < plant["wet_threshold"] <= 100
        assert plant["temp_cold_threshold"] < plant["temp_hot_threshold"]
        assert 0 <= plant["humidity_low_threshold"] <= 100
        assert len(plant["care_guide"]) == 8


def test_corrected_names_preserve_old_selections_and_ids():
    pitcher = find_species("Rattlesnake Plant Vine")
    assert pitcher is find_species("Tropical Pitcher Plant")
    assert pitcher["id"] == "rattlesnake-plant-vine-nepenthes-alata-tropical-pitcher"
    assert pitcher["profile"] == "moist_airy"
    assert find_species("Dracaena hahnii") is find_species("Dracaena trifasciata 'Hahnii'")
    assert find_species("Christmas Cactus")["scientific_name"] == "Schlumbergera × buckleyi"
    assert find_species("Thanksgiving Cactus")["scientific_name"] == "Schlumbergera truncata"
    assert find_species("Schlumbergera truncata")["display_name"] == "Thanksgiving Cactus"
    assert find_species("Haworthia attenuata")["scientific_name"] == "Haworthiopsis attenuata"
    assert find_species("Astrophytum ornatum")["display_name"] == "Ornate Star Cactus"
    assert find_species("Bird's Nest Sansevieria")["dry_threshold"] < find_species("Monstera")["dry_threshold"]


@pytest.mark.parametrize("name", ["Umbrella Papyrus", "Venus Flytrap", "Pitcher Plant", "Sundew"])
def test_bog_plants_do_not_receive_drying_advice_or_wet_alerts(name):
    # Include an existing installation's old threshold: safety is not limited
    # to entries created after the catalogue update.
    plant = make_plant(species=name, wet_threshold=80)
    plant.soil_moisture = 99
    plant._recompute()
    assert plant.overwatered is False
    assert PlantOverwateredBinarySensor(plant.entry, plant).is_on is False
    assert not PlantNotifier(plant.hass, plant.entry, plant)._is_overwatered()
    assert "opdrogen" not in plant.advice
    assert plant.health_score == 100
    plant.soil_moisture = None
    assert plant.overwatered is None


def test_nepenthes_is_not_treated_as_a_bog_plant():
    plant = make_plant(species="Tropical Pitcher Plant", wet_threshold=60)
    plant.soil_moisture = 90
    plant._recompute()
    assert plant.overwatered is True
    assert "opdrogen" in plant.advice


@pytest.mark.parametrize("name", ["Living Stones", "Caladium", "Cyclamen", "Dendrobium Orchid"])
def test_dormancy_sensitive_plants_require_growth_phase_check(name):
    plant = make_plant(species=name)
    plant.soil_moisture = 0
    plant._recompute()
    assert "groeifase" in plant.advice
    assert "Geef nu water" not in plant.advice
    assert plant.water_prediction == "Controleer groeifase"


def test_all_species_advice_fits_state_limit_without_fixed_volume_or_misting():
    for species in load_species():
        plant = make_plant(species=species["display_name"])
        for soil in (None, 0, 100):
            plant.soil_moisture, plant.humidity, plant.battery = soil, 0, 0
            for temperature in (-15, 45):
                plant.temperature = temperature
                plant._recompute()
                assert len(plant.advice) <= 255, species["display_name"]
                assert "besproei" not in plant.advice
                assert "200 ml" not in plant.advice


def test_corrected_care_and_toxicity_claims():
    assert "50-70%" in find_species("Calathea Rufibarba")["care_guide"]["humidity"]
    assert "verbetert de drainage niet" in find_species("Alocasia Polly")["care_guide"]["repotting"]
    for name in ("Baseball Plant", "Fishtail Palm", "Asparagus Fern", "Rubber Plant"):
        assert "Giftig of irriterend" in find_species(name)["care_guide"]["toxicity"]
    for plant in load_species():
        assert "meestal niet levensbedreigend" not in plant["care_tip"]
        assert "Wordt door de ASPCA beschouwd" not in plant["care_tip"]


@pytest.mark.asyncio
@pytest.mark.parametrize("name,cold,humidity", [("Golden Barrel Cactus", 5, 20), ("Calathea Rufibarba", 16, 50)])
async def test_new_entries_use_profile_environment_defaults(hass, name, cold, humidity):
    flow = PlantMonitorConfigFlow()
    flow.hass = hass
    flow._data = {"species": name}
    result = await flow.async_step_advanced()
    defaults = {str(key): key.default() for key in result["data_schema"].schema}
    assert defaults["temp_cold_threshold"] == cold
    assert defaults["humidity_low_threshold"] == humidity


@pytest.mark.asyncio
async def test_bundled_photos_are_served_off_loop_and_upload_credit_is_not_reused(hass):
    loop_thread = threading.get_ident()
    original_read = Path.read_bytes
    reads = []

    def checked_read(path):
        if path.parent.name == "photos":
            reads.append(path)
            assert threading.get_ident() != loop_thread
        return original_read(path)

    illustrated = [p for p in load_species() if p["stock_photo_url"]]
    assert len(illustrated) == 8
    with patch.object(Path, "read_bytes", checked_read):
        for species in illustrated:
            plant = make_plant(hass, species["display_name"])
            with patch("custom_components.plant_monitor.image._device_info", return_value={}):
                entity = PlantPhotoImage(hass, plant.entry, plant)
            content = await entity.async_image()
            assert content[:4] == b"RIFF" and content[8:12] == b"WEBP"
            assert entity.content_type == "image/webp"
            assert entity.extra_state_attributes["photo_generated"] is True
            assert "AI-gegenereerde" in entity.extra_state_attributes["photo_credit"]
            plant.entry.options["photo_path"] = "/local/plant_monitor/own.jpg"
            assert plant.photo_url.endswith("own.jpg")
            assert entity.extra_state_attributes == {"photo_source": "user_upload", "photo_generated": False}
    assert len(reads) == 8


@pytest.mark.asyncio
async def test_bundled_photo_rejects_traversal_and_handles_missing_file(hass):
    plant = make_plant(hass)
    with patch("custom_components.plant_monitor.image._device_info", return_value={}):
        entity = PlantPhotoImage(hass, plant.entry, plant)
    for path in ("/plant_monitor_bundled/../manifest.json", "/plant_monitor_bundled/..\\manifest.json", "/plant_monitor_bundled/missing.webp"):
        assert await hass.async_add_executor_job(entity._read_bundled_file, path) is None


def test_brand_assets_have_required_png_dimensions_and_transparency():
    for filename, size in (("icon.png", 256), ("icon@2x.png", 512)):
        png = (ROOT / "custom_components/plant_monitor/brand" / filename).read_bytes()
        assert png[:8] == b"\x89PNG\r\n\x1a\n"
        width, height, _, colour_type = struct.unpack(">IIBB", png[16:26])
        assert (width, height) == (size, size)
        assert colour_type in (4, 6) or b"tRNS" in png
