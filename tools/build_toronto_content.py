#!/usr/bin/env python3
"""Build the Toronto 2080 content and lore-district package.

The catalogue combines the official SR6 poster and 30 Nights campaign with
the substantial older Toronto material. Present-day Toronto neighbourhoods
only provide linework for the eight SR6 lore districts.
"""

from __future__ import annotations

import json
from pathlib import Path

from build_us_city_content import CityCatalogue, name_key, write_json


ROOT = Path(__file__).resolve().parents[1]
CITY_ID = "toronto-2080"
CITY_DIR = ROOT / "data" / CITY_ID


BOOKS = [
    {"id": "mercurial-sr1", "title": "Mercurial", "edition": "SR1"},
    {"id": "target-ucas-sr2", "title": "Target: UCAS", "edition": "SR2"},
    {"id": "underworld-sr2", "title": "Underworld Sourcebook / Unterwelt-Quellenbuch", "edition": "SR2"},
    {"id": "prime-runners-sr2", "title": "Prime Runners", "edition": "SR2"},
    {"id": "lone-star-sr2", "title": "Lone Star", "edition": "SR2"},
    {"id": "corporate-shadowfiles-sr2", "title": "Corporate Shadowfiles / Megakons", "edition": "SR2"},
    {"id": "super-tuesday-sr2", "title": "Super Tuesday", "edition": "SR2"},
    {
        "id": "portfolio-dragon-sr2",
        "title": "Portfolio of a Dragon / Portfolio eines Drachen",
        "edition": "SR2",
    },
    {
        "id": "sona-toronto-sr3",
        "title": "Nordamerika in den Schatten / Shadows of North America",
        "edition": "SR3",
    },
    {"id": "target-matrix-sr3", "title": "Target: Matrix / Brennpunkt Matrix", "edition": "SR3"},
    {
        "id": "dragons-sixth-world-sr3",
        "title": "Dragons of the Sixth World / Drachen der 6. Welt",
        "edition": "SR3",
    },
    {"id": "system-failure-sr3", "title": "System Failure / Systemausfall", "edition": "SR3"},
    {"id": "threats-2-sr3", "title": "Threats 2 / Bedrohliche 6. Welt", "edition": "SR3"},
    {"id": "sota-2064-sr3", "title": "State of the Art: 2064", "edition": "SR3"},
    {"id": "jet-set-sr4", "title": "Jet Set", "edition": "SR4"},
    {
        "id": "sixth-world-almanac-sr4",
        "title": "Sixth World Almanac / Almanach der Sechsten Welt",
        "edition": "SR4",
    },
    {"id": "emergence-sr4", "title": "Emergence / Emergenz", "edition": "SR4"},
    {"id": "artifacts-unbound-sr4", "title": "Artifacts Unbound", "edition": "SR4"},
    {"id": "srm04-07-sr4", "title": "SRM04-07: Burn", "edition": "SR4"},
    {"id": "srm04-12-sr4", "title": "SRM04-12: Showcase", "edition": "SR4"},
    {"id": "corporate-guide-sr4", "title": "Corporate Guide / Konzerndossier", "edition": "SR4"},
    {"id": "anarchy-sr5", "title": "Shadowrun: Anarchy", "edition": "SR5"},
    {
        "id": "toronto-poster-sr6",
        "title": "Toronto Poster 2080",
        "edition": "SR6",
    },
    {
        "id": "30-nights-sr6",
        "title": "30 Nächte und 3 Tage",
        "edition": "SR6",
    },
    {
        "id": "blackout-sr6",
        "title": "Blackout / Cutting Black",
        "edition": "SR6",
    },
    {"id": "schlagschatten-sr6", "title": "Schlagschatten / Slip Streams", "edition": "SR6"},
    {"id": "konzerngewalten-sr6", "title": "Konzerngewalten / Power Plays", "edition": "SR6"},
]


ANCHORS = {
    "Toronto": (43.6532, -79.3832),
    "Downtown/Alt-Toronto": (43.6534, -79.3830),
    "Toronto Islands": (43.6218, -79.3785),
    "East York": (43.6890, -79.3260),
    "Uptown": (43.7040, -79.4010),
    "West End": (43.6530, -79.4620),
    "Etobicoke": (43.6550, -79.5400),
    "North York": (43.7540, -79.4140),
    "Scarborough": (43.7580, -79.2480),
    "Cabbagetown": (43.6677, -79.3670),
    "Chinatown": (43.6530, -79.3980),
    "Harbourfront": (43.6400, -79.3650),
    "High Park": (43.6465, -79.4637),
    "Jane & Finch": (43.7560, -79.5160),
    "Markham": (43.8561, -79.3370),
    "Thornhill": (43.8130, -79.4240),
    "University of Toronto": (43.6629, -79.3957),
    "York University": (43.7735, -79.5019),
}


DISTRICTS = [
    (
        "Downtown/Alt-Toronto",
        "Downtown ist Torontos Finanz-, Verwaltungs-, Medien- und Unterhaltungszentrum. Cabbagetown, Chinatown, Little Italy, Hafenviertel, Krankenhausviertel und PATH verbinden Wohlstand, Konzernmacht und sichtbare Schatten.",
    ),
    (
        "Toronto Islands",
        "Die Inseln vor Downtown bilden Torontos Freizeitbezirk mit Centreville, Stränden, Bootsanlegern und Billy Bishop Airport; abgelegene Piers und Tunnel werden zugleich für Schmuggel genutzt.",
    ),
    (
        "East York",
        "East York ist ein stark von Einwanderung geprägter Teilraum mit The Beaches und Little India. Die Don Valley Toxic Zone, das Don-Gefängnis und industrielle Altlasten schaffen gefährliche Schattenkorridore.",
    ),
    (
        "Uptown",
        "Uptown ist eine geordnete Schlafstadt für Konzernangestellte. Moore Park und Casa Loma markieren die abgeschirmten Wohlstandsbereiche, in denen Diskretion mehr zählt als öffentliche Sichtbarkeit.",
    ),
    (
        "West End",
        "Das West End reicht vom gepflegten High Park über The Junction bis Bloor West. Wohlhabende Wohnlagen, Spezialgeschäfte und sozialer Abstieg liegen hier nur wenige Straßenzüge auseinander.",
    ),
    (
        "Etobicoke",
        "Etobicoke verbindet Industrie, Verkehr und Wohngebiete. Pearson Airport, Fabriken nahe Highway 427 und Gardiner Expressway sowie heruntergekommene nördliche Quartiere machen den Westen des Sprawls runrelevant.",
    ),
    (
        "North York",
        "North York ist ein eigener Sprawl im Sprawl: Willowdale, Downsview, York University, Yorkdale, Bathurst Manor und Hoggs Hollow stehen den Barrens von Jane & Finch und dem Triadengebiet Thornhill gegenüber.",
    ),
    (
        "Scarborough",
        "Scarborough ist der größte östliche Stadtteil und wichtigstes Einwanderungsziel. Seine Scarkologien, Agincourt, Markham, der Toronto Zoo und die Malvern Sports University prägen den Teilraum.",
    ),
]


# Number, name, scope, category, longitude/latitude, editorial summary.
POSTER_SPOTS = [
    (1, "Bloor West", "West End", "Stadtteile", [-79.4830, 43.6500], "Bloor West ist ein erschwinglicheres West-End-Viertel für Menschen, die um sozialen Aufstieg oder gegen den Abstieg kämpfen."),
    (2, "Cabbagetown", "Downtown/Alt-Toronto", "Stadtteile", [-79.3670, 43.6677], "Cabbagetown mischt Wohlhabende, SINlose, Kunstszene und Hochstapler auf ungewöhnlich engem Raum."),
    (3, "Casa Loma (Viertel)", "Uptown", "Stadtteile", [-79.4100, 43.6838], "Das Viertel Casa Loma ist eine abgeschirmte Wohlstandszone der Konzernelite rund um das historische Schloss."),
    (4, "Don Valley Toxic Zone", "East York", "Magie und Gefahren", [-79.3500, 43.6900], "Das verseuchte Don Valley ist eine toxische Zone mit belastetem Wasser, verzerrtem Mana und gefährlichen Rückzugsräumen."),
    (5, "Etobicoke", "Etobicoke", "Stadtteile", [-79.5400, 43.6550], "Etobicoke verbindet Verkehrsknoten, Konzernindustrie, wohlhabende Seeuferlagen und heruntergekommene nördliche Wohngebiete."),
    (6, "Golden Mile", "Scarborough", "Stadtteile", [-79.2850, 43.7200], "Golden Mile ist ein östlicher Gewerbe- und Industriekorridor im Scarborough-Teil des Sprawls."),
    (7, "Hafenviertel", "Downtown/Alt-Toronto", "Stadtteile", [-79.3540, 43.6410], "Wuxing modernisierte das Hafenviertel zu einem bedeutenden Warenumschlagplatz; Triaden und ein geheimes Dock ergänzen die legale Logistik."),
    (8, "High Park", "West End", "Freizeit und Natur", [-79.4637, 43.6465], "High Park ist gepflegter Freizeitpark, Wohnlage und kontrollierter Paracritter-Lebensraum im West End."),
    (9, "Jane & Finch", "North York", "Stadtteile", [-79.5160, 43.7560], "Jane & Finch ist Torontos größtes Barrensgebiet, in dem Gangs statt Polizei die Straßen kontrollieren."),
    (10, "Moore Park", "Uptown", "Stadtteile", [-79.3830, 43.6900], "Moore Park ist durch Bahntrasse, Friedhof und Schlucht abgeschirmt und dient der Elite als diskreter Rückzugsraum."),
    (11, "Scarborough", "Scarborough", "Stadtteile", [-79.2580, 43.7730], "Scarborough bildet den großen östlichen Einwanderungs- und Arkologienbezirk Torontos."),
    (12, "Taddle-Creek-Parkanlage", "Downtown/Alt-Toronto", "Freizeit und Natur", [-79.3920, 43.6660], "Die Taddle-Creek-Parkanlage schützt einen wichtigen Teil der städtischen Wasser- und Grüninfrastruktur."),
    (13, "The Junction", "West End", "Stadtteile", [-79.4700, 43.6650], "The Junction bietet günstigeren Wohnraum und spezialisierte kleine Geschäfte nördlich von High Park."),
    (14, "Thornhill", "North York", "Stadtteile", [-79.4240, 43.8130], "Thornhill steht unter der festen Kontrolle der Long-de-Shou- beziehungsweise Weißen-Lotos-Triade."),
    (15, "76 Coral Gable Drive", "North York", "Magie und Gefahren", [-79.5230, 43.7670], "Das Haus in der Coral Gable Drive ist ein zentraler Ermittlungs- und Ritualort der Kampagne."),
    (16, "Eglinton Avenue", "Uptown", "Straßen und Verkehr", [-79.4010, 43.7060], "Eglinton Avenue bildet einen wichtigen Ost-West-Korridor durch Uptown."),
    (17, "27 Lombard Street", "Downtown/Alt-Toronto", "Sonstige Spots", [-79.3750, 43.6520], "Die Adresse 27 Lombard Street ist ein ausdrücklich kartierter innerstädtischer Kampagnenort."),
    (18, "Yonge Street", "Toronto", "Straßen und Verkehr", [-79.4000, 43.7000], "Yonge Street ist Torontos zentrale Nord-Süd-Achse, Trennlinie zwischen Ost und West und dicht überwachter Handelsraum."),
    (19, "Billy Bishop Airport International", "Toronto Islands", "Verkehr", [-79.3962, 43.6285], "Billy Bishop Airport verbindet die Toronto Islands über Fähre und Tunnel mit Downtown."),
    (20, "Black Creek Pioneer Village", "North York", "Bildung und Kultur", [-79.5160, 43.7730], "Das Freilichtmuseum nahe York University eignet sich während des Blackouts als Zuflucht und Operationsbasis."),
    (21, "Brass Rail", "Downtown/Alt-Toronto", "Bars und Clubs", [-79.4110, 43.6650], "Das Brass Rail ist Bunrakusalon, Unterwelttreff und ein verlässlicher Ort für Drogen- und Schattenkontakte."),
    (22, "Campus der University of Toronto", "University of Toronto", "Bildung und Kultur", [-79.3957, 43.6629], "Die University of Toronto ist Eliteuniversität, medizinisches Zentrum und Schwerpunkt der metaplanaren Forschung."),
    (23, "Casa Loma (Museum)", "Uptown", "Bildung und Kultur", [-79.4094, 43.6780], "Casa Loma ist Museum, gesellschaftlicher Treffpunkt der Elite und während des Blackouts ein besonders gesicherter magischer Ort."),
    (24, "Dominion Public Building", "Downtown/Alt-Toronto", "Magie und Religion", [-79.3770, 43.6435], "Das Dom steht auf einer Kreuzung zweier Leylinien und zieht Geister, Astraltouristen, Gangs und geheime Akteure an."),
    (25, "Don-Gefängnis", "East York", "Sicherheit und Justiz", [-79.3540, 43.6677], "Das von Lone Star betriebene Don-Gefängnis weist während des Blackouts gefährliche Personal- und Sicherheitslücken auf."),
    (26, "Dorogoya Moya Bar", "Etobicoke", "Bars und Clubs", [-79.5500, 43.6200], "Die Dorogoya Moya Bar ist ein kartierter Treffpunkt im westlichen Toronto."),
    (27, "Dundas-Street-Enklave", "Downtown/Alt-Toronto", "Konzerne", [-79.3800, 43.6560], "Wuxings 68-stöckige Wohnenklave an der Dundas Street besitzt Helipad, Konzernsicherheit und kritische Forschungsbezüge."),
    (28, "Hospital for Sick Children", "Downtown/Alt-Toronto", "Medizin", [-79.3871, 43.6572], "SickKids gehört zum dicht konzentrierten und streng kontrollierten Krankenhausviertel."),
    (29, "Mackenzie-Arkologie", "Jane & Finch", "Arkologien", [-79.5100, 43.7600], "Die alternde Mackenzie-Arkologie sollte Jane & Finch erneuern, ist 2080 jedoch vernachlässigt und intern von konkurrierenden Gruppen zersplittert."),
    (30, "Mt. Sinai Hospital", "Downtown/Alt-Toronto", "Medizin", [-79.3900, 43.6576], "Mt. Sinai ist eines der renommierten Häuser des Torontoer Krankenhausviertels."),
    (31, "Nekropolis von Toronto", "Cabbagetown", "Magie und Religion", [-79.3610, 43.6670], "Die Nekropolis zieht Ghule, Geister und magische Experimente an und weist einen verstärkten Manafluss auf."),
    (32, "Netzkontrollzentrum", "Harbourfront", "Infrastruktur", [-79.3370, 43.6510], "Das zentrale Stromnetzkontrollzentrum auf dem früheren Hearn-Gelände ist der Schlüsselschauplatz für die Wiederherstellung der Energieversorgung."),
    (33, "Neverland Candy Shoppe", "Uptown", "Einkaufen", [-79.3990, 43.7100], "Neverland Candy Shoppe dient als Fassade und Versorgungspunkt im Umfeld der Long-de-Shou-Triade."),
    (34, "Osgoode Hall", "Downtown/Alt-Toronto", "Magie und Religion", [-79.3853, 43.6524], "Osgoode Hall ist Gerichtsgebäude und Schauplatz eines Rituals der Schwarzen Loge."),
    (35, "Pearson International Airport", "Etobicoke", "Verkehr", [-79.6248, 43.6777], "Pearson ist der wichtigste internationale Flughafen des Toronto-Sprawls."),
    (36, "Princess Margaret Hospital", "Downtown/Alt-Toronto", "Medizin", [-79.3900, 43.6580], "Princess Margaret gehört zum innerstädtischen Krankenhauscluster."),
    (37, "Queen Vic", "Downtown/Alt-Toronto", "Bars und Clubs", [-79.3800, 43.6550], "Das Queen Vic ist ein Treffpunkt und Jagdgebiet für Grid-Piraten während des Blackouts."),
    (38, "Sonata Data Processing Services", "Downtown/Alt-Toronto", "Konzerne", [-79.4100, 43.6450], "Sonata betreibt physisch gesicherte Datenspeicher, die während des Blackouts Ziel eines Coquillards-Runs werden."),
    (39, "Stadtbibliothek Toronto", "Downtown/Alt-Toronto", "Bildung und Kultur", [-79.3860, 43.6718], "Die Stadtbibliothek besitzt eine breite Sammlung einschließlich einzelner seltener arkaner Texte."),
    (40, "Tin Can", "East York", "Bars und Clubs", [-79.3200, 43.6600], "Das Tin Can ist ein kartierter Treffpunkt im östlichen Toronto."),
    (41, "Toronto General Hospital", "Downtown/Alt-Toronto", "Medizin", [-79.3870, 43.6580], "Toronto General ist ein großer Campus und spezialisiert auf Organtransplantationen."),
    (42, "Toronto Western Hospital", "Downtown/Alt-Toronto", "Medizin", [-79.4050, 43.6530], "Toronto Western liegt westlich des zentralen Krankenhausclusters."),
    (43, "Women’s College Hospital", "Downtown/Alt-Toronto", "Medizin", [-79.3870, 43.6610], "Women’s College Hospital ist Teil des eng konzentrierten medizinischen Zentrums."),
    (44, "York University", "North York", "Bildung und Kultur", [-79.5019, 43.7735], "York University besitzt eine starke thaumaturgische Fakultät und eine bedeutende Sammlung von Zauberformeln."),
]


