"""One-off helper: record a hash of every care_tip text any earlier release
of species_data.json ever generated, into scripts/legacy_care_tip_hashes.json.

Why: the care tip is copied into a plant's config entry at setup time, so
plants added with an older release keep that release's (possibly English,
or generic profile-templated) text forever. With these hashes the
integration can recognise "this is still an untouched, auto-generated tip"
and show the current guide instead - while never overriding a tip the user
actually edited themselves (its hash won't be in the list).

Usage (from the repo root, needs git):
    python scripts/collect_legacy_care_tips.py

generate_species_data.py also appends the hash of every tip it generates,
so this only needs re-running if history is rewritten.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components", "plant_monitor"))
from care_tip_hash import care_tip_hash  # noqa: E402

DATA_PATH = "custom_components/plant_monitor/species_data.json"
OUT_PATH = os.path.join(os.path.dirname(__file__), "legacy_care_tip_hashes.json")


def main() -> None:
    commits = subprocess.run(
        ["git", "log", "--format=%H", "--", DATA_PATH], capture_output=True, text=True, check=True
    ).stdout.split()

    hashes: dict[str, set[str]] = {}
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH, encoding="utf-8") as f:
            hashes = {k: set(v) for k, v in json.load(f).items()}

    for commit in commits:
        raw = subprocess.run(
            ["git", "show", f"{commit}:{DATA_PATH}"], capture_output=True, check=True
        ).stdout.decode("utf-8")
        for entry in json.loads(raw):
            tip = entry.get("care_tip")
            if tip:
                hashes.setdefault(entry["display_name"], set()).add(care_tip_hash(tip))

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump({k: sorted(v) for k, v in sorted(hashes.items())}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"Recorded hashes for {len(hashes)} plants from {len(commits)} commits -> {OUT_PATH}")


if __name__ == "__main__":
    main()
