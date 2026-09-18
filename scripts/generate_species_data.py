"""One-off generator for species_data.json - grouped by watering-need profile.

Usage (from the repo root):
    python scripts/generate_species_data.py

Regenerates custom_components/plant_monitor/species_data.json in place.
Adding a plant: add a tuple to PLANTS (display_name, scientific_name,
profile, one-line extra note). Adding a Dutch common name: add/extend its
entry in DUTCH_NAMES, keyed by that same display_name.

Thresholds are NOT lab-measured values (no such universal standard exists -
soil-moisture % readings depend heavily on sensor type, soil mix and pot
size). They are a consistent, documented translation of well-established
qualitative watering guidance (e.g. "let dry out between waterings" vs.
"keep evenly moist") into approximate percentage ranges, meant as a sensible
starting point that the user can - and should - adjust to their own sensor
and potting mix.
"""
import json
import os

PROFILES = {
    # key: (dry_threshold, wet_threshold, generic_note)
    "desert_cactus": (5, 30, "Echte woestijncactus: geef zelden maar rijkelijk water en laat daarna helemaal opdrogen. Fel, direct zonlicht."),
    "succulent": (10, 40, "Vetplant: laat de grond bijna helemaal opdrogen tussen de beurten door. Veel licht."),
    "drought_tolerant": (12, 50, "Zeer vergevingsgezind: laat de grond goed opdrogen tussen de beurten door. Verdraagt weinig licht."),
    "standard": (15, 55, "Laat de bovenste laag van de grond opdrogen voor je opnieuw water geeft. Helder, indirect licht."),
    "epiphytic": (15, 45, "Groeit in schors-/orchideeënmengsel, dat weinig water vasthoudt: geef grondig water en laat daarna opdrogen. Laat de wortels nooit in water staan."),
    "moisture_loving": (30, 70, "Houd de grond gelijkmatig en constant vochtig - laat 'm niet helemaal opdrogen. Houdt van hogere luchtvochtigheid."),
    "high_moisture": (40, 80, "Houd de grond constant nat. Houdt van hoge luchtvochtigheid en, voor sommige van deze planten, gedistilleerd/regenwater."),
}

# Multi-section care guide content, shared by every plant on a given
# profile for everything EXCEPT watering (species-specific, built from its
# own thresholds) and toxicity (species/genus-specific, see TOXICITY below).
# This is deliberately templated rather than hand-written per species (202
# bespoke essays isn't tractable to do well) - still genuinely useful,
# accurate general guidance, just shared within a watering-need category.
CARE_GUIDE_SECTIONS = {
    "desert_cactus": {
        "light": "Heeft zoveel mogelijk direct zonlicht nodig - een zuidraam is ideaal. Te weinig licht geeft een bleke, uitgerekte (vergeilde) groei.",
        "humidity": "Lage luchtvochtigheid is prima en zelfs gewenst; gemiddelde kamervochtigheid (30-40%) is meer dan genoeg. Hoge luchtvochtigheid samen met natte grond nodigt uit tot rot.",
        "temperature": "Voelt zich prettig bij normale kamertemperatuur (18-27\u00b0C). Een koelere winterrust (10-15\u00b0C) met veel minder water bevordert de bloei het volgende seizoen.",
        "fertilizing": "Bemest spaarzaam met cactus-/vetplantenvoeding, één keer per maand en alleen in voorjaar en zomer; in herfst en winter helemaal niet bemesten.",
        "repotting": "Verpot elke 2-4 jaar, alleen als de plant duidelijk potgebonden is, in snel drainerende cactusgrond (extra zand/perliet/puimsteen). Gebruik gevouwen papier of een tang om de stekels te vermijden.",
        "common_problems": "Zachte, verkleurde of papperige plekken wijzen vrijwel altijd op te veel water of rot - de meest voorkomende manier om een cactus te verliezen. Uitgerekte, bleke groei betekent te weinig licht.",
    },
    "succulent": {
        "light": "Houdt van veel licht, het liefst een paar uur direct zonlicht - een zuid- of westraam werkt goed. Te weinig licht geeft uitgerekte, slappe groei en verbleekte kleur.",
        "humidity": "Gemiddelde kamervochtigheid is prima; deze planten geven de voorkeur aan drogere lucht en goede luchtcirculatie boven een vochtige omgeving.",
        "temperature": "Voelt zich het prettigst bij 18-26\u00b0C. Houd boven de 10\u00b0C - de meeste vetplanten hebben veel meer moeite met koude, natte omstandigheden dan met warmte.",
        "fertilizing": "Een lichte voeding met verdunde cactus-/vetplantenmeststof, één keer per maand in voorjaar en zomer, is voldoende; te veel bemesten geeft zwakke, slappe groei.",
        "repotting": "Verpot elke 1-2 jaar in het voorjaar, in een grove, snel drainerende vetplantengrond. Laat gesneden of afgebroken stekken na vermeerdering eerst een dag of twee eeltvorming laten ontwikkelen voor je ze verpot.",
        "common_problems": "Papperige, doorschijnende of verkleurde (zwarte) bladeren wijzen op te veel water of rot. Uitrekken richting het licht met grote afstand tussen de bladeren betekent dat de plant meer zon nodig heeft.",
    },
    "drought_tolerant": {
        "light": "Verdraagt weinig licht goed en doet het ook prima in helder, indirect licht - een van de meest vergevingsgezinde planten qua lichtbehoefte.",
        "humidity": "Niet kieskeurig; normale binnenluchtvochtigheid is prima, geen besproeien of luchtbevochtiger nodig.",
        "temperature": "Voelt zich prettig binnen een breed bereik, ruwweg 15-27\u00b0C. Vermijd koude tocht en vorst.",
        "fertilizing": "Bemest licht met een evenwichtige kamerplantenvoeding, één keer per maand van voorjaar tot vroege herfst; groeit langzaam en heeft niet veel nodig.",
        "repotting": "Verpot elke 2-3 jaar, of zodra de plant duidelijk potgebonden is, in een goed drainerende algemene kamerplantengrond.",
        "common_problems": "Vergelende onderste bladeren wijzen meestal op te veel water (de meest voorkomende fout bij deze verder erg tolerante planten). Trage groei bij weinig licht is normaal, geen probleem.",
    },
    "standard": {
        "light": "Helder, indirect licht geeft de beste groei en bladkleur; verdraagt matig licht, maar de groei vertraagt dan en bontheid kan vervagen. Vermijd felle, directe middagzon, die de bladeren kan verbranden.",
        "humidity": "Gemiddelde kamervochtigheid (40-50%) is over het algemeen prima; hogere luchtvochtigheid (via een schaaltje water of luchtbevochtiger) bevordert snellere, weelderigere groei, vooral 's winters bij droge verwarmingslucht.",
        "temperature": "Houdt van 18-27\u00b0C en niet van koude tocht, plotselinge temperatuurschommelingen, of een plek vlak bij een koud raam of airco.",
        "fertilizing": "Bemest met vloeibare, evenwichtige kamerplantenvoeding elke 2-4 weken in voorjaar en zomer; verminder in herfst en winter tot eens per maand of stop helemaal.",
        "repotting": "Verpot elke 1-2 jaar in het voorjaar zodra de wortels rond de pot beginnen te groeien of uit de drainagegaten komen, in een pot die ongeveer 2-5 cm groter is.",
        "common_problems": "Gele bladeren wijzen meestal op te veel water; knapperige bruine bladpunten komen vaak door te droge lucht of te geconcentreerd water/voeding. Lange, kale groei met grote afstand tussen de bladeren betekent dat er meer licht nodig is.",
    },
    "epiphytic": {
        "light": "Helder, indirect licht is het beste; vermijd direct zonlicht, dat bij de meeste van deze planten het blad of de bloemen kan verbranden.",
        "humidity": "Waardeert hogere luchtvochtigheid (50%+), omdat de plant van nature tegen bomen aan groeit in vochtige lucht, niet in de grond; een schaaltje water of luchtbevochtiger helpt, zeker binnenshuis in de winter.",
        "temperature": "Houdt van stabiele warmte, ruwweg 18-27\u00b0C, en niet van koude tocht of een plek vlak tegen koud glas.",
        "fertilizing": "Gebruik een verdunde orchideeën-/epifytenvoeding ongeveer elke 2-4 weken tijdens actieve groei; dit zijn doorgaans lichte eters vergeleken met kamerplanten die in grond groeien.",
        "repotting": "Verpot slechts elke 1-3 jaar, of zodra het groeimedium is afgebroken en niet meer goed draineert - niet zomaar omdat er wortels zichtbaar zijn, want dat is normaal bij deze planten.",
        "common_problems": "Verschrompelde, gerimpelde groei betekent meestal dat de plant te lang te weinig water heeft gehad; zwarte of papperige wortels betekenen dat het medium te lang te nat is gebleven."
    },
    "moisture_loving": {
        "light": "Houdt van helder, indirect licht en over het algemeen niet van direct zonlicht, dat de bladeren kan verbleken of verbranden. Verdraagt wat minder licht beter dan uitdroging.",
        "humidity": "Wil graag een hogere luchtvochtigheid (50%+); droge binnenlucht (zeker bij winterverwarming) is vaak als eerste te zien aan knapperige, bruine bladranden.",
        "temperature": "Houdt van een stabiele 18-26\u00b0C en niet van koude tocht, koude vensterbanken of plotselinge temperatuurdalingen.",
        "fertilizing": "Bemest met vloeibare, evenwichtige voeding op halve sterkte elke 2-4 weken in voorjaar en zomer; bouw dit af in herfst en winter.",
        "repotting": "Verpot elke 1-2 jaar in het voorjaar, geleidelijk opschalend, met een vochtvasthoudende maar toch goed doorluchte potgrond (extra kokosvezel of een turfvrije vochtvasthoudende toevoeging helpt).",
        "common_problems": "Knapperige, bruin wordende bladranden wijzen meestal op te droge lucht in plaats van te droge grond - check eerst de luchtvochtigheid voordat je meer water geeft. Slap hangen ondanks vochtige grond kan wijzen op wortelrot door te lang te nat staan.",
    },
    "high_moisture": {
        "light": "Helder, indirect licht past bij de meeste van deze planten goed; een paar (zoals zonnedauw en trompetbekers) willen zoveel mogelijk licht, het liefst met wat directe zon.",
        "humidity": "Houdt van vochtige lucht bovenop constant natte grond; een schaaltje water, luchtbevochtiger, of een van nature vochtige ruimte (zoals een lichte badkamer) helpt de plant goed groeien.",
        "temperature": "Voelt zich prettig bij normale kamertemperatuur, ruwweg 18-26\u00b0C; vermijd koude tocht.",
        "fertilizing": "De meeste planten in deze groep zijn lichte eters - een verdunde, evenwichtige voeding eens per maand tijdens het groeiseizoen is voldoende. Vleesetende planten mogen nooit via de grond bemest worden; zij halen hun voeding uit prooien.",
        "repotting": "Verpot elke 1-2 jaar in het voorjaar in een vochtvasthoudend mengsel; vleesetende planten hebben specifiek een voedselarm mengsel nodig, zoals veenmos of een turf-/perlietmix, nooit gewone potgrond of meststof.",
        "common_problems": "Bruine, knapperige plekken wijzen meestal erop dat de grond even is opgedroogd - deze planten zijn daar veel gevoeliger voor dan de meeste kamerplanten. Kraanwater kan mineraalafzetting of verbrande bladpunten veroorzaken; regenwater of gedistilleerd water is veiliger voor de gevoelige soorten.",
    },
}