MAP_30_NIGHTS = [
    (1, "CN Tower", "Downtown/Alt-Toronto", [-79.3871, 43.6426]),
    (2, "Cabbagetown", "Downtown/Alt-Toronto", [-79.3670, 43.6677]),
    (3, "Little Italy", "Downtown/Alt-Toronto", [-79.4166, 43.6550]),
    (4, "Chinatown", "Downtown/Alt-Toronto", [-79.3980, 43.6530]),
    (5, "Casa Loma (Museum)", "Uptown", [-79.4094, 43.6780]),
    (6, "Moore Park", "Uptown", [-79.3830, 43.6900]),
    (7, "University of Toronto / Krankenhausviertel", "Downtown/Alt-Toronto", [-79.3920, 43.6580]),
    (8, "Entertainment District", "Downtown/Alt-Toronto", [-79.3920, 43.6460]),
    (9, "Eaton Centre", "Downtown/Alt-Toronto", [-79.3802, 43.6544]),
    (10, "Honest Ed’s", "West End", [-79.4120, 43.6654]),
    (11, "Billy Bishop Airport International", "Toronto Islands", [-79.3962, 43.6285]),
    (12, "The Beaches", "East York", [-79.2977, 43.6685]),
    (13, "Little India", "East York", [-79.3220, 43.6720]),
    (14, "Don Valley Toxic Zone", "East York", [-79.3500, 43.6900]),
    (15, "High Park", "West End", [-79.4637, 43.6465]),
    (16, "Bloor West", "West End", [-79.4830, 43.6500]),
    (17, "The Junction", "West End", [-79.4700, 43.6650]),
    (18, "Pearson International Airport", "Etobicoke", [-79.6248, 43.6777]),
    (19, "York University", "North York", [-79.5019, 43.7735]),
    (20, "Jane & Finch", "North York", [-79.5160, 43.7560]),
    (21, "Willowdale", "North York", [-79.4000, 43.7700]),
    (22, "Downsview Airport", "North York", [-79.4700, 43.7450]),
    (23, "Hoggs Hollow", "North York", [-79.4050, 43.7420]),
    (24, "Bathurst Manor", "North York", [-79.4542, 43.7722]),
    (25, "Yorkdale Megaplex", "North York", [-79.4510, 43.7255]),
    (26, "Thornhill", "North York", [-79.4240, 43.8130]),
    (27, "Agincourt", "Scarborough", [-79.2720, 43.7930]),
    (28, "Markham", "Scarborough", [-79.3370, 43.8561]),
    (29, "Toronto Zoo", "Scarborough", [-79.1810, 43.8177]),
    (30, "Malvern Sports University", "Scarborough", [-79.2230, 43.8030]),
]


ADDITIONAL_PLACES = [
    ("Royal York Hotel", "Downtown/Alt-Toronto", "Hotels", [-79.3817, 43.6459], "Das historische Großhotel dient während der ersten Blackout-Nacht als mögliche Operationsbasis."),
    ("Atticus High School", "North York", "Bildung und Kultur", None, "Renrakus private Atticus High School wird zum Schauplatz des Kampfes um einen ungeplünderten Brotlaster."),
    ("Zephyrus-Kühllager", "Etobicoke", "Konzerne", None, "Das Kühllager nimmt während des Blackouts ungeklärte Todesfälle auf und wird von Camazotz’ Dienern heimgesucht."),
    ("The Triple", "High Park", "Konzerne", None, "The Triple ist der energieautarke Testlieferwagen, um den mehrere Grid-Piraten und Gangs konkurrieren."),
    ("Centreville-Freizeitpark", "Toronto Islands", "Freizeit und Natur", [-79.3710, 43.6205], "Centreville ist ein dauerhafter AR-Jahrmarkt und Zentrum des Freizeitbezirks auf den Inseln."),
    ("Ontario Place", "Toronto Islands", "Freizeit und Natur", [-79.4150, 43.6295], "Das stillgelegte Freizeitgelände ist von Squattern und einem Technomancer-Stamm besetzt."),
    ("Snake Island Schmugglerpier", "Toronto Islands", "Schmuggel und Schatten", [-79.3940, 43.6215], "Ein heruntergekommener markierter Pier vermittelt diskrete Bootsfahrten zu privaten Anlegern und Schmuggelrouten."),
    ("Tommy Thompson Park Schmuggeltunnel", "Toronto Islands", "Schmuggel und Schatten", [-79.3300, 43.6200], "Unter dem Tommy Thompson Park liegen in den Quellen erwähnte Schmuggelzugänge."),
    ("PATH", "Downtown/Alt-Toronto", "Infrastruktur", [-79.3820, 43.6500], "PATH ist ein über vierzig Kilometer langes unterirdisches Laden- und Passagennetz mit zunehmend gesetzlosen Randbereichen."),
    ("Ryerson University", "Downtown/Alt-Toronto", "Bildung und Kultur", [-79.3780, 43.6577], "Ryerson ist eine der drei führenden Hochschulen des Sprawls und bildet insbesondere Wirtschaftskräfte aus."),
    ("Massey Hall", "Downtown/Alt-Toronto", "Bildung und Kultur", [-79.3790, 43.6542], "Massey Hall ist ein historischer Konzertsaal im Theaterkorridor."),
    ("Toronto Stock Exchange", "Downtown/Alt-Toronto", "Konzerne", [-79.3800, 43.6460], "Die Börse ist ein bedeutender Finanz- und Matrixknoten und schon im SR3-Stadtstand Ziel von Datendiebstahl und Insiderhandel."),
    ("Toronto Data Haven / t.matrix", "Toronto", "Matrix und Metaplanes", None, "t.matrix ist Torontos wichtigster Datahaven und virtueller Treffpunkt mit Verbindungen zu anderen nordamerikanischen Schattenknoten."),
    ("Filmhaus", "Uptown", "Bildung und Kultur", None, "Das analog betriebene Kino ist Operationsbasis der Coquillards in einem von Saeder-Krupp kontrollierten Teilraum."),
    ("Senator Hotel", "Downtown/Alt-Toronto", "Hotels", [-79.3760, 43.6560], "Das eingeigelte Senator Hotel schützt prominente Gäste, kompromittierende Daten und einen schwer verletzten Decker."),
    ("CityTV am Dundas Square", "Downtown/Alt-Toronto", "Konzerne", [-79.3800, 43.6562], "Der Medienstandort am Dundas Square ist ein beobachteter Schauplatz während des Blackouts."),
    ("Silver Spoon Bar", "Jane & Finch", "Bars und Clubs", None, "Die ruppige Bar ist ausschließliches Territorium der Maulers."),
    ("Verlassenes Hafenhotel der Ancients", "Harbourfront", "Gangs", None, "Ein zum Abriss vorgesehenes Hafenhotel dient dem örtlichen Ancients-Chapter als Basis."),
    ("Bloodrippers-Lagerhaus", "Etobicoke", "Gangs", None, "Ein Lagerhaus dient den Bloodrippers als befestigte Operationsbasis."),
    ("Metro Food Services", "Toronto", "Einkaufen", None, "Die Supermarktkette wird während des Blackouts zum umkämpften Versorgungsnetz."),
    ("Fiesta Farms Market", "West End", "Einkaufen", [-79.4200, 43.6680], "Der unabhängige Markt ist Versorgungsort und Station eines korrumpierten Geistes."),
    ("Hockey Hall of Fame", "Downtown/Alt-Toronto", "Bildung und Kultur", [-79.3770, 43.6473], "Die Hockey Hall of Fame ist Kulturdenkmal, Geisterort und Schauplatz eines geplanten Anschlags."),
    ("Wendigo Pond", "High Park", "Magie und Gefahren", [-79.4670, 43.6570], "Der bewaldete Teich am Nordende von High Park ist ein alter Ritual- und Opferort."),
    ("Green Groves", "Etobicoke", "Magie und Religion", None, "Unter einem Lagerhaus verbirgt Green Groves ein magisches Gewächshaus und einen von Seoulpa-Soldaten geschützten Reagenzienhandel."),
    ("Moore’s on Danforth", "East York", "Bars und Clubs", [-79.3400, 43.6800], "Die traditionsreiche Musikbar ist erste Bühne für neue Künstler und ein Kampagnentreffpunkt."),
    ("True Sake Bar", "Downtown/Alt-Toronto", "Restaurants", [-79.3920, 43.6490], "Die kleine Sake-Bar an der Queen Street dient als diskreter Treffpunkt und Critter-Schauplatz."),
    ("The Feeding Block", "Downtown/Alt-Toronto", "Einkaufen", None, "Stillgelegte Foodtrucks bilden einen neuen Markt, der von zwei Gangs und einer brüchigen Polizeipräsenz geschützt wird."),
    ("Regent Park", "Downtown/Alt-Toronto", "Freizeit und Natur", [-79.3593, 43.6596], "Regent Park ist Torontos Straßenbasketballzentrum und eine demilitarisierte Zone zwischen Ganggebieten."),
    ("Queen’s Park", "Downtown/Alt-Toronto", "Freizeit und Natur", [-79.3925, 43.6643], "Queen’s Park wird während der metaplanaren Störungen zu einem Brennpunkt unberechenbarer Tore."),
    ("Crothers Woods", "East York", "Freizeit und Natur", [-79.3550, 43.6980], "In Crothers Woods wird eine Manifestation Kojotes durch die Schwarze Loge gefangen gehalten."),
    ("Altes Rathaus Toronto", "Downtown/Alt-Toronto", "Magie und Religion", [-79.3812, 43.6527], "Das Alte Rathaus besitzt durch seine konfliktreiche Geschichte eine hermetisch ausgerichtete Manablase."),
    ("Keg Mansion", "Downtown/Alt-Toronto", "Magie und Religion", [-79.3765, 43.6716], "Das frühere Wohnhaus und Restaurant weist eine schamanisch verzerrte Atmosphäre auf."),
    ("Ecke Yonge und St. Clair", "Uptown", "Magie und Religion", [-79.3940, 43.6880], "Ein historischer rassistischer Mordanschlag hinterließ an der Kreuzung eine Manablase."),
    ("Carrying-Place-Leylinie", "Toronto", "Magie und Religion", None, "Die alte Route zwischen Ontario- und Simcoe-See folgt einer starken schamanischen Leylinie durch den Sprawl."),
    ("Magic Beans", "Cabbagetown", "Einkaufen", None, "Penelope Beans Taliskrämerladen ist für seine ungewöhnlich breite, aber nicht immer verlässliche Reagenzienauswahl bekannt."),
    ("Massey Foundation", "Downtown/Alt-Toronto", "Magie und Religion", None, "Die Stiftung besitzt eine der besten Sammlungen zur regionalen Manageschichte."),
    ("Wuxing-Geheimdock", "Harbourfront", "Schmuggel und Schatten", None, "Wuxing und verbündete Triaden nutzen ein verborgenes Dock im modernisierten Hafenviertel."),
]


