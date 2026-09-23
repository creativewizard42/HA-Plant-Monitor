# Changelog

## 0.9.1

- **Bugfix**: after updating, the dashboard kept running the previous
  release's card from the browser cache (e.g. the Waterbehoefte/advice
  footnote stayed left-aligned after 0.9.0 centered it). The Lovelace
  resource URL now includes the integration version
  (`/plant_monitor_files/plant-monitor-card.js?v=0.9.1`), and an existing
  entry from an older release is updated to it automatically on startup,
  so every update loads the new card.

## 0.9.0

- **Every plant now has its own Dutch care guide.** All 203 species get
  species-specific light, watering, humidity, temperature, fertilizing,
  repotting and common-problem advice (new `scripts/care_guides_nl/`),
  instead of the shared per-category template most plants used before.
- **Existing plants pick up the new guides automatically.** The care tip is
  copied into a plant's config at setup time, so plants added with an
  older release kept that release's (sometimes English) text. The
  integration now recognises an untouched auto-filled tip, using a hash
  of every tip text ever generated for that species (see
  `scripts/legacy_care_tip_hashes.json`), and shows the current guide
  instead. Any tip you edited yourself is kept as-is.
- **Dutch by default**: the advice sensor ("Geef nu water...", "Alles OK,
  geen actie nodig.") and the water prediction ("Over ongeveer X uur",
  "Geen duidelijke daling", "Nu water nodig", "Onbekend") are now Dutch,
  matching the card and care guides. The device model / care-guide header
  shows the Dutch name plus the Latin name (e.g. "Malabar Kastanje
  (Pachira aquatica)") instead of the English name. Also added 35 more
  Dutch common names.
- **Card**: the water-need/advice footnote is now centered, and multi-line
  advice keeps its line breaks.
## 0.8.1

- **Bugfix**: a soil-only plant sensor got linked as *air humidity* even
  when that field was left empty during setup. Two causes: the setup form
  pre-filled sensors as voluptuous `default`s, which Home Assistant
  silently re-applies when you clear a field; and the auto-mapping took a
  soil sensor reporting with the `humidity` device_class (no "soil" in its
  name) for an air-humidity sensor. Pre-fills are now suggestions (clearing
  sticks), an entity can never fill two roles, and a lone humidity-class
  entity on a plant sensor is mapped as soil moisture.
- **Bugfix**: changing the linked sensors afterwards via *Configure* had no
  effect on the dashboard card - the integration only ever read the sensors
  chosen during initial setup. Changes (and clearing a sensor) now apply
  immediately.
- **Bugfix**: existing plants whose soil sensor was also linked as air
  humidity no longer show the soil value in the "Lucht" tile - no
  reconfiguration needed.
- **Bugfix**: automatic registration of the dashboard card as a Lovelace
  resource failed silently on Home Assistant 2025.2+.

## 0.8.0

- **Bugfix**: humidity/battery/temperature weren't showing on the card.
  Root cause: the card looked for them on the same HA "device" as Plant
  Monitor's own entities, but the linked hardware sensor is a *different*
  device entirely. Fixed by exposing the linked entity_ids as attributes
  on `sensor.<plant>_soil_moisture`, which the card now reads directly.
- **Bugfix**: care guides showed as very short / cut off. Root cause: Home
  Assistant caps sensor *states* at 255 characters, and a full guide is
  1000+ characters. Fixed by moving the full text to the `care_tip`
  sensor's `full_text` attribute (no length cap) and keeping the state
  itself short; verified against a real Home Assistant instance
  (`test_care_tip_sensor_state_never_exceeds_ha_limit_but_full_text_survives`).
- **10 plants now have an individually researched, in-depth Dutch care
  guide** instead of the shorter templated one: Bird of Paradise, Wijze
  Varen, Monstera, Calathea Rufibarba (new species), Mini Monstera,
  Heartleaf Philodendron, Chinese Money Plant, Turtle Vine, Alocasia
  Polly, and Blue Star Fern (new species) - the plants this project's own
  reference dashboard actually uses. Grounded in multiple Dutch
  gardening/plant-care sources per species.
- **New: optional push notifications.** Pick a device (e.g. your phone)
  and toggle "notify when dry/overwatered" and/or "daily status summary" -
  both off by default, offered automatically as the last step of the setup
  wizard and revisitable via Configure -> Notifications. Uses
  `notify.send_message` with device targeting - no notify service name to
  guess. Notifies once per dry/overwatered *transition*, not on every
  update (verified with dedicated tests, including a real
  `vol.Optional` + `DeviceSelector` bug the tests caught: an unset device
  with a `None` default failed schema validation - fixed by omitting the
  default entirely when empty, matching the pattern already used for
  optional entity selectors).
- New `notifications.py` (`PlantNotifier`), new options-flow /
  initial-wizard step, new `tests/test_notifications.py` (4 tests).

## 0.7.0

- **Care guide content is now Dutch**, using the exact categories
  requested: Licht, Water geven, Luchtvochtigheid, Temperatuur, Bemesten,
  Verpotten, Veelvoorkomende problemen, plus a Giftigheid (toxicity)
  footnote. Translated the profile-level templates, all ~201
  species-specific notes, and the toxicity text/fallback. This is a
  content-language change (baked into `species_data.json`), separate from
  the UI's existing EN/NL translation system.
- **Card: tap the hero to open the soil-moisture sensor's more-info
  dialog** (`hass-more-info` event), for the full native history view.
- **Card: the 14-day graph is now hoverable** - move over it to see a
  tooltip with the exact date/time and moisture % at that point, plus a
  guide line and marker dot.
- **Card: a visible expand/collapse chevron** on the care-guide section
  (rotates on open) - it was accidentally left without a visible marker
  in the v0.6.0 redesign.
- The dashboard-resource URL (`/plant_monitor_files/plant-monitor-card.js`)
  is now also mentioned directly in the integration's own setup screen and
  in the README's Setup section, not only in the Repairs notice if
  auto-registration fails.
- New jsdom tests: click-to-more-info, Dutch category rendering +
  chevron, and graph hover/tooltip behaviour.
- Note: the dynamic `advice`/`water_prediction` sensor text (generated in
  `plant_data.py`, not from `species_data.json`) is still English - only
  the species care guide content was in scope for this release.

## 0.6.0

- **Card visually redesigned** to match a hand-built reference dashboard's
  look: the photo now fills the entire hero (not a strip above a separate
  section), with the moisture readout, gradient bar, three glass-style
  tiles and the water-need/advice footnote all overlaid on a bottom-up
  scrim over the photo - not on a plain background below it.
- The history graph now sits in its own dark, rounded, bordered panel
  (matching a `stack-in-card` look) and uses a smoothed line (quadratic
  bezier through midpoints) plus a marker dot on the latest reading,
  instead of a plain straight-segment polyline.
- The care guide now renders as flowing bold-labelled paragraphs (e.g.
  **Watering:** ...) with the toxicity note as an italic footnote, instead
  of boxed icon items - closer to a natural-reading care guide.
- Status label changed from "Dorstig" to "Droog" to match the reference
  wording.
- Config format is unchanged - existing `type: custom:plant-monitor-card`
  cards just pick up the new look after updating.

## 0.5.1

- **Bugfix**: the "add the Lovelace resource manually" Repairs notice
  could appear even on completely normal storage-mode dashboards. Cause:
  `lovelace` wasn't declared as a manifest dependency, so Plant Monitor's
  `async_setup()` could run *before* Lovelace had finished its own setup -
  `hass.data["lovelace"]` simply didn't exist yet, which looked identical
  from the outside to the genuine YAML-mode case. Added `lovelace` to
  `dependencies`, so Home Assistant now guarantees it's ready first.
- Added the test that should have caught this originally:
  `test_storage_mode_lovelace_gets_resource_registered_automatically` in
  `tests/test_frontend.py` actually asserts the resource lands in the
  collection on a normal setup, not just that failures are handled
  gracefully (which was all `test_frontend.py` covered before).
- If you already have the Repairs notice: update, restart, and it should
  register itself and clear the notice automatically. If it doesn't, the
  one-step manual instruction the notice already gives you always works
  regardless of the cause.

## 0.5.0

- **Multi-section care guide** for all 201 plants: Light, Watering,
  Humidity, Temperature, Fertilizing, Repotting, Common problems, and pet
  Toxicity - templated per watering-need profile with species-specific
  watering and toxicity, shown in the card's expandable section. Fixed a
  duplicate/broken Strelitzia entry found while building this.
- **Toxicity data** grounded in the ASPCA toxic/non-toxic plant database
  for 182 of 201 plants (e.g. confirmed Bird of Paradise is mildly toxic -
  it was previously unlisted).
- New `sensor.<plant>_soil_moisture`: mirrors the linked source sensor
  under a stable, Plant-Monitor-owned entity so the recorder keeps its own
  history for it - used by the card's new history graph.
- **Card redesign** to match the project's own 3-section reference
  dashboard: photo hero with a gradient moisture bar + tiles, a 14-day
  soil-moisture history graph (via `history/history_during_period`, its
  exact response shape verified against a real test Home Assistant
  instance) with the dry/wet "optimal" range shaded, and an expandable
  care-guide section parsed from the care_tip sensor.
- **Stock photos**: 4 of 201 plants (Bird of Paradise, Wijze Varen,
  Monstera, Snake Plant) now show a verified, properly-credited Wikimedia
  Commons photo automatically if the user hasn't uploaded their own - see
  `PHOTO_CREDITS.md` for licensing and how to add more. Fetched live at
  view time, not stored in the repo.
- `image.py` rewritten to serve either a local upload or a remote stock
  photo through one unified `async_image()`.
- New/updated tests: `tests/test_species.py` gained no new tests here but
  the card's jsdom suite now covers the history graph (using the verified
  response shape) and the care-guide parser; `test_plant_data.py` gained
  `test_photo_url_fallback_chain`.

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
