"""Runtime state & calculations for a single Plant Monitor config entry.

This intentionally does NOT use a DataUpdateCoordinator with polling: every
value here is derived from other entities' states, so we simply listen for
state-changed events on the source entities and recompute. A small in-memory
rolling buffer of soil-moisture samples is kept to estimate a drying rate
without needing recorder/history queries.
"""
from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, State, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from .const import (
    CONF_BATTERY_ENTITY,
    CONF_BATTERY_LOW,
    CONF_CARE_TIP,
    CONF_DRY_THRESHOLD,
    CONF_HUMIDITY_ENTITY,
    CONF_HUMIDITY_LOW,
    CONF_NOTIFY_DAILY_SUMMARY_ENABLED,
    CONF_NOTIFY_DEVICE_ID,
    CONF_NOTIFY_ENABLED,
    CONF_PHOTO_PATH,
    CONF_SOIL_MOISTURE_ENTITY,
    CONF_SPECIES,
    CONF_TEMP_COLD,
    CONF_TEMP_HOT,
    CONF_TEMPERATURE_ENTITY,
    CONF_WATER_JUMP,
    CONF_WET_THRESHOLD,
    DEFAULT_BATTERY_LOW,
    DEFAULT_CARE_TIP,
    DEFAULT_DRY_THRESHOLD,
    DEFAULT_HUMIDITY_LOW,
    DEFAULT_TEMP_COLD,
    DEFAULT_TEMP_HOT,
    DEFAULT_WATER_JUMP,
    DEFAULT_WET_THRESHOLD,
    HISTORY_MAX_AGE_HOURS,
    HISTORY_MAX_SAMPLES,
    MIN_SPAN_MINUTES_FOR_RATE,
    SIGNAL_UPDATE,
)
from .care_tip_hash import care_tip_hash
from .species import find_species

_LOGGER = logging.getLogger(__name__)


def _to_float(state: State | None) -> float | None:
    """Best-effort float conversion of an entity's state."""
    if state is None:
        return None
    try:
        return float(state.state)
    except (ValueError, TypeError):
        return None


def _is_auto_filled_care_tip(value: str | None, species: dict) -> bool:
    """True for an empty tip, a (current or former) "no species matched"
    placeholder, or any text this species' entry has ever shipped with."""
    if not value or not value.strip():
        return True
    digest = care_tip_hash(value)
    return digest in species.get("care_tip_hashes", []) or digest in _PLACEHOLDER_HASHES


_PLACEHOLDER_HASHES = {
    care_tip_hash(DEFAULT_CARE_TIP),
    care_tip_hash("No species matched - add your own care notes here."),
}


@dataclass
class _Sample:
    timestamp: datetime
    value: float