# Benannte Schauplätze aus den einzelnen Nächten, die weder Bestandteil der
# Posterlegende noch der 30-Nights-Übersichtskarte sind.
NIGHT_PLACES = [
    ("Villiers Island", "Harbourfront", "Stadtteile", [-79.3480, 43.6470], "Die künstlich entwickelte Hafeninsel gehört zum modernisierten East Bayfront und markiert einen wichtigen Übergang zwischen Downtown und Hafenindustrie."),
    ("East Bayfront", "Downtown/Alt-Toronto", "Stadtteile", [-79.3650, 43.6440], "East Bayfront ist ein Lagerhaus- und Hafenkorridor östlich von Downtown, in dem Gangs während des Blackouts vergleichsweise unauffällig operieren können."),
    ("St. Luke’s United", "Cabbagetown", "Magie und Religion", [-79.3710, 43.6610], "Die Kirche in Cabbagetown wird als mögliche Operations- und Versorgungszentrale einer Stadtteilgemeinschaft genannt."),
    ("Mount Pleasant Cemetery", "Uptown", "Freizeit und Natur", [-79.3860, 43.6960], "Der Friedhof bildet eine natürliche Grenze von Moore Park und liegt nahe wichtiger Triaden- und Kampagnenschauplätze."),
    ("Thornhill Commons", "Thornhill", "Einkaufen", None, "Thornhill Commons ist ein abgeschirmter Treff- und Handelskomplex im Kerngebiet der Long-de-Shou-Triade."),
    ("Xiao’s House of Gold", "Thornhill", "Restaurants", None, "Das traditionsbewusste Restaurant und die unterirdische Manufaktur dienen Großmutter Biyu als Empfangsort und wirtschaftliche Basis."),
    ("Yonge-Dundas-Memorial-Lagerkomplex", "Downtown/Alt-Toronto", "Schmuggel und Schatten", None, "Der manuell gesicherte Lagerkomplex bewahrt Waren und Informationen auf, ohne für den Zugang auf AR oder SIN-Prüfung angewiesen zu sein."),
    ("Run & Sollars", "Downtown/Alt-Toronto", "Dienstleistungen", None, "Run & Sollars ist ein Karten- und Vermessungsgeschäft, dessen analoges Fachwissen während des Blackouts besonders wertvoll wird."),
    ("Seven Sisters Legal", "Harbourfront", "Dienstleistungen", None, "Die juristische Korrespondenz-Kooperative arbeitet aus dem Hafenviertel und vermittelt diskrete Aufträge und Informationen."),
    ("CMC-Verteilzentrum", "Harbourfront", "Konzerne", None, "Das eingezäunte Verteilzentrum der Crystal Maize Cooperative umfasst Büro, Hochregallager und eigene magische Sicherung."),
    ("Taddle-Creek-Kläranlage", "Downtown/Alt-Toronto", "Infrastruktur", [-79.3920, 43.6660], "Der Backsteinkomplex in der Taddle-Creek-Parkanlage reinigt Wasser und wird zum magischen Operationsort im Kampf gegen Mezcallus Negh."),
    ("Nathan Phillips Square / The Cluster", "Downtown/Alt-Toronto", "Öffentliche Plätze", [-79.3834, 43.6525], "Nathan Phillips Square wird im Blackout als The Cluster zum öffentlichen Sammelpunkt, Protestort und Schauplatz politischer Gewalt."),
    ("Kensington Market", "Downtown/Alt-Toronto", "Einkaufen", [-79.4005, 43.6545], "Der Markt bleibt ein dichtes Handels- und Ausgehviertel, steht jedoch unter dem Einfluss der örtlichen Yakuza."),
    ("TTC-U-Bahnnetz", "Toronto", "Verkehr", [-79.3850, 43.6550], "Das U-Bahnnetz der Toronto Transit Commission wird im Blackout zu einem schwer kontrollierbaren unterirdischen Bewegungs- und Gefahrenraum."),
    ("Top o’ the Senator", "Downtown/Alt-Toronto", "Bars und Clubs", [-79.3761, 43.6561], "Die Bar auf dem Senator Hotel ist Treffpunkt von Prominenten, Konzernleuten und Schattenkontakten."),
    ("TTC-Schrottplatz / Wilson Bus Garage and Subway Yard", "North York", "Verkehr", [-79.4500, 43.7380], "Der aufgegebene Betriebshof für Busse und U-Bahnzüge dient als Versteck für funktionsfähige Fahrzeuge und als Gangschauplatz."),
    ("Old Yonge", "Downtown/Alt-Toronto", "Stadtteile", [-79.4000, 43.6600], "Old Yonge ist ein Arbeiterquartier aus Wohnungen und kleinen Läden an Markham Street und Yonge Street, durchsetzt von Syndikatsangehörigen."),
    ("Die Grube", "Downtown/Alt-Toronto", "Gangs", None, "Ein verlassenes Loft in Old Yonge dient mit Billigung der Mafia als Hundekampfarena."),
    ("The Purrfect Pet", "Downtown/Alt-Toronto", "Einkaufen", None, "Dr. Tilda Aurands Edel-Tierhandlung verbirgt ein Genlabor, in dem erwachte und gentechnisch veränderte Critter gezüchtet werden."),
    ("Evergreen-Ziegelei", "East York", "Bildung und Kultur", [-79.3650, 43.6840], "Die Evergreen Brick Works verbinden ökologische Lehre, grüne Technik und umweltbewusste Magie."),
    ("Union Station", "Downtown/Alt-Toronto", "Verkehr", [-79.3806, 43.6452], "Der modernisierte Hauptbahnhof wird zur strategischen Drehscheibe für Hilfslieferungen und zum umkämpften Gangterritorium."),
    ("St. Paul’s Basilica", "Cabbagetown", "Magie und Religion", [-79.3634, 43.6556], "Die Basilika ist ein wiederkehrender Aufenthalts- und Beobachtungsort im Umfeld der South Cabbage Warlordz."),
    ("Silverthorn", "West End", "Stadtteile", [-79.4760, 43.6890], "Silverthorn ist ein heruntergekommenes West-End-Viertel, dessen geschlossene Bibliothek mehreren magischen Gruppen als Ziel dient."),
    ("Silverthorn-Bibliothek", "West End", "Bildung und Kultur", None, "Die seit 2060 geschlossene Bibliothek wird im Blackout zum ungestörten Treffpunkt für toxische und gegnerische Erwachte."),
    ("Cross International Container Yards", "Etobicoke", "Konzerne", None, "Der Container- und Verwertungshof lagert nicht abgeholte oder beschlagnahmte Fracht und wird zum Ziel einer Extraktion."),
    ("Leuty Lifeguard Station", "The Beaches", "Sicherheit und Justiz", [-79.2950, 43.6690], "Die Rettungsschwimmerstation an The Beaches dient als verabredeter Übergabe- und Fluchtpunkt."),
    ("The People’s Bank", "Downtown/Alt-Toronto", "Finanzen", None, "Die Schattenbank tauscht Konzernwährungen und Vorschüsse diskret in beglaubigte Nuyen-Credsticks um."),
    ("Saeder-Krupp-Etobicoke-Komplex", "Etobicoke", "Konzerne", None, "Einer von zwei Torontoer Wohnkomplexen für S-K-Angestellte beherbergt vor allem Arbeiter und technische Fachkräfte."),
    ("Mervyn’s Pawn / Handelsposten", "Downtown/Alt-Toronto", "Einkaufen", None, "Das Pfandhaus bietet unauffällige Unterkunft, Handel und Informationsaustausch, ist aber durch die Schulden seines Besitzers kompromittiert."),
    ("ShinJin Electronics", "Golden Mile", "Einkaufen", [-79.2850, 43.7200], "Der Elektronikladen an der Golden Mile dient als Zugang zu belastenden Transaktionsdaten."),
    ("Gurdwara im nördlichen Großraum", "North York", "Magie und Religion", None, "Die von Greater Toronto Khalsa geschützte Gurdwara dient während des Blackouts als Zuflucht, Vorratslager und medizinische Hilfsstation."),
]