# Toxicity to cats/dogs, keyed by display_name. Grounded in the ASPCA Animal
# Poison Control Center's toxic/non-toxic plant lists (the standard
# reference for this). "toxic" / "mildly_toxic" / "non_toxic" - if a plant
# isn't listed here, the generator falls back to a cautious "unknown" note
# rather than asserting safety it can't back up. This is general awareness
# information, not a substitute for veterinary advice.
TOXICITY = {
    # --- Toxic (aroids: Araceae family - calcium oxalate crystals) ---
    "Monstera": "toxic", "Swiss Cheese Vine": "toxic", "Mini Monstera": "toxic",
    "Golden Pothos": "toxic", "Marble Queen Pothos": "toxic", "Satin Pothos": "toxic",
    "Neon Pothos": "toxic", "Cebu Blue Pothos": "toxic", "Silver Pothos": "toxic",
    "Heartleaf Philodendron": "toxic", "Split-Leaf Philodendron": "toxic",
    "Philodendron Birkin": "toxic", "Pink Princess Philodendron": "toxic",
    "Philodendron Xanadu": "toxic", "Philodendron Prince of Orange": "toxic",
    "Philodendron Congo": "toxic", "Philodendron Brasil": "toxic", "Philodendron Micans": "toxic",
    "Arrowhead Plant": "toxic", "Chinese Evergreen": "toxic", "Red Aglaonema": "toxic",
    "Dumb Cane": "toxic", "Peace Lily": "toxic", "Peace Lily 'Domino'": "toxic",
    "Calla Lily (potted)": "toxic", "African Mask Plant": "toxic", "Alocasia Polly": "toxic",
    "Alocasia Black Velvet": "toxic", "Alocasia Zebrina": "toxic", "Kris Plant": "toxic",
    "Elephant Ear": "toxic", "Caladium": "toxic", "Flamingo Flower": "toxic",
    "Anthurium Clarinervium": "toxic", "Anthurium Crystallinum": "toxic",
    # --- Toxic (Dracaena genus incl. former Sansevieria - saponins) ---
    "Snake Plant": "mildly_toxic", "Cylindrical Snake Plant": "mildly_toxic",
    "Bird's Nest Sansevieria": "mildly_toxic",
    "Dragon Tree": "mildly_toxic", "Corn Plant": "mildly_toxic", "Song of India": "mildly_toxic",
    "Lemon Lime Dracaena": "mildly_toxic", "Lucky Bamboo": "mildly_toxic",
    # --- Toxic (succulents with known toxic principles) ---
    "Jade Plant": "mildly_toxic", "Aloe Vera": "mildly_toxic", "Lace Aloe": "mildly_toxic",
    "Flaming Katy": "toxic", "Christmas Kalanchoe": "toxic", "Panda Plant": "mildly_toxic",
    "Mother of Thousands": "toxic",
    "Pencil Cactus": "toxic", "African Milk Tree": "toxic", "Poinsettia": "mildly_toxic",
    "String of Pearls": "toxic", "String of Bananas": "toxic", "String of Dolphins": "toxic",
    "Desert Rose": "toxic",
    # --- Toxic (Araliaceae - Schefflera, ivy, Fatsia) ---
    "Umbrella Tree": "toxic", "Dwarf Umbrella Tree": "toxic", "English Ivy": "toxic", "Fatsia": "toxic",
    # --- Toxic (ZZ Plant - Zamioculcas, oxalates) ---
    "ZZ Plant": "toxic",
    # --- Toxic (Sago Palm - Cycas, one of the most dangerous common houseplants) ---
    "Sago Palm": "toxic",
    # --- Toxic (Amaryllidaceae - bulbs) ---
    "Amaryllis": "toxic", "Clivia": "toxic", "Rain Lily": "mildly_toxic",
    # --- Toxic (other well-documented cases) ---
    "Cyclamen": "toxic", "Azalea (potted)": "toxic", "Hydrangea (potted)": "mildly_toxic",
    "Purple Shamrock": "mildly_toxic", "Ti Plant": "mildly_toxic", "Croton": "toxic",
    "Coffee Plant": "toxic", "Chinese Hibiscus": "mildly_toxic",
    "Rex Begonia": "mildly_toxic", "Polka Dot Begonia": "mildly_toxic", "Angel Wing Begonia": "mildly_toxic",
    "Norfolk Island Pine": "mildly_toxic", "Silver Squill": "mildly_toxic",
    "Lemon Tree (potted)": "mildly_toxic", "Venus Flytrap": "non_toxic",
    # --- Non-toxic (well-documented pet-safe favourites) ---
    "Spider Plant": "non_toxic", "Boston Fern": "non_toxic", "Maidenhair Fern": "non_toxic",
    "Bird's Nest Fern": "non_toxic", "Wijze Varen (Bird's Nest Fern)": "non_toxic",
    "Table Fern": "non_toxic", "Staghorn Fern": "non_toxic", "Rabbit's Foot Fern": "non_toxic",
    "African Violet": "non_toxic", "Cape Primrose": "non_toxic",
    "Parlor Palm": "non_toxic", "Kentia Palm": "non_toxic", "Areca Palm": "non_toxic",
    "Lady Palm": "non_toxic", "Bamboo Palm": "non_toxic", "Fishtail Palm": "non_toxic",
    "Canary Island Date Palm": "non_toxic", "Pygmy Date Palm": "non_toxic", "European Fan Palm": "non_toxic",
    "Cast Iron Plant": "non_toxic", "Chinese Money Plant": "non_toxic", "Aluminum Plant": "non_toxic",
    "Wax Plant": "non_toxic", "Sweetheart Hoya": "non_toxic", "Hoya Bella": "non_toxic",
    "Baby Rubber Plant": "non_toxic", "Emerald Ripple Peperomia": "non_toxic",
    "Watermelon Peperomia": "non_toxic", "Watermelon Begonia": "non_toxic",
    "Raindrop Peperomia": "non_toxic", "Cupid Peperomia": "non_toxic", "Red Log Peperomia": "non_toxic",
    "Trailing Jade": "non_toxic", "Peperomia Hope": "non_toxic",
    "Calathea Orbifolia": "non_toxic", "Calathea Medallion": "non_toxic", "Peacock Plant": "non_toxic",
    "Rattlesnake Plant": "non_toxic", "Calathea White Fusion": "non_toxic",
    "Prayer Plant": "non_toxic", "Fishbone Prayer Plant": "non_toxic", "Never-Never Plant": "non_toxic",
    "Nerve Plant": "non_toxic", "Baby's Tears": "non_toxic", "Polka Dot Plant": "non_toxic",
    "Zebra Haworthia": "non_toxic", "Haworthia (Pearl Plant)": "non_toxic", "Ox Tongue Plant": "non_toxic",
    "Mexican Snowball": "non_toxic", "Echeveria 'Perle von Nurnberg'": "non_toxic",
    "Tree Houseleek": "non_toxic", "Hens and Chicks": "non_toxic", "Ghost Plant": "non_toxic",
    "Moonstones": "non_toxic", "Jelly Bean Plant": "non_toxic", "Fairy Washboard": "non_toxic",
    "Watch Chain Plant": "non_toxic", "Baseball Plant": "non_toxic", "Living Stones": "non_toxic",
    "Starfish Flower": "non_toxic",
    "Golden Barrel Cactus": "non_toxic", "Prickly Pear Cactus": "non_toxic", "Pincushion Cactus": "non_toxic",
    "Old Lady Cactus": "non_toxic", "Star Cactus": "non_toxic", "Goat's Horn Cactus": "non_toxic",
    "Peanut Cactus": "non_toxic", "Torch Cactus": "non_toxic", "Fishhook Barrel Cactus": "non_toxic",
    "Bunny Ear Cactus": "non_toxic",
    "Christmas Cactus": "non_toxic", "Thanksgiving Cactus": "non_toxic",
    "Wandering Jew": "mildly_toxic", "Inch Plant": "mildly_toxic", "Purple Heart": "mildly_toxic",
    "Turtle Vine": "non_toxic", "Boat Lily": "mildly_toxic",
    "Money Tree": "non_toxic", "Ponytail Palm": "non_toxic", "Ponytail Palm (dwarf)": "non_toxic",
    "Yucca Cane": "toxic",
    "Bird of Paradise": "mildly_toxic",
    "Moth Orchid": "non_toxic", "Dendrobium Orchid": "non_toxic", "Cattleya Orchid": "non_toxic",
    "Oncidium Orchid": "non_toxic",
    "Guzmania Bromeliad": "non_toxic", "Vriesea Bromeliad": "non_toxic", "Aechmea Bromeliad": "non_toxic",
    "Pitcher Plant": "non_toxic", "Sundew": "non_toxic",
    "Passion Flower": "non_toxic", "Jasmine": "non_toxic", "Gardenia": "mildly_toxic",
    "Primrose": "mildly_toxic", "Sensitive Plant": "mildly_toxic",
    "Umbrella Papyrus": "non_toxic", "Banana Plant": "non_toxic", "Room Lime": "non_toxic",
    "Rose Grape": "non_toxic", "Orchid Cactus": "non_toxic",
}
DEFAULT_TOXICITY_NOTE = (
    "Geen bevestigde ASPCA-vermelding gevonden voor deze specifieke plant - wees "
    "voorzichtig met huisdieren en kinderen, en neem bij vermoeden van inname "
    "contact op met een dierenarts of het vergiftigingeninformatiecentrum."
)
TOXICITY_TEXT = {
    "toxic": "Giftig voor katten en honden (en houd 'm ook uit de buurt van kleine kinderen) bij inname - neem bij inname contact op met een dierenarts of het vergiftigingeninformatiecentrum.",
    "mildly_toxic": "Licht giftig / kan maagklachten veroorzaken bij inname door huisdieren of kinderen - meestal niet levensbedreigend, maar toch buiten bereik houden.",
    "non_toxic": "Wordt door de ASPCA beschouwd als niet giftig voor katten en honden - een van de veiligere keuzes als je huisdieren hebt.",
}

