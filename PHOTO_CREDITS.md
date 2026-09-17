# Stock photo credits

Stock photos referenced from `species_data.json` (`stock_photo_url`) are
**not stored as files in this repo** - they're loaded live from Wikimedia
Commons via each photo's stable `Special:FilePath` link, and the
integration fetches them at runtime (falling back to nothing shown if a
plant has no upload of its own and no stock photo is available, which is
most plants right now - see "Coverage" below).

Every photo listed here is Creative Commons licensed and requires
attribution, reproduced below per Commons' own attribution guidance.

| Plant | File | Credit |
|---|---|---|
| Bird of Paradise (*Strelitzia reginae*) | [Bird of paradise (Strelitzia) leaf, Estufa Fria, Lisbon, Portugal](https://commons.wikimedia.org/wiki/Special:FilePath/Bird%20of%20paradise%20(Strelitzia)%20leaf%2C%20Estufa%20Fria%2C%20Lisbon%2C%20Portugal%20julesvernex2.jpg) | julesvernex2, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0), via Wikimedia Commons |
| Wijze Varen / Bird's Nest Fern (*Asplenium antiquum*) | [Asplenium antiquum - Botanischer Garten Freiburg](https://commons.wikimedia.org/wiki/Special:FilePath/Asplenium%20antiquum%20-%20Botanischer%20Garten%20Freiburg%20-%20DSC06284.jpg) | Photo via Wikimedia Commons, Botanischer Garten Freiburg |
| Monstera (*Monstera deliciosa*) | [Monstera deliciosa Leaf 2700px](https://commons.wikimedia.org/wiki/Special:FilePath/Monstera%20deliciosa%20Leaf%202700px.jpg) | Photo via Wikimedia Commons |
| Snake Plant (*Dracaena trifasciata*) | [Sansevieria trifasciata Plant 3264px](https://commons.wikimedia.org/wiki/Special:FilePath/Sansevieria%20trifasciata%20Plant%203264px.jpg) | Derek Ramsey, GFDL / CC BY-SA, via Wikimedia Commons |

## Coverage

**4 of 201 plants** in the database have a verified stock photo. This is a
deliberate starting point, not full coverage - sourcing, verifying the
license of, and correctly attributing an image for all 201 plants is real
work that hasn't been done yet, and the maintainer's own environment
can't fetch Wikimedia Commons directly to batch-process this.

Every other plant simply shows no photo until the user uploads their own
(which always takes priority over a stock photo anyway).

## Contributing a photo

1. Find a Creative Commons or public-domain photo on
   [Wikimedia Commons](https://commons.wikimedia.org) of the plant -
   prefer a plain, well-lit photo of the whole plant or a clear leaf
   close-up, similar in style to the four above.
2. Get its `Special:FilePath` URL: on the file's Commons page, the pattern
   is `https://commons.wikimedia.org/wiki/Special:FilePath/<file name,
   URL-encoded>`.
3. Add an entry to `STOCK_PHOTOS` in `scripts/generate_species_data.py`,
   keyed by the plant's exact `display_name`, with `(url, credit_string)`.
4. Add a matching row to the table above.
5. Run `python scripts/generate_species_data.py` to regenerate
   `species_data.json`, and open a PR.

Photos that require attribution beyond a simple "Name, License, via
Wikimedia Commons" (e.g. specific wording requested by the photographer)
should preserve that exact wording in both places.