PEOPLE = [
    ("Ariel", "Technomancerin und Coquillards-Hackerin", "Coquillards", "Ariel ist die talentierteste Hackerin der Coquillards und verbirgt ihre Technomancer-Fähigkeiten.", "Filmhaus"),
    ("Dr. Tilda Aurand", "Genetikerin und entflohene Konzernforscherin", "Ares", "Die renommierte elfische Genetikerin kennt Ares’ geheime Critter- und Insektengeistforschung.", "True Sake Bar"),
    ("Freddy Bales", "Akademiker und Logenagent", "Schwarze Loge", "Bales tarnt seine Rolle in der Schwarzen Loge hinter einem angenehm unauffälligen Universitätsdasein.", "Campus der University of Toronto"),
    ("Großmutter Biyu", "Matriarchin der Long-de-Shou", "Long-de-Shou / Weißer Lotos", "Die uralte und magisch mächtige Triadenmatriarchin führt ihre Leute mit strenger Loyalität.", "Thornhill"),
    ("Alastair Browning", "Politischer und gesellschaftlicher Kontakt", "Toronto", "Browning bewegt sich zwischen Politik, Aktivismus und gesellschaftlichen Kontakten des Sprawls.", None),
    ("Brunwyn", "Westliche Drachin und S-K-Abgesandte", "Saeder-Krupp", "Brunwyn ist eine mit Lofwyr verbundene Drachin, die S-Ks Interessen und die magische Krise in Toronto untersucht.", "Casa Loma (Museum)"),
    ("Camazotz", "Freier Geist der Angst", "Blutsöhne der Maya / Camazotz-Kult", "Camazotz nährt sich von der Angst des Blackouts und lässt Leichen durch Schattengeister heimsuchen.", "Zephyrus-Kühllager"),
    ("Astrid Case", "Kampagnenakteurin", "Toronto", "Astrid Case ist eine wiederkehrende Akteurin der Toronto-Kampagne.", None),
    ("Dr. Fen Cheung Jr.", "Wuxing-Systemprogrammierer", "Wuxing", "Cheung Jr. entwickelt Sicherheits- und Interaktionsprotokolle für semiautonome Systeme.", "Dundas-Street-Enklave"),
    ("Dr. Fen Cheung Sr.", "Leitender Wuxing-Forscher", "Wuxing", "Cheung Sr. ist für Wuxings lokale Forschung so wichtig, dass mehrere Konzerne seine Extraktion betreiben.", "Dundas-Street-Enklave"),
    ("Daiyanna “D2” DiMeeko", "Technomancerin und Informationsbrokerin", "High Park", "D2 unterhält ein Netz aus Sprites, Spionen und schamanischen Kontakten.", "High Park"),
    ("Lucas Epstein", "S-K-Ingenieur", "Saeder-Krupp", "Epstein kennt gemeinsame Schwachstellen verkabelter Industrieanlagen und wird Ziel interner S-K-Intrigen.", None),
    ("Camden Espinoza", "MCT-Decker und Programmierer", "Mitsuhama", "Espinoza erleidet im Blackout einen absichtlich herbeigeführten Auswurfschock und wird im Senator versteckt.", "Senator Hotel"),
    ("Felix Gagnon", "KFS-infizierter Ex-Wuxing-Programmierer", "Wuxing", "Gagnon arbeitete am Matrix-Killswitch und versucht nach seiner Infektion ein neues Leben aufzubauen.", None),
    ("Harry Gale", "Kampagnenkontakt", "Toronto", "Harry Gale ist ein einflussreicher Trollkontakt der Toronto-Kampagne.", None),
    ("Karyos", "Leiter der Loge des Nostradamus", "Schwarze Loge", "Karyos leitet Torontos niedrigste Logenzelle und will durch das große Ritual aufsteigen.", "Osgoode Hall"),
    ("Kashish Jatt Sidhu", "Prinzessin der Armen und Honest-Ed’s-Eigentümerin", "Honest Ed’s", "Kash hält Honest Ed’s durch Politik, Versorgung und ein strikt gewaltfreies Umfeld offen.", "Honest Ed’s"),
    ("Krampus", "Trollischer Überlebenskünstler", "Toronto", "Krampus gehört zu den frühen wiederkehrenden Verbündeten oder Rivalen der Blackout-Kampagne.", None),
    ("Dr. Magdalena Krilow", "Ärztin und Gemeinschaftsführerin", "Toronto", "Krilow entwickelt sich während des Blackouts zu einer verlässlichen medizinischen und sozialen Führungskraft.", None),
    ("Moritz Lange", "Kampagnenakteur", "Toronto", "Moritz Lange ist ein wiederkehrender Akteur der Toronto-Kampagne.", None),
    ("Liam der Schwarze", "Wizganger und Ritualmagier", "Coven", "Liam führt den Coven, den die Schwarze Loge für gefährliche Rituale einsetzt.", "76 Coral Gable Drive"),
    ("Magier des Hügels", "Mysteriöser Erwachter", "Toronto", "Der Magier des Hügels ist ein rätselhafter Erwachter der Toronto-Kampagne.", None),
    ("Peregrine", "Nomadischer Schattenakteur", "Toronto", "Peregrine baut rasch ein lokales Netzwerk auf und verbindet mehrere Handlungsfäden des Blackouts.", "Dominion Public Building"),
    ("Aleksandr Popov", "Gesuchter Schattenakteur", "Toronto", "Popov wird während des Blackouts stadtweit gesucht und besitzt wertvolle Kontakte.", "The Feeding Block"),
    ("Prospero", "Anführer der Coquillards", "Coquillards", "Prospero ist ein charismatischer Hacker und Meister des Social Engineering.", "Filmhaus"),
    ("Pygmy", "Serienmörder und Blutmagier", "Toronto", "Pygmy tarnt seine Gefährlichkeit hinter einem harmlosen Auftreten und wird von der Jaguargarde verfolgt.", "The Junction"),
    ("Ripper", "Anführerin der Cutters", "Cutters", "Ripper führt ihr Cutters-Chapter wie ein effizientes Unternehmen.", "Dominion Public Building"),
    ("Erich Rothers alias Vater Gorgon", "Toxischer Schamane", "Aztechnology", "Rothers arbeitet als korrumpierter Konzernmagier und skrupelloser Söldner.", "Don Valley Toxic Zone"),
    ("Rubberhead", "Schmuggler und Teamführer", "Toronto", "Rubberhead kontrolliert funktionierende Fahrzeuge und wird dadurch zum Ziel der North Lords.", None),
    ("Sana", "Schamanin und Umweltschützerin", "Black Creek", "Sana folgt dem Schutzgeist Berg und arbeitet an der Heilung des Black Creek sowie gegen dunkle Rituale.", "Black Creek Pioneer Village"),
    ("Lynn Sauer", "S-K-Managerin", "Saeder-Krupp", "Sauer gerät während des Blackouts in die internen Machtkämpfe der Torontoer S-K-Führung.", None),
    ("Aldridge Smoach", "Paranormaler Privatdetektiv", "Toronto", "Smoach untersucht paranormale Vorgänge und arbeitet gegen Gefallen oder Bezahlung.", None),
    ("Miles Two-Go", "Fotograf und Drachenjäger", "Toronto", "Miles sucht nach einzigartigen Bildern von Drachen und anderen seltenen Motiven.", None),
    ("Marjorie Watts", "Ehemalige Militärführerin", "Mackenzie-Arkologie", "Watts organisiert in der Mackenzie-Arkologie eine strenge, aber schützende Selbstverwaltung.", "Mackenzie-Arkologie"),
    ("Shi Zhe Xian", "Elfischer Magier", "Toronto", "Shi Zhe Xian ist ein entschlossener Erwachter der Toronto-Kampagne.", None),
    ("Bindaas", "Ganganführerin und Beschützerin", "Torontoer Straßengang", "Bindaas schützt ihre kleine Gang und ist für gegenseitige Hilfe mit den Runnern offen.", None),
    ("Little Smoke", "Gewaltorientierter Ganganführer", "Torontoer Straßengang", "Little Smoke nutzt den Blackout, um Chaos zu stiften und Territorium zu gewinnen.", None),
    ("Eeka Krause", "Lokale Organisatorin und Kontakt", "Toronto", "Eeka Krause koordiniert Hilfe, Informationen und Kontakte während des Blackouts.", None),
    ("Ocho Chthoni", "Blutvater des Camazotz-Kults", "Blutsöhne der Maya / Camazotz-Kult", "Der Troll und Jaguarschamane dient Camazotz und verbreitet dessen Einfluss in Toronto.", "Zephyrus-Kühllager"),
    ("Strict-9", "Anführer des Sw@rm", "Sw@rm", "Strict-9 ist ein sadistischer Zwergenrigger, der Profit und Gewalt verbindet.", "The Triple"),
    ("Donny Brook", "Grid-Pirat", "Toronto", "Donny Brook gehört zu den Grid-Piraten, die energieautarke Lieferwagen übernehmen.", "Queen Vic"),
    ("Tator", "Decker und Triadenschuldner", "Long-de-Shou", "Tator ist ein exzentrischer Matrixspezialist mit hohen Schulden bei der Triade.", "Neverland Candy Shoppe"),
    ("Lester Tusk", "Prominenter Meta-Aktivist", "Toronto", "Tusk nutzt seine Bekanntheit für öffentliche Meta-Anliegen und wird Ziel eines Anschlags.", "Hockey Hall of Fame"),
    ("Hans Brackhaus", "Saeder-Krupp-Johnson", "Saeder-Krupp", "Brackhaus tritt als kultivierter S-K-Auftraggeber mit auffälligen goldenen Augen auf.", "Brass Rail"),
    ("Odella Adams", "Senator-Hotel-Akteurin", "Senator Hotel", "Odella Adams gehört zu den wichtigen Personen im abgeschotteten Senator Hotel.", "Senator Hotel"),
    ("Captain Dami Bodie-Disu", "Leiterin der Gefängnissicherheit", "Lone Star", "Bodie-Disu versucht das Don-Gefängnis ohne unnötige Tote unter Kontrolle zu halten.", "Don-Gefängnis"),
    ("Butch Bayard", "Humanis-Rädelsführer", "Humanis Policlub", "Bayard ist ein verurteilter Mörder und geschickter rassistischer Agitator.", "Don-Gefängnis"),
    ("Helen Baptiste", "Thaumaturgin und Logenzellenleiterin", "Schwarze Loge", "Baptiste leitet die Suche nach einem Ritualort, ohne den Gesamtplan der Loge zu kennen.", "Osgoode Hall"),
    ("Jonesy", "Möchtegern-Johnson und Wuxing-Zeitarbeiter", "Wuxing", "Jonesy versucht, aus den Verhältnissen in der Mackenzie-Arkologie ein Schattengeschäft zu machen.", "Mackenzie-Arkologie"),
    ("Florio", "Schieber", "Toronto", "Florio verkauft Informationen über Fahrzeuge und spielt Gangs und Käufer gegeneinander aus.", None),
    ("Jack Gambino", "Mafiasoldat", "Toronto Mafia", "Gambino ist ein niedrigrangiger Mafiaschläger, der sich in seiner Nachbarschaft profilieren will.", None),
    ("Emily Horton", "Lone-Star-Ermittlerin", "Lone Star", "Horton ist eine ehrgeizige Polizistin mit Erfolgen gegen Torontos Gangs.", None),
    ("Wanderer der Wege", "Magische Mittlerperson", "Toronto", "Der Wanderer der Wege verbindet NAN, Konzerne und Manasphäre und gehört zu Torontos wichtigsten magischen Kontakten.", None),
    ("Adam Branch", "Ares-Johnson", "Ares", "Branch koordiniert während des Blackouts eine riskante Serie von Extraktionen.", None),
    ("Simone Palomer", "Professorin für Metaplanare Risse", "University of Toronto", "Palomer ist eine international gefragte Forscherin zu metaplanaren Rissen.", "Campus der University of Toronto"),
    ("Vinh Trong", "Professor für Zauberformeln", "York University", "Trong sammelt und klassifiziert Varianten praktischer Zauberei.", "York University"),
    ("Penelope Bean", "Taliskrämerin", "Magic Beans", "Bean beschafft ungewöhnliche Reagenzien und hält auch zweifelhafte Stücke für authentisch.", "Magic Beans"),
    ("Roderick Kensington", "In Ungnade gefallener Akademiker", "Jane & Finch", "Kensington vertritt wilde Magietheorien, warnte aber schon vor dem Blackout vor totaler Finsternis.", "Jane & Finch"),
    ("Cable Prawn", "Hinterhofmagier", "Toronto", "Prawn zieht durch Hinterhöfe und bietet Heil- und Manipulationsmagie außerhalb des Konzernsystems an.", None),
    ("Francesco “Frankie C” Commisso", "Mafiaboss", "Commisso ’ndrina", "Commisso kontrolliert große Teile des Schmuggels und der Schutzgelderpressung im Großraum Toronto.", "Markham"),
    ("Adrian Violi", "Mafiaboss", "Violi Family", "Violi erweitert von Hamilton aus seinen Einfluss auf Torontos Bau-, Gewerkschafts- und Schmuggelgeschäfte.", "Little Italy"),
    ("One-Eyed Lee", "Logenmeister der Goldenen Pagode", "Goldene Pagode", "Lee führt die Goldene Pagode und ihren BTL-Handel im Toronto-Sprawl.", "Chinatown"),
    ("Boa Chan", "Grassandale der Goldenen Pagode", "Goldene Pagode", "Boa Chan vergibt operative Aufträge und führt den Wirtschaftskrieg gegen die Mafia.", "Chinatown"),
    ("Lucky Ma", "Roter Stab des Weißen Lotos", "Weißer Lotos", "Lucky Ma leitet die Angriffe des Weißen Lotos auf Commisso-Interessen.", "Thornhill"),
    ("Li Wei", "Blutmagier und ehemaliger Firewatch-Magier", "Toronto", "Li Wei greift während der Blackouts wiederholt Gurdwaras im Großraum Toronto an.", None),
    ("Sikh Burn", "Sikh-Adept und Gemeinschaftsbeschützer", "Greater Toronto Khalsa", "Sikh Burn verteidigt während des Blackouts eine Gurdwara und organisiert Versorgung und Schutz für ihre Gemeinschaft.", "York University"),
    ("Jag", "Organisator einer Gurdwara", "Greater Toronto Khalsa", "Jag koordiniert Wachen, Vorräte und medizinische Hilfe in einer nördlich von Toronto gelegenen Gurdwara.", "York University"),
    ("Howell", "Drachenkundiger Auftraggeber", "Society of Saint George", "Howell untersucht Brunwyns Flüge und vermittelt Aufträge mit Bezug zu Drachenaktivitäten in Toronto.", "Casa Loma (Museum)"),
    ("Marbella Pasquelle", "CMC-Vertreterin und Magierin", "Aztechnology", "Pasquelle hilft bei der Jagd auf den korrumpierten Geist Mezcallus Negh und besitzt Konzern- wie Hexenzirkelkontakte.", "Taddle-Creek-Parkanlage"),
    ("Mario Pileggi", "Geschäftsführer des Senator Hotels", "Senator Hotel", "Pileggi schützt Diskretion, Gäste und kompromittierende Daten des Hotels und bereitet zugleich einen möglichen Rückzug vor.", "Senator Hotel"),
    ("Dorothy", "Gebundener Ortsgeist", "Hockey Hall of Fame", "Dorothy ist ein wiederholt beobachteter Geist in der Hockey Hall of Fame.", "Hockey Hall of Fame"),
    ("Lukas", "Wirt und Musikförderer", "Moore’s on Danforth", "Der Troll Lukas führt Moore’s on Danforth und unterstützt Torontos lokale Musikszene.", "Moore’s on Danforth"),
]