# Starter set of stock photos, keyed by display_name - a curated, verified
# subset (NOT all 201 plants). Each points at a specific Wikimedia Commons
# file via its stable Special:FilePath redirect, which resolves to whatever
# the current file revision is; the license/attribution for each is in
# PHOTO_CREDITS below and duplicated into custom_components/plant_monitor/
# PHOTO_CREDITS.md. Community PRs adding more are very welcome - see
# scripts/generate_species_data.py's module docstring for how.
STOCK_PHOTOS = {
    "Bird of Paradise": (
        "https://commons.wikimedia.org/wiki/Special:FilePath/Bird%20of%20paradise%20(Strelitzia)%20leaf%2C%20Estufa%20Fria%2C%20Lisbon%2C%20Portugal%20julesvernex2.jpg",
        "julesvernex2, CC BY-SA 4.0, via Wikimedia Commons",
    ),
    "Wijze Varen (Bird's Nest Fern)": (
        "https://commons.wikimedia.org/wiki/Special:FilePath/Asplenium%20antiquum%20-%20Botanischer%20Garten%20Freiburg%20-%20DSC06284.jpg",
        "Photo via Wikimedia Commons, Botanischer Garten Freiburg",
    ),
    "Monstera": (
        "https://commons.wikimedia.org/wiki/Special:FilePath/Monstera%20deliciosa%20Leaf%202700px.jpg",
        "Photo via Wikimedia Commons",
    ),
    "Snake Plant": (
        "https://commons.wikimedia.org/wiki/Special:FilePath/Sansevieria%20trifasciata%20Plant%203264px.jpg",
        "Derek Ramsey, GFDL/CC-BY-SA, via Wikimedia Commons",
    ),
}



