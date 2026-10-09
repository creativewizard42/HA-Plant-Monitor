"""Validation shared by configuration flows and threshold services."""

import math

from .const import CONF_DRY_THRESHOLD, CONF_WET_THRESHOLD, CONF_TEMP_COLD, CONF_TEMP_HOT


def thresholds_valid(values: dict, low_key: str, high_key: str) -> bool:
    """Require finite, ordered threshold pairs within their supported bounds."""
    try:
        low, high = float(values[low_key]), float(values[high_key])
    except (KeyError, ValueError, TypeError):
        return False
    if not (math.isfinite(low) and math.isfinite(high) and low < high):
        return False
    if (low_key, high_key) == (CONF_DRY_THRESHOLD, CONF_WET_THRESHOLD):
        return 0 <= low < high <= 100
    if (low_key, high_key) == (CONF_TEMP_COLD, CONF_TEMP_HOT):
        return -10 <= low <= 40 and 0 <= high <= 50
    return True