NIGHT_PEOPLE = [
    ("Helena Myrryr", "Paranormale Privatdetektivin", "Smoach & Myrryr", "Myrryr bildet mit Aldridge Smoach ein ungewöhnliches Ermittlerduo und kennt sich mit Geistern und anderen paranormalen Fällen aus.", "Magic Beans"),
    ("Rennie Browser", "Alchemist und Ladenbesitzer", "Magic Beans", "Browser ist der gegenwärtige Besitzer von Magic Beans und versorgt Erwachte mit Reagenzien und alchemistischem Fachwissen.", "Magic Beans"),
    ("Benny", "Elfischer Rigger und Grid-Pirat", "Grid-Piraten", "Benny gehört mit Carrot und Kolds zur Besatzung eines Lieferwagens und kennt dessen technische Fähigkeiten.", "The Triple"),
    ("Carrot", "Albino-orkische Deckerin und Grid-Piratin", "Grid-Piraten", "Carrot untersucht mit Benny und Kolds die energieautarken Lieferwagen und ihre verwertbare Technik.", "The Triple"),
    ("Kolds", "Menschlicher Technomancer und Grid-Pirat", "Grid-Piraten", "Kolds ist der Technomancer des dreiköpfigen Grid-Piraten-Teams um den Testlieferwagen.", "The Triple"),
    ("Stella Hoargrave", "Gesellschaftsdame und Casa-Loma-Verwalterin", "Casa Loma", "Hoargrave bewegt sich sicher in Torontos Elite und übernimmt während der Krise organisatorische Verantwortung in Casa Loma.", "Casa Loma (Museum)"),
    ("Natalya Podge alias Digilante", "Deckerin und digitale Vigilantin", "Toronto", "Podge jagt unter dem Straßennamen Digilante Kriminelle in der Matrix und wird in den Konflikt im Queen Vic hineingezogen.", "Queen Vic"),
    ("Grissom “Growler” Dushane", "Orkischer Dealer", "Toronto", "Growler ist ein körperlich auffälliger Dealer und Kontakt im Umfeld des Queen Vic.", "Queen Vic"),
    ("Zennia", "Zwergische Schieberin", "Toronto", "Zennia vermittelt einen mehrstufigen Auftrag zwischen mehreren Gangs und kontrolliert dessen Bezahlung und Informationsfluss.", "Silver Spoon Bar"),
    ("Togle", "Anführerin des Torontoer Ancients-Chapters", "Ancients Toronto Chapter", "Togle führt das Torontoer Chapter der Ancients und verhandelt vom aufgegebenen Hafenhotel aus.", "Verlassenes Hafenhotel der Ancients"),
    ("Skug", "Anführer der Maulers", "Maulers", "Skug führt die Maulers und verhandelt aus deren Revier in Jane & Finch.", "Silver Spoon Bar"),
    ("Kruft", "Maulers-Ganger und Armdrücker", "Maulers", "Kruft prüft Besucher der Maulers mit körperlichen Kraftproben und vertritt die gewaltbetonte Kultur der Gang.", "Silver Spoon Bar"),
    ("Grikchuk", "Anführer der Bloodrippers", "Bloodrippers", "Grikchuk führt die Bloodrippers aus ihrem befestigten unterirdischen Stützpunkt.", "Bloodrippers-Lagerhaus"),
    ("Luna Khan", "Rao und rivalisierende Triadenoffizierin", "Torontoer Triaden", "Luna Khan ist der Straßenname einer Rao, an die Großmutter Biyu eine unmissverständliche Botschaft überbringen lässt.", "Thornhill Commons"),
    ("Lynum Helvettimal", "Verschuldeter Geschäftsmann", "Toronto", "Helvettimal ist ein elfischer Geschäftsmann und Ziel einer Triadenforderung; er verkehrt in Casa Loma und im Top o’ the Senator.", "Top o’ the Senator"),
    ("Piotr “Peter Pan” Ostrowlski", "Ghulischer Confiseur und Gruppenführer", "Lost Boys (and Girls)", "Peter Pan leitet die Lost Boys und hält ihre Selbstbeherrschung durch die Süßwarenproduktion im Neverland aufrecht.", "Neverland Candy Shoppe"),
    ("Elias “der Kartograf” Hanson", "Kartograf", "Run & Sollars", "Hanson gehört zu den Fachleuten von Run & Sollars und kann im Blackout benötigte analoge Karten anfertigen.", "Run & Sollars"),
    ("Mezcallus Negh", "Korrumpierter Geist", "Crystal Maize Cooperative", "Der korrumpierte Geist nutzt Lebensmittel- und Wasserversorgung, um seinen Einfluss auf Toronto auszuweiten.", "CMC-Verteilzentrum"),
    ("Irwin “War Dog” Weston", "Radikaler Aktivist", "Rise Movement", "Weston formt aus einem Protestumfeld das militante Rise Movement und treibt die Eskalation am Nathan Phillips Square voran.", "Nathan Phillips Square / The Cluster"),
    ("Karl Boncore", "Humanis-Agitator", "Humans Right", "Boncore leitet einen lokalen Humanis-Ableger und schürt bei The Cluster Hass gegen Metamenschen.", "Nathan Phillips Square / The Cluster"),
    ("Lorena Espinoza", "Spinrad-Global-Managerin", "Spinrad Global", "Espinoza vertritt Spinrad Global im abgeschotteten Senator Hotel und verfolgt eigene Konzerninteressen.", "Senator Hotel"),
    ("Barry Mana", "Prominenter Mediengast", "Torontoer Medienwelt", "Mana gehört zu den prominenten und einflussreichen Gästen des Senator Hotels und kann die Lage öffentlich prägen.", "Top o’ the Senator"),
    ("Lila Hyung", "Prominente Medienakteurin", "Torontoer Medienwelt", "Hyung ist eine der im Senator Hotel eingeschlossenen Persönlichkeiten mit wertvollen Kontakten und Informationen.", "Top o’ the Senator"),
    ("Rai Watanashi", "Konzernakteur mit Leibwache", "Torontoer Konzernszene", "Watanashi bewegt sich mit starker Leibwache im abgeschotteten Hotel und wird für mehrere Parteien interessant.", "Senator Hotel"),
    ("Patrick La Fleur", "Prominenter Hotelgast", "Toronto", "La Fleur gehört zu den wichtigen Bewohnern des Senator Hotels während der Isolation.", "Senator Hotel"),
    ("Chuck Cermak", "Insasse und Vermittler", "Don-Gefängnis", "Cermak ist einer der benannten Akteure im festgefahrenen Machtkampf des Don-Gefängnisses.", "Don-Gefängnis"),
    ("Cullen Burdock", "Insasse und Vermittler", "Don-Gefängnis", "Burdock ist ein weiterer benannter Schlüsselakteur unter den Gefangenen des Don.", "Don-Gefängnis"),
    ("Jurgen", "Anführer der North Lords", "North Lords", "Der große Troll führt die North Lords und will Rubberheads funktionsfähige Fahrzeuge übernehmen.", "TTC-Schrottplatz / Wilson Bus Garage and Subway Yard"),
    ("Skids", "Riggerin und Mitglied von Rubberheads Team", "Rubberheads Team", "Skids gehört zu dem kleinen Riggerteam, das die funktionsfähigen Vans auf dem TTC-Schrottplatz bewacht.", "TTC-Schrottplatz / Wilson Bus Garage and Subway Yard"),
    ("Wil", "Rigger und Mitglied von Rubberheads Team", "Rubberheads Team", "Wil ist einer der beiden Riggerzwillinge in Rubberheads Fahrzeugteam.", "TTC-Schrottplatz / Wilson Bus Garage and Subway Yard"),
    ("Gobble", "Rigger und Mitglied von Rubberheads Team", "Rubberheads Team", "Gobble ist der zweite Riggerzwilling in Rubberheads Fahrzeugteam.", "TTC-Schrottplatz / Wilson Bus Garage and Subway Yard"),
    ("1291", "Genetisch modifizierter Barghest", "The Purrfect Pet", "Der Barghest mit der Versuchsnummer 1291 ist ein entlaufenes Jagdexperiment mit mehreren Todesopfern.", "Old Yonge"),
    ("1737 alias Earl", "Genetisch modifizierte erwachte Katze", "Keepers", "Die schwarze Katze 1737 besitzt erwachte Kräfte und wurde von den Keepers als Earl aufgenommen.", "Kensington Market"),
    ("1101", "Genetisch modifizierter Hund", "The Purrfect Pet", "Der Dalmatiner 1101 hat eine Bindung zu Jack Gambino und schützt sein neues Herrchen.", "Kensington Market"),
    ("1109", "Genetisch modifizierter Hund", "The Purrfect Pet", "Der aggressive Pitbull-Chow-Chow-Mischling 1109 streift nach seiner Flucht auf Nahrungssuche umher.", "Kensington Market"),
    ("Martin Wrobelski", "Praktikant und Umweltaktivist", "Evergreen-Ziegelei", "Wrobelski arbeitet als Praktikant in der Evergreen-Ziegelei und wird in die Suche nach Popov verwickelt.", "Evergreen-Ziegelei"),
    ("Amanda Leppert", "Freiwillige und Umweltaktivistin", "Evergreen-Ziegelei", "Leppert engagiert sich freiwillig in der Evergreen-Ziegelei und ist Teil ihres sozialen Umfelds.", "Evergreen-Ziegelei"),
    ("Kojote", "Manifestation eines Schutzgeistes", "First Nations Toronto", "Ein Avatar Kojotes wird in Crothers Woods von einer Manabarriere der Schwarzen Loge gefangen gehalten.", "Crothers Woods"),
    ("Blight", "Toxischer Geist", "Scions of Blight", "Blight fördert Zerstörung und Verfall, sammelt toxische Schamanen um sich und nutzt die Silverthorn-Bibliothek als Treffpunkt.", "Silverthorn-Bibliothek"),
]


