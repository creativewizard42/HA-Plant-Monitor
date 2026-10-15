"""Corrections from the complete 203-entry care review (October 2026).

Keys use the original catalogue names so shipped IDs, aliases and care-tip
hashes remain compatible. Percentages are sensor-calibration starting points,
not measured botanical requirements. See docs/PLANT_PROFILE_REVIEW.md.
"""

PROFILE_OVERRIDES = {
    "String of Turtles": "standard",
    "Aloe Vera": "succulent",
    "Lace Aloe": "succulent",
    "Agave": "succulent",
    "Silver Squill": "succulent",
    "Bird's Nest Sansevieria": "drought_tolerant",
    "Rattlesnake Plant Vine": "moist_airy",
    "Bird of Paradise": "standard",
    "Sensitive Plant": "moisture_loving",
    "Hoya Bella": "standard",
    "Trailing Jade": "standard",
    **dict.fromkeys([
        "African Mask Plant", "Alocasia Polly", "Alocasia Black Velvet",
        "Alocasia Zebrina", "Kris Plant", "Flamingo Flower",
        "Anthurium Clarinervium", "Anthurium Crystallinum", "Rex Begonia",
        "African Violet", "Cape Primrose", "Croton", "Ti Plant",
        "Coffee Plant", "Ficus Ginseng (Bonsai)", "Areca Palm",
        "Bamboo Palm", "Fishtail Palm", "Rex Begonia Vine",
        "Guzmania Bromeliad", "Vriesea Bromeliad", "Aechmea Bromeliad",
    ], "moist_airy"),
}

SCIENTIFIC_NAMES = {
    "Bird's Nest Sansevieria": "Dracaena trifasciata 'Hahnii'",
    "Christmas Cactus": "Schlumbergera × buckleyi",
    "Haworthia (Pearl Plant)": "Haworthiopsis attenuata",
    "Zebra Haworthia": "Haworthiopsis fasciata",
    "Cylindrical Snake Plant": "Dracaena angolensis",
    "Split-Leaf Philodendron": "Thaumatophyllum bipinnatifidum",
    "Rattlesnake Plant Vine": "Nepenthes alata",
    "String of Pearls": "Curio rowleyanus",
    "String of Bananas": "Curio radicans",
    "String of Dolphins": "Curio × peregrinus",
    "African Mask Plant": "Alocasia × amazonica",
    "Peperomia Hope": "Peperomia 'Hope'",
}

DISPLAY_NAMES = {
    "Rattlesnake Plant Vine": "Tropical Pitcher Plant",
    "Haworthia (Pearl Plant)": "Haworthia (Zebra Plant)",
    "Star Cactus": "Ornate Star Cactus",
}

# Avoid inferring human safety from a pet-toxicity list or promising that
# poisoning is "usually not life-threatening". Uncertain species stay unknown.
TOXICITY_OVERRIDES = {
    "Baseball Plant": "toxic",  # Euphorbia latex; previous non-toxic claim wrong.
    "Fishtail Palm": "toxic",  # Fruit contains irritating calcium oxalate.
    "Asparagus Fern": "toxic",  # Berries and sap, not a true pet-safe fern.
    "Rubber Plant": "toxic", "Fiddle Leaf Fig": "toxic",
    "Weeping Fig": "toxic", "Audrey Ficus": "toxic",
    "Ficus Ginseng (Bonsai)": "toxic", "Agave": "toxic",
    "Fatsia": "non_toxic", "Zebra Plant": "non_toxic",
    "Watch Chain Plant": "unknown", "Jelly Bean Plant": "unknown",
    "Turtle Vine": "unknown", "Room Lime": "unknown",
    "Rose Grape": "unknown", "Chinese Hibiscus": "unknown",
    "Sensitive Plant": "unknown",
}

HUMIDITY_NORMAL = (
    "Normale kamerlucht is meestal voldoende. Bij langdurig droge lucht kan een "
    "luchtbevochtiger helpen; sproeien of een waterschaaltje verhoogt de "
    "luchtvochtigheid niet blijvend. Houd nat blad niet langdurig vochtig."
)
HUMIDITY_TROPICAL = (
    "Streef naar ongeveer 50-60% luchtvochtigheid met goede luchtcirculatie. "
    "Gebruik bij droge lucht een luchtbevochtiger of een geschikte lichte ruimte. "
    "Sproeien en waterschaaltjes vervangen geen blijvend vochtige lucht."
)

