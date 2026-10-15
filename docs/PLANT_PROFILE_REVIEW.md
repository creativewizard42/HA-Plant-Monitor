# Review van alle 203 plantenprofielen

Uitgevoerd op 15 oktober 2026 voor v0.9.4. Alle bestaande records zijn
nagelopen op de combinatie van naam, waterprofiel, verzorgingsadvies,
licht, temperatuur, luchtvochtigheid, rust en giftigheidsclaims. De tabel
hieronder bevat **alle 203 records**, ook synoniemen en cultuurvormen.

Dit is een inhoudelijke en technische controle van de catalogus. De live
pagina's van RHS, NC State en ASPCA waren vanuit deze omgeving geblokkeerd.
Daarom zijn de profielen niet alle 203 onafhankelijk aan actuele bronnen
geverifieerd. Het overzicht vermeldt startwaarden, geen gemeten ideale
waarden of overlevingsgrenzen. Controleer uitzonderlijke soorten/hybriden
op het exacte etiket. Bij onduidelijke giftigheid blijft de tekst voorzichtig.

## Belangrijkste correcties

- Kleine sansevieria naar droogtetolerant; zilveruitje, aloë en agave naar
  een passend droog profiel. String of Turtles, Hoya bella en Peperomia
  rotundifolia krijgen geen woestijnvetplantenprofiel.
- Licht vochtige, luchtige wortelkluiten hebben een eigen `moist_airy`
  categorie (25–60 als sensorstartwaarden), in plaats van dezelfde natte
  benadering als vochtminnende varens. Dit geldt onder meer voor Alocasia,
  Anthurium en bromelia's. Tankwater is niet meetbaar met een bodemprobe.
- Nepenthes heet Tropical Pitcher Plant en hoort niet bij moerasplanten.
  Papyrus, Sarracenia, Dionaea en Drosera capensis krijgen geen automatisch
  uitdroogadvies of gezondheidspuntenaftrek vanwege alleen natte grond.
  Tijdens winterrust kunnen ook moerasplanten minder nat nodig hebben.
- Strelitzia reginae krijgt een gewoon groeiseizoenprofiel en veel licht,
  met zon na gewenning; een donker noordraam is geen bloeiplaats.
- Kerstcactus (`Schlumbergera × buckleyi`) en Thanksgiving Cactus
  (`S. truncata`) worden onderscheiden. Een exacte actuele wetenschappelijke
  naam krijgt bij zoeken voorrang op een verouderde alias.
- De verkeerd benoemde Pearl Plant blijft dezelfde eerder opgenomen soort
  (Haworthia attenuata, nu Haworthiopsis attenuata) en heet Zebra Plant.
  Er wordt niet ongemerkt een andere soort, Tulista pumila, van gemaakt.
  Star Cactus heet Ornate Star Cactus bij de bestaande Astrophytum ornatum.
- Niet alle Dendrobium-soorten hebben een koude, droge winterrust. Het type
  moet eerst bekend zijn. Zantedeschia aethiopica krijgt niet automatisch
  na elke bloei de rustregels van gekleurde Calla-hybriden.
- Dagelijks sproeien is geen vervanging voor blijvend hogere
  luchtvochtigheid. Kleikorrels onder potgrond verbeteren drainage niet.
  Calathea rufibarba hoeft niet standaard boven 80% luchtvochtigheid.
- Geen universele gietbeurt van 200 ml. Adviezen houden rekening met groei
  en rust. Symptomen worden niet als zekere diagnose gepresenteerd.
- Euphorbia obesa en Caryota-vruchten worden niet meer als veilig aangeduid.
  Ficus, Agave en Asparagus krijgen ontbrekende waarschuwingen. Onvoldoende
  onderbouwde veiligheidclaims worden teruggezet naar onbekend. Huisdier-
  lijsten bewijzen geen veiligheid voor kinderen en voorspellen niet de
  ernst van een vergiftiging. Sago en hartglycosidehoudende planten krijgen
  een duidelijke waarschuwing voor ernstige vergiftiging.

## Bestaande installaties en sensoren

Alle 203 IDs en eerdere keuzenamen blijven behouden. Oude keuzenamen kunnen
als compatibiliteitsalias blijven bestaan; ze zijn geen botanische
synoniemenlijst. Eerder automatisch ingevulde verzorgingstekst wordt via
bewaarde hashes vernieuwd. Zelfgeschreven tekst en ingestelde drempels
worden behouden. Nieuwe planten krijgen de nieuwe vocht-, temperatuur- en
luchtvochtigheidsstartwaarden. Bekijk bij bestaande planten de drempels
via Configureren of de number-entiteiten als je die wilt overnemen.