# (display_name, scientific_name, profile, extra_note)
# extra_note is appended to the profile's generic note as a short species-specific tip.
PLANTS = [
    # --- Vetplanten ---
    ("Jade Plant", "Crassula ovata", "succulent", "Houtachtige stengels; makkelijk te vermeerderen uit stekjes."),
    ("String of Pearls", "Senecio rowleyanus", "succulent", "Hangend; het mooist in een hangpot."),
    ("String of Bananas", "Senecio radicans", "succulent", "Hangend; vergelijkbare verzorging als String of Pearls."),
    ("String of Dolphins", "Senecio peregrinus", "succulent", "Hangend; opvallende dolfijnvormige blaadjes."),
    ("String of Hearts", "Ceropegia woodii", "succulent", "Hangend; verdraagt verwaarlozing goed."),
    ("String of Turtles", "Peperomia prostrata", "succulent", "Hangend; kleine getekende blaadjes."),
    ("Burro's Tail", "Sedum morganianum", "succulent", "Hangend; blaadjes vallen snel af bij aanraking."),
    ("Panda Plant", "Kalanchoe tomentosa", "succulent", "Donzige, zilvergroene blaadjes."),
    ("Flaming Katy", "Kalanchoe blossfeldiana", "succulent", "Bloeiende vetplant; heeft een donkere rustperiode nodig om opnieuw te bloeien."),
    ("Elephant Bush", "Portulacaria afra", "succulent", "Geschikt voor bonsai; wordt soms verward met de jadeplant."),
    ("Pencil Cactus", "Euphorbia tirucalli", "succulent", "Sap irriteert huid/ogen - wees voorzichtig."),
    ("African Milk Tree", "Euphorbia trigona", "succulent", "Sap irriteert - wees voorzichtig."),
    ("String of Buttons", "Crassula perforata", "succulent", "Gestapelde driehoekige blaadjes."),
    ("Donkey's Tail", "Sedum morganianum", "succulent", "Dezelfde plant als Burro's Tail (andere naam)."),
    ("Ghost Plant", "Graptopetalum paraguayense", "succulent", "Bleke, stoffig-roze rozetten."),
    ("Moonstones", "Pachyphytum oviferum", "succulent", "Dikke, eivormige blaadjes."),
    ("Hens and Chicks", "Sempervivum tectorum", "succulent", "Winterhard; maakt kleine 'kuikentjes' als uitlopers."),
    ("Zebra Haworthia", "Haworthia fasciata", "succulent", "Verdraagt minder licht beter dan de meeste vetplanten."),
    ("Haworthia (Pearl Plant)", "Haworthia attenuata", "succulent", "Klein, makkelijk, groeit langzaam."),
    ("Ox Tongue Plant", "Gasteria bicolor", "succulent", "Verdraagt minder licht; groeit langzaam."),
    ("Desert Rose", "Adenium obesum", "succulent", "Gezwollen voetstuk; heeft veel licht en warmte nodig om te bloeien."),

    # --- Woestijncactussen ---
    ("Golden Barrel Cactus", "Echinocactus grusonii", "desert_cactus", "Groeit langzaam; heeft uitstekende drainage nodig."),
    ("Prickly Pear Cactus", "Opuntia microdasys", "desert_cactus", "Fijne stekeltjes (glochiden) irriteren de huid - wees voorzichtig."),
    ("Pincushion Cactus", "Mammillaria spp.", "desert_cactus", "Compact; bloeit in een kransje rond de top."),
    ("Old Lady Cactus", "Mammillaria hahniana", "desert_cactus", "Bedekt met fijne witte haartjes."),
    ("Star Cactus", "Astrophytum ornatum", "desert_cactus", "Groeit langzaam, stervormige ribben."),
    ("Goat's Horn Cactus", "Astrophytum capricorne", "desert_cactus", "Gekromde stekels die op hoorns lijken."),
    ("Peanut Cactus", "Echinopsis chamaecereus", "desert_cactus", "Vormt kluitjes; bloeit makkelijk."),
    ("Torch Cactus", "Echinopsis spachiana", "desert_cactus", "Snelgroeiende zuilcactus."),
    ("Fishhook Barrel Cactus", "Ferocactus wislizeni", "desert_cactus", "Gehaakte stekels - wees voorzichtig."),

    # --- Droogtetolerant ---
    ("Snake Plant", "Dracaena trifasciata", "drought_tolerant", "Zeer vergevingsgezind; verdraagt weinig licht. Ook bekend als Sansevieria."),
    ("Cylindrical Snake Plant", "Dracaena cylindrica", "drought_tolerant", "Ronde, speervormige bladeren."),
    ("ZZ Plant", "Zamioculcas zamiifolia", "drought_tolerant", "Glanzende bladeren; groeit goed bij verwaarlozing en weinig licht."),
    ("Ponytail Palm", "Beaucarnea recurvata", "drought_tolerant", "Geen echte palm; gezwollen voet slaat water op."),
    ("Yucca Cane", "Yucca elephantipes", "drought_tolerant", "Zwaardvormige bladeren; scherpe punten - plaats uit de looproute."),
    ("Sago Palm", "Cycas revoluta", "drought_tolerant", "Groeit zeer langzaam; giftig voor huisdieren bij inname."),
    ("Cast Iron Plant", "Aspidistra elatior", "drought_tolerant", "Zeer tolerant voor weinig licht en verwaarlozing."),
    ("Aloe Vera", "Aloe vera", "drought_tolerant", "Gel uit de bladeren wordt gebruikt om de huid te verzachten; heeft veel licht nodig."),
    ("Lace Aloe", "Aristaloe aristata", "drought_tolerant", "Compacte rozet; verdraagt wat schaduw."),
    ("Agave", "Agave americana", "drought_tolerant", "Scherpe bladpunten; het best op een lichte plek, bijv. bij een zonnig raam."),

    # --- Standaard tropisch groen (de grootste groep) ---
    ("Monstera", "Monstera deliciosa", "standard", "Bladeren krijgen gaten en insnijdingen naarmate de plant ouder wordt en meer licht krijgt."),
    ("Swiss Cheese Vine", "Monstera adansonii", "standard", "Kleinere, meer klimmende verwant van de Monstera deliciosa."),
    ("Mini Monstera", "Rhaphidophora tetrasperma", "standard", "Geen echte Monstera; klimt goed langs een mosstok."),
    ("Golden Pothos", "Epipremnum aureum", "standard", "Zeer vergevingsgezind; hangt of klimt."),
    ("Marble Queen Pothos", "Epipremnum aureum 'Marble Queen'", "standard", "Heeft veel licht nodig om de witte bontheid te behouden."),
    ("Satin Pothos", "Scindapsus pictus", "standard", "Zilverachtige, glanzende bladstructuur."),
    ("Heartleaf Philodendron", "Philodendron hederaceum", "standard", "Snelgroeiende hangplant, zeer vergevingsgezind."),
    ("Split-Leaf Philodendron", "Philodendron bipinnatifidum", "standard", "Grote, diep ingesneden bladeren; heeft ruimte nodig."),
    ("Philodendron Birkin", "Philodendron 'Birkin'", "standard", "Crèmekleurige strepen op donkergroene bladeren."),
    ("Pink Princess Philodendron", "Philodendron erubescens 'Pink Princess'", "standard", "Heeft veel licht nodig om de roze bontheid te ontwikkelen."),
    ("Philodendron Xanadu", "Thaumatophyllum xanadu", "standard", "Compact, niet-klimmend, diep ingesneden bladeren."),
    ("Arrowhead Plant", "Syngonium podophyllum", "standard", "Bladvorm verandert naarmate de plant ouder wordt."),
    ("Dragon Tree", "Dracaena marginata", "standard", "Dunne, boogvormige bladeren; verdraagt enige verwaarlozing."),
    ("Corn Plant", "Dracaena fragrans", "standard", "Genoemd naar de op maïs lijkende bladeren."),
    ("Song of India", "Dracaena reflexa", "standard", "Geel-groen gestreepte bladeren."),
    ("Rubber Plant", "Ficus elastica", "standard", "Glanzende, dikke bladeren; veeg af en toe het stof eraf."),
    ("Fiddle Leaf Fig", "Ficus lyrata", "standard", "Houdt niet van verplaatsen; gevoelig voor plotselinge licht-/waterveranderingen."),
    ("Weeping Fig", "Ficus benjamina", "standard", "Laat bladeren vallen na grote veranderingen in licht of locatie."),
    ("Audrey Ficus", "Ficus benghalensis", "standard", "Brede bladeren met een donzige rand."),
    ("Umbrella Tree", "Schefflera arboricola", "standard", "Glanzende, handvormige blaadjes."),
    ("Baby Rubber Plant", "Peperomia obtusifolia", "standard", "Dikke, vlezige bladeren; compacte groeier."),
    ("Emerald Ripple Peperomia", "Peperomia caperata", "standard", "Diep getextureerde, hartvormige bladeren."),
    ("Watermelon Peperomia", "Peperomia argyreia", "standard", "Gestreepte bladeren die op een watermeloenschil lijken."),
    ("Wax Plant", "Hoya carnosa", "standard", "Wasachtige bladeren, geurende bloemtrossen; groeit graag wat krap in de pot."),
    ("Sweetheart Hoya", "Hoya kerrii", "standard", "Hartvormige bladeren; groeit extreem langzaam."),
    ("Spider Plant", "Chlorophytum comosum", "standard", "Maakt jonge plantjes aan lange uitlopers."),
    ("Wandering Jew", "Tradescantia zebrina", "standard", "Paars-zilver gestreepte bladeren; hangt mooi."),
    ("Inch Plant", "Tradescantia fluminensis", "standard", "Groeit snel, makkelijk te vermeerderen uit stekjes."),
    ("Chinese Money Plant", "Pilea peperomioides", "standard", "Ronde, muntvormige bladeren; maakt makkelijk deelbare kindjes."),
    ("Aluminum Plant", "Pilea cadierei", "standard", "Zilverkleurig spikkelpatroon op de bladeren."),
    ("Chinese Evergreen", "Aglaonema commutatum", "standard", "Zeer tolerant voor weinig licht."),
    ("Croton", "Codiaeum variegatum", "standard", "Heeft veel licht nodig om de felle bladkleuren te behouden."),
    ("Ti Plant", "Cordyline fruticosa", "standard", "Kleurrijke, zwaardvormige bladeren."),
    ("English Ivy", "Hedera helix", "standard", "Hangende klimplant; houdt van koelere kamers."),
    ("Swedish Ivy", "Plectranthus verticillatus", "standard", "Hangend; geen echte klimop."),
    ("Fatsia", "Fatsia japonica", "standard", "Grote, glanzende, handvormige bladeren."),
    ("Kentia Palm", "Howea forsteriana", "standard", "Elegante, onderhoudsarme palm; verdraagt minder licht."),
    ("Parlor Palm", "Chamaedorea elegans", "standard", "Compacte palm, geschikt voor kleinere kamers."),
    ("Areca Palm", "Dypsis lutescens", "standard", "Vederachtige bladeren; houdt van hogere luchtvochtigheid."),
    ("Lady Palm", "Rhapis excelsa", "standard", "Groeit langzaam, verdraagt minder licht."),
    ("Bamboo Palm", "Chamaedorea seifrizii", "standard", "Vormt bosjes; verdraagt minder licht."),
    ("Poinsettia", "Euphorbia pulcherrima", "standard", "Kerstplant; sap kan de huid irriteren."),
    ("Christmas Cactus", "Schlumbergera truncata", "standard", "Een regenwoudcactus, geen woestijncactus - heeft meer vocht nodig dan een gewone cactus."),
    ("Thanksgiving Cactus", "Schlumbergera truncata", "standard", "Zeer vergelijkbare verzorging als de Kerstcactus."),
    ("Norfolk Island Pine", "Araucaria heterophylla", "standard", "Zachte, dennenachtige naalden; houdt van veel licht en luchtvochtigheid."),
    ("Money Tree", "Pachira aquatica", "standard", "Vaak verkocht met gevlochten stammen; verdraagt een breed lichtbereik."),
    ("Ficus Ginseng (Bonsai)", "Ficus microcarpa", "standard", "Populaire indoor bonsai; dikke, blootliggende wortels."),
    ("Polka Dot Begonia", "Begonia maculata", "standard", "Zilver gespikkelde bladeren; voorkom natte bladeren."),
    ("Rex Begonia Vine", "Cissus discolor", "standard", "Geen echte Begonia; fluweelachtige, getekende bladeren."),
    ("Angel Wing Begonia", "Begonia coccinea", "standard", "Rietachtige stengels, trossen bloemen."),
    ("Dumb Cane", "Dieffenbachia seguine", "standard", "Sap is giftig bij inname - houd uit de buurt van huisdieren/kinderen."),
    ("Silver Squill", "Ledebouria socialis", "standard", "Kleine bolplant met zilver gevlekte bladeren."),
    ("Coffee Plant", "Coffea arabica", "standard", "Glanzende bladeren; kan binnenshuis uiteindelijk bloeien en vruchten dragen."),
    ("Bird's Nest Sansevieria", "Dracaena hahnii", "standard", "Compacte rozetvorm van de vrouwentong."),
    ("Rattlesnake Plant Vine", "Nepenthes alata (tropical pitcher)", "high_moisture", "Vleesetend - houd de grond constant vochtig, bij voorkeur met gedistilleerd/regenwater."),

    # --- Epifytisch / orchidee-achtig ---
    ("Moth Orchid", "Phalaenopsis spp.", "epiphytic", "Groeit in schorsmengsel; water geven door te dompelen, daarna goed laten uitlekken."),
    ("Dendrobium Orchid", "Dendrobium spp.", "epiphytic", "Heeft na de bloei een duidelijk drogere rustperiode nodig."),
    ("Cattleya Orchid", "Cattleya spp.", "epiphytic", "Heeft veel licht nodig om opnieuw te bloeien."),
    ("Oncidium Orchid", "Oncidium spp.", "epiphytic", "Dansende bloementrossen; houdt van fel, indirect licht."),
    ("Staghorn Fern", "Platycerium bifurcatum", "epiphytic", "Vaak gemonteerd in plaats van gepot; besproei of doop de houder."),

    # --- Vochtminnend ---
    ("Peace Lily", "Spathiphyllum wallisii", "moisture_loving", "Hangt zichtbaar bij dorst, herstelt snel na water geven."),
    ("Prayer Plant", "Maranta leuconeura", "moisture_loving", "Bladeren vouwen 's nachts omhoog."),
    ("Rattlesnake Plant", "Calathea lancifolia", "moisture_loving", "Golvende bladranden met donkere tekening."),
    ("Peacock Plant", "Calathea makoyana", "moisture_loving", "Opvallend getekende bladeren; gevoelig voor mineralen in leidingwater."),
    ("Calathea Medallion", "Calathea roseopicta", "moisture_loving", "Ronde, getekende bladeren met paarse onderkant."),
    ("Calathea Orbifolia", "Calathea orbifolia", "moisture_loving", "Grote, zilverachtig gestreepte ronde bladeren."),
    ("Fishbone Prayer Plant", "Ctenanthe burle-marxii", "moisture_loving", "Visgraatpatroon op de bladeren."),
    ("Never-Never Plant", "Ctenanthe oppenheimiana", "moisture_loving", "Bonte bladeren met paarse onderkant."),
    ("Nerve Plant", "Fittonia albivenis", "moisture_loving", "Hangt dramatisch bij droogte, maar herstelt meestal na water geven - hou 'm liever gelijkmatig vochtig om die stress te voorkomen."),
    ("African Mask Plant", "Alocasia amazonica", "moisture_loving", "Dramatische pijlvormige bladeren; gevoelig voor zowel te veel als te weinig water."),
    ("Elephant Ear", "Colocasia esculenta", "moisture_loving", "Zeer grote bladeren; een echte waterdrinker tijdens het groeiseizoen."),
    ("Flamingo Flower", "Anthurium andraeanum", "moisture_loving", "Glanzende, wasachtige bloemschutbladen; houdt van een grove, luchtige potgrond."),
    ("Rex Begonia", "Begonia rex", "moisture_loving", "Opvallende bladtekening; voorkom natte bladeren."),
    ("Boston Fern", "Nephrolepis exaltata", "moisture_loving", "Houdt van hoge luchtvochtigheid; bladpunten verkleuren bruin bij te droge lucht."),
    ("Maidenhair Fern", "Adiantum raddianum", "moisture_loving", "Delicate blaadjes; hangt snel slap als de plant te droog komt te staan."),
    ("Bird's Nest Fern", "Asplenium nidus", "moisture_loving", "Rozet van brede, ongedeelde bladeren."),
    ("Wijze Varen (Bird's Nest Fern)", "Asplenium antiquum", "moisture_loving", "Rozet van brede, ongedeelde bladeren - een veelverkochte cultivar onder deze Nederlandse naam."),
    ("Table Fern", "Pteris cretica", "moisture_loving", "Compacte varen, geschikt voor terraria of vochtige badkamers."),
    ("Baby's Tears", "Soleirolia soleirolii", "moisture_loving", "Piepkleine blaadjes, vormt een mosachtig tapijt."),
    ("Spikemoss", "Selaginella kraussiana", "moisture_loving", "Houdt van een vochtige, terrarium-achtige omgeving."),
    ("African Violet", "Saintpaulia ionantha", "moisture_loving", "Geef water van onderaf om de donzige bladeren droog te houden."),
    ("Cape Primrose", "Streptocarpus spp.", "moisture_loving", "Vergelijkbare verzorging als het Kaaps Viooltje."),
    ("Cyclamen", "Cyclamen persicum", "moisture_loving", "Gaat 's zomers in rust - geef dan minder water."),
    ("Primrose", "Primula vulgaris", "moisture_loving", "Vaak gekweekt als tijdelijke bloeiende kamerplant."),
    ("Caladium", "Caladium bicolor", "moisture_loving", "Groeit uit een knol; gaat 's winters in rust."),
    ("Guzmania Bromeliad", "Guzmania lingulata", "moisture_loving", "Houd ook de centrale 'beker' van de rozet gevuld met water."),
    ("Vriesea Bromeliad", "Vriesea splendens", "moisture_loving", "Houd ook de centrale 'beker' van de rozet gevuld met water."),
    ("Aechmea Bromeliad", "Aechmea fasciata", "moisture_loving", "Houd ook de centrale 'beker' van de rozet gevuld met water."),
    ("Azalea (potted)", "Rhododendron simsii", "moisture_loving", "Houdt van licht zure grond; laat niet uitdrogen."),
    ("Hydrangea (potted)", "Hydrangea macrophylla", "moisture_loving", "Hangt snel bij dorst; een echte waterdrinker."),
    ("Bird of Paradise", "Strelitzia reginae", "drought_tolerant", "Houdt van helder licht; laat de grond duidelijk opdrogen tussen de beurten door."),

    # --- Hoog vocht / vleesetend / moerasplanten ---
    ("Umbrella Papyrus", "Cyperus alternifolius", "high_moisture", "Een moerasplant - staat graag in een ondiep schoteltje water."),
    ("Venus Flytrap", "Dionaea muscipula", "high_moisture", "Gebruik uitsluitend gedistilleerd of regenwater; nooit bemesten via de grond."),
    ("Pitcher Plant", "Sarracenia spp.", "high_moisture", "Gebruik uitsluitend gedistilleerd of regenwater; heeft veel licht nodig."),
    ("Sundew", "Drosera capensis", "high_moisture", "Gebruik uitsluitend gedistilleerd of regenwater; houd het schoteltje gevuld."),
    ("Calla Lily (potted)", "Zantedeschia aethiopica", "high_moisture", "Houdt van gelijkmatig vochtige, bijna drassige grond."),
    ("Sensitive Plant", "Mimosa pudica", "high_moisture", "Bladeren vouwen dicht bij aanraking; houd de grond gelijkmatig vochtig."),

    # --- Meer vetplanten ---
    ("Mexican Snowball", "Echeveria elegans", "succulent", "Vormt rozetten; maakt makkelijk uitlopers."),
    ("Echeveria 'Perle von Nurnberg'", "Echeveria 'Perle von Nurnberg'", "succulent", "Stoffig paars-roze rozet."),
    ("Tree Houseleek", "Aeonium arboreum", "succulent", "Rozetten op houtachtige stengels; verliest op natuurlijke wijze onderste bladeren."),
    ("Mother of Thousands", "Kalanchoe daigremontiana", "succulent", "Maakt piepkleine plantjes langs de bladrand - kan zichzelf overvloedig uitzaaien."),
    ("Watch Chain Plant", "Crassula muscosa", "succulent", "Strak gestapeld, kettingachtig blad."),
    ("Fairy Washboard", "Haworthiopsis limifolia", "succulent", "Geribbelde, donkergroene bladeren."),
    ("Baseball Plant", "Euphorbia obesa", "succulent", "Rond, zonder stekels; sap kan de huid irriteren."),
    ("Living Stones", "Lithops spp.", "succulent", "Geef pas water als het oude bladpaar helemaal verschrompeld is - erg makkelijk te veel water te geven."),
    ("Jelly Bean Plant", "Sedum rubrotinctum", "succulent", "Bladeren kleuren rood bij veel licht."),
    ("Starfish Flower", "Stapelia grandiflora", "succulent", "Stervormige bloemen met een onaangename geur (trekt vliegen aan als bestuivers)."),
    ("Hoya Bella", "Hoya bella", "succulent", "Compact, hangend; geurende bloemtrossen."),

    # --- Meer standaard tropisch groen ---
    ("Neon Pothos", "Epipremnum aureum 'Neon'", "standard", "Felgroene bladeren; heeft goed licht nodig om de kleur te behouden."),
    ("Cebu Blue Pothos", "Epipremnum pinnatum", "standard", "Zilverblauwe glans op de bladeren."),
    ("Philodendron Prince of Orange", "Philodendron 'Prince of Orange'", "standard", "Nieuwe bladeren komen oranje op en verkleuren later groen."),
    ("Philodendron Congo", "Philodendron 'Congo'", "standard", "Grote, rechtopstaande, niet-klimmende bladeren."),
    ("Philodendron Brasil", "Philodendron hederaceum 'Brasil'", "standard", "Geel-groen gestreepte variant van de Heartleaf Philodendron."),
    ("Alocasia Polly", "Alocasia 'Amazonica Polly'", "moisture_loving", "Opvallend wit geaderde bladeren; gevoelig voor zowel te veel als te weinig water."),
    ("Alocasia Black Velvet", "Alocasia reginula", "moisture_loving", "Donkere, fluweelachtige bladeren; houd de luchtvochtigheid hoog."),
    ("Alocasia Zebrina", "Alocasia zebrina", "moisture_loving", "Opvallend gestreepte bladstelen."),
    ("Anthurium Clarinervium", "Anthurium clarinervium", "moisture_loving", "Uitgesproken witte nervatuur op fluweelachtige bladeren."),
    ("Anthurium Crystallinum", "Anthurium crystallinum", "moisture_loving", "Grote fluweelachtige bladeren met zilveren nerven."),
    ("Calathea White Fusion", "Calathea lietzei 'White Fusion'", "moisture_loving", "Wit-groen gemarmerde bladeren; gevoelig voor mineralen in leidingwater."),
    ("Raindrop Peperomia", "Peperomia polybotrya", "standard", "Ronde, glanzende, druppelvormige bladeren."),
    ("Cupid Peperomia", "Peperomia scandens", "standard", "Hangende, hartvormige bonte bladeren."),
    ("Red Log Peperomia", "Peperomia verticillata", "standard", "Kleine, kransgewijs geplaatste blaadjes op roodachtige stelen."),
    ("Trailing Jade", "Peperomia rotundifolia", "succulent", "Kleine ronde blaadjes aan hangende stelen."),
    ("Zebra Plant", "Aphelandra squarrosa", "moisture_loving", "Opvallend wit geaderde bladeren; kan lastig zijn qua gelijkmatige vochtbehoefte."),
    ("Polka Dot Plant", "Hypoestes phyllostachya", "moisture_loving", "Gespikkelde bladeren; wordt snel kaal onderaan en heeft baat bij toppen."),
    ("Purple Heart", "Tradescantia pallida", "standard", "Levendig paars blad; kleurt het mooist bij veel licht."),
    ("Turtle Vine", "Callisia repens", "standard", "Klein, snel hangend, makkelijk te vermeerderen."),
    ("Red Aglaonema", "Aglaonema 'Red Valentine'", "standard", "Roze-groene bladeren; verdraagt gemiddeld binnenlicht."),
    ("Lemon Lime Dracaena", "Dracaena 'Lemon Lime'", "standard", "Felgeel-groen gestreepte bladeren."),
    ("Asparagus Fern", "Asparagus setaceus", "moisture_loving", "Geen echte varen; delicaat, veerachtig blad."),
    ("Rabbit's Foot Fern", "Davallia fejeensis", "moisture_loving", "Harige wortelstokken die over de potrand kruipen."),
    ("Purple Shamrock", "Oxalis triangularis", "standard", "Bladeren vouwen 's nachts op; kan periodiek in rust gaan - geef dan minder water."),
    ("Lucky Bamboo", "Dracaena sanderiana", "moisture_loving", "Vaak op water gekweekt, maar groeit ook goed in een vochtige, goed drainerende potgrond."),
    ("Amaryllis", "Hippeastrum spp.", "standard", "Groeit uit een bol; geef minder water zodra de bloei voorbij is en de plant in rust gaat."),
    ("Clivia", "Clivia miniata", "drought_tolerant", "Heeft een koele, droge rustperiode in de winter nodig om goed te bloeien."),
    ("Rain Lily", "Zephyranthes spp.", "standard", "Kleine bol; bloeit enkele dagen na een flinke gietbeurt."),
    ("Jasmine", "Jasminum polyanthum", "moisture_loving", "Geurend; houdt van koelere nachten en gelijkmatig vocht om te bloeien."),
    ("Gardenia", "Gardenia jasminoides", "moisture_loving", "Geurende bloemen; heeft baat bij licht zure grond en gelijkmatig vocht."),
    ("Chinese Hibiscus", "Hibiscus rosa-sinensis", "moisture_loving", "Een echte waterdrinker, zeker tijdens de bloei."),
    ("Passion Flower", "Passiflora caerulea", "standard", "Krachtige klimmer; heeft baat bij een rek of steun."),
    ("Boat Lily", "Tradescantia spathacea", "standard", "Paars-groene, bootvormige bladschutten."),
    ("Peperomia Hope", "Peperomia tetraphylla 'Hope'", "standard", "Hangend, kleine ronde blaadjes; makkelijke groeier."),
    ("Watermelon Begonia", "Peperomia argyreia", "standard", "Dezelfde plant als de Watermelon Peperomia (andere naam)."),
    ("Silver Pothos", "Scindapsus pictus 'Silvery Ann'", "standard", "Sterk zilver gespikkelde bladeren."),
    ("Philodendron Micans", "Philodendron hederaceum 'Micans'", "standard", "Fluweelachtige, glanzend bronsgroene bladeren."),
    ("Peace Lily 'Domino'", "Spathiphyllum 'Domino'", "moisture_loving", "Bonte, wit gespikkelde bladeren; zelfde verzorging als de gewone Lepelplant."),
    ("Dwarf Umbrella Tree", "Schefflera arboricola 'Compacta'", "standard", "Compacte cultivar van de Schefflera."),
    ("Ponytail Palm (dwarf)", "Beaucarnea recurvata 'Nolina'", "drought_tolerant", "Compacte vorm van de gewone Olifantspoot."),
    ("Bunny Ear Cactus", "Opuntia microdasys 'Albata'", "desert_cactus", "Wit-stekelige vorm van de Bunny Ear (schijfcactus)."),
    ("Christmas Kalanchoe", "Kalanchoe blossfeldiana 'Calandiva'", "succulent", "Dubbelbloemige vorm van de Flaming Katy."),
    ("Bunny Succulent", "Monilaria obconica", "succulent", "Seizoensgebonden vetplant die als jonge plant op kleine konijnenoortjes lijkt."),

    # --- Toegevoegd na review van Nederlandse tuincentrum-assortimenten (Intratuin e.a.) ---
    ("Banana Plant", "Musa spp.", "moisture_loving", "Grote, indrukwekkende bladeren; een echte water- en voedingdrinker tijdens het groeiseizoen."),
    ("Canary Island Date Palm", "Phoenix canariensis", "standard", "Grote, boogvormige, vederachtige bladeren; houdt van veel licht."),
    ("Pygmy Date Palm", "Phoenix roebelenii", "standard", "Compacte dadelpalm, kleiner dan zijn Canarische verwant."),
    ("European Fan Palm", "Chamaerops humilis", "drought_tolerant", "Mediterrane palm; droogtetoleranter dan de meeste kamerpalmen."),
    ("Room Lime", "Sparrmannia africana", "moisture_loving", "Een traditionele Nederlandse kamerplant met zachte, donzige bladeren; een echte waterdrinker."),
    ("Rose Grape", "Medinilla magnifica", "moisture_loving", "Indrukwekkende roze bloemtrossen; houdt van hoge luchtvochtigheid en het liefst regenwater."),
    ("Fishtail Palm", "Caryota mitis", "standard", "Opvallende, gerafelde, visstaartvormige blaadjes."),
    ("Lemon Tree (potted)", "Citrus limon", "standard", "Heeft zoveel mogelijk fel, direct licht nodig binnenshuis; profiteert van een zomer buiten."),
    ("Orchid Cactus", "Epiphyllum spp.", "epiphytic", "Een epifytische 'bladcactus' - laat, anders dan woestijncactussen, niet helemaal uitdrogen."),
    ("Kris Plant", "Alocasia sanderiana", "moisture_loving", "Golvende, donkere bladeren met lichte nerven; gevoelig voor zowel te veel als te weinig water."),

]

