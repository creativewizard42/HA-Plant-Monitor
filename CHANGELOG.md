# Changelog

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
