# Changelog

## 0.2.0

- **Free-text plant names** with a bundled 192-species database
  (`species_data.json`) for auto-filled thresholds and care tips; unmatched
  names fall back to generic defaults and an editable tip field.
- **Device-based sensor auto-mapping**: pick a device and its soil
  moisture/temperature/humidity/battery entities are guessed automatically
  (by device_class and name), still fully adjustable.
- **Photo upload** via a real drag-and-drop `FileSelector`, served through a
  new `image.<plant>_photo` entity; stored under `config/www/plant_monitor/`.
- New `sensor.<plant>_care_tip` entity (static species-level guidance,
  separate from the dynamic situational `advice` sensor).
- Options flow reorganised into a menu: entities / care & tip / photo /
  advanced - no need to redo the whole wizard to change one thing.
- New `file_upload` manifest dependency.
- New end-to-end config-flow tests (`tests/test_config_flow.py`) via
  `pytest-homeassistant-custom-component`, run in a new CI job.

## 0.1.0 - Initial release

- Config flow: point Plant Monitor at any existing soil moisture sensor
  (optionally temperature/humidity/battery), with species presets
  (Strelitzia, Monstera, Calathea, Asplenium, Custom) for sensible default
  thresholds.
- Options flow to adjust thresholds after setup.
- Entities per plant: advice, health score, drying rate, water prediction,
  last watered, waterings this week, dry/overwatered binary sensors, and
  live-adjustable dry/wet threshold sliders.
- `plant_monitor.log_watering` service for manual logging.
- Notification blueprint for dry/overwatered alerts with a configurable
  overwatered delay.
- Example dashboard using only built-in Lovelace cards.
- CI: hassfest + HACS repository validation, plus a logic test suite run on
  every push.

### Known limitations

- Drying-rate history is in-memory only; it resets on restart or when a
  threshold changes (entry reload).
- Watering detection is jump-based and may miss very slow drip irrigation
  (use the manual service for those).
- Not yet verified end-to-end inside a running Home Assistant UI - please
  test in a dev instance first and open an issue if something's off.
