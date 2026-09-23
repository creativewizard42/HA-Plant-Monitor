"""Soortspecifieke Nederlandse verzorgingsgidsen, gebruikt door
generate_species_data.py. Elke part*.py bevat een GUIDES-dict:
display_name -> tuple van 7 teksten in de volgorde van SECTION_KEYS.
"""
from . import part1, part2, part3, part4

SECTION_KEYS = (
    "light", "watering", "humidity", "temperature",
    "fertilizing", "repotting", "common_problems",
)

# Plants that are the same species under another name in PLANTS share one guide.
GUIDE_ALIASES = {
    "Donkey's Tail": "Burro's Tail",
    "Watermelon Begonia": "Watermelon Peperomia",
}


def all_guides() -> dict[str, tuple[str, ...]]:
    merged: dict[str, tuple[str, ...]] = {}
    for part in (part1, part2, part3, part4):
        for name, texts in part.GUIDES.items():
            if name in merged:
                raise ValueError(f"duplicate care guide for {name!r}")
            if len(texts) != len(SECTION_KEYS) or not all(t.strip() for t in texts):
                raise ValueError(f"care guide for {name!r} must have {len(SECTION_KEYS)} non-empty texts")
            merged[name] = texts
    return merged
