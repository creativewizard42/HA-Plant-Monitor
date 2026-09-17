# Changelog

## 0.4.0

- **Bundled Lovelace card** (`plant-monitor-card`): shows one plant's
  photo, advice, care tip and key stats. Ships inside the integration -
  no separate HACS "plugin" install needed.
  - Served via a new `frontend.py` (static path registration).
  - Auto-registers itself as a dashboard resource on storage-mode
    Lovelace; falls back to a Settings -> Repairs notice with the one
    manual step otherwise (or if anything about that ever fails - this
    can never break the rest of the integration).
  - Auto-discovers a plant's entities from its device via
    `translation_key` (not `entity_id`, which is language-dependent -
    e.g. "advies" vs "advice" - and therefore unsafe to pattern-match).
    An explicit `entities:` map in the card config always overrides
    auto-discovery.
- New `http` manifest dependency (guarantees `hass.http` is available).
- New tests: `tests/test_frontend.py` (the file is actually served, byte
  for byte, over real HTTP; setup never raises even without Lovelace) and
  `tests/card/test_card.js` (jsdom - auto-discovery, photo rendering,
  status badges, manual override, HTML-escaping).
- New CI job running the card's jsdom tests via Node.

## 0.3.0

- Species database grown from 192 to **202 plants**, reviewed against Dutch
  garden-centre (Intratuin) assortments; added Banana Plant, Canary Island
  Date Palm, Pygmy Date Palm, European Fan Palm, Room Lime (Kamerlinde),
  Rose Grape (Medinilla), Fishtail Palm, potted Lemon Tree, Orchid Cactus,
  and Kris Plant.
- **Dutch common names** added as matchable aliases for 65 entries
  (Pannenkoekenplant, Vrouwentong, Gatenplant, Drakenbloedboom, Lepelplant,
  Aronskelk, Geluksplant, Geluksbamboe, Kamerlinde, Bananenplant, and more)
  - fixes plants not being found when typed by their Dutch name.
- The species picker now shows **common name(s) and the formal Latin name
  together** (e.g. "Chinese Money Plant / Pannenkoekenplant (Pilea
  peperomioides)"), generated from the same data used for matching.
- `scripts/generate_species_data.py` (the database generator) is now part
  of the repo, so contributors can add or correct entries via PR.
- New `tests/test_species.py`: database integrity (no duplicate IDs) and a
  Dutch-name regression test.

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
