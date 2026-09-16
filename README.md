# Plant Monitor for Home Assistant

Turns a plain soil-moisture sensor (any brand, any integration) into a full
plant-care dashboard: species-aware advice, a 0-100 health score, a drying
rate, a "water needed in X hours" prediction, and an automatic watering log
- with a companion notification blueprint.

This is **not** tied to any specific sensor brand. During setup you simply
point it at the entities you already have in Home Assistant.

## Features

- **Works with any soil moisture sensor** - Zigbee2MQTT, ESPHome, Xiaomi Mi
  Flora, Tuya, whatever exposes a plain `sensor.*` percentage.
- **Species presets** (Strelitzia, Monstera, Calathea, Asplenium, or Custom)
  pre-fill sensible dry/overwater thresholds - fully editable, before and
  after setup.
- **One config entry per plant**, so you can add as many as you like from
  *Settings -> Devices & services -> Add integration -> Plant Monitor*.
- Entities created per plant:
  - `sensor.<plant>_advice` - a plain-language tip combining moisture,
    temperature, humidity and battery
  - `sensor.<plant>_health_score` - weighted 0-100 score
  - `sensor.<plant>_drying_rate` - %/hour, calculated from a rolling window
    of recent readings (no recorder/history queries needed)
  - `sensor.<plant>_water_prediction` - "in about X hours" / "water needed
    now" / "no clear trend"
  - `sensor.<plant>_last_watered` and `sensor.<plant>_waterings_this_week` -
    automatic watering log, detected from a sudden moisture jump
  - `binary_sensor.<plant>_dry` / `binary_sensor.<plant>_overwatered`
  - `number.<plant>_dry_threshold` / `number.<plant>_wet_threshold` - live
    sliders, usable straight from a dashboard tile
- **`plant_monitor.log_watering` service** to log a watering manually (for
  slow drip-irrigation the jump-detection won't catch)
- **Notification blueprint** for "needs water" / "overwatered" alerts with a
  configurable delay on the overwatered check

## Installation

### Option A - HACS custom repository (available immediately)

1. In Home Assistant, open **HACS**.
2. Go to any HACS section, open the **⋮** menu -> **Custom repositories**.
3. Add `https://github.com/YOUR_GITHUB_USERNAME/ha-plant-monitor`, category
   **Integration**.
4. Search for "Plant Monitor" in HACS and install it.
5. Restart Home Assistant.

### Option B - manual

Copy `custom_components/plant_monitor` into your Home Assistant's
`config/custom_components/` folder and restart.

## Setup

1. **Settings -> Devices & services -> Add integration -> Plant Monitor.**
2. Give the plant a name, pick a species (or "Custom"), and select your
   existing soil moisture sensor. Temperature/humidity/battery are optional.
3. Review the pre-filled thresholds and adjust if you like.
4. Repeat for each plant - each one is a separate config entry (and its own
   device).

You can revisit thresholds any time via the device's **Configure** button,
or by dragging the `number.<plant>_dry_threshold` / `wet_threshold` sliders
directly on a dashboard.

## Notifications

Import the blueprint: **Settings -> Automations & scenes -> Blueprints ->
Import blueprint**, paste the raw URL to
`blueprints/automation/plant_monitor/plant_needs_attention.yaml` from this
repo. Create one automation per plant from it, picking that plant's `Dry`
and `Overwatered` sensors and your notification target.

## Dashboard

There's no bundled custom card (that would be a second HACS "plugin"
project) - instead, `examples/dashboard_row.yaml` shows a "photo + advice +
trend + gauge" row built entirely from Home Assistant's built-in cards, so
it works with no extra dependencies. Copy it and swap in your own entity
IDs from the plant's device page.

## Testing

`tests/test_plant_data.py` exercises the calculation engine (advice text,
health score, drying rate, water prediction, watering detection, weekly
counter, options-override-data precedence) against lightweight stubs, no
running Home Assistant instance required:

```bash
pip install homeassistant  # provides voluptuous, dt_util, etc.
python tests/test_plant_data.py
```

All modules have also been import-checked against a real installed
`homeassistant` package (2025.1.4) to catch API mismatches.

## Known limitations (v0.1.0)

- The drying-rate history is kept in memory, not in the recorder database:
  it resets on a Home Assistant restart and briefly after a threshold
  change (options reload), so the drying rate / prediction take a little
  while to reappear afterwards.
- Watering detection is a simple "moisture jumped by more than X% between
  two readings" check. Very slow drip irrigation may not trigger it - use
  the `plant_monitor.log_watering` service for those.
- This has been tested for correctness by code review, `py_compile` and
  JSON validation, but **not yet against a running Home Assistant
  instance**. Please try it in a test/dev instance before relying on it,
  and open an issue if something doesn't load.

## Before you publish this yourself

Replace `YOUR_GITHUB_USERNAME` in `custom_components/plant_monitor/manifest.json`,
`blueprints/automation/plant_monitor/plant_needs_attention.yaml`, and this
README with your actual GitHub username/repo, then push to a new repo named
e.g. `ha-plant-monitor`.

## License

MIT - see `LICENSE`.