# Well-known distinct Dutch common names, keyed by the English display_name
# above. Where Dutch retail (Intratuin, Bakker, Plantsome, tuincentrum.nl)
# just uses the Latin genus name too (e.g. "Calathea", "Alocasia"), that's
# already covered by scientific_name and isn't repeated here.
DUTCH_NAMES = {
    "Snake Plant": ["Vrouwentong"],
    "Monstera": ["Gatenplant"],
    "Swiss Cheese Vine": ["Klimmende Gatenplant"],
    "Peace Lily": ["Lepelplant", "Vaantjesplant", "Vredeslelie"],
    "Peace Lily 'Domino'": ["Lepelplant 'Domino'"],
    "Bird of Paradise": ["Paradijsvogel", "Paradijsvogelbloem"],
    "Calla Lily (potted)": ["Aronskelk"],
    "Flamingo Flower": ["Flamingoplant"],
    "Yucca Cane": ["Palmlelie"],
    "Dragon Tree": ["Drakenbloedboom"],
    "Corn Plant": ["Drakenbloedboom"],
    "Song of India": ["Drakenbloedboom"],
    "Poinsettia": ["Kerstster"],
    "Christmas Cactus": ["Kerstcactus", "Lidcactus"],
    "Thanksgiving Cactus": ["Kerstcactus"],
    "Lucky Bamboo": ["Geluksbamboe"],
    "ZZ Plant": ["Geluksplant"],
    "Spider Plant": ["Graslelie", "Spinnenplant"],
    "Ponytail Palm": ["Olifantspoot", "Paardenstaart"],
    "Areca Palm": ["Goudpalm"],
    "Parlor Palm": ["Kamerpalm", "Mexicaanse Dwergpalm"],
    "Bamboo Palm": ["Bamboepalm"],
    "Money Tree": ["Malabar Kastanje"],
    "Gardenia": ["Kaapse Jasmijn"],
    "Moth Orchid": ["Vlinderorchidee", "Orchidee"],
    "Nerve Plant": ["Mozaïekplant"],
    "Umbrella Tree": ["Parapluplantje", "Vingerplant"],
    "Umbrella Papyrus": ["Papyrusplant"],
    "Chinese Money Plant": ["Pannenkoekenplant", "Pannenkoekplant", "Pannekoekplant", "Chinese Muntplant"],
    "Baby Rubber Plant": ["Vetblad Peperomia"],
    "Rubber Plant": ["Rubberplant"],
    "Fiddle Leaf Fig": ["Vioolbladplant", "Vioolplant"],
    "Weeping Fig": ["Treurvijg"],
    "Dumb Cane": ["Hondsoor"],
    "Cast Iron Plant": ["IJzeren Plant"],
    "Silver Squill": ["Zilveruitje"],
    "African Violet": ["Kaaps Viooltje"],
    "Elephant Ear": ["Olifantsoor"],
    "African Mask Plant": ["Olifantsoor"],
    "Boston Fern": ["Zwaardvaren"],
    "Bird's Nest Fern": ["Vogelnestvaren"],
    "Wijze Varen (Bird's Nest Fern)": ["Wijze Varen", "Vogelnestvaren"],
    "Staghorn Fern": ["Hertshoornvaren"],
    "Baby's Tears": ["Helxine", "Sterremos"],
    "Wax Plant": ["Wasbloem", "Hoya"],
    "Purple Shamrock": ["Klaverzuring"],
    "Amaryllis": ["Ridderster"],
    "Rain Lily": ["Regenlelie"],
    "Passion Flower": ["Passiebloem"],
    "Turtle Vine": ["Schildpadplant"],
    "Croton": ["Bonte Codiaeum"],
    "Coffee Plant": ["Koffieplant"],
    "Chinese Hibiscus": ["Hibiscus"],
    "Jasmine": ["Jasmijn"],
    "Aloe Vera": ["Echte Aloë"],
    "Jade Plant": ["Geldboompje"],
    "Banana Plant": ["Bananenplant"],
    "Canary Island Date Palm": ["Canarische Dadelpalm"],
    "Pygmy Date Palm": ["Dwergdadelpalm"],
    "European Fan Palm": ["Europese Dwergpalm"],
    "Room Lime": ["Kamerlinde"],
    "Rose Grape": ["Medinilla"],
    "Fishtail Palm": ["Vistaartpalm"],
    "Lemon Tree (potted)": ["Citroenboom"],
    "Orchid Cactus": ["Bladcactus"],
}

