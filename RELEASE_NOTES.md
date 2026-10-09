# Plant Monitor v0.9.3

This bugfix release removes blocking species-database reads from Home Assistant's event loop and fixes the configuration, notification and dashboard edge cases found during review.

- Load the species database in an executor during cold startup and configuration; report read failures without caching an empty database.
- Migrate version-1 plant entries while preserving custom thresholds, sensors and options.
- Show unknown health/status when the required soil sensor is unavailable; reject non-finite readings and convert Fahrenheit/Kelvin readings to Celsius.
- Validate dry/wet and cold/hot threshold ordering, including live threshold number updates.
- Route Mobile App notifications through the real device action and other supported devices through notify entities; validate recipients, allow clearing them and fix daily-summary Unicode.
- Fix the notification blueprint's action list. When configuring it, set your notification action's message to `{{ plant_message }}`.
- Reset weekly watering counts at the local day boundary when the week changes; prevent unrelated sensor updates from evicting soil samples.
- Recover dashboard discovery after delayed registry loading, merge partial entity overrides, and ignore stale history responses when changing plants.
- Update the vulnerable test-only source-map dependency; npm audit reports zero vulnerabilities for the installed card test dependency tree.
- Correct the config-only schema, service selector metadata and manifest ordering; bundle original HACS brand icons and preserve/add the Home Assistant repository topic.
- Add regression tests, tested Python 3.12/3.13 dependency versions, frozen npm installation, and a release workflow gated on tests plus HACS/Hassfest validation.

Validation: 59 Python tests pass on each of Home Assistant 2025.1.4 / Python 3.12 and Home Assistant 2026.2.3 / Python 3.13; all 14 jsdom card checks pass. Syntax, JSON/translation checks and actionlint pass; npm audit reports zero vulnerabilities. Physical sensor hardware, external stock-photo fetching and real phone push delivery were not tested.