CARE_OVERRIDES = {
    "Bird of Paradise": {
        "light": "Zet zo licht mogelijk, vlak bij een zonnig raam. Na geleidelijke gewenning verdraagt Strelitzia reginae meerdere uren directe zon; voldoende zon is belangrijk voor bloei. Een donker noordraam is meestal onvoldoende.",
        "watering": "Geef grondig water zodra de bovenste 2-3 cm droog is en laat goed uitlekken. Houd de rest van de kluit tijdens actieve groei licht vochtig; in een koelere, donkere winter minder water. Controleer de grond in plaats van een vast weekschema.",
        "humidity": HUMIDITY_NORMAL,
    },
    "Monstera": {
        "humidity": HUMIDITY_NORMAL,
        "fertilizing": "Bemest tijdens actieve groei in voorjaar en zomer ongeveer maandelijks met verdunde kamerplantenvoeding. Bij weinig groei in herfst en winter minderen of stoppen.",
    },
    "Wijze Varen (Bird's Nest Fern)": {
        "watering": "Houd de kluit licht vochtig en laat alleen de bovenste 1-2 cm licht opdrogen. Geef water langs de rand, niet in het hart van de rozet, en laat goed uitlekken. Controleer de grond in plaats van een vast gietschema.",
        "humidity": HUMIDITY_TROPICAL,
        "fertilizing": "Bemest tijdens actieve groei in voorjaar en zomer ongeveer maandelijks op kwart- tot halve sterkte. Bij winterrust niet bemesten.",
    },
    "Bird's Nest Fern": {
        "watering": "Houd de kluit licht vochtig, laat de bovenste 1-2 cm licht opdrogen en giet langs de potrand. Geen water in het hart van de rozet en geen stilstaand water onder de pot.",
    },
    "Heartleaf Philodendron": {
        "watering": "Geef grondig water als de bovenste 2-3 cm droog is en laat goed uitlekken. In de winter bij minder licht minder vaak; beoordeel de grond en geef niet volgens een vast weekschema.",
        "humidity": HUMIDITY_NORMAL,
        "common_problems": "Gele bladeren kunnen door te natte grond, wortelproblemen, licht of veroudering komen. Controleer grond en wortels voordat je extra water geeft. Krullend blad en droge randen kunnen op uitdroging of droge lucht wijzen.",
    },
    "Chinese Money Plant": {"humidity": HUMIDITY_NORMAL},
    "Calathea Rufibarba": {
        "watering": "Houd de kluit licht vochtig en geef water zodra de bovenste 1-2 cm licht opdroogt. Gebruik kalkarm water; laat goed uitlekken. In de winter bij minder groei minder vaak gieten, maar de kluit niet volledig laten uitdrogen.",
        "humidity": "Streef naar ongeveer 50-70% luchtvochtigheid met luchtcirculatie. Boven 80% is geen algemene vereiste. Gebruik bij droge lucht een luchtbevochtiger; herhaald sproeien verhoogt de luchtvochtigheid niet blijvend.",
        "fertilizing": "Bemest tijdens actieve groei in voorjaar en zomer ongeveer maandelijks met evenwichtige kamerplantenvoeding op halve sterkte.",
        "repotting": "Verpot als de wortels de pot vullen, meestal om de 1-2 jaar in het voorjaar, in luchtige vochtvasthoudende potgrond. Verwijder alleen beschadigde of afgestorven bladeren bij de basis.",
    },
    "Alocasia Polly": {
        "watering": "Laat de bovenste 2-3 cm opdrogen en houd de kluit tijdens actieve groei licht vochtig, nooit drassig. Bij weinig groei of winterrust minder water; een rustende knol hoeft niet constant vochtig te blijven.",
        "humidity": HUMIDITY_TROPICAL,
        "temperature": "Streef tijdens actieve groei naar 18-27°C en vermijd temperaturen onder ongeveer 15°C, koude tocht en hete radiatoren.",
        "repotting": "Verpot wanneer de wortels de pot vullen in een luchtig mengsel met schors en perliet. Gebruik een pot met drainagegaten en laat uitlekken. Een laag kleikorrels onder potgrond verbetert de drainage niet.",
        "common_problems": "Bruine randen kunnen door droge lucht, waterstress, zoutophoping of wortelproblemen ontstaan. Geel blad kan op te natte grond, weinig licht of veroudering wijzen. Controleer op spint en trips; vervormd blad bewijst geen overwatering.",
    },
    "Blue Star Fern": {
        "watering": "Houd de kluit licht vochtig, laat de bovenste laag licht opdrogen en laat na het gieten uitlekken. Houd de wortelstok boven de grond. Giet naar behoefte; een vast schema van één of twee beurten per week is niet betrouwbaar.",
        "humidity": HUMIDITY_TROPICAL,
        "common_problems": "Bruin blad kan door droge lucht, uitdroging, zoutophoping of wortelproblemen ontstaan. Geel blad kan ook door te natte grond, weinig licht of veroudering komen; bemest niet zonder de oorzaak te controleren.",
    },
    "String of Turtles": {
        "watering": "Laat de bovenste 1-2 cm opdrogen en geef dan bescheiden maar grondig water met goede drainage. Laat de kleine wortelkluit niet langdurig volledig uitdrogen; voorkom ook drassige grond.",
    },
    "Trailing Jade": {
        "watering": "Laat de bovenste 1-2 cm opdrogen en houd de rest van de kluit licht vochtig tijdens groei. Deze tropische Peperomia is geen woestijnvetplant; vermijd zowel langdurig uitdrogen als natte voeten.",
    },
    "Hoya Bella": {
        "watering": "Laat de bovenste 1-2 cm licht opdrogen, geef grondig water en laat uitlekken. Hoya bella heeft minder dikke bladeren dan Hoya carnosa en mag tijdens actieve groei niet langdurig helemaal uitdrogen. In een koele winter minder water.",
        "common_problems": "Knopval kan door uitdroging, temperatuurwisselingen of verplaatsen komen. Uitgebloeide steeltjes van Hoya bella vallen vaak vanzelf af; het advies om alle bloemsporen te bewaren geldt vooral voor Hoya carnosa.",
    },
    "Peperomia Hope": {"watering": "Laat de bovenste 2-3 cm opdrogen en geef dan water met goede drainage. De dikke blaadjes verdragen enige droogte, maar laat de wortelkluit niet langdurig kurkdroog worden."},
    "Red Log Peperomia": {"watering": "Laat de bovenste 2-3 cm opdrogen en laat na het gieten uitlekken. Voorkom langdurig volledig uitdrogen en drassige grond."},
    "Rattlesnake Plant Vine": {
        "watering": "Houd het luchtige, voedselarme substraat licht vochtig met regenwater, gedistilleerd water of omgekeerde-osmosewater. Laat uitlekken; Nepenthes hoort niet permanent in een schotel water zoals Sarracenia.",
        "humidity": "Ongeveer 50-70% luchtvochtigheid helpt de bekervorming. Geen bekers kan ook door te weinig licht of aanpassing na aankoop komen; hoge luchtvochtigheid alleen is geen garantie.",
        "fertilizing": "Gebruik geen gewone potgrondmest. De plant vangt zelf kleine insecten; handmatig voeren is niet nodig. Voedselarm substraat en mineraalarm water zijn belangrijker dan bijmesten.",
        "common_problems": "Geen bekers kan door weinig licht, droge lucht of acclimatisatie komen. Oude bekers sterven vanzelf af. In winkels als Nepenthes alata verkochte planten zijn vaak hybriden zoals N. × ventrata; controleer het etiket voor specifieke temperatuurbehoeften.",
    },
    "Dendrobium Orchid": {
        "watering": "Geef tijdens groei grondig water als de schors bijna droog is en laat uitlekken. Een koele, drogere rust geldt voor nobile-typen; warm groeiende bigibbum-/phalaenopsis-typen mogen niet dezelfde koude, droge rust krijgen. Controleer het type op het etiket.",
        "temperature": "De behoefte hangt af van de soort of hybride. Nobile-typen waarderen koelere nachten tijdens de rust; warm groeiende bigibbum-/phalaenopsis-typen liever boven ongeveer 15°C houden. Eén koele winterregel past niet bij alle Dendrobium-soorten.",
        "fertilizing": "Bemest tijdens actieve groei ongeveer elke 2-4 weken met verdunde orchideeënvoeding. Alleen minderen of stoppen wanneer het betreffende type rust of weinig groeit.",
        "common_problems": "Geen bloei kan door licht, rijpheid of een rustbehoefte komen. Pas een koude, droge rust alleen toe bij een type dat die nodig heeft; keiki-vorming heeft meerdere mogelijke oorzaken.",
    },
    "Calla Lily (potted)": {
        "watering": "Houd Zantedeschia aethiopica tijdens actieve groei gelijkmatig vochtig. In warme of droge omstandigheden kan hij rusten: verminder pas als het blad terugloopt. Een verplichte droge rust direct na elke bloei geldt niet voor alle aethiopica-planten.",
        "repotting": "Verpot de wortelstok indien nodig in voedzame, vochtvasthoudende grond. Maak onderscheid met gekleurde Zantedeschia-hybriden, die doorgaans een uitgesprokener droge rust hebben.",
        "common_problems": "Geel blad kan door rust, waterstress of voeding ontstaan. Geen bloei kan door licht, groeiomstandigheden of een jonge wortelstok komen; forceer niet automatisch een droge rust.",
    },
    "Snake Plant": {"light": "Groeit het best in helder, indirect licht; na gewenning kan ook zon. Verdraagt tijdelijk weinig licht maar groeit dan nauwelijks. Een blijvend donkere hoek is geen goede groeiplek."},
    "ZZ Plant": {"common_problems": "Gele stelen en zachte knollen kunnen op wortelrot door te veel water wijzen. Langzame groei bij weinig licht is normaal; aanhoudende bladval vraagt controle van licht, water en wortels."},
    "Cast Iron Plant": {"light": "Verdraagt weinig indirect licht en halfschaduw, maar heeft wel daglicht nodig. Vermijd felle middagzon; een volledig donkere hoek is ongeschikt."},
    "Haworthia (Pearl Plant)": {"light": "Haworthiopsis attenuata heeft helder licht met zachte ochtendzon nodig. Wen geleidelijk aan sterkere zon en vermijd hete middagzon achter glas; een donkere plek is ongeschikt. De handelsnaam Pearl Plant hoort doorgaans bij Tulista pumila, een andere soort."},
    "Guzmania Bromeliad": {"fertilizing": "Tijdens groei ongeveer maandelijks zeer verdunde bromelia- of kamerplantenvoeding op het substraat of volgens het productetiket over het blad. Geen geconcentreerde mest in de centrale koker; ververs het kokerwater regelmatig."},
    "Vriesea Bromeliad": {"fertilizing": "Tijdens groei ongeveer maandelijks zeer verdunde bromeliavoeding op het substraat of volgens het productetiket over het blad. Vermijd mestophoping in de koker."},
    "Aechmea Bromeliad": {"fertilizing": "Tijdens groei ongeveer maandelijks zeer verdunde bromeliavoeding op het substraat of volgens het productetiket over het blad. Geen geconcentreerde mest in de koker."},
    "Sundew": {"humidity": "Drosera capensis doet het doorgaans goed bij normale kamervochtigheid, met veel licht en voldoende water. Een afgesloten, heet terrarium is niet nodig."},
    "Calathea Orbifolia": {"humidity": "Ongeveer 50-70% luchtvochtigheid met luchtcirculatie is een bruikbaar uitgangspunt. Gebruik bij langdurig droge lucht een luchtbevochtiger; die is niet in elk huis nodig."},
    "Cape Primrose": {"common_problems": "Bruine bladpunten kunnen door waterstress, zoutophoping of droge lucht komen. Zachte bladvoeten vragen controle op te natte grond; behandel niet elke droge punt als normale groei."},
    "Mother of Thousands": {"common_problems": "Een oudere plant kan onderaan kaal worden; uitgerekte, slappe groei wijst ook op te weinig licht. Zachte stengels vragen controle op rot. Verwijder ongewenste broedplantjes."},
    "Sensitive Plant": {"common_problems": "Gesloten blaadjes in de nacht zijn normaal. Overdag gesloten blad kan door aanraking, kou, waterstress of weinig licht komen; raak de plant niet steeds aan."},
}