class PlantData:
    """Holds live values and derived calculations for one plant."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._unsub: list = []
        self._history: deque[_Sample] = deque(maxlen=HISTORY_MAX_SAMPLES)
        self._week_key: tuple[int, int] | None = None

        self.soil_moisture: float | None = None
        self.temperature: float | None = None
        self.humidity: float | None = None
        self.battery: float | None = None

        self.advice: str = ""
        self.health_score: int | None = None
        self.drying_rate: float | None = None  # %/hour, positive = drying out
        self.water_prediction: str = "Onbekend"

        self.last_watered: datetime | None = None
        self.waterings_this_week: int = 0

    # ---- configuration (options override initial data) --------------------
    def _conf(self, key: str, default: float) -> float:
        value = self.entry.options.get(key, self.entry.data.get(key, default))
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @property
    def dry_threshold(self) -> float:
        return self._conf(CONF_DRY_THRESHOLD, DEFAULT_DRY_THRESHOLD)

    @property
    def wet_threshold(self) -> float:
        return self._conf(CONF_WET_THRESHOLD, DEFAULT_WET_THRESHOLD)

    @property
    def temp_hot(self) -> float:
        return self._conf(CONF_TEMP_HOT, DEFAULT_TEMP_HOT)

    @property
    def temp_cold(self) -> float:
        return self._conf(CONF_TEMP_COLD, DEFAULT_TEMP_COLD)

    @property
    def humidity_low(self) -> float:
        return self._conf(CONF_HUMIDITY_LOW, DEFAULT_HUMIDITY_LOW)

    @property
    def battery_low(self) -> float:
        return self._conf(CONF_BATTERY_LOW, DEFAULT_BATTERY_LOW)

    @property
    def water_jump(self) -> float:
        return self._conf(CONF_WATER_JUMP, DEFAULT_WATER_JUMP)

    @property
    def care_tip(self) -> str:
        """The stored care tip, unless it's still an untouched auto-filled
        one: the tip is copied into the config entry at setup time, so a
        plant added with an older release would otherwise keep that
        release's (English or generic) text forever. Anything the user
        edited themselves is always kept as-is."""
        value = self.entry.options.get(CONF_CARE_TIP, self.entry.data.get(CONF_CARE_TIP))
        match = find_species(self.entry.data.get(CONF_SPECIES, ""))
        if match and match.get("care_tip") and _is_auto_filled_care_tip(value, match):
            return match["care_tip"]
        return value if value else DEFAULT_CARE_TIP

    @property
    def care_guide_sections(self) -> dict[str, str]:
        """Parse the flattened 'Label: text' lines into a dict, so the
        dashboard card (and anything else) can read individual sections
        without re-parsing the raw text itself."""
        sections: dict[str, str] = {}
        for line in self.care_tip.split("\n"):
            if ":" not in line:
                continue
            label, _, text = line.partition(":")
            sections[label.strip()] = text.strip()
        return sections

    @property
    def photo_path(self) -> str | None:
        return self.entry.options.get(CONF_PHOTO_PATH, self.entry.data.get(CONF_PHOTO_PATH))

    @property
    def photo_url(self) -> str | None:
        """The user's own uploaded photo takes priority; falls back to the
        matched species' bundled stock photo (an external, verified URL)
        if the plant has none of its own yet."""
        uploaded = self.photo_path
        if uploaded:
            return uploaded
        match = find_species(self.entry.data.get(CONF_SPECIES, ""))
        if match and match.get("stock_photo_url"):
            return match["stock_photo_url"]
        return None

    def _entity(self, key: str) -> str | None:
        # Options (set via "Configure" after setup) override the initial
        # config-flow data. A key that is present in options but empty means
        # the user explicitly cleared that sensor, so don't fall back to data.
        if key in self.entry.options:
            return self.entry.options.get(key) or None
        return self.entry.data.get(key) or None

    @property
    def temperature_entity_id(self) -> str | None:
        return self._entity(CONF_TEMPERATURE_ENTITY)

    @property
    def humidity_entity_id(self) -> str | None:
        humidity = self._entity(CONF_HUMIDITY_ENTITY)
        # Older versions could auto-link the soil sensor as air humidity too;
        # the same entity can never be both, so ignore it in that slot.
        if humidity and humidity == self._entity(CONF_SOIL_MOISTURE_ENTITY):
            return None
        return humidity

    @property
    def battery_entity_id(self) -> str | None:
        return self._entity(CONF_BATTERY_ENTITY)

    @property
    def notify_enabled(self) -> bool:
        return bool(self.entry.options.get(CONF_NOTIFY_ENABLED, self.entry.data.get(CONF_NOTIFY_ENABLED, False)))

    @property
    def notify_device_id(self) -> str | None:
        return self.entry.options.get(CONF_NOTIFY_DEVICE_ID, self.entry.data.get(CONF_NOTIFY_DEVICE_ID))

    @property
    def notify_daily_summary_enabled(self) -> bool:
        return bool(
            self.entry.options.get(
                CONF_NOTIFY_DAILY_SUMMARY_ENABLED,
                self.entry.data.get(CONF_NOTIFY_DAILY_SUMMARY_ENABLED, False),
            )
        )

    # ---- lifecycle ----------------------------------------------------------
    async def async_setup(self) -> None:
        entities = [
            entity_id
            for entity_id in (
                self._entity(CONF_SOIL_MOISTURE_ENTITY),
                self._entity(CONF_TEMPERATURE_ENTITY),
                self.humidity_entity_id,
                self._entity(CONF_BATTERY_ENTITY),
            )
            if entity_id
        ]

        @callback
        def _handle_event(_event) -> None:
            self._refresh_from_states()
            self._recompute()
            async_dispatcher_send(self.hass, f"{SIGNAL_UPDATE}_{self.entry.entry_id}")

        if entities:
            self._unsub.append(
                async_track_state_change_event(self.hass, entities, _handle_event)
            )

        # Prime initial values so entities aren't "unknown" until the next change.
        self._refresh_from_states()
        self._recompute()

    async def async_unload(self) -> None:
        for unsub in self._unsub:
            unsub()
        self._unsub.clear()

    def log_manual_watering(self) -> None:
        """Record a watering that the automatic jump-detection might have missed."""
        now = dt_util.utcnow()
        self.last_watered = now
        self._bump_weekly_counter(now)
        async_dispatcher_send(self.hass, f"{SIGNAL_UPDATE}_{self.entry.entry_id}")

    # ---- internal computation ------------------------------------------------
    def _refresh_from_states(self) -> None:
        hass = self.hass
        previous_soil = self.soil_moisture

        soil_id = self._entity(CONF_SOIL_MOISTURE_ENTITY)
        self.soil_moisture = _to_float(hass.states.get(soil_id)) if soil_id else None

        temp_id = self._entity(CONF_TEMPERATURE_ENTITY)
        self.temperature = _to_float(hass.states.get(temp_id)) if temp_id else None

        hum_id = self.humidity_entity_id
        self.humidity = _to_float(hass.states.get(hum_id)) if hum_id else None

        batt_id = self._entity(CONF_BATTERY_ENTITY)
        self.battery = _to_float(hass.states.get(batt_id)) if batt_id else None

        if self.soil_moisture is None:
            return

        now = dt_util.utcnow()
        self._history.append(_Sample(now, self.soil_moisture))
        self._trim_history(now)

        if (
            previous_soil is not None
            and (self.soil_moisture - previous_soil) >= self.water_jump
        ):
            self.last_watered = now
            self._bump_weekly_counter(now)

    def _trim_history(self, now: datetime) -> None:
        cutoff = now - timedelta(hours=HISTORY_MAX_AGE_HOURS)
        while self._history and self._history[0].timestamp < cutoff:
            self._history.popleft()

    def _bump_weekly_counter(self, now: datetime) -> None:
        local_now = dt_util.as_local(now)
        key = (local_now.isocalendar()[0], local_now.isocalendar()[1])
        if key != self._week_key:
            self._week_key = key
            self.waterings_this_week = 0
        self.waterings_this_week += 1

    def _recompute(self) -> None:
        self._recompute_drying_rate()
        self._recompute_advice()
        self._recompute_health_score()
        self._recompute_water_prediction()

    def _recompute_drying_rate(self) -> None:
        if len(self._history) < 2:
            self.drying_rate = None
            return
        oldest, newest = self._history[0], self._history[-1]
        span_hours = (newest.timestamp - oldest.timestamp).total_seconds() / 3600.0
        if span_hours * 60 < MIN_SPAN_MINUTES_FOR_RATE:
            self.drying_rate = None
            return
        # Positive = drying out (moisture decreasing over time).
        self.drying_rate = round((oldest.value - newest.value) / span_hours, 2)

    def _recompute_advice(self) -> None:
        tips: list[str] = []
        soil = self.soil_moisture

        if soil is not None and soil < self.dry_threshold:
            tips.append("\U0001f331 Geef nu water (ongeveer 200 ml, tot het onderin wegloopt).")
        if soil is not None and soil > self.wet_threshold:
            tips.append("\U0001f4a7 Laat de grond eerst opdrogen voor je weer water geeft.")
        if self.temperature is not None and self.temperature > self.temp_hot:
            tips.append("\U0001f321\ufe0f Het is warm - besproei de bladeren of zet de plant op een koelere plek.")
        if self.temperature is not None and self.temperature < self.temp_cold:
            tips.append("\U0001f321\ufe0f Het is te koud - zet de plant op een warmere plek.")
        if self.humidity is not None and self.humidity < self.humidity_low:
            tips.append("\U0001f4a8 De lucht is droog - besproei de bladeren regelmatig.")
        if self.battery is not None and self.battery < self.battery_low:
            tips.append("\U0001f50b Vervang de batterij van de sensor.")

        self.advice = "\n".join(tips) if tips else "\u2705 Alles OK, geen actie nodig. \U0001f33f"

    def _recompute_health_score(self) -> None:
        soil = self.soil_moisture
        if soil is None:
            soil = (self.dry_threshold + self.wet_threshold) / 2
        temp = self.temperature
        if temp is None:
            temp = (self.temp_cold + self.temp_hot) / 2
        battery = self.battery if self.battery is not None else 100.0

        if self.dry_threshold <= soil <= self.wet_threshold:
            moisture_score = 100.0
        elif soil < self.dry_threshold:
            moisture_score = max(0.0, 100 - (self.dry_threshold - soil) * 5)
        else:
            moisture_score = max(0.0, 100 - (soil - self.wet_threshold) * 5)

        if self.temp_cold <= temp <= self.temp_hot:
            temp_score = 100.0
        elif temp < self.temp_cold:
            temp_score = max(0.0, 100 - (self.temp_cold - temp) * 10)
        else:
            temp_score = max(0.0, 100 - (temp - self.temp_hot) * 10)

        battery_score = max(0.0, min(100.0, battery))

        score = moisture_score * 0.55 + temp_score * 0.30 + battery_score * 0.15
        self.health_score = round(score)

    def _recompute_water_prediction(self) -> None:
        soil = self.soil_moisture
        if soil is None:
            self.water_prediction = "Onbekend"
            return
        if soil <= self.dry_threshold:
            self.water_prediction = "Nu water nodig"
            return
        rate = self.drying_rate
        if rate is None or rate <= 0.05:
            self.water_prediction = "Geen duidelijke daling"
            return
        hours = (soil - self.dry_threshold) / rate
        self.water_prediction = f"Over ongeveer {hours:.1f} uur"