GROUPS = [
    ("Toronto-Québec Front", "Politische Untergrundbewegung", "Ares unterstützt radikale Zellen indirekt mit Material und Spezialisten für Operationen in Toronto und Québec."),
    ("Commisso ’ndrina", "Mafiaorganisation", "Die Commisso-Fraktion kontrolliert Schmuggel, Drogen und Schutzgelderpressung mit Schwerpunkt Markham."),
    ("Violi Family", "Mafiaorganisation", "Die Violi-Fraktion dringt von Hamilton nach Toronto vor und konkurriert um Wirtschaftsverbrechen und Schutzgelder."),
    ("Goldene Pagode", "Triade", "Die Goldene Pagode kontrolliert Chinatown, BTL-Handel und Teile der innerstädtischen Wirtschaftskriminalität."),
    ("Weißer Lotos / Long-de-Shou", "Triade", "Der Weiße Lotos kontrolliert Thornhill und ist mit dem Bund des Roten Drachen verbunden."),
    ("Coquillards", "Hackergang", "Die Coquillards kombinieren Social Engineering, Fleischweltoperationen und Matrixangriffe."),
    ("Screaming Tunnel Spelunkers", "Erwachte Recherchegruppe", "Die Gruppe erkundet Torontos Tunnel und sammelt Informationen über Veränderungen der lokalen Manasphäre."),
    ("Massey Foundation", "Magische Stiftung", "Die Stiftung sammelt Wissen zur regionalen Magie- und Manageschichte."),
    ("Sw@rm", "Go-Gang", "Der Sw@rm betreibt Grid-Piraterie und verfolgt energieautarke Fahrzeuge."),
    ("Ancients Toronto Chapter", "Gang", "Das örtliche Ancients-Chapter operiert von einem verlassenen Hafenhotel aus."),
    ("Maulers", "Gang", "Die Maulers kontrollieren die Silver Spoon Bar in Jane & Finch."),
    ("Bloodrippers", "Gang", "Die Bloodrippers unterhalten ein befestigtes Lagerhaus und konkurrieren mit anderen Straßengangs."),
    ("Cutters", "Gang", "Die Cutters arbeiten ungewöhnlich professionell und effizient, pflegen aber eine tief verwurzelte Feindschaft mit den Ancients."),
    ("North Lords", "Gang", "Die North Lords greifen Rubberheads Team an, um an funktionsfähige Fahrzeuge zu gelangen."),
    ("Devil Rats", "Arkologie-Gang", "Die Devil Rats kontrollieren Etagen der Mackenzie-Arkologie."),
    ("Ice Shards", "Arkologie-Gang", "Die Ice Shards sind eine zweite organisierte Bewohnergang der Mackenzie-Arkologie."),
    ("Ghunday", "Gang", "Die Ghunday sind eine einfache, aber zahlenmäßig starke Gang im Konflikt um Peregrine."),
    ("Coven", "Wizgang", "Der von Liam dem Schwarzen gegründete Coven führt im Auftrag der Schwarzen Loge Rituale durch."),
    ("Schwarze Loge Toronto", "Magische Geheimgesellschaft", "Die Torontoer Zellen der Schwarzen Loge nutzen den Blackout für gefährliche metaplanare Rituale."),
    ("Blutsöhne der Maya / Camazotz-Kult", "Magischer Kult", "Die Blutsöhne der Maya verehren Camazotz, verbreiten Angst und begehen Menschenopfer, um den Einfluss des Geistes zu stärken."),
    ("Toronto Data Haven", "Matrixgemeinschaft", "Der Toronto Data Haven beziehungsweise t.matrix ist der wichtigste Schattenknoten der Stadt."),
    ("First Nations Toronto", "Gang und Gemeinschaft", "First Nations ist eine lokale amerindianische Straßen- und Schutzgemeinschaft."),
    ("Toronto Mafia", "Syndikatsnetz", "Torontos Mafia ist zwischen Commisso, Violi und einer dritten kleineren Fraktion gespalten."),
    ("Torontoer Triaden", "Syndikatsnetz", "Goldene Pagode und Weißer Lotos teilen Chinatown und Thornhill unter sich auf."),
    ("Familie Gagnon", "Arkologiebewohner", "Terese, Claude, Juliet und Edward Gagnon werden während der Unruhen aus der Mackenzie-Arkologie evakuiert."),
    ("Friezes", "Arkologie-Gemeinschaft", "Die Friezes schützen eine kontrollierte Wohnetage der Mackenzie-Arkologie und nehmen die Familie Gagnon auf."),
    ("Bloodletters", "Gang", "Die Bloodletters gehören zu den Gruppen, die im Konflikt um Peregrine und das Dom auftreten."),
    ("Society of Saint George", "Drachenforschungsgruppe", "Die Gesellschaft sammelt Informationen über Drachen und beauftragt Howell mit der Untersuchung Brunwyns."),
    ("Jaguargarde", "Aztechnology-Spezialeinheit", "Die Jaguargarde verfolgt den Blutmagier Pygmy und versucht ihn lebend zu sichern."),
    ("Greater Toronto Khalsa", "Sikh-Schutzgemeinschaft", "Khalsa-Mitglieder schützen Gurdwaras und versorgen während des Blackouts gestrandete Menschen."),
]


NIGHT_GROUPS = [
    ("Lost Boys (and Girls)", "Ghulgruppe und Confiserie-Team", "Die Ghule um Peter Pan produzieren im Neverland Süßwaren, um Beschäftigung, Nahrung und Selbstbeherrschung zu sichern.", "Neverland Candy Shoppe"),
    ("Crystal Maize Cooperative", "Lebensmittelkonzern", "Die CMC betreibt Verteilung und magisch gestützte Agrarlogistik, wird aber von Mezcallus Neghs Einfluss unterwandert.", "CMC-Verteilzentrum"),
    ("Crimson Callers", "Magischer Kult", "Die Crimson Callers unterstützen den korrumpierten Geist Mezcallus Negh und versuchen seine Ausbreitung zu fördern.", "Taddle-Creek-Kläranlage"),
    ("Rise Movement", "Radikale Protestbewegung", "Irwin Weston formt die militante Bewegung aus der aufgeheizten Menge bei The Cluster.", "Nathan Phillips Square / The Cluster"),
    ("Humans Right", "Humanis-Ableger", "Karl Boncores lokaler Humanis-Ableger nutzt den Blackout für metafeindliche Agitation und Gewalt.", "Nathan Phillips Square / The Cluster"),
    ("Rubberheads Team", "Riggerteam", "Rubberhead, Skids, Wil und Gobble bewachen auf dem TTC-Schrottplatz mehrere funktionsfähige Vans.", "TTC-Schrottplatz / Wilson Bus Garage and Subway Yard"),
    ("Tamanous Toronto", "Organhandelsring", "Tamanous nutzt Informanten im Krankenhausviertel und schickt Teams aus, um transplantationsfähige Organe abzufangen.", "Toronto General Hospital"),
    ("Keepers", "Straßenkinder-Gemeinschaft", "Die Keepers überleben mit Kleinkriminalität, Wach- und Kurierdiensten und haben die erwachte Katze Earl aufgenommen.", "Kensington Market"),
    ("Yakuza Toronto", "Syndikatsnetz", "Die Yakuza besitzt nur eine kleine Präsenz im Sprawl, kontrolliert aber unter anderem den Kensington Market.", "Kensington Market"),
    ("Vory Toronto", "Syndikatsnetz", "Die lokalen Vory operieren aus Orten wie der Dorogoya Moya Bar und beschäftigen Attentäter wie Aleksandr Popov.", "Dorogoya Moya Bar"),
    ("South Cabbage Warlordz", "Gang", "Die Warlordz sind eine lokale Gang im südlichen Cabbagetown und geraten in Konflikte um Regent Park und St. Paul’s Basilica.", "St. Paul’s Basilica"),
    ("Hell’s Reapers", "Wizgang", "Die todesverehrenden Emo-Goth-Straßenpunks operieren nahe der instabilen metaplanaren Tore in Downtown.", "Queen’s Park"),
    ("Desolation Angels", "Insektengeist-Gang", "Das Torontoer Chapter besteht aus verborgenen Insektengeistern und verfolgt zugleich andere Arten von Insektengeistern.", "Silverthorn-Bibliothek"),
    ("Scions of Blight", "Toxischer Schamanenzirkel", "Die Akolythen Blights halten sich bedeckt, vergrößern ihre Macht und verteidigen ihr Gebiet.", "Silverthorn-Bibliothek"),
    ("Lone Star Toronto", "Polizei- und Sicherheitskonzern", "Lone Star überwacht Verkehr und öffentliche Ordnung, betreibt das Don-Gefängnis und ist im Blackout stark überlastet.", "Don-Gefängnis"),
    ("Ares Global Entertainment Toronto", "Medienkonzern", "AGE ist der letzte größere Ares-Unternehmensteil in Toronto und wird von konkurrierenden Megakonzernen bedrängt.", "Toronto Media Studios"),
    ("Saeder-Krupp Toronto", "Megakonzern-Niederlassung", "Saeder-Krupp übernahm zahlreiche ehemalige Ares-Fabriken, Wohnkomplexe und Eisenbahninteressen im Toronto-Sprawl.", "Saeder-Krupp-Etobicoke-Komplex"),
    ("Spinrad Global Toronto", "Megakonzern-Niederlassung", "SpinGlobal konkurriert um AGE, die Torontoer Matrixverwaltung und S-Ks Industrieinteressen.", "Toronto Media Studios"),
    ("Wuxing Toronto", "Megakonzern-Niederlassung", "Wuxing investiert in Hafenlogistik, Konsumgüterproduktion, Börsenzugang und ehemalige Ares-Fabriken.", "Wuxing-Geheimdock"),
    ("Mitsuhama Toronto", "Megakonzern-Niederlassung", "Mitsuhama besitzt Medien- und Eisenbahninteressen und steht dabei in wachsender Konkurrenz zu Saeder-Krupp.", "Toronto Media Studios"),
]


OLDER_PLACES = [
    ("Hungerunruhen von Toronto 2048", "Toronto", "Historische Ereignisse", None, "Mercurial belegt die stadtweiten Hungerunruhen von 2048 durch zeitgenössisches Bildmaterial; der Marker bezeichnet das Ereignis, keinen hausgenauen Schauplatz.", "SR1", "mercurial-sr1", "Mercurial", "Mercurial, Konzertszene und Toronto Food Riots, S. 35"),
    ("Microsoft Canada – Hauptquartier", "Downtown/Alt-Toronto", "Konzerne", None, "Corporate Shadowfiles verortet das kanadische Microsoft-Hauptquartier ausdrücklich in Toronto.", "SR2", "corporate-shadowfiles-sr2", "Corporate Shadowfiles / Megakons", "Corporate Shadowfiles, Corporate Culture, S. 11"),
    ("Taylor Paulines Torontoer Büro", "East York", "Dienstleistungen", None, "Prime Runners beschreibt Paulines kleines Büro in einem unscheinbaren Geschäftsblock im Osten Torontos.", "SR2", "prime-runners-sr2", "Prime Runners", "Prime Runners, Taylor Kimball Pauline, S. 55-57"),
    ("Hauptquartier der Magical Reform Society", "Toronto", "Magie und Religion", None, "Die Magical Reform Society unterhält ihr Hauptquartier in Toronto und dient zugleich als Tarn- und Einflussorganisation der Illuminates of the New Dawn.", "SR2", "underworld-sr2", "Underworld Sourcebook / Unterwelt-Quellenbuch", "Unterwelt-Quellenbuch, Magical Reform Society, S. 82"),
    ("Dunkelzahns Torontoer Büro", "Downtown/Alt-Toronto", "Dienstleistungen", None, "Dunkelzahns Testament nennt ausdrücklich ein Büro in Toronto, in dem Teile seines Nachlasses verwahrt wurden.", "SR2", "portfolio-dragon-sr2", "Portfolio of a Dragon / Portfolio eines Drachen", "Portfolio eines Drachen, Testament, S. 25"),
    ("Shadowland Toronto", "Toronto", "Matrix und Metaplanes", None, "Der Torontoer Shadowland-Knoten verlor nach der Durchtrennung nicht registrierter Leitungen seinen Nexus-Anschluss und kehrte unter anderem Namen zurück.", "SR3", "target-matrix-sr3", "Target: Matrix / Brennpunkt Matrix", "Target: Matrix, Shadowland Nodes, S. 27"),
    ("Transys Neuronet America – Hauptbüro", "Downtown/Alt-Toronto", "Konzerne", None, "Das nordamerikanische Hauptbüro von Transys Neuronet befindet sich im SR3-Stadtstand in Toronto.", "SR3", "dragons-sixth-world-sr3", "Dragons of the Sixth World / Drachen der 6. Welt", "Drachen der 6. Welt, Transys Neuronet, S. 50"),
    ("Hauptquartier von Realm Beyond", "Downtown/Alt-Toronto", "Matrix und Metaplanes", None, "Der lokale KI- und Technomancer-Kult Realm Beyond unterhält ein von der Polizei beobachtetes Hauptquartier in Toronto.", "SR4", "emergence-sr4", "Emergence / Emergenz", "Emergence, Realm Beyond, S. 102"),
    ("Ice Princess", "Downtown/Alt-Toronto", "Bars und Clubs", None, "Der aufstrebende Club wird von Frankie Hamilton geführt und bietet Zugang zu dessen Draco-Foundation-Kontakten.", "SR4", "jet-set-sr4", "Jet Set", "Jet Set, Plot Point One, S. 38"),
]