# Alert presets for newly configured plants, not survival limits. Dormancy
# must still be handled by the user; static thresholds cannot infer seasons.
ENVIRONMENT_BY_PROFILE = {
    "desert_cactus": (5, 35, 20), "succulent": (10, 32, 20),
    "drought_tolerant": (10, 32, 30), "standard": (15, 30, 40),
    "epiphytic": (15, 30, 50), "moist_airy": (15, 30, 50),
    "moisture_loving": (15, 30, 50), "high_moisture": (10, 32, 40),
}
ENVIRONMENT_OVERRIDES = {
    **dict.fromkeys(["English Ivy", "Fatsia", "Room Lime", "Cyclamen",
                     "Primrose", "Azalea (potted)", "Baby's Tears"], (7, 24, 40)),
    "Hydrangea (potted)": (5, 27, 40), "Norfolk Island Pine": (10, 27, 50),
    "Cast Iron Plant": (7, 30, 30), "Hens and Chicks": (0, 35, 20),
    "Venus Flytrap": (0, 35, 30), "Pitcher Plant": (0, 35, 30),
    "Sundew": (10, 32, 40), "Lemon Tree (potted)": (5, 35, 40),
    "Canary Island Date Palm": (5, 35, 30), "European Fan Palm": (0, 35, 30),
    "Tree Houseleek": (5, 30, 20), "Bunny Succulent": (5, 28, 20),
    "Clivia": (10, 30, 40), "Jasmine": (8, 30, 50),
    "Rattlesnake Plant Vine": (15, 32, 50),
    "Caladium": (16, 32, 50), "Banana Plant": (12, 35, 50),
    **dict.fromkeys(["Calathea Rufibarba", "Calathea Orbifolia", "Calathea Medallion",
                     "Peacock Plant", "Rattlesnake Plant", "Calathea White Fusion",
                     "Prayer Plant", "Fishbone Prayer Plant", "Never-Never Plant",
                     "Alocasia Black Velvet", "Alocasia Zebrina", "Kris Plant"], (16, 30, 50)),
}