# Keep the four originals from the first release's thresholds verbatim
# (already-known-good values from real-world use), so upgrading doesn't
# shift anyone's existing values.
LEGACY_OVERRIDES = {
    "Bird of Paradise": (15.0, 65.0),
    "Monstera": (15.0, 55.0),
    "Wijze Varen (Bird's Nest Fern)": (30.0, 75.0),
}


def slugify(name: str) -> str:
    out = []
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


def build() -> list[dict]:
    seen_ids: set[str] = set()
    species = []
    for display_name, scientific_name, profile, extra_note in PLANTS:
        dry, wet, generic_note = PROFILES[profile]
        if display_name in LEGACY_OVERRIDES:
            dry, wet = LEGACY_OVERRIDES[display_name]
        species_id = slugify(f"{display_name}-{scientific_name}")
        base_id = species_id
        i = 2
        while species_id in seen_ids:
            species_id = f"{base_id}-{i}"
            i += 1
        seen_ids.add(species_id)

        dutch_names = DUTCH_NAMES.get(display_name, [])
        aliases = sorted({display_name, scientific_name, *dutch_names})

        sections = CARE_GUIDE_SECTIONS[profile]
        toxicity_level = TOXICITY.get(display_name)
        toxicity_text = TOXICITY_TEXT.get(toxicity_level, DEFAULT_TOXICITY_NOTE)
        care_guide = {
            "light": sections["light"],
            "watering": f"{generic_note} {extra_note}".strip(),
            "humidity": sections["humidity"],
            "temperature": sections["temperature"],
            "fertilizing": sections["fertilizing"],
            "repotting": sections["repotting"],
            "common_problems": sections["common_problems"],
            "toxicity": toxicity_text,
        }
        # A single flattened string for simple display (e.g. the sensor's
        # state) - the structured `care_guide` above is what the dashboard
        # card's expandable section actually renders from.
        section_labels = [
            ("Licht", "light"), ("Water geven", "watering"), ("Luchtvochtigheid", "humidity"),
            ("Temperatuur", "temperature"), ("Bemesten", "fertilizing"),
            ("Verpotten", "repotting"), ("Veelvoorkomende problemen", "common_problems"),
            ("Giftigheid", "toxicity"),
        ]
        care_tip = "\n".join(f"{label}: {care_guide[key]}" for label, key in section_labels)

        stock_photo = STOCK_PHOTOS.get(display_name)

        species.append(
            {
                "id": species_id,
                "display_name": display_name,
                "scientific_name": scientific_name,
                "dutch_names": dutch_names,
                "select_label": (
                    display_name if not dutch_names else f"{display_name} / {dutch_names[0]}"
                ) + f" ({scientific_name})",
                "aliases": aliases,
                "profile": profile,
                "dry_threshold": dry,
                "wet_threshold": wet,
                "care_guide": care_guide,
                "care_tip": care_tip,
                "stock_photo_url": stock_photo[0] if stock_photo else None,
                "stock_photo_credit": stock_photo[1] if stock_photo else None,
            }
        )
    return species


