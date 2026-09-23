"""Whitespace-insensitive fingerprint of a care tip text.

Shared by the integration (to recognise an untouched, auto-generated care
tip stored by an older release) and by the scripts that generate
species_data.json. Deliberately dependency-free so the scripts can import
it without Home Assistant installed.
"""
from __future__ import annotations

import hashlib


def care_tip_hash(text: str) -> str:
    normalized = " ".join(str(text).split())
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]
