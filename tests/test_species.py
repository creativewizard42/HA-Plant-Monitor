"""Tests for species.py - in particular Dutch common-name matching, since
that was a reported gap (e.g. "pannenkoekenplant" not resolving to its
English-labelled database entry)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from custom_components.plant_monitor.species import find_species, load_species, species_select_options


def test_database_loads_and_has_no_duplicate_ids():
    data = load_species()
    assert len(data) > 150
    ids = [e["id"] for e in data]
    assert len(ids) == len(set(ids)), "duplicate species ids found"
    print(f"test_database_loads_and_has_no_duplicate_ids: OK ({len(data)} species)")


def test_dutch_common_names_resolve():
    cases = {
        "pannenkoekenplant": "Chinese Money Plant",
        "Pannenkoekplant": "Chinese Money Plant",
        "vrouwentong": "Snake Plant",
        "gatenplant": "Monstera",
        "geluksplant": "ZZ Plant",
        "aronskelk": "Calla Lily (potted)",
        "kamerlinde": "Room Lime",
        "bananenplant": "Banana Plant",
        "lepelplant": "Peace Lily",
        "drakenbloedboom": "Dragon Tree",
    }
    for dutch_name, expected_display_name in cases.items():
        match = find_species(dutch_name)
        assert match is not None, f"{dutch_name!r} did not match anything"
        assert match["display_name"] == expected_display_name, (
            f"{dutch_name!r} matched {match['display_name']!r}, expected {expected_display_name!r}"
        )
    print(f"test_dutch_common_names_resolve: OK ({len(cases)} names checked)")


def test_scientific_name_and_english_name_still_resolve():
    assert find_species("Pilea peperomioides")["display_name"] == "Chinese Money Plant"
    assert find_species("Chinese Money Plant")["display_name"] == "Chinese Money Plant"
    assert find_species("chinese money plant")["display_name"] == "Chinese Money Plant"  # case-insensitive
    print("test_scientific_name_and_english_name_still_resolve: OK")


def test_unknown_name_returns_none():
    assert find_species("Definitely Not A Real Plant 12345") is None
    print("test_unknown_name_returns_none: OK")


def test_select_options_show_common_and_latin_name():
    options = species_select_options()
    pilea_option = next(o for o in options if o["value"] == "Chinese Money Plant")
    assert "Pannenkoekenplant" in pilea_option["label"]
    assert "Pilea peperomioides" in pilea_option["label"]
    print("test_select_options_show_common_and_latin_name: OK ->", pilea_option["label"])


def test_every_species_has_its_own_dutch_care_guide():
    # The old generic profile template's watering line - no species should
    # fall back to it any more.
    generic = "Laat de bovenste laag van de grond opdrogen voor je opnieuw water geeft."
    sections = ("Licht:", "Water geven:", "Luchtvochtigheid:", "Temperatuur:", "Bemesten:",
                "Verpotten:", "Veelvoorkomende problemen:", "Giftigheid:")
    for entry in load_species():
        tip = entry["care_tip"]
        assert generic not in tip, f"{entry['display_name']} still uses the generic template"
        for label in sections:
            assert label in tip, f"{entry['display_name']} is missing {label!r}"
        assert entry.get("nl_label"), f"{entry['display_name']} has no nl_label"
        assert entry.get("care_tip_hashes"), f"{entry['display_name']} has no care_tip_hashes"
    print("test_every_species_has_its_own_dutch_care_guide: OK")


if __name__ == "__main__":
    tests = [
        test_database_loads_and_has_no_duplicate_ids,
        test_every_species_has_its_own_dutch_care_guide,
        test_dutch_common_names_resolve,
        test_scientific_name_and_english_name_still_resolve,
        test_unknown_name_returns_none,
        test_select_options_show_common_and_latin_name,
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
