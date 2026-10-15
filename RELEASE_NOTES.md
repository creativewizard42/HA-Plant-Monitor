# Plant Monitor v0.9.4

This release reviews the 203-entry plant catalogue, bundles eight original generated plant illustrations, and adds a new Plant Monitor logo.

- Correct 37 moisture profiles/ranges, several botanical labels, and care guidance for light, drainage, humidity, dormancy and toxicity. A complete table for all 203 entries is in `docs/PLANT_PROFILE_REVIEW.md`.
- Add profile-based temperature/humidity alert defaults for newly configured plants. Keep existing thresholds and custom notes; retain all IDs, legacy names and previous auto-filled care-tip hashes.
- Stop interpreting wet roots alone as overwatering for papyrus, Sarracenia, Venus flytrap and Cape sundew, including existing entries. Keep Nepenthes separate. Dormancy-sensitive plants ask you to check the growth phase; there is no automatic season detection.
- Remove blanket 200 ml watering quantities and misting recommendations. All advice still fits Home Assistant's 255-character state limit.
- Add eight locally served, labelled AI-generated plant illustrations, approximately 1.1 MB in total. An uploaded photo always takes priority. The other 195 entries still need an uploaded photo.
- Bundle a new transparent plant/pot/water-drop icon in 256 and 512 px sizes and show it in the HACS-readable README. Home Assistant 2026.3+ supports local custom brand assets; older versions and HACS previews before installation may still use legacy central branding. A live HACS download-list preview has not been verified.

Validation: 77 Python tests pass on each of Home Assistant 2025.1.4 / Python 3.12 and Home Assistant 2026.2.3 / Python 3.13; 15 card checks pass. Generated photo file reads are verified to run off the event loop; all 203 IDs and previous care-tip hashes are retained.

Care percentages are calibration starting points, not universal botanical measurements. Live RHS, NC State and ASPCA pages were blocked by the execution environment, so this is not a claim of 203 independently source-verified profiles. New thresholds do not overwrite existing user settings. Physical sensor behaviour, plant growth outcomes and live HACS rendering have not been tested.