OLDER_PEOPLE = [
    ("Arthur Vogel", "Umweltanwalt und UCAS-Politiker", "One World Association", "Vogel wuchs im Toronto-Sprawl auf; die dort erlebte Konzernverschmutzung prägte seinen späteren politischen und juristischen Umweltkampf.", None, "SR2", "super-tuesday-sr2", "Super Tuesday", "Super Tuesday, Arthur Vogel, S. 18"),
    ("Taylor Kimball Pauline", "Kontraktvermittler", "Torontoer Schatten", "Der in Toronto lebende Vermittler verbindet Konzernkunden mit Runnerteams, gilt aber als geschickter und riskanter Geschäftemacher.", "Taylor Paulines Torontoer Büro", "SR2", "prime-runners-sr2", "Prime Runners", "Prime Runners, Taylor Kimball Pauline, S. 55-57"),
    ("Dr. Conrad Jellico", "Präsident der Magical Reform Society", "Magical Reform Society", "Jellico führt die Torontoer MRS und ist in den inneren Kreis der Illuminates of the New Dawn initiiert.", "Hauptquartier der Magical Reform Society", "SR2", "underworld-sr2", "Underworld Sourcebook / Unterwelt-Quellenbuch", "Unterwelt-Quellenbuch, Magical Reform Society, S. 82"),
    ("Judy Kamura", "Reporterin", "KNUT-Toronto", "Kamura berichtet als ausdrücklich Toronto zugeordnete Journalistin über die UCAS-Präsidentschaftswahl.", None, "SR2", "portfolio-dragon-sr2", "Portfolio of a Dragon / Portfolio eines Drachen", "Portfolio of a Dragon, Wahlberichterstattung, S. 12"),
    ("Dunkelzahn", "Großer Drache und UCAS-Präsident", "Draco Foundation", "Dunkelzahns Testament belegt ein eigenes Büro in Toronto, das auch zur Verwahrung besonderer Nachlassstücke diente.", "Dunkelzahns Torontoer Büro", "SR2", "portfolio-dragon-sr2", "Portfolio of a Dragon / Portfolio eines Drachen", "Portfolio eines Drachen, Testament, S. 25"),
    ("Jeremy Thomason", "Direktor von Transys Neuronet America", "Transys Neuronet", "Thomason leitet die nordamerikanische Transys-Division von ihrem Torontoer Hauptbüro aus.", "Transys Neuronet America – Hauptbüro", "SR3", "dragons-sixth-world-sr3", "Dragons of the Sixth World / Drachen der 6. Welt", "Drachen der 6. Welt, Transys Neuronet, S. 50"),
    ("Winston Griffith III alias Dark Father", "Philanthrop und Otaku", "Mirages Netzwerk", "Der bekannte Torontoer Wohltäter führte als Dark Father ein geheimes Leben im Otaku-Netzwerk und wurde 2064 ermordet.", None, "SR3", "system-failure-sr3", "System Failure / Systemausfall", "System Failure, The Network, S. 10 und 45"),
    ("Josephine “Speed Queen” Simmons", "Weltrekord-Sprinterin", "Toronto Championship", "Simmons läuft bei den Toronto Championships einen 100-Meter-Weltrekord und wird trotz negativer Tests zum Gegenstand von Enhancement-Gerüchten.", None, "SR3", "sota-2064-sr3", "State of the Art: 2064", "State of the Art: 2064, Track and Field, S. 167"),
    ("Amelia Desaulniers", "Torontoer Stadträtin", "Stadt Toronto", "Desaulniers gerät öffentlich mit dem Technomancer-Kult Realm Beyond in Konflikt, nachdem ihr Sohn dessen Hauptquartier beitritt.", "Hauptquartier von Realm Beyond", "SR4", "emergence-sr4", "Emergence / Emergenz", "Emergence, Realm Beyond, S. 102"),
    ("Vagabond", "Technomancerin und Kultführerin", "Realm Beyond", "Vagabond führt Realm Beyond und behauptet, als Einzige die Stimme der Matrix verstehen zu können.", "Hauptquartier von Realm Beyond", "SR4", "emergence-sr4", "Emergence / Emergenz", "Emergence, Realm Beyond, S. 102"),
    ("Joseph Willis “J.W.” Ellis", "Anwalt, Politiker und Logenmagier", "Schwarze Loge", "Ellis arbeitete nach der Gründung der UCAS als Konzernanwalt in Toronto und stieg parallel in der Schwarzen Loge auf.", None, "SR4", "artifacts-unbound-sr4", "Artifacts Unbound", "Artifacts Unbound, J.W. Ellis, S. 125"),
    ("Francis “Frankie” Hamilton", "Fixer, Informationsbroker und Clubbetreiber", "Draco Foundation", "Hamilton betreibt den Ice Princess und besitzt Zugang zu wichtigen internen Informationen der Draco Foundation.", "Ice Princess", "SR4", "jet-set-sr4", "Jet Set", "Jet Set, Plot Point One, S. 38"),
    ("Mark Sedgwick", "Urban-Brawl-Spieler der Toronto Maple Leafs", "Toronto Maple Leafs", "Sedgwick wird als Center der Toronto Maple Leafs mit zehn Toren und vierzehn Assists geführt.", None, "SR4", "srm04-07-sr4", "SRM04-07: Burn", "SRM04-07: Burn, Mark 10:14, S. 35"),
    ("Professor Christian Mealer", "Thaumaturgieprofessor und Illuminat", "Illuminates of the New Dawn", "Der in Toronto geborene und aufgewachsene Magier wurde später Professor am MIT&T und Magus der Illuminates.", None, "SR4", "srm04-12-sr4", "SRM04-12: Showcase", "SRM04-12: Showcase, Christian Mealer, S. 55"),
    ("Rose Red", "Mystische Adeptin und neoanarchistische Runnerin", "Black Star", "Rose Red betrieb zunächst in Toronto ein kriminelles Netzwerk, lebte später auf dessen Straßen und schloss sich dort der neoanarchistischen Bewegung an.", "Toronto", "SR5", "anarchy-sr5", "Shadowrun: Anarchy", "Shadowrun: Anarchy, Rose Red, S. 116"),
]


OLDER_GROUPS = [
    ("Microsoft Canada", "Technologiekonzern-Niederlassung", "Microsoft Canada wird im SR2-Konzernstand von einem Hauptquartier in Toronto aus geführt.", "Microsoft Canada – Hauptquartier", "SR2", "corporate-shadowfiles-sr2", "Corporate Shadowfiles / Megakons", "Corporate Shadowfiles, Corporate Culture, S. 11"),
    ("Magical Reform Society", "Magische Interessenorganisation", "Die MRS vertritt öffentlich magisch Aktive, ist im Schatten jedoch in die Illuminates of the New Dawn eingebunden.", "Hauptquartier der Magical Reform Society", "SR2", "underworld-sr2", "Underworld Sourcebook / Unterwelt-Quellenbuch", "Unterwelt-Quellenbuch, Magical Reform Society, S. 82"),
    ("Transys Neuronet America", "Technologiekonzern-Division", "Die nordamerikanische Transys-Division wird von Toronto aus geleitet und umfasst mehrere Software-, Forschungs- und Kommunikationsfirmen.", "Transys Neuronet America – Hauptbüro", "SR3", "dragons-sixth-world-sr3", "Dragons of the Sixth World / Drachen der 6. Welt", "Drachen der 6. Welt, Transys Neuronet, S. 50"),
    ("Aleph Society Toronto", "Magischer Kultableger", "Threats 2 nennt ein im Aufbau befindliches Torontoer Chapter der auf persönliche Erweckung ausgerichteten Aleph Society.", "Hauptquartier der Magical Reform Society", "SR3", "threats-2-sr3", "Threats 2 / Bedrohliche 6. Welt", "Threats 2, Aleph Society, S. 44"),
    ("Realm Beyond", "KI- und Technomancer-Kult", "Der lokale Kult folgt Vagabonds angeblicher Kommunikation mit der Stimme der Matrix und wird von der Polizei beobachtet.", "Hauptquartier von Realm Beyond", "SR4", "emergence-sr4", "Emergence / Emergenz", "Emergence, Realm Beyond, S. 102"),
    ("Toronto Maple Leafs", "Urban-Brawl-Team", "Das Torontoer Profiteam wird durch den Center Mark Sedgwick ausdrücklich im Ligakontext belegt.", "Toronto", "SR4", "srm04-07-sr4", "SRM04-07: Burn", "SRM04-07: Burn, Mark 10:14, S. 35"),
    ("New Toronto Re", "Rückversicherungsgesellschaft", "NTR wird von S-K Prime als überbewertete finanzielle Falle aufgebaut und später in die Zerschlagung von Cord Mutual einbezogen.", "Toronto Stock Exchange", "SR6", "konzerngewalten-sr6", "Konzerngewalten / Power Plays", "Konzerngewalten, Saeder-Krupp, S. 125"),
    ("Transnational Communications", "Medienkonzern", "TNC verlegte seinen Sitz nach der Chicago-Katastrophe nach Toronto und besitzt weiterhin lokale Sender- und Produktionsinteressen.", "Toronto Media Studios", "SR6", "konzerngewalten-sr6", "Konzerngewalten / Power Plays", "Konzerngewalten, Saeder-Krupp, S. 128"),
]


SR3_PLACES = [
    ("Toronto Stock Exchange", "Downtown/Alt-Toronto", "Torontos Börse ist 2062 ein zentrales Ziel für Datendiebstahl, Insiderhandel und finanzielle Verschleierung."),
    ("Toronto Matrix", "Toronto", "Die geordnete Matrix folgt städtischen Gestaltungsstandards und verbindet Unterhaltung, virtuelle Einkaufszentren und Konzernwirtschaft."),
    ("Toronto Media Studios", "Downtown/Alt-Toronto", "VisionQuest, NBS, Mediaworks, Brilliant Genesis und weitere Medienunternehmen machen Toronto zur Unterhaltungshauptstadt der UCAS."),
]