if __name__ == "__main__":
    plant_names = {p[0] for p in PLANTS}
    unknown_keys = set(DUTCH_NAMES) - plant_names
    if unknown_keys:
        raise SystemExit(f"DUTCH_NAMES has keys with no matching plant: {unknown_keys}")
    unknown_toxicity_keys = set(TOXICITY) - plant_names
    if unknown_toxicity_keys:
        raise SystemExit(f"TOXICITY has keys with no matching plant: {unknown_toxicity_keys}")
    unknown_photo_keys = set(STOCK_PHOTOS) - plant_names
    if unknown_photo_keys:
        raise SystemExit(f"STOCK_PHOTOS has keys with no matching plant: {unknown_photo_keys}")

    data = build()
    with_dutch = sum(1 for e in data if e["dutch_names"])
    with_known_toxicity = sum(1 for e in data if e["display_name"] in TOXICITY)
    with_stock_photo = sum(1 for e in data if e["stock_photo_url"])
    print(
        f"Generated {len(data)} species entries "
        f"({with_dutch} with a distinct Dutch name, "
        f"{with_known_toxicity} with a confirmed ASPCA toxicity listing, "
        f"{with_stock_photo} with a verified stock photo)."
    )
    out_path = os.path.join(
        os.path.dirname(__file__), "..", "custom_components", "plant_monitor", "species_data.json"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Written to {os.path.abspath(out_path)}")