Een vochtpercentage hangt af van sensor, grond, pot en meetdiepte. Kalibreer
vooral bij schors, veenmos en mineraalsubstraat. Een lage waarde tijdens
rust betekent niet automatisch water geven. Rust wordt niet automatisch
herkend; pas drempels aan of pauzeer meldingen. Lucky bamboo in water en
bromelia-kokers vragen aparte visuele controle. Dit systeem is geen
zelfstandige irrigatieregelaar.

Temperatuur- en luchtvochtigheidswaarden hieronder zijn meldingsdrempels,
niet een ideale constante omgeving. Sommige koele winterrustplaatsen zijn
bewust toegestaan. Hoge luchtvochtigheid vraagt ook ventilatie.

## Referenties om op exacte soort te controleren

Deze zijn aanbevolen vervolgreferenties; ze konden tijdens deze review
niet live geraadpleegd worden:

- RHS houseplant care: https://www.rhs.org.uk/plants/types/houseplants
- NC State Extension Plant Toolbox: https://plants.ces.ncsu.edu/
- ASPCA toxic/non-toxic plants: https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants
- American Orchid Society culture sheets: https://www.aos.org/orchid-care/care-sheets

## Alle records en nieuwe startwaarden

**37** records hebben een gewijzigd vochtprofiel of andere
vochtgrenzen. Alle records krijgen expliciete omgevingsstartwaarden.
De wijzigingskolom hieronder laat daarnaast de gewijzigde verzorgingssecties
zien; gedeelde voorzichtigere formuleringen kunnen meerdere records raken.

