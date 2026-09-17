"""Loads the bundled species database and matches a free-text plant name
against it.

Thresholds in species_data.json are an approximate, documented translation
of general watering guidance into percentages - not lab-measured values -
since soil-moisture sensor readings vary by sensor type, soil mix and pot.
They're meant as a sensible starting point; every value stays editable.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA_FILE = Path(__file__).parent / "species_data.json"


@lru_cache(maxsize=1)
def load_species() -> list[dict[str, Any]]:
    """Load and cache the bundled species database."""
    try:
        with open(_DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return []


def find_species(name: str) -> dict[str, Any] | None:
    """Case-insensitive match of a typed/selected name against display_name
    or any alias. Returns None if nothing matches (a genuinely custom plant)."""
    if not name:
        return None
    needle = name.strip().casefold()
    for entry in load_species():
        if entry["display_name"].casefold() == needle:
            return entry
        if any(alias.casefold() == needle for alias in entry.get("aliases", [])):
            return entry
    return None


def species_select_options() -> list[dict[str, str]]:
    """Options for a SelectSelector: value is the canonical display_name
    (what find_species() matches on), label shows common name(s) + the
    Latin name together so the dropdown's own type-ahead search also
    matches on a Dutch name or the scientific name."""
    return [
        {"value": entry["display_name"], "label": entry.get("select_label", entry["display_name"])}
        for entry in sorted(load_species(), key=lambda e: e["display_name"].casefold())
    ]
