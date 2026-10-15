# Plant illustrations

Eight original, AI-generated, photo-style illustrations are bundled in
`custom_components/plant_monitor/photos/`. They were exported as compressed WebP assets. They were generated for this
project with OpenAI image generation in October 2026 and visually checked
for the intended plant's broad leaf shape. They are illustrative, not
photographs of verified specimens and not a plant-identification tool.

| Plant | File | Depicted form |
| --- | --- | --- |
| Monstera | `monstera.webp` | Monstera deliciosa, mature fenestrated leaves |
| Snake Plant | `snake-plant.webp` | Dracaena trifasciata, yellow-edged form |
| Chinese Money Plant | `chinese-money-plant.webp` | Pilea peperomioides |
| Bird of Paradise | `bird-of-paradise.webp` | Strelitzia reginae, foliage |
| Golden Pothos | `golden-pothos.webp` | Epipremnum aureum, golden variegation |
| ZZ Plant | `zz-plant.webp` | Zamioculcas zamiifolia |
| Peace Lily | `peace-lily.webp` | Spathiphyllum wallisii |
| Bird's Nest Fern | `bird-nest-fern.webp` | Asplenium nidus |

The illustrations are provided with the project under its MIT licence to
the extent applicable. No third-party photo licence or attribution is
asserted. The image entities expose their generated origin and the card
displays “AI-gegenereerde plantenillustratie voor Plant Monitor”. An uploaded
photo takes priority and never inherits the generated image's credit.

These eight illustrations are served from local integration files through
Home Assistant's image entities, with file reads in the executor. They
need no external photo service, API key, account, or startup download.
The remaining 195 entries have no fallback illustration; upload your own.
The older Asplenium antiquum entry is deliberately not given an A. nidus
illustration as if it were an exact photograph of that species.

The previous four Wikimedia URL references have been removed. Their live
licences and original authors could not be verified from this environment
because access to Commons is blocked; two credits were incomplete. This
does not assert that those images were unlicensed. Future contributions of
real photographs should record the exact file page, author, licence name
and licence URL, and any modifications, after checking the original source.
