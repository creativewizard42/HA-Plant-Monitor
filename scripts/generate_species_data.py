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
    "desert_cactus": (5, 30, "True desert cactus: water rarely and deeply, then let it dry out completely. Bright, direct sun."),
    "succulent": (10, 40, "Succulent: let the soil dry out almost completely between waterings. Bright light."),
    "drought_tolerant": (12, 50, "Very forgiving: let the soil dry out well between waterings. Tolerates low light."),
    "standard": (15, 55, "Let the top layer of soil dry before watering again. Bright, indirect light."),
    "epiphytic": (15, 45, "Grown in bark/orchid mix, which holds little water: water thoroughly, then let it dry out. Never let roots sit in water."),
    "moisture_loving": (30, 70, "Keep the soil consistently and evenly moist - don't let it fully dry out. Likes higher humidity."),
    "high_moisture": (40, 80, "Keep the soil consistently wet. Likes high humidity and, for several of these, distilled/rain water."),
}

# (display_name, scientific_name, profile, extra_note)
# extra_note is appended to the profile's generic note as a short species-specific tip.
PLANTS = [
    # --- Succulents ---
    ("Jade Plant", "Crassula ovata", "succulent", "Woody stems; propagates easily from leaf cuttings."),
    ("String of Pearls", "Senecio rowleyanus", "succulent", "Trailing; best in a hanging pot."),
    ("String of Bananas", "Senecio radicans", "succulent", "Trailing; similar care to String of Pearls."),
    ("String of Dolphins", "Senecio peregrinus", "succulent", "Trailing; distinctive dolphin-shaped leaves."),
    ("String of Hearts", "Ceropegia woodii", "succulent", "Trailing; tolerates neglect well."),
    ("String of Turtles", "Peperomia prostrata", "succulent", "Trailing; small patterned leaves."),
    ("Burro's Tail", "Sedum morganianum", "succulent", "Trailing; leaves drop easily when handled."),
    ("Panda Plant", "Kalanchoe tomentosa", "succulent", "Fuzzy, silver-green leaves."),
    ("Flaming Katy", "Kalanchoe blossfeldiana", "succulent", "Flowering succulent; needs a dark-rest period to rebloom."),
    ("Elephant Bush", "Portulacaria afra", "succulent", "Bonsai-friendly; sometimes confused with jade plant."),
    ("Pencil Cactus", "Euphorbia tirucalli", "succulent", "Sap is irritating to skin/eyes - handle with care."),
    ("African Milk Tree", "Euphorbia trigona", "succulent", "Sap is irritating - handle with care."),
    ("String of Buttons", "Crassula perforata", "succulent", "Stacked triangular leaves."),
    ("Donkey's Tail", "Sedum morganianum", "succulent", "Same plant as Burro's Tail (regional name)."),
    ("Ghost Plant", "Graptopetalum paraguayense", "succulent", "Pale, dusty-pink rosettes."),
    ("Moonstones", "Pachyphytum oviferum", "succulent", "Plump, egg-shaped leaves."),
    ("Hens and Chicks", "Sempervivum tectorum", "succulent", "Cold-hardy; produces small offset 'chicks'."),
    ("Zebra Haworthia", "Haworthia fasciata", "succulent", "Tolerates lower light better than most succulents."),
    ("Haworthia (Pearl Plant)", "Haworthia attenuata", "succulent", "Small, easy, slow-growing."),
    ("Ox Tongue Plant", "Gasteria bicolor", "succulent", "Tolerates lower light; slow-growing."),
    ("Desert Rose", "Adenium obesum", "succulent", "Swollen caudex; needs bright light and warmth to flower."),

    # --- Desert cacti ---
    ("Golden Barrel Cactus", "Echinocactus grusonii", "desert_cactus", "Slow-growing; needs excellent drainage."),
    ("Prickly Pear Cactus", "Opuntia microdasys", "desert_cactus", "Fine spines (glochids) irritate skin - handle carefully."),
    ("Pincushion Cactus", "Mammillaria spp.", "desert_cactus", "Compact; flowers in a ring around the top."),
    ("Old Lady Cactus", "Mammillaria hahniana", "desert_cactus", "Covered in fine white hairs."),
    ("Star Cactus", "Astrophytum ornatum", "desert_cactus", "Slow-growing, star-shaped ribs."),
    ("Goat's Horn Cactus", "Astrophytum capricorne", "desert_cactus", "Curved spines resembling horns."),
    ("Peanut Cactus", "Echinopsis chamaecereus", "desert_cactus", "Clumping; easy bloomer."),
    ("Torch Cactus", "Echinopsis spachiana", "desert_cactus", "Fast-growing columnar cactus."),
    ("Fishhook Barrel Cactus", "Ferocactus wislizeni", "desert_cactus", "Hooked spines - handle with care."),

    # --- Drought tolerant ---
    ("Snake Plant", "Dracaena trifasciata", "drought_tolerant", "Very forgiving; tolerates low light. Also known as Sansevieria."),
    ("Cylindrical Snake Plant", "Dracaena cylindrica", "drought_tolerant", "Rounded, spear-like leaves."),
    ("ZZ Plant", "Zamioculcas zamiifolia", "drought_tolerant", "Glossy leaves; thrives on neglect and low light."),
    ("Ponytail Palm", "Beaucarnea recurvata", "drought_tolerant", "Not a true palm; swollen base stores water."),
    ("Yucca Cane", "Yucca elephantipes", "drought_tolerant", "Sword-like leaves; sharp tips - place away from foot traffic."),
    ("Sago Palm", "Cycas revoluta", "drought_tolerant", "Very slow-growing; toxic to pets if ingested."),
    ("Cast Iron Plant", "Aspidistra elatior", "drought_tolerant", "Extremely tolerant of low light and neglect."),
    ("Aloe Vera", "Aloe vera", "drought_tolerant", "Gel from leaves is used for minor skin soothing; needs bright light."),
    ("Lace Aloe", "Aristaloe aristata", "drought_tolerant", "Compact rosette; tolerates some shade."),
    ("Agave", "Agave americana", "drought_tolerant", "Sharp leaf tips; best in a bright spot, e.g. near a sunny window."),

    # --- Standard tropical foliage (the largest group) ---
    ("Monstera", "Monstera deliciosa", "standard", "Split leaves develop with age and more light."),
    ("Swiss Cheese Vine", "Monstera adansonii", "standard", "Smaller, more vining relative of Monstera deliciosa."),
    ("Mini Monstera", "Rhaphidophora tetrasperma", "standard", "Not a true Monstera; climbs well on a pole."),
    ("Golden Pothos", "Epipremnum aureum", "standard", "Very forgiving; trails or climbs."),
    ("Marble Queen Pothos", "Epipremnum aureum 'Marble Queen'", "standard", "Needs bright light to keep its white variegation."),
    ("Satin Pothos", "Scindapsus pictus", "standard", "Silvery, quilted leaf texture."),
    ("Heartleaf Philodendron", "Philodendron hederaceum", "standard", "Fast-growing trailing vine, very forgiving."),
    ("Split-Leaf Philodendron", "Philodendron bipinnatifidum", "standard", "Large, deeply lobed leaves; needs space."),
    ("Philodendron Birkin", "Philodendron 'Birkin'", "standard", "Cream pinstripes on dark green leaves."),
    ("Pink Princess Philodendron", "Philodendron erubescens 'Pink Princess'", "standard", "Needs bright light for pink variegation to develop."),
    ("Philodendron Xanadu", "Thaumatophyllum xanadu", "standard", "Compact, non-climbing, deeply lobed leaves."),
    ("Arrowhead Plant", "Syngonium podophyllum", "standard", "Leaf shape changes as the plant matures."),
    ("Dragon Tree", "Dracaena marginata", "standard", "Thin, arching leaves; tolerates some neglect."),
    ("Corn Plant", "Dracaena fragrans", "standard", "Named for its corn-stalk-like leaves."),
    ("Song of India", "Dracaena reflexa", "standard", "Yellow-and-green striped leaves."),
    ("Rubber Plant", "Ficus elastica", "standard", "Glossy, thick leaves; wipe dust off occasionally."),
    ("Fiddle Leaf Fig", "Ficus lyrata", "standard", "Dislikes being moved; sensitive to sudden light/water changes."),
    ("Weeping Fig", "Ficus benjamina", "standard", "Drops leaves after big changes in light or location."),
    ("Audrey Ficus", "Ficus benghalensis", "standard", "Broad, fuzzy-edged leaves."),
    ("Umbrella Tree", "Schefflera arboricola", "standard", "Glossy, hand-shaped leaflets."),
    ("Baby Rubber Plant", "Peperomia obtusifolia", "standard", "Thick, succulent-like leaves; compact grower."),
    ("Emerald Ripple Peperomia", "Peperomia caperata", "standard", "Deeply textured, heart-shaped leaves."),
    ("Watermelon Peperomia", "Peperomia argyreia", "standard", "Striped leaves resemble a watermelon rind."),
    ("Wax Plant", "Hoya carnosa", "standard", "Waxy leaves, fragrant flower clusters; likes to be slightly pot-bound."),
    ("Sweetheart Hoya", "Hoya kerrii", "standard", "Heart-shaped leaves; extremely slow growing."),
    ("Spider Plant", "Chlorophytum comosum", "standard", "Produces baby plantlets on long runners."),
    ("Wandering Jew", "Tradescantia zebrina", "standard", "Striped purple-and-silver leaves; trails well."),
    ("Inch Plant", "Tradescantia fluminensis", "standard", "Fast-growing, easy to propagate from cuttings."),
    ("Chinese Money Plant", "Pilea peperomioides", "standard", "Round, coin-shaped leaves; produces easy-to-share pups."),
    ("Aluminum Plant", "Pilea cadierei", "standard", "Silver-splashed leaf pattern."),
    ("Chinese Evergreen", "Aglaonema commutatum", "standard", "Very tolerant of lower light."),
    ("Croton", "Codiaeum variegatum", "standard", "Needs bright light to keep its bold leaf colours."),
    ("Ti Plant", "Cordyline fruticosa", "standard", "Colourful, sword-shaped leaves."),
    ("English Ivy", "Hedera helix", "standard", "Trailing vine; prefers cooler rooms."),
    ("Swedish Ivy", "Plectranthus verticillatus", "standard", "Trailing; not a true ivy."),
    ("Fatsia", "Fatsia japonica", "standard", "Large, glossy, hand-shaped leaves."),
    ("Kentia Palm", "Howea forsteriana", "standard", "Elegant, low-maintenance palm; tolerates lower light."),
    ("Parlor Palm", "Chamaedorea elegans", "standard", "Compact palm, good for smaller rooms."),
    ("Areca Palm", "Dypsis lutescens", "standard", "Feathery fronds; likes higher humidity."),
    ("Lady Palm", "Rhapis excelsa", "standard", "Slow-growing, tolerant of lower light."),
    ("Bamboo Palm", "Chamaedorea seifrizii", "standard", "Clumping palm; tolerates lower light."),
    ("Poinsettia", "Euphorbia pulcherrima", "standard", "Holiday plant; sap can irritate skin."),
    ("Christmas Cactus", "Schlumbergera truncata", "standard", "A rainforest cactus, not a desert one - wants more moisture than typical cacti."),
    ("Thanksgiving Cactus", "Schlumbergera truncata", "standard", "Very similar care to Christmas Cactus."),
    ("Norfolk Island Pine", "Araucaria heterophylla", "standard", "Soft, conifer-like foliage; likes bright light and humidity."),
    ("Money Tree", "Pachira aquatica", "standard", "Often sold with braided trunks; tolerates a range of light."),
    ("Ficus Ginseng (Bonsai)", "Ficus microcarpa", "standard", "Popular indoor bonsai; thick, exposed roots."),
    ("Polka Dot Begonia", "Begonia maculata", "standard", "Silver-spotted leaves; avoid wetting the foliage."),
    ("Rex Begonia Vine", "Cissus discolor", "standard", "Not a true Begonia; velvety, patterned leaves."),
    ("Angel Wing Begonia", "Begonia coccinea", "standard", "Cane-like stems, clusters of flowers."),
    ("Dumb Cane", "Dieffenbachia seguine", "standard", "Sap is toxic if ingested - keep away from pets/children."),
    ("Silver Squill", "Ledebouria socialis", "standard", "Small bulbous plant with silver-mottled leaves."),
    ("Coffee Plant", "Coffea arabica", "standard", "Glossy leaves; may eventually flower and fruit indoors."),
    ("Bird's Nest Sansevieria", "Dracaena hahnii", "standard", "Compact rosette form of snake plant."),
    ("Rattlesnake Plant Vine", "Nepenthes alata (tropical pitcher)", "high_moisture", "Carnivorous - keep the soil constantly damp, ideally with distilled/rain water."),

    # --- Epiphytic / orchid-type ---
    ("Moth Orchid", "Phalaenopsis spp.", "epiphytic", "Grown in bark mix; water by soaking, then drain fully."),
    ("Dendrobium Orchid", "Dendrobium spp.", "epiphytic", "Needs a distinct drier rest period after flowering."),
    ("Cattleya Orchid", "Cattleya spp.", "epiphytic", "Needs bright light to reflower."),
    ("Oncidium Orchid", "Oncidium spp.", "epiphytic", "Dancing-lady flower sprays; likes bright, indirect light."),
    ("Staghorn Fern", "Platycerium bifurcatum", "epiphytic", "Often mounted rather than potted; mist or soak the mount."),

    # --- Moisture-loving ---
    ("Peace Lily", "Spathiphyllum wallisii", "moisture_loving", "Droops visibly when thirsty, recovers quickly after watering."),
    ("Prayer Plant", "Maranta leuconeura", "moisture_loving", "Leaves fold up at night."),
    ("Rattlesnake Plant", "Calathea lancifolia", "moisture_loving", "Wavy-edged leaves with dark markings."),
    ("Peacock Plant", "Calathea makoyana", "moisture_loving", "Strikingly patterned leaves; sensitive to tap-water minerals."),
    ("Calathea Medallion", "Calathea roseopicta", "moisture_loving", "Round, patterned leaves with purple undersides."),
    ("Calathea Orbifolia", "Calathea orbifolia", "moisture_loving", "Large, silvery-striped round leaves."),
    ("Fishbone Prayer Plant", "Ctenanthe burle-marxii", "moisture_loving", "Herringbone leaf pattern."),
    ("Never-Never Plant", "Ctenanthe oppenheimiana", "moisture_loving", "Variegated leaves with purple undersides."),
    ("Nerve Plant", "Fittonia albivenis", "moisture_loving", "Wilts dramatically when dry, but usually recovers after watering - best kept evenly moist to avoid the stress."),
    ("African Mask Plant", "Alocasia amazonica", "moisture_loving", "Dramatic arrow-shaped leaves; sensitive to both over- and under-watering."),
    ("Elephant Ear", "Colocasia esculenta", "moisture_loving", "Very large leaves; a heavy drinker in the growing season."),
    ("Flamingo Flower", "Anthurium andraeanum", "moisture_loving", "Glossy, waxy flower spathes; likes chunky, well-aerated mix."),
    ("Rex Begonia", "Begonia rex", "moisture_loving", "Striking leaf patterns; avoid wetting the foliage."),
    ("Boston Fern", "Nephrolepis exaltata", "moisture_loving", "Likes high humidity; browns at the tips if the air is too dry."),
    ("Maidenhair Fern", "Adiantum raddianum", "moisture_loving", "Delicate fronds; wilts quickly if allowed to dry out."),
    ("Bird's Nest Fern", "Asplenium nidus", "moisture_loving", "Rosette of broad, undivided fronds."),
    ("Wijze Varen (Bird's Nest Fern)", "Asplenium antiquum", "moisture_loving", "Rosette of broad, undivided fronds - a common cultivar sold under this Dutch name."),
    ("Table Fern", "Pteris cretica", "moisture_loving", "Compact fern, good for terrariums or humid bathrooms."),
    ("Baby's Tears", "Soleirolia soleirolii", "moisture_loving", "Tiny leaves, spreads into a moss-like mat."),
    ("Spikemoss", "Selaginella kraussiana", "moisture_loving", "Likes a humid, terrarium-like environment."),
    ("African Violet", "Saintpaulia ionantha", "moisture_loving", "Water from below to avoid wetting the fuzzy leaves."),
    ("Cape Primrose", "Streptocarpus spp.", "moisture_loving", "Similar care to African Violet."),
    ("Cyclamen", "Cyclamen persicum", "moisture_loving", "Goes dormant in summer - reduce watering then."),
    ("Primrose", "Primula vulgaris", "moisture_loving", "Often grown as a temporary flowering pot plant."),
    ("Caladium", "Caladium bicolor", "moisture_loving", "Grown from a tuber; goes dormant in winter."),
    ("Guzmania Bromeliad", "Guzmania lingulata", "moisture_loving", "Keep the central rosette 'cup' topped up with water too."),
    ("Vriesea Bromeliad", "Vriesea splendens", "moisture_loving", "Keep the central rosette 'cup' topped up with water too."),
    ("Aechmea Bromeliad", "Aechmea fasciata", "moisture_loving", "Keep the central rosette 'cup' topped up with water too."),
    ("Azalea (potted)", "Rhododendron simsii", "moisture_loving", "Prefers slightly acidic soil; avoid letting it dry out."),
    ("Hydrangea (potted)", "Hydrangea macrophylla", "moisture_loving", "Wilts fast when thirsty; a heavy drinker."),
    ("Paradijsvogel (Wijze Varen bundle name)", "Strelitzia reginae", "drought_tolerant", "Bird of Paradise - loves bright light; let the soil dry noticeably between waterings."),
    ("Bird of Paradise", "Strelitzia reginae", "drought_tolerant", "Loves bright light; let the soil dry noticeably between waterings."),

    # --- High moisture / carnivorous / bog plants ---
    ("Umbrella Papyrus", "Cyperus alternifolius", "high_moisture", "A bog plant - happy sitting in a shallow saucer of water."),
    ("Venus Flytrap", "Dionaea muscipula", "high_moisture", "Use distilled or rainwater only; never fertilise the soil."),
    ("Pitcher Plant", "Sarracenia spp.", "high_moisture", "Use distilled or rainwater only; needs lots of bright light."),
    ("Sundew", "Drosera capensis", "high_moisture", "Use distilled or rainwater only; keep the tray topped up."),
    ("Calla Lily (potted)", "Zantedeschia aethiopica", "high_moisture", "Likes consistently moist, almost boggy soil."),
    ("Sensitive Plant", "Mimosa pudica", "high_moisture", "Leaves fold up when touched; keep the soil consistently moist."),

    # --- More succulents ---
    ("Mexican Snowball", "Echeveria elegans", "succulent", "Rosette-forming; offsets easily."),
    ("Echeveria 'Perle von Nurnberg'", "Echeveria 'Perle von Nurnberg'", "succulent", "Dusty purple-pink rosette."),
    ("Tree Houseleek", "Aeonium arboreum", "succulent", "Rosettes on woody stems; sheds lower leaves naturally."),
    ("Mother of Thousands", "Kalanchoe daigremontiana", "succulent", "Produces tiny plantlets along leaf edges - can self-seed prolifically."),
    ("Watch Chain Plant", "Crassula muscosa", "succulent", "Tightly stacked, chain-like foliage."),
    ("Fairy Washboard", "Haworthiopsis limifolia", "succulent", "Ridged, dark green leaves."),
    ("Baseball Plant", "Euphorbia obesa", "succulent", "Round, spineless; sap can irritate skin."),
    ("Living Stones", "Lithops spp.", "succulent", "Water only when the old leaf pair has fully shrivelled - very easy to overwater."),
    ("Jelly Bean Plant", "Sedum rubrotinctum", "succulent", "Leaves blush red in bright light."),
    ("Starfish Flower", "Stapelia grandiflora", "succulent", "Star-shaped flowers with an unpleasant smell (attracts flies as pollinators)."),
    ("Hoya Bella", "Hoya bella", "succulent", "Compact, trailing; fragrant flower clusters."),

    # --- More standard tropical foliage ---
    ("Neon Pothos", "Epipremnum aureum 'Neon'", "standard", "Bright chartreuse leaves; needs good light to keep the colour."),
    ("Cebu Blue Pothos", "Epipremnum pinnatum", "standard", "Silvery-blue sheen on the leaves."),
    ("Philodendron Prince of Orange", "Philodendron 'Prince of Orange'", "standard", "New leaves emerge orange, maturing to green."),
    ("Philodendron Congo", "Philodendron 'Congo'", "standard", "Large, upright, non-climbing leaves."),
    ("Philodendron Brasil", "Philodendron hederaceum 'Brasil'", "standard", "Yellow-green striped variant of Heartleaf Philodendron."),
    ("Alocasia Polly", "Alocasia 'Amazonica Polly'", "moisture_loving", "Striking white-veined leaves; sensitive to both over- and under-watering."),
    ("Alocasia Black Velvet", "Alocasia reginula", "moisture_loving", "Dark, velvety leaves; keep humidity high."),
    ("Alocasia Zebrina", "Alocasia zebrina", "moisture_loving", "Distinctive striped leaf stems."),
    ("Anthurium Clarinervium", "Anthurium clarinervium", "moisture_loving", "Bold white venation on velvety leaves."),
    ("Anthurium Crystallinum", "Anthurium crystallinum", "moisture_loving", "Large velvety leaves with silvery veins."),
    ("Calathea White Fusion", "Calathea lietzei 'White Fusion'", "moisture_loving", "White-and-green marbled leaves; sensitive to tap-water minerals."),
    ("Raindrop Peperomia", "Peperomia polybotrya", "standard", "Round, glossy, raindrop-shaped leaves."),
    ("Cupid Peperomia", "Peperomia scandens", "standard", "Trailing, heart-shaped variegated leaves."),
    ("Red Log Peperomia", "Peperomia verticillata", "standard", "Small whorled leaves on reddish stems."),
    ("Trailing Jade", "Peperomia rotundifolia", "succulent", "Small round leaves on trailing stems."),
    ("Zebra Plant", "Aphelandra squarrosa", "moisture_loving", "Bold white-veined leaves; can be fussy about consistent moisture."),
    ("Polka Dot Plant", "Hypoestes phyllostachya", "moisture_loving", "Spotted leaves; tends to get leggy and benefits from pinching back."),
    ("Purple Heart", "Tradescantia pallida", "standard", "Vivid purple foliage; colours best in bright light."),
    ("Turtle Vine", "Callisia repens", "standard", "Small, fast-trailing, easy to propagate."),
    ("Red Aglaonema", "Aglaonema 'Red Valentine'", "standard", "Pink-and-green leaves; tolerant of average indoor light."),
    ("Lemon Lime Dracaena", "Dracaena 'Lemon Lime'", "standard", "Bright yellow-green striped leaves."),
    ("Asparagus Fern", "Asparagus setaceus", "moisture_loving", "Not a true fern; delicate, feathery foliage."),
    ("Rabbit's Foot Fern", "Davallia fejeensis", "moisture_loving", "Fuzzy rhizomes creep over the pot's edge."),
    ("Purple Shamrock", "Oxalis triangularis", "standard", "Leaves fold up at night; may go dormant periodically - reduce watering then."),
    ("Lucky Bamboo", "Dracaena sanderiana", "moisture_loving", "Often grown in water, but also does well in a moist, well-draining potting mix."),
    ("Amaryllis", "Hippeastrum spp.", "standard", "Grown from a bulb; reduce watering once it goes dormant after flowering."),
    ("Clivia", "Clivia miniata", "drought_tolerant", "Needs a cool, dry rest period in winter to flower well."),
    ("Rain Lily", "Zephyranthes spp.", "standard", "Small bulb; flowers a few days after a good watering."),
    ("Jasmine", "Jasminum polyanthum", "moisture_loving", "Fragrant; likes cooler nights and consistent moisture to flower."),
    ("Gardenia", "Gardenia jasminoides", "moisture_loving", "Fragrant flowers; prefers slightly acidic soil and consistent moisture."),
    ("Chinese Hibiscus", "Hibiscus rosa-sinensis", "moisture_loving", "Heavy drinker, especially while flowering."),
    ("Passion Flower", "Passiflora caerulea", "standard", "Vigorous climber; benefits from a trellis or support."),
    ("Boat Lily", "Tradescantia spathacea", "standard", "Purple-and-green boat-shaped leaf bracts."),
    ("Peperomia Hope", "Peperomia tetraphylla 'Hope'", "standard", "Trailing, small round leaves; easy grower."),
    ("Watermelon Begonia", "Peperomia argyreia", "standard", "Same plant as Watermelon Peperomia (alternate common name)."),
    ("Silver Pothos", "Scindapsus pictus 'Silvery Ann'", "standard", "Heavily silver-speckled leaves."),
    ("Philodendron Micans", "Philodendron hederaceum 'Micans'", "standard", "Velvety, iridescent bronze-green leaves."),
    ("Peace Lily 'Domino'", "Spathiphyllum 'Domino'", "moisture_loving", "Variegated white-splashed leaves; same care as regular Peace Lily."),
    ("Dwarf Umbrella Tree", "Schefflera arboricola 'Compacta'", "standard", "Compact cultivar of the Umbrella Tree."),
    ("Ponytail Palm (dwarf)", "Beaucarnea recurvata 'Nolina'", "drought_tolerant", "Compact form of the standard Ponytail Palm."),
    ("Bunny Ear Cactus", "Opuntia microdasys 'Albata'", "desert_cactus", "White-spined form of the Bunny Ear (Prickly Pear) Cactus."),
    ("Christmas Kalanchoe", "Kalanchoe blossfeldiana 'Calandiva'", "succulent", "Double-flowered form of Flaming Katy."),
    ("Bunny Succulent", "Monilaria obconica", "succulent", "Seasonal succulent resembling tiny rabbit ears when young."),

    # --- Added after reviewing Dutch garden-centre (Intratuin) assortments ---
    ("Banana Plant", "Musa spp.", "moisture_loving", "Large, dramatic leaves; a heavy drinker and feeder in the growing season."),
    ("Canary Island Date Palm", "Phoenix canariensis", "standard", "Large, arching feathery fronds; likes bright light."),
    ("Pygmy Date Palm", "Phoenix roebelenii", "standard", "Compact date palm, smaller than its Canary Island relative."),
    ("European Fan Palm", "Chamaerops humilis", "drought_tolerant", "Mediterranean palm; more drought-tolerant than most indoor palms."),
    ("Room Lime", "Sparrmannia africana", "moisture_loving", "A traditional Dutch houseplant with soft, fuzzy leaves; a thirsty grower."),
    ("Rose Grape", "Medinilla magnifica", "moisture_loving", "Dramatic pink flower clusters; likes high humidity and rainwater if possible."),
    ("Fishtail Palm", "Caryota mitis", "standard", "Distinctive ragged, fishtail-shaped leaflets."),
    ("Lemon Tree (potted)", "Citrus limon", "standard", "Needs as much bright, direct light as you can give it indoors; benefits from a summer outdoors."),
    ("Orchid Cactus", "Epiphyllum spp.", "epiphytic", "An epiphytic 'leaf cactus' - unlike desert cacti, don't let it dry out completely."),
    ("Kris Plant", "Alocasia sanderiana", "moisture_loving", "Wavy-edged, dark leaves with pale veins; sensitive to both over- and under-watering."),

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
    "Paradijsvogel (Wijze Varen bundle name)": (15.0, 65.0),
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
        care_tip = f"{generic_note} {extra_note}".strip()

        # Shown in the config flow's species picker: common name + the
        # formal Latin name together, e.g. "Snake Plant / Vrouwentong
        # (Dracaena trifasciata)" - directly answers "which plant is this?"
        # without needing to open the care-tip step first. Only the primary
        # Dutch name is shown here to keep the label readable; every
        # spelling variant still lives in `aliases` for matching.
        common_part = display_name if not dutch_names else f"{display_name} / {dutch_names[0]}"
        select_label = f"{common_part} ({scientific_name})"

        species.append(
            {
                "id": species_id,
                "display_name": display_name,
                "scientific_name": scientific_name,
                "dutch_names": dutch_names,
                "select_label": select_label,
                "aliases": aliases,
                "profile": profile,
                "dry_threshold": dry,
                "wet_threshold": wet,
                "care_tip": care_tip,
            }
        )
    return species


if __name__ == "__main__":
    plant_names = {p[0] for p in PLANTS}
    unknown_keys = set(DUTCH_NAMES) - plant_names
    if unknown_keys:
        raise SystemExit(f"DUTCH_NAMES has keys with no matching plant: {unknown_keys}")

    data = build()
    with_dutch = sum(1 for e in data if e["dutch_names"])
    print(f"Generated {len(data)} species entries ({with_dutch} with a distinct Dutch name).")
    out_path = os.path.join(
        os.path.dirname(__file__), "..", "custom_components", "plant_monitor", "species_data.json"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Written to {os.path.abspath(out_path)}")