def add_content() -> CityCatalogue:
    city = CityCatalogue(CITY_ID, "Toronto", ANCHORS["Toronto"], ANCHORS, BOOKS)

    for name, summary in DISTRICTS:
        city.add_district_version(
            name,
            "SR6",
            "30-nights-sr6",
            "30 Nächte und 3 Tage",
            "30 Nächte und 3 Tage, Toronto - Stadtteile, S. 11-17",
            summary,
        )

    for number, name, scope, category, coordinates, summary in POSTER_SPOTS:
        city.add_place(
            name,
            scope,
            "SR6",
            "toronto-poster-sr6",
            "Toronto Poster 2080",
            f"Toronto Poster 2080, Legende Nr. {number}",
            category=category,
            summary=summary,
            coordinates=coordinates,
            map_number=number,
            exact=coordinates is not None,
        )

    for number, name, scope, coordinates in MAP_30_NIGHTS:
        summary = f"{name} ist auf der offiziellen Übersichtskarte von 30 Nächte als wichtiger Torontoer Ort ausgewiesen."
        category = (
            "Stadtteile"
            if name in {
                "Cabbagetown", "Little Italy", "Chinatown", "Moore Park",
                "Entertainment District", "The Beaches", "Little India",
                "Bloor West", "The Junction", "Jane & Finch", "Willowdale",
                "Hoggs Hollow", "Bathurst Manor", "Thornhill", "Agincourt",
                "Markham",
            }
            else None
        )
        city.add_place(
            name,
            scope,
            "SR6",
            "30-nights-sr6",
            "30 Nächte und 3 Tage",
            f"30 Nächte und 3 Tage, Toronto-Karte, Legende Nr. {number}",
            category=category,
            summary=summary,
            coordinates=coordinates,
            exact=True,
        )

    for name, scope, category, coordinates, summary in ADDITIONAL_PLACES:
        city.add_place(
            name,
            scope,
            "SR6",
            "30-nights-sr6",
            "30 Nächte und 3 Tage",
            "30 Nächte und 3 Tage, Toronto und Die Nächte, S. 11-144",
            category=category,
            summary=summary,
            coordinates=coordinates,
            exact=coordinates is not None,
        )

    for name, scope, category, coordinates, summary in NIGHT_PLACES:
        city.add_place(
            name,
            scope,
            "SR6",
            "30-nights-sr6",
            "30 Nächte und 3 Tage",
            "30 Nächte und 3 Tage, Nacht 1-30, S. 25-144",
            category=category,
            summary=summary,
            coordinates=coordinates,
            exact=coordinates is not None,
        )

    for name, scope, category, coordinates, summary, edition, book_id, title, citation in OLDER_PLACES:
        city.add_place(
            name,
            scope,
            edition,
            book_id,
            title,
            citation,
            category=category,
            summary=summary,
            coordinates=coordinates,
            exact=coordinates is not None,
        )

    for name, scope, summary in SR3_PLACES:
        city.add_place(
            name,
            scope,
            "SR3",
            "sona-toronto-sr3",
            "Nordamerika in den Schatten / Shadows of North America",
            "Nordamerika in den Schatten, Toronto, S. 175-176",
            summary=summary,
        )

    for name, role, affiliation, summary, location in PEOPLE:
        city.add_person(
            name,
            "SR6",
            "30-nights-sr6",
            "30 Nächte und 3 Tage",
            "30 Nächte und 3 Tage, Die Nächte und Charakter-Fundgrube, S. 25-163",
            role=role,
            affiliation=affiliation,
            summary=summary,
            location_name=location,
        )

    for name, role, affiliation, summary, location in NIGHT_PEOPLE:
        city.add_person(
            name,
            "SR6",
            "30-nights-sr6",
            "30 Nächte und 3 Tage",
            "30 Nächte und 3 Tage, Nacht 4-29, S. 37-144",
            role=role,
            affiliation=affiliation,
            summary=summary,
            location_name=location,
        )

    for name, role, affiliation, summary, location, edition, book_id, title, citation in OLDER_PEOPLE:
        city.add_person(
            name,
            edition,
            book_id,
            title,
            citation,
            role=role,
            affiliation=affiliation,
            summary=summary,
            location_name=location,
        )

    # Li Wei's Toronto status is explicitly expanded in the Blackout bounty
    # dossier and therefore receives an additional source in the same edition.
    city.add_person(
        "Li Wei",
        "SR6",
        "blackout-sr6",
        "Blackout / Cutting Black",
        "Blackout, Defende nos in proelio, S. 78",
        role="Blutmagier und ehemaliger Firewatch-Magier",
        affiliation="Greater Toronto",
        summary="Li Wei wird nach mehreren Angriffen auf geschützte Gurdwaras im Großraum Toronto gesucht.",
    )

    for name, role, summary in GROUPS:
        edition, book_id, title, citation = (
            ("SR2", "target-ucas-sr2", "Target: UCAS", "Target: UCAS, Toronto-Québec Front, S. 65")
            if name == "Toronto-Québec Front"
            else ("SR6", "30-nights-sr6", "30 Nächte und 3 Tage", "30 Nächte und 3 Tage, Toronto und Die Nächte, S. 11-144")
        )
        location = {
            "Commisso ’ndrina": "Markham",
            "Violi Family": "Little Italy",
            "Goldene Pagode": "Chinatown",
            "Weißer Lotos / Long-de-Shou": "Thornhill",
            "Coquillards": "Filmhaus",
            "Sw@rm": "The Triple",
            "Ancients Toronto Chapter": "Verlassenes Hafenhotel der Ancients",
            "Maulers": "Silver Spoon Bar",
            "Bloodrippers": "Bloodrippers-Lagerhaus",
            "Devil Rats": "Mackenzie-Arkologie",
            "Ice Shards": "Mackenzie-Arkologie",
            "Coven": "76 Coral Gable Drive",
            "Schwarze Loge Toronto": "Osgoode Hall",
            "Blutsöhne der Maya / Camazotz-Kult": "Zephyrus-Kühllager",
            "Toronto Data Haven": "Toronto Data Haven / t.matrix",
            "Familie Gagnon": "Mackenzie-Arkologie",
            "Friezes": "Mackenzie-Arkologie",
            "Society of Saint George": "Casa Loma (Museum)",
            "Jaguargarde": "The Junction",
            "Greater Toronto Khalsa": "York University",
        }.get(name)
        city.add_person(
            name,
            edition,
            book_id,
            title,
            citation,
            role=role,
            affiliation="Toronto",
            summary=summary,
            entity_type="group",
            location_name=location,
        )

    for name, role, summary, location in NIGHT_GROUPS:
        city.add_person(
            name,
            "SR6",
            "30-nights-sr6",
            "30 Nächte und 3 Tage",
            "30 Nächte und 3 Tage, Toronto und Nacht 11-29, S. 17-144",
            role=role,
            affiliation="Toronto",
            summary=summary,
            entity_type="group",
            location_name=location,
        )

    for name, role, summary, location, edition, book_id, title, citation in OLDER_GROUPS:
        city.add_person(
            name,
            edition,
            book_id,
            title,
            citation,
            role=role,
            affiliation="Toronto",
            summary=summary,
            entity_type="group",
            location_name=location,
        )

    # Derselbe Cutters-Datensatz erhält den historischen SR2-Beleg, statt
    # neben dem SR6-Chapter einen zweiten gleichnamigen Eintrag zu erzeugen.
    city.add_person(
        "Cutters",
        "SR2",
        "underworld-sr2",
        "Underworld Sourcebook / Unterwelt-Quellenbuch",
        "Underworld Sourcebook, Cutters, S. 106",
        role="Gang",
        affiliation="Toronto",
        summary="Das Underworld Sourcebook nennt eine zehnköpfige Torontoer Cutters-Fraktion im Great-Lakes-Netzwerk.",
        entity_type="group",
        location_name="Dominion Public Building",
    )
    for edition, book_id, title, citation, summary in (
        (
            "SR2",
            "lone-star-sr2",
            "Lone Star",
            "Lone Star, Contract Law, S. 20",
            "Lone Star hält bereits im SR2-Stand Polizeiverträge in Toronto und mehreren weiteren kanadischen Großstädten.",
        ),
        (
            "SR4",
            "corporate-guide-sr4",
            "Corporate Guide / Konzerndossier",
            "Konzerndossier, Lone Star Security Services, S. 176",
            "Im SR4-Konzernstand ist Lone Stars Toronto-Vertrag durch Gangkriege und die Konkurrenz mit Knight Errant gefährdet.",
        ),
    ):
        city.add_person(
            "Lone Star Toronto",
            edition,
            book_id,
            title,
            citation,
            role="Polizei- und Sicherheitskonzern",
            affiliation="Toronto",
            summary=summary,
            entity_type="group",
            location_name="Don-Gefängnis",
        )

    # SR3 city-state descriptions for organisations that remain recognisable
    # in later material.
    for name, role, summary in (
        ("VisionQuest", "Medienkonzern", "VisionQuest unterhält 2062 bedeutende Studios in der UCAS-Unterhaltungshauptstadt Toronto."),
        ("NBS Toronto", "Medienkonzern", "NBS gehört zu den großen Medienunternehmen mit Torontoer Studiobetrieb."),
        ("Mediaworks Toronto", "Medienkonzern", "Mediaworks betreibt Studios in Torontos wachsender Unterhaltungsindustrie."),
        ("Brilliant Genesis Toronto", "Medienkonzern", "Brilliant Genesis ist im Torontoer Film- und SimSinn-Markt aktiv."),
    ):
        city.add_person(
            name,
            "SR3",
            "sona-toronto-sr3",
            "Nordamerika in den Schatten / Shadows of North America",
            "Nordamerika in den Schatten, Toronto, S. 175-176",
            role=role,
            affiliation="Toronto",
            summary=summary,
            entity_type="group",
            location_name="Toronto Media Studios",
        )

    # Der Almanach liefert eigene SR4-Beschreibungsstände für die Börse und
    # die Medien-/Technologieszene; sie werden als Editionsreiter ergänzt.
    city.add_place(
        "Toronto Stock Exchange",
        "Downtown/Alt-Toronto",
        "SR4",
        "sixth-world-almanac-sr4",
        "Sixth World Almanac / Almanach der Sechsten Welt",
        "Almanach der Sechsten Welt, Toronto, S. 195",
        summary="Die Börse dient als zweiter UCAS-Marktindikator und als Zugang für Transaktionen zwischen ausländischen Investoren und UCAS-Konzernen.",
        coordinates=[-79.3800, 43.6460],
        exact=True,
    )
    city.add_place(
        "Toronto Media Studios",
        "Downtown/Alt-Toronto",
        "SR4",
        "sixth-world-almanac-sr4",
        "Sixth World Almanac / Almanach der Sechsten Welt",
        "Almanach der Sechsten Welt, Toronto, S. 195",
        summary="Toronto ist im SR4-Stadtstand die Unterhaltungshauptstadt der UCAS mit SimSinn-Studios und einer großen Technologie-Startup-Szene.",
    )
    city.add_person(
        "Simone Palomer",
        "SR6",
        "schlagschatten-sr6",
        "Schlagschatten / Slip Streams",
        "Schlagschatten, Falten, Furchen und Risse, S. 74",
        role="Professorin für Metaplanare Risse",
        affiliation="University of Toronto",
        summary="Palomers 2079 veröffentlichte Theorie zur metaplanaren Balance beeinflusst internationale Experimente mit Alcheras und Rissen.",
        location_name="Campus der University of Toronto",
    )
    return city


def polygon_parts(geometry: dict) -> list[list]:
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiPolygon":
        return geometry["coordinates"]
    raise ValueError(f"Nicht unterstützte Geometrie {geometry['type']}")


def part_center(part: list) -> tuple[float, float]:
    ring = part[0]
    return (
        sum(point[0] for point in ring) / len(ring),
        sum(point[1] for point in ring) / len(ring),
    )


def classify_neighbourhood(name: str, x: float, y: float) -> str:
    if name == "Waterfront Communities-The Island":
        return "Downtown/Alt-Toronto"
    if x < -79.52 or (x < -79.50 and y < 43.69):
        return "Etobicoke"
    if x > -79.315 or (x > -79.335 and y > 43.72):
        return "Scarborough"
    if y > 43.72:
        return "North York"
    if x > -79.34 or name in {
        "Old East York", "Thorncliffe Park", "Leaside-Bennington",
        "Broadview North", "Danforth Village - East York",
        "Danforth Village - Toronto", "Playter Estates-Danforth",
        "North Riverdale", "South Riverdale", "Blake-Jones",
        "Greenwood-Coxwell", "East End-Danforth", "The Beaches",
        "Woodbine Corridor", "O'Connor-Parkview", "Victoria Village",
    }:
        return "East York"
    if y > 43.68 and x > -79.45:
        return "Uptown"
    if x < -79.42:
        return "West End"
    return "Downtown/Alt-Toronto"


def build_district_boundaries() -> None:
    source = json.loads((CITY_DIR / "neighborhoods.geojson").read_text(encoding="utf-8"))
    grouped: dict[str, list[list]] = {name: [] for name, _ in DISTRICTS}
    for feature in source["features"]:
        name = feature["properties"]["name"]
        parts = polygon_parts(feature["geometry"])
        if name == "Waterfront Communities-The Island":
            # The reference dataset combines the waterfront mainland and the
            # islands. The northern component is Downtown, all southern
            # components form the dedicated lore district.
            for part in parts:
                _x, y = part_center(part)
                grouped["Downtown/Alt-Toronto" if y > 43.6355 else "Toronto Islands"].append(part)
            continue
        all_points = [point for part in parts for point in part[0]]
        x = sum(point[0] for point in all_points) / len(all_points)
        y = sum(point[1] for point in all_points) / len(all_points)
        grouped[classify_neighbourhood(name, x, y)].extend(parts)

    summaries = dict(DISTRICTS)
    features = []
    labels = []
    for name, _summary in DISTRICTS:
        parts = grouped[name]
        if not parts:
            raise ValueError(f"Toronto-Distrikt ohne Geometrie: {name}")
        anchor = ANCHORS[name]
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "name": name,
                    "basis": (
                        "Lore-Zuordnung nach 30 Nächte und 3 Tage, S. 11-17; "
                        "heutige Stadtteilgrenzen dienen nur als präzise Linienbasis"
                    ),
                    "boundary_role": "lore-district",
                    "description": summaries[name],
                    "source": "30 Nächte und 3 Tage",
                    "edition": "SR6",
                },
                "geometry": {"type": "MultiPolygon", "coordinates": parts},
            }
        )
        labels.append({"name": name, "lat": anchor[0], "lon": anchor[1], "type": "district"})
    write_json(
        CITY_DIR / "districts.geojson",
        {"type": "FeatureCollection", "name": "Toronto Lore-Distrikte", "features": features},
    )
    write_json(CITY_DIR / "labels.json", labels)


def update_atlas(city: CityCatalogue) -> None:
    atlas_path = CITY_DIR / "atlas.json"
    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    poster_names = {name_key(item[1]) for item in POSTER_SPOTS}
    nights_names = {name_key(item[1]) for item in MAP_30_NIGHTS}
    ids = {
        key: feature["properties"]["id"]
        for key, feature in city.places.items()
    }
    for plan in atlas:
        if plan["key"] == "toronto-poster":
            plan["markerIds"] = [ids[key] for key in poster_names if key in ids]
        elif plan["key"] == "toronto-30-nights":
            plan["markerIds"] = [ids[key] for key in nights_names if key in ids]
    write_json(atlas_path, atlas)
    manifest_path = CITY_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["dataVersion"] = 8
    manifest["summary"]["detail_marker_instances"] = sum(
        len(plan.get("markerIds", [])) for plan in atlas
    )
    write_json(manifest_path, manifest)


def main() -> None:
    city = add_content()
    city.finish(
        2080,
        (
            "Toronto aus den lokalen SR1- bis SR6-Belegen des Quellenarchivs: "
            "Stadtprofil, Kampagne und Karten mit Lore-Distrikten, Orten, "
            "Personen, Gangs, Organisationen und Editionsbeschreibungen."
        ),
        bounds=[[43.54, -79.72], [43.90, -79.10]],
        zoom=10,
    )
    build_district_boundaries()
    update_atlas(city)
    print(f"Toronto: {len(city.places)} Orte, {len(city.people)} Personen/Gruppen")


if __name__ == "__main__":
    main()