WATERLOGGING_TOLERANT = {"Umbrella Papyrus", "Venus Flytrap", "Pitcher Plant", "Sundew"}
WATERING_CAUTIONS = {
    "Living Stones": "Controleer eerst de groeifase: tijdens bladwisseling en zomerrust geen water geven, ook niet bij een lage sensorwaarde.",
    **dict.fromkeys(["Caladium", "Cyclamen", "Amaryllis", "Clivia", "Desert Rose",
                     "Tree Houseleek", "Bunny Succulent", "Purple Shamrock"],
                    "Controleer eerst of de plant groeit of rust. Een lage bodemvochtwaarde is tijdens rust geen opdracht om water te geven; volg de soortspecifieke verzorging."),
    "Dendrobium Orchid": "Controleer eerst het Dendrobium-type en de groeifase; een koele, droge rust hoort alleen bij bepaalde typen.",
    **dict.fromkeys(["Venus Flytrap", "Pitcher Plant"],
                    "Gebruik mineraalarm water. Houd tijdens winterrust vochtig, maar doorgaans minder nat dan tijdens actieve groei; controleer de groeifase."),
}


def reviewed_guide(name: str, guide: dict[str, str]) -> dict[str, str]:
    """Apply named corrections and common issues found across the catalogue."""
    guide = {**guide, **CARE_OVERRIDES.get(name, {})}
    humidity = guide["humidity"]
    if any(word in humidity.casefold() for word in ("besproei", "benevel", "schaaltje")):
        guide["humidity"] = HUMIDITY_TROPICAL if any(
            word in humidity.casefold() for word in ("50", "60", "hoog", "tropisch")
        ) else HUMIDITY_NORMAL
    # A charcoal filter does not reliably remove dissolved minerals/fluoride.
    guide["watering"] = guide["watering"].replace(
        "regenwater of gefilterd water", "regenwater of omgekeerde-osmosewater"
    )
    # Common signs have several causes; they are not a diagnosis.
    guide["common_problems"] = guide["common_problems"].replace(" = ", " kan wijzen op ")
    guide["common_problems"] = guide["common_problems"].replace("bijna altijd", "vaak").replace("vrijwel altijd", "vaak")
    if "spiritus" in guide["common_problems"]:
        guide["common_problems"] = "Een zachte stam of veel bladval vraagt controle van water en temperatuur. Witte wollige plukjes kunnen wolluis zijn: isoleer de plant, verwijder zichtbare insecten en gebruik zo nodig een geschikt middel volgens het etiket."
    return guide