| Plant (actuele wetenschappelijke naam) | Profiel | Droog–nat % (oud → nieuw waar gewijzigd) | Koud–warm °C | Lucht laag % | Gewijzigde secties / foto |
| --- | --- | --- | --- | --- | --- |
| Jade Plant (Crassula ovata) | succulent | 10–40 | 10–32 | 20 | lucht, problemen, giftigheid |
| String of Pearls (Curio rowleyanus) | succulent | 10–40 | 10–32 | 20 | naam, lucht, giftigheid |
| String of Bananas (Curio radicans) | succulent | 10–40 | 10–32 | 20 | naam, lucht, giftigheid |
| String of Dolphins (Curio × peregrinus) | succulent | 10–40 | 10–32 | 20 | naam, lucht, problemen, giftigheid |
| String of Hearts (Ceropegia woodii) | succulent | 10–40 | 10–32 | 20 | lucht, giftigheid |
| String of Turtles (Peperomia prostrata) | standard | 10–40 → 15–55 | 15–30 | 40 | water, problemen, giftigheid |
| Burro's Tail (Sedum morganianum) | succulent | 10–40 | 10–32 | 20 | lucht, giftigheid |
| Panda Plant (Kalanchoe tomentosa) | succulent | 10–40 | 10–32 | 20 | lucht, giftigheid |
| Flaming Katy (Kalanchoe blossfeldiana) | succulent | 10–40 | 10–32 | 20 | lucht, giftigheid |
| Elephant Bush (Portulacaria afra) | succulent | 10–40 | 10–32 | 20 | problemen, giftigheid |
| Pencil Cactus (Euphorbia tirucalli) | succulent | 10–40 | 10–32 | 20 | giftigheid |
| African Milk Tree (Euphorbia trigona) | succulent | 10–40 | 10–32 | 20 | giftigheid |
| String of Buttons (Crassula perforata) | succulent | 10–40 | 10–32 | 20 | lucht, giftigheid |
| Donkey's Tail (Sedum morganianum) | succulent | 10–40 | 10–32 | 20 | lucht, giftigheid |
| Ghost Plant (Graptopetalum paraguayense) | succulent | 10–40 | 10–32 | 20 | problemen, giftigheid |
| Moonstones (Pachyphytum oviferum) | succulent | 10–40 | 10–32 | 20 | lucht, problemen, giftigheid |
| Hens and Chicks (Sempervivum tectorum) | succulent | 10–40 | 0–35 | 20 | problemen, giftigheid |
| Zebra Haworthia (Haworthiopsis fasciata) | succulent | 10–40 | 10–32 | 20 | naam, problemen, giftigheid |
| Haworthia (Zebra Plant) (Haworthiopsis attenuata) | succulent | 10–40 | 10–32 | 20 | naam, licht, problemen, giftigheid |
| Ox Tongue Plant (Gasteria bicolor) | succulent | 10–40 | 10–32 | 20 | giftigheid |
| Desert Rose (Adenium obesum) | succulent | 10–40 | 10–32 | 20 | giftigheid |
| Golden Barrel Cactus (Echinocactus grusonii) | desert_cactus | 5–30 | 5–35 | 20 | problemen, giftigheid |
| Prickly Pear Cactus (Opuntia microdasys) | desert_cactus | 5–30 | 5–35 | 20 | problemen, giftigheid |
| Pincushion Cactus (Mammillaria spp.) | desert_cactus | 5–30 | 5–35 | 20 | giftigheid |
| Old Lady Cactus (Mammillaria hahniana) | desert_cactus | 5–30 | 5–35 | 20 | problemen, giftigheid |
| Ornate Star Cactus (Astrophytum ornatum) | desert_cactus | 5–30 | 5–35 | 20 | naam, problemen, giftigheid |
| Goat's Horn Cactus (Astrophytum capricorne) | desert_cactus | 5–30 | 5–35 | 20 | giftigheid |
| Peanut Cactus (Echinopsis chamaecereus) | desert_cactus | 5–30 | 5–35 | 20 | problemen, giftigheid |
| Torch Cactus (Echinopsis spachiana) | desert_cactus | 5–30 | 5–35 | 20 | giftigheid |
| Fishhook Barrel Cactus (Ferocactus wislizeni) | desert_cactus | 5–30 | 5–35 | 20 | problemen, giftigheid |
| Snake Plant (Dracaena trifasciata) | drought_tolerant | 12–50 | 10–32 | 30 | licht, giftigheid, gegenereerde foto |
| Cylindrical Snake Plant (Dracaena angolensis) | drought_tolerant | 12–50 | 10–32 | 30 | naam, problemen, giftigheid |
| ZZ Plant (Zamioculcas zamiifolia) | drought_tolerant | 12–50 | 10–32 | 30 | problemen, giftigheid, gegenereerde foto |
| Ponytail Palm (Beaucarnea recurvata) | drought_tolerant | 12–50 | 10–32 | 30 | giftigheid |
| Yucca Cane (Yucca elephantipes) | drought_tolerant | 12–50 | 10–32 | 30 | giftigheid |
| Sago Palm (Cycas revoluta) | drought_tolerant | 12–50 | 10–32 | 30 | giftigheid |
| Cast Iron Plant (Aspidistra elatior) | drought_tolerant | 12–50 | 7–30 | 30 | licht, giftigheid |
| Aloe Vera (Aloe vera) | succulent | 12–50 → 10–40 | 10–32 | 20 | problemen, giftigheid |
| Lace Aloe (Aristaloe aristata) | succulent | 12–50 → 10–40 | 10–32 | 20 | problemen, giftigheid |
| Agave (Agave americana) | succulent | 12–50 → 10–40 | 10–32 | 20 | giftigheid |
| Monstera (Monstera deliciosa) | standard | 15–55 | 15–30 | 40 | lucht, voeding, giftigheid, gegenereerde foto |
| Swiss Cheese Vine (Monstera adansonii) | standard | 15–55 | 15–30 | 40 | lucht, problemen, giftigheid |
| Mini Monstera (Rhaphidophora tetrasperma) | standard | 15–55 | 15–30 | 40 | giftigheid |
| Golden Pothos (Epipremnum aureum) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid, gegenereerde foto |
| Marble Queen Pothos (Epipremnum aureum 'Marble Queen') | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Satin Pothos (Scindapsus pictus) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Heartleaf Philodendron (Philodendron hederaceum) | standard | 15–55 | 15–30 | 40 | water, lucht, problemen, giftigheid |
| Split-Leaf Philodendron (Thaumatophyllum bipinnatifidum) | standard | 15–55 | 15–30 | 40 | naam, problemen, giftigheid |
| Philodendron Birkin (Philodendron 'Birkin') | standard | 15–55 | 15–30 | 40 | giftigheid |
| Pink Princess Philodendron (Philodendron erubescens 'Pink Princess') | standard | 15–55 | 15–30 | 40 | giftigheid |
| Philodendron Xanadu (Thaumatophyllum xanadu) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Arrowhead Plant (Syngonium podophyllum) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Dragon Tree (Dracaena marginata) | standard | 15–55 | 15–30 | 40 | giftigheid |
| Corn Plant (Dracaena fragrans) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Song of India (Dracaena reflexa) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Rubber Plant (Ficus elastica) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Fiddle Leaf Fig (Ficus lyrata) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Weeping Fig (Ficus benjamina) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Audrey Ficus (Ficus benghalensis) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Umbrella Tree (Schefflera arboricola) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Baby Rubber Plant (Peperomia obtusifolia) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Emerald Ripple Peperomia (Peperomia caperata) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Watermelon Peperomia (Peperomia argyreia) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Wax Plant (Hoya carnosa) | standard | 15–55 | 15–30 | 40 | giftigheid |
| Sweetheart Hoya (Hoya kerrii) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Spider Plant (Chlorophytum comosum) | standard | 15–55 | 15–30 | 40 | giftigheid |
| Wandering Jew (Tradescantia zebrina) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Inch Plant (Tradescantia fluminensis) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Chinese Money Plant (Pilea peperomioides) | standard | 15–55 | 15–30 | 40 | lucht, giftigheid, gegenereerde foto |
| Aluminum Plant (Pilea cadierei) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Chinese Evergreen (Aglaonema commutatum) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Croton (Codiaeum variegatum) | moist_airy | 15–55 → 25–60 | 15–30 | 50 | problemen, giftigheid |
| Ti Plant (Cordyline fruticosa) | moist_airy | 15–55 → 25–60 | 15–30 | 50 | problemen, giftigheid |
| English Ivy (Hedera helix) | standard | 15–55 | 7–24 | 40 | giftigheid |
| Swedish Ivy (Plectranthus verticillatus) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Fatsia (Fatsia japonica) | standard | 15–55 | 7–24 | 40 | problemen, giftigheid |
| Kentia Palm (Howea forsteriana) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Parlor Palm (Chamaedorea elegans) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Areca Palm (Dypsis lutescens) | moist_airy | 15–55 → 25–60 | 15–30 | 50 | problemen, giftigheid |
| Lady Palm (Rhapis excelsa) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Bamboo Palm (Chamaedorea seifrizii) | moist_airy | 15–55 → 25–60 | 15–30 | 50 | problemen, giftigheid |
| Poinsettia (Euphorbia pulcherrima) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Christmas Cactus (Schlumbergera × buckleyi) | standard | 15–55 | 15–30 | 40 | naam, problemen, giftigheid |
| Thanksgiving Cactus (Schlumbergera truncata) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Norfolk Island Pine (Araucaria heterophylla) | standard | 15–55 | 10–27 | 50 | problemen, giftigheid |
| Money Tree (Pachira aquatica) | standard | 15–55 | 15–30 | 40 | lucht, giftigheid |
| Ficus Ginseng (Bonsai) (Ficus microcarpa) | moist_airy | 15–55 → 25–60 | 15–30 | 50 | lucht, problemen, giftigheid |
| Polka Dot Begonia (Begonia maculata) | standard | 15–55 | 15–30 | 40 | lucht, problemen, giftigheid |
| Rex Begonia Vine (Cissus discolor) | moist_airy | 15–55 → 25–60 | 15–30 | 50 | problemen, giftigheid |
| Angel Wing Begonia (Begonia coccinea) | standard | 15–55 | 15–30 | 40 | lucht, problemen, giftigheid |
| Dumb Cane (Dieffenbachia seguine) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Silver Squill (Ledebouria socialis) | succulent | 15–55 → 10–40 | 10–32 | 20 | problemen, giftigheid |
| Coffee Plant (Coffea arabica) | moist_airy | 15–55 → 25–60 | 15–30 | 50 | lucht, problemen, giftigheid |
| Bird's Nest Sansevieria (Dracaena trifasciata 'Hahnii') | drought_tolerant | 15–55 → 12–50 | 10–32 | 30 | naam, problemen, giftigheid |
| Tropical Pitcher Plant (Nepenthes alata) | moist_airy | 40–80 → 25–60 | 15–32 | 50 | naam, water, lucht, voeding, problemen, giftigheid |
| Moth Orchid (Phalaenopsis spp.) | epiphytic | 15–45 | 15–30 | 50 | problemen, giftigheid |
| Dendrobium Orchid (Dendrobium spp.) | epiphytic | 15–45 | 15–30 | 50 | water, temperatuur, voeding, problemen, giftigheid |
| Cattleya Orchid (Cattleya spp.) | epiphytic | 15–45 | 15–30 | 50 | problemen, giftigheid |
| Oncidium Orchid (Oncidium spp.) | epiphytic | 15–45 | 15–30 | 50 | problemen, giftigheid |
| Staghorn Fern (Platycerium bifurcatum) | epiphytic | 15–45 | 15–30 | 50 | problemen, giftigheid |
| Peace Lily (Spathiphyllum wallisii) | moisture_loving | 30–70 | 15–30 | 50 | lucht, problemen, giftigheid, gegenereerde foto |
| Prayer Plant (Maranta leuconeura) | moisture_loving | 30–70 | 16–30 | 50 | problemen, giftigheid |
| Rattlesnake Plant (Calathea lancifolia) | moisture_loving | 30–70 | 16–30 | 50 | water, problemen, giftigheid |
| Peacock Plant (Calathea makoyana) | moisture_loving | 30–70 | 16–30 | 50 | problemen, giftigheid |
| Calathea Medallion (Calathea roseopicta) | moisture_loving | 30–70 | 16–30 | 50 | water, problemen, giftigheid |
| Calathea Orbifolia (Calathea orbifolia) | moisture_loving | 30–70 | 16–30 | 50 | water, lucht, problemen, giftigheid |
| Fishbone Prayer Plant (Ctenanthe burle-marxii) | moisture_loving | 30–70 | 16–30 | 50 | problemen, giftigheid |
| Never-Never Plant (Ctenanthe oppenheimiana) | moisture_loving | 30–70 | 16–30 | 50 | problemen, giftigheid |
| Nerve Plant (Fittonia albivenis) | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| African Mask Plant (Alocasia × amazonica) | moist_airy | 30–70 → 25–60 | 15–30 | 50 | naam, problemen, giftigheid |
| Elephant Ear (Colocasia esculenta) | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| Flamingo Flower (Anthurium andraeanum) | moist_airy | 30–70 → 25–60 | 15–30 | 50 | problemen, giftigheid |
| Rex Begonia (Begonia rex) | moist_airy | 30–70 → 25–60 | 15–30 | 50 | lucht, problemen, giftigheid |
| Boston Fern (Nephrolepis exaltata) | moisture_loving | 30–70 | 15–30 | 50 | lucht, problemen, giftigheid |
| Maidenhair Fern (Adiantum raddianum) | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| Bird's Nest Fern (Asplenium nidus) | moisture_loving | 30–70 | 15–30 | 50 | water, problemen, giftigheid, gegenereerde foto |
| Wijze Varen (Bird's Nest Fern) (Asplenium antiquum) | moisture_loving | 30–75 | 15–30 | 50 | water, lucht, voeding, giftigheid |
| Table Fern (Pteris cretica) | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| Baby's Tears (Soleirolia soleirolii) | moisture_loving | 30–70 | 7–24 | 40 | problemen, giftigheid |
| Spikemoss (Selaginella kraussiana) | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| African Violet (Saintpaulia ionantha) | moist_airy | 30–70 → 25–60 | 15–30 | 50 | lucht, problemen, giftigheid |
| Cape Primrose (Streptocarpus spp.) | moist_airy | 30–70 → 25–60 | 15–30 | 50 | problemen, giftigheid |
| Cyclamen (Cyclamen persicum) | moisture_loving | 30–70 | 7–24 | 40 | problemen, giftigheid |
| Primrose (Primula vulgaris) | moisture_loving | 30–70 | 7–24 | 40 | problemen, giftigheid |
| Caladium (Caladium bicolor) | moisture_loving | 30–70 | 16–32 | 50 | problemen, giftigheid |
| Guzmania Bromeliad (Guzmania lingulata) | moist_airy | 30–70 → 25–60 | 15–30 | 50 | voeding, problemen, giftigheid |
| Vriesea Bromeliad (Vriesea splendens) | moist_airy | 30–70 → 25–60 | 15–30 | 50 | voeding, problemen, giftigheid |
| Aechmea Bromeliad (Aechmea fasciata) | moist_airy | 30–70 → 25–60 | 15–30 | 50 | voeding, problemen, giftigheid |
| Azalea (potted) (Rhododendron simsii) | moisture_loving | 30–70 | 7–24 | 40 | problemen, giftigheid |
| Hydrangea (potted) (Hydrangea macrophylla) | moisture_loving | 30–70 | 5–27 | 40 | problemen, giftigheid |
| Bird of Paradise (Strelitzia reginae) | standard | 15–65 → 15–55 | 15–30 | 40 | licht, water, lucht, giftigheid, gegenereerde foto |
| Umbrella Papyrus (Cyperus alternifolius) | high_moisture | 40–80 → 40–100 | 10–32 | 40 | problemen, giftigheid |
| Venus Flytrap (Dionaea muscipula) | high_moisture | 40–80 → 40–100 | 0–35 | 30 | problemen, giftigheid |
| Pitcher Plant (Sarracenia spp.) | high_moisture | 40–80 → 40–100 | 0–35 | 30 | problemen, giftigheid |
| Sundew (Drosera capensis) | high_moisture | 40–80 → 40–100 | 10–32 | 40 | lucht, problemen, giftigheid |
| Calla Lily (potted) (Zantedeschia aethiopica) | high_moisture | 40–80 | 10–32 | 40 | water, verpotten, problemen, giftigheid |
| Sensitive Plant (Mimosa pudica) | moisture_loving | 40–80 → 30–70 | 15–30 | 50 | problemen, giftigheid |
| Mexican Snowball (Echeveria elegans) | succulent | 10–40 | 10–32 | 20 | lucht, problemen, giftigheid |
| Echeveria 'Perle von Nurnberg' (Echeveria 'Perle von Nurnberg') | succulent | 10–40 | 10–32 | 20 | problemen, giftigheid |
| Tree Houseleek (Aeonium arboreum) | succulent | 10–40 | 5–30 | 20 | problemen, giftigheid |
| Mother of Thousands (Kalanchoe daigremontiana) | succulent | 10–40 | 10–32 | 20 | problemen, giftigheid |
| Watch Chain Plant (Crassula muscosa) | succulent | 10–40 | 10–32 | 20 | problemen, giftigheid |
| Fairy Washboard (Haworthiopsis limifolia) | succulent | 10–40 | 10–32 | 20 | problemen, giftigheid |
| Baseball Plant (Euphorbia obesa) | succulent | 10–40 | 10–32 | 20 | problemen, giftigheid |
| Living Stones (Lithops spp.) | succulent | 10–40 | 10–32 | 20 | problemen, giftigheid |
| Jelly Bean Plant (Sedum rubrotinctum) | succulent | 10–40 | 10–32 | 20 | problemen, giftigheid |
| Starfish Flower (Stapelia grandiflora) | succulent | 10–40 | 10–32 | 20 | problemen, giftigheid |
| Hoya Bella (Hoya bella) | standard | 10–40 → 15–55 | 15–30 | 40 | water, problemen, giftigheid |
| Neon Pothos (Epipremnum aureum 'Neon') | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Cebu Blue Pothos (Epipremnum pinnatum) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Philodendron Prince of Orange (Philodendron 'Prince of Orange') | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Philodendron Congo (Philodendron 'Congo') | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Philodendron Brasil (Philodendron hederaceum 'Brasil') | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Alocasia Polly (Alocasia 'Amazonica Polly') | moist_airy | 30–70 → 25–60 | 15–30 | 50 | water, lucht, temperatuur, verpotten, problemen, giftigheid |
| Alocasia Black Velvet (Alocasia reginula) | moist_airy | 30–70 → 25–60 | 16–30 | 50 | problemen, giftigheid |
| Alocasia Zebrina (Alocasia zebrina) | moist_airy | 30–70 → 25–60 | 16–30 | 50 | problemen, giftigheid |
| Anthurium Clarinervium (Anthurium clarinervium) | moist_airy | 30–70 → 25–60 | 15–30 | 50 | problemen, giftigheid |
| Anthurium Crystallinum (Anthurium crystallinum) | moist_airy | 30–70 → 25–60 | 15–30 | 50 | problemen, giftigheid |
| Calathea White Fusion (Calathea lietzei 'White Fusion') | moisture_loving | 30–70 | 16–30 | 50 | water, problemen, giftigheid |
| Raindrop Peperomia (Peperomia polybotrya) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Cupid Peperomia (Peperomia scandens) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Red Log Peperomia (Peperomia verticillata) | standard | 15–55 | 15–30 | 40 | water, problemen, giftigheid |
| Trailing Jade (Peperomia rotundifolia) | standard | 10–40 → 15–55 | 15–30 | 40 | water, problemen, giftigheid |
| Zebra Plant (Aphelandra squarrosa) | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| Polka Dot Plant (Hypoestes phyllostachya) | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| Purple Heart (Tradescantia pallida) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Turtle Vine (Callisia repens) | standard | 15–55 | 15–30 | 40 | giftigheid |
| Red Aglaonema (Aglaonema 'Red Valentine') | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Lemon Lime Dracaena (Dracaena 'Lemon Lime') | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Asparagus Fern (Asparagus setaceus) | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| Rabbit's Foot Fern (Davallia fejeensis) | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| Purple Shamrock (Oxalis triangularis) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Lucky Bamboo (Dracaena sanderiana) | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| Amaryllis (Hippeastrum spp.) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Clivia (Clivia miniata) | drought_tolerant | 12–50 | 10–30 | 40 | problemen, giftigheid |
| Rain Lily (Zephyranthes spp.) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Jasmine (Jasminum polyanthum) | moisture_loving | 30–70 | 8–30 | 50 | problemen, giftigheid |
| Gardenia (Gardenia jasminoides) | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| Chinese Hibiscus (Hibiscus rosa-sinensis) | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| Passion Flower (Passiflora caerulea) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Boat Lily (Tradescantia spathacea) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Peperomia Hope (Peperomia 'Hope') | standard | 15–55 | 15–30 | 40 | naam, water, problemen, giftigheid |
| Watermelon Begonia (Peperomia argyreia) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Silver Pothos (Scindapsus pictus 'Silvery Ann') | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Philodendron Micans (Philodendron hederaceum 'Micans') | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Peace Lily 'Domino' (Spathiphyllum 'Domino') | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| Dwarf Umbrella Tree (Schefflera arboricola 'Compacta') | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| Ponytail Palm (dwarf) (Beaucarnea recurvata 'Nolina') | drought_tolerant | 12–50 | 10–32 | 30 | problemen, giftigheid |
| Bunny Ear Cactus (Opuntia microdasys 'Albata') | desert_cactus | 5–30 | 5–35 | 20 | problemen, giftigheid |
| Christmas Kalanchoe (Kalanchoe blossfeldiana 'Calandiva') | succulent | 10–40 | 10–32 | 20 | lucht, giftigheid |
| Bunny Succulent (Monilaria obconica) | succulent | 10–40 | 5–28 | 20 | problemen, giftigheid |
| Banana Plant (Musa spp.) | moisture_loving | 30–70 | 12–35 | 50 | problemen, giftigheid |
| Canary Island Date Palm (Phoenix canariensis) | standard | 15–55 | 5–35 | 30 | problemen, giftigheid |
| Pygmy Date Palm (Phoenix roebelenii) | standard | 15–55 | 15–30 | 40 | problemen, giftigheid |
| European Fan Palm (Chamaerops humilis) | drought_tolerant | 12–50 | 0–35 | 30 | problemen, giftigheid |
| Room Lime (Sparrmannia africana) | moisture_loving | 30–70 | 7–24 | 40 | problemen, giftigheid |
| Rose Grape (Medinilla magnifica) | moisture_loving | 30–70 | 15–30 | 50 | problemen, giftigheid |
| Fishtail Palm (Caryota mitis) | moist_airy | 15–55 → 25–60 | 15–30 | 50 | problemen, giftigheid |
| Lemon Tree (potted) (Citrus limon) | standard | 15–55 | 5–35 | 40 | problemen, giftigheid |
| Orchid Cactus (Epiphyllum spp.) | epiphytic | 15–45 | 15–30 | 50 | problemen, giftigheid |
| Kris Plant (Alocasia sanderiana) | moist_airy | 30–70 → 25–60 | 16–30 | 50 | problemen, giftigheid |
| Calathea Rufibarba (Calathea rufibarba) | moisture_loving | 30–70 | 16–30 | 50 | water, lucht, voeding, verpotten, giftigheid |
| Blue Star Fern (Phlebodium aureum) | moisture_loving | 30–70 | 15–30 | 50 | water, lucht, problemen, giftigheid |
