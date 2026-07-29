#!/usr/bin/env python3
"""Build the second city wave from its strongest city and regional sources."""

from __future__ import annotations

import json

from build_us_city_content import write_json
from build_wave1_city_packages import (
    ROOT,
    WORKS,
    build_city,
    n,
    p,
)


CONFIGS = {
    "san-francisco": {
        "name": "San Francisco Metroplex", "year": 2078,
        "center": (37.7749, -122.4194),
        "bounds": [[37.25, -122.75], [38.15, -121.75]], "zoom": 9,
        "books": [
            "sr2-california-free-state",
            "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex",
        ],
        "profile": {
            "SR2": ("sr2-california-free-state", "California Free State", "Kapitel San Francisco", "Der frühe Quellenstand zeigt den japanisch kontrollierten Bay-Area-Plex und seine scharfen sozialen Konflikte."),
            "SR5": ("sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "City by Shadow: San Francisco Metroplex", "gesamter Band", "Der spätere Stand beschreibt den wiedererstarkten Metroplex, Konzerne, Unterwelt und die miteinander verwachsenen Teilstädte."),
        },
        "districts": [
            ("Downtown San Francisco", (37.789, -122.401), "Downtown ist Finanz-, Konzern- und Verwaltungskern des Metroplexes.", "SR5", "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "Kapitel Downtown"),
            ("Oakland", (37.804, -122.271), "Oakland ist ein eigenständiger östlicher Teilraum mit Industrie, Hafen und ausgeprägter Straßenszene.", "SR5", "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "Kapitel Oakland"),
            ("South City", (37.654, -122.408), "South City umfasst die südlichen Industrie-, Wohn- und Verkehrsräume des Plexes.", "SR5", "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "Kapitel South City"),
        ],
        "places": [
            p("NeoNET San Francisco", "Downtown San Francisco", "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "Konzernprofil NeoNET", "NeoNET unterhält einen wichtigen Standort im San-Francisco-Metroplex.", "Konzerne"),
            p("Wuxing San Francisco", "San Francisco Metroplex", "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "Konzernprofil Wuxing", "Wuxing gehört zu den im Metroplex ausdrücklich belegten Konzernakteuren.", "Konzerne"),
            p("The People’s University", "San Francisco Metroplex", "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "The People’s University", "The People’s University ist ein im Stadtquellenband benannter Bildungsstandort.", "Bildung und Kultur"),
        ],
        "people": [
            n("Ancients San Francisco", "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "Gangs – Ancients", "Go-Gang", "San Francisco", "Die Ancients sind im Bay-Area-Plex als Go-Gang präsent.", "group"),
            n("Blindfish", "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "Gangs – Blindfish", "Gang", "San Francisco", "Blindfish ist eine lokale Gang des San-Francisco-Metroplexes.", "group"),
            n("Bloody Tusks", "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "Gangs – Bloody Tusks", "Gang", "San Francisco", "Die Bloody Tusks gehören zur lokalen Ganglandschaft.", "group"),
            n("Chulos", "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "Gangs – Chulos", "Gang", "San Francisco", "Die Chulos sind als Gang im Stadtquellenband belegt.", "group"),
            n("San Francisco Mafia", "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "Organized Crime – Mafia", "Verbrechersyndikat", "San Francisco", "Die Mafia gehört zu den im Metroplex aktiven Unterweltmächten.", "group"),
            n("San Francisco Yakuza", "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "Organized Crime – Yakuza", "Verbrechersyndikat", "San Francisco", "Die Yakuza ist eine zentrale Macht der lokalen organisierten Kriminalität.", "group"),
            n("SFPD Outreach Team", "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex", "SFPD Outreach Team", "Polizeieinheit", "San Francisco", "Das Outreach Team ist eine spezialisierte Einheit der Stadtpolizei.", "group"),
            n("Ares CFS", "sr2-california-free-state", "Ares CFS", "Konzernabteilung", "California Free State", "Ares CFS ist die regionale Ares-Präsenz im kalifornischen Quellenstand.", "group"),
            n("Fuchi CFS", "sr2-california-free-state", "Fuchi CFS", "Historische Konzernabteilung", "California Free State", "Fuchi CFS ist eine historische Konzernpräsenz des frühen Editionsstands.", "group"),
            n("MCT California", "sr2-california-free-state", "MCT California", "Konzernabteilung", "California Free State", "MCT California ist als regionale Mitsuhama-Struktur belegt.", "group"),
            n("Yamatetsu California", "sr2-california-free-state", "Yamatetsu California", "Historische Konzernabteilung", "California Free State", "Yamatetsu California ist eine historische regionale Konzernstruktur.", "group"),
        ],
    },
    "cheyenne": {
        "name": "Cheyenne", "year": 2078, "center": (41.1400, -104.8202),
        "bounds": [[40.85, -105.15], [41.35, -104.45]], "zoom": 10,
        "books": [
            "sr5-shadows-in-focus-city-by-shadow-cheyenne",
            "sr5-mission-sioux-nation",
            "sr5-shadows-in-focus-sioux-nation",
        ],
        "profile": {
            "SR5": ("sr5-shadows-in-focus-city-by-shadow-cheyenne", "City by Shadow: Cheyenne", "gesamter Band", "Cheyenne ist Hauptstadt der Sioux Nation, Regierungszentrum, Militärstandort und kultureller Brennpunkt."),
        },
        "districts": [
            ("Corporate Zone", (41.135, -104.806), "Die Corporate Zone bündelt die wichtigsten Konzernstandorte und besonders gesicherte Geschäftsflächen.", "SR5", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "The Corporate Zone"),
            ("South Cheyenne", (41.105, -104.817), "South Cheyenne umfasst südliche Wohn-, Gewerbe- und Randbereiche.", "SR5", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Kapitel South Cheyenne"),
            ("Cheyenne Military Complex", (41.155, -104.865), "Der Militärkomplex ist ein strategischer Sicherheits- und Kommandostandort der Sioux Nation.", "SR5", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Cheyenne Military Complex"),
        ],
        "places": [
            p("Council of Chiefs Hall", "Cheyenne", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Council of Chiefs Hall", "Die Halle ist ein zentraler politischer Ort der Sioux Nation.", "Behörden"),
            p("Cheyenne City Hall", "Cheyenne", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Cheyenne City Hall", "Das Rathaus ist der Sitz der kommunalen Verwaltung.", "Behörden"),
            p("University of Cheyenne", "Cheyenne", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "University of Cheyenne", "Die Universität ist ein wichtiger Bildungs- und Forschungsstandort.", "Bildung und Kultur"),
            p("Destiny’s Link Club", "Corporate Zone", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Destiny’s Link Club", "Destiny’s Link Club ist ein vernetzter Ausgeh- und Geschäftstreff.", "Bars und Clubs"),
            p("Little Bighorn Bar", "Cheyenne", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Little Bighorn Bar", "Die Little Bighorn Bar ist ein lokaler Treffpunkt.", "Bars und Kneipen"),
            p("Phoenix’s Tavern", "Cheyenne", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Phoenix’s Tavern", "Phoenix’s Tavern gehört zu den belegten Cheyenner Schattenlokalen.", "Bars und Kneipen"),
            p("Cheyenne Regional Airport", "Cheyenne", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Cheyenne Regional Airport", "Der Regionalflughafen ist ein wichtiger Zugang zur Hauptstadt der Sioux Nation.", "Verkehr", [-104.8118, 41.1557]),
            p("Court Building", "Cheyenne", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Court Building", "Das Gerichtsgebäude gehört zum Regierungs- und Justizkomplex.", "Behörden"),
            p("Healing Winds Club", "Cheyenne", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Healing Winds Club", "Healing Winds ist ein lokaler Club und Treffpunkt.", "Bars und Clubs"),
            p("The Royal Fortune", "Cheyenne", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "The Royal Fortune", "The Royal Fortune ist ein benannter Cheyenner Ausgeh- und Kontaktort.", "Bars und Clubs"),
            p("Vintage Wheels", "Cheyenne", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Vintage Wheels", "Vintage Wheels ist ein lokaler Fahrzeug- und Szenestandort.", "Einkaufen"),
            p("Warpdrive Systems", "Corporate Zone", "sr5-mission-sioux-nation", "Warpdrive Systems", "Warpdrive Systems ist ein in Cheyenne belegter Technologie- und Konzernstandort.", "Konzerne"),
            p("Yahto’s Sports Bar", "Cheyenne", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Yahto’s Sports Bar", "Yahto’s ist eine lokale Sportsbar und ein möglicher Schattenkontaktpunkt.", "Bars und Kneipen"),
            p("Ares District HQ Cheyenne", "Corporate Zone", "sr5-shadows-in-focus-sioux-nation", "Ares – District HQ: Cheyenne", "Das regionale Ares-Hauptquartier bündelt die Konzerninteressen in der Hauptstadt.", "Konzerne"),
            p("Copper and Brass Club", "Cheyenne", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Copper and Brass Club – W. 21st St. and Dey Ave.", "Der Steampunk-Club verlangt passende Kleidung und lässt Anglos nur mit offiziellem Aufenthalts- oder Bürgerstatus ein.", "Bars und Clubs"),
            p("MCT Cheyenne / Elk-Sedge Systems", "Corporate Zone", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "MCT – I-80 and Meridan Ave.", "Mitsuhamas Cheyenner Büros liegen verdeckt unter dem Namen der Tochter Elk-Sedge Systems am östlichen Stadtrand.", "Konzerne"),
            p("Saeder-Krupp Cheyenne", "Corporate Zone", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Saeder-Krupp – W. 18th St. and Carey Ave.", "Das Saeder-Krupp-Gebäude prägt die Downtown-Silhouette nahe den politischen Ratsgebäuden.", "Konzerne"),
            p("Shiawase Cheyenne Headquarters", "Corporate Zone", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Shiawase – Concord Rd. and E. Pershing Blvd.", "Der dreißigstöckige Hauptsitz beherbergt mehrere Shiawase-Sparten und Tochterunternehmen.", "Konzerne"),
            p("Stripes", "Cheyenne Military Complex", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Stripes – Randall Ave. and Rodgers Dr.", "Stripes ist eine Bar für ehemalige und aktive Wildcats im Cheyenne Military Complex.", "Bars und Kneipen"),
        ],
        "people": [
            n("Sioux National Police", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Sioux National Police", "Nationale Polizei", "Sioux Nation", "Die Sioux National Police ist eine der prägenden Sicherheitsorganisationen Cheyennes.", "group"),
            n("Apache Mustangs", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "The Apache Mustangs", "Gang oder Fahrergemeinschaft", "Cheyenne", "Die Apache Mustangs sind als lokale Gruppe belegt.", "group"),
            n("Lakota Mafia", "sr5-shadows-in-focus-city-by-shadow-cheyenne", "Lakota Mafia", "Verbrechersyndikat", "Cheyenne", "Die Lakota Mafia gehört zur organisierten Unterwelt der Stadt.", "group"),
            n("High Plains Coding", "sr5-mission-sioux-nation", "High Plains Coding", "Technologiekonzern", "Cheyenne", "High Plains Coding ist ein in Cheyenne ansässiger Softwarekonzern und Pionier eingebetteter Systeme.", "group", "Corporate Zone"),
        ],
    },
    "karlsruhe": {
        "name": "Karlsruhe", "year": 2080, "center": (49.0069, 8.4037),
        "bounds": [[48.80, 8.10], [49.22, 8.72]], "zoom": 10,
        "books": ["sr2-chrom-dioxin", "sr5-datapuls-karlsruhe"],
        "profile": {
            "SR5": ("sr5-datapuls-karlsruhe", "Datapuls Karlsruhe", "gesamter Band", "Karlsruhe ist Bundeswehr-, Verwaltungs- und Technologiestandort mit militärisch geprägten Teilräumen."),
        },
        "districts": [
            ("C-Ring", (49.008, 8.418), "Der C-Ring ist ein im Quellenband benannter, stark kontrollierter innerer Stadtbereich.", "SR5", "sr5-datapuls-karlsruhe", "Der C-Ring"),
            ("Die Kasernen", (49.026, 8.389), "Die Kasernen bündeln militärische Anlagen und die daran angeschlossene Infrastruktur.", "SR5", "sr5-datapuls-karlsruhe", "Die Kasernen"),
            ("Umliegende Stadtviertel", (49.006, 8.365), "Die umliegenden Viertel bilden den weniger militärisch verdichteten Stadtraum außerhalb der Kernanlagen.", "SR5", "sr5-datapuls-karlsruhe", "Umliegende Stadtviertel"),
        ],
        "places": [
            p("Ahab", "Karlsruhe", "sr5-datapuls-karlsruhe", "Ahab", "Ahab ist ein im Karlsruher Stadtquellenband benannter Schauplatz.", "Sonstige Spots"),
        ],
        "people": [
            n("Rächer des Kaspar Hauser", "sr2-chrom-dioxin", "Rächer des Kaspar Hauser", "Lokale Gruppe", "Karlsruhe", "Die Rächer des Kaspar Hauser sind als regionale Gruppe belegt.", "group"),
        ],
    },
    "new-orleans": {
        "name": "New Orleans", "year": 2082, "center": (29.9511, -90.0715),
        "bounds": [[29.55, -90.55], [30.25, -89.55]], "zoom": 9,
        "books": [
            "sr2-target-smuggler-havens",
            "sr6-shadows-in-focus-easy-come-easy-go-new-orleans",
        ],
        "profile": {
            "SR2": ("sr2-target-smuggler-havens", "Target: Smuggler Havens", "Kapitel New Orleans", "New Orleans ist ein wichtiger Schmugglerhafen mit Voodoo-, Unterwelt- und Flussverbindungen."),
            "SR6": ("sr6-shadows-in-focus-easy-come-easy-go-new-orleans", "Easy Come, Easy Go", "gesamter Band", "Der spätere Quellenstand vertieft Stadtzonen, lokale Wirtschaft und das Leben in der Crescent City."),
        },
        "districts": [
            ("Business District", (29.950, -90.075), "Der Business District bildet den wirtschaftlichen Kern der Stadt.", "SR6", "sr6-shadows-in-focus-easy-come-easy-go-new-orleans", "Business District"),
            ("Business Zone", (29.962, -90.083), "Die Business Zone ist ein besonders kommerziell und konzerngeprägter Teilraum.", "SR6", "sr6-shadows-in-focus-easy-come-easy-go-new-orleans", "Business Zone"),
            ("Lakeview", (30.002, -90.110), "Lakeview zieht sich entlang des Lake Pontchartrain und bildet einen nördlichen Siedlungsraum.", "SR6", "sr6-shadows-in-focus-easy-come-easy-go-new-orleans", "Lakeview"),
            ("The Barrens", (29.980, -90.020), "The Barrens ist ein prekärer und gefährlicher Teilraum außerhalb der wohlhabenden Kernzonen.", "SR6", "sr6-shadows-in-focus-easy-come-easy-go-new-orleans", "The Barrens"),
        ],
        "places": [
            p("Boutique Bougie", "New Orleans", "sr6-shadows-in-focus-easy-come-easy-go-new-orleans", "Boutique Bougie", "Boutique Bougie ist ein im Stadtquellenband benannter Geschäfts- und Szenestandort.", "Einkaufen"),
            p("Liar’s Medium", "New Orleans", "sr6-shadows-in-focus-easy-come-easy-go-new-orleans", "Liar’s Medium", "Liar’s Medium ist ein lokaler Treffpunkt mit Bezug zur magischen und medialen Szene.", "Bars und Clubs"),
        ],
        "people": [
            n("Crescent City Mafia", "sr6-shadows-in-focus-easy-come-easy-go-new-orleans", "The Crescent City Mafia", "Mafiafamilien und -gruppen", "New Orleans", "Die Crescent City Mafia ist eine zentrale Macht der organisierten Unterwelt.", "group"),
            n("The Krewes", "sr6-shadows-in-focus-easy-come-easy-go-new-orleans", "The Krewes", "Lokale Gemeinschaften und Machtgruppen", "New Orleans", "Die Krewes verbinden Tradition, Sozialleben, Politik und lokale Machtinteressen.", "group"),
        ],
    },
    "paris": {
        "name": "Paris", "year": 2083, "center": (48.8566, 2.3522),
        "bounds": [[48.55, 1.95], [49.15, 2.80]], "zoom": 9,
        "books": ["sr3-shadows-of-europe", "sr5-gestohlene-seelen",
                  "sr6-final-bets-paris-grand-tour"],
        "profile": {
            "SR3": ("sr3-shadows-of-europe", "Shadows of Europe", "Kapitel France/Paris", "Paris ist politisches, kulturelles und wirtschaftliches Zentrum Frankreichs mit tiefen Macht- und Klassengegensätzen."),
            "SR6": ("sr6-final-bets-paris-grand-tour", "Final Bets", "Paris Grand Tour", "Der Grand-Tour-Stand erschließt zahlreiche konkrete Pariser Schauplätze, Personen und Gruppen."),
        },
        "districts": [
            ("Quartier Latin", (48.849, 2.344), "Das Quartier Latin ist ein traditionsreicher Bildungs-, Kultur- und Ausgehbezirk.", "SR6", "sr6-final-bets-paris-grand-tour", "Le Quartier Latin"),
            ("Créteil", (48.790, 2.455), "Créteil ist ein südöstlicher Teilraum mit eigener BTL- und Straßenszene.", "SR6", "sr6-final-bets-paris-grand-tour", "Créteil"),
        ],
        "places": [
            p("La Closerie des Lilas", "Paris", "sr6-final-bets-paris-grand-tour", "La Closerie des Lilas", "La Closerie des Lilas ist ein traditionsreicher Pariser Gastronomie- und Treffpunkt.", "Restaurants", [2.3327, 48.8421]),
            p("Institut Médico-Légal de Paris", "Paris", "sr6-final-bets-paris-grand-tour", "L’Institut Médico-Légal de Paris", "Das rechtsmedizinische Institut ist ein wichtiger Ermittlungs- und Missionsschauplatz.", "Medizin"),
            p("Longchamp Racetrack", "Paris", "sr6-final-bets-paris-grand-tour", "Longchamp Racetrack", "Die Rennbahn Longchamp ist Veranstaltungs- und Grand-Tour-Schauplatz.", "Freizeit und Natur", [2.233, 48.858]),
            p("Stade de France", "Paris", "sr6-final-bets-paris-grand-tour", "Stade de France", "Das Stade de France ist eine der großen Arenen des Pariser Plexes.", "Freizeit und Natur", [2.3601, 48.9245]),
            p("The Fairground Museum", "Paris", "sr6-final-bets-paris-grand-tour", "The Fairground Museum", "Das Musée des Arts Forains ist als besonderer Kultur- und Missionsort belegt.", "Bildung und Kultur"),
            p("Au Trésor des Belles", "Paris", "sr6-final-bets-paris-grand-tour", "The Joygirl", "Das exklusive Modegeschäft im 8. Arrondissement dient im Grand-Tour-Plot als Kontakt- und Übergabeort.", "Einkaufen"),
            p("Bibliothèque François Mitterrand", "Paris", "sr6-final-bets-paris-grand-tour", "The French National Library", "Die Nationalbibliothek bewahrt trotz der Matrixcrashs einen außergewöhnlich vollständigen Archivbestand.", "Bildung und Kultur", [2.3765, 48.8337]),
            p("Lutetia Hotel Tunnel", "Paris", "sr6-final-bets-paris-grand-tour", "The Lutetia Hotel Tunnel", "Ein besonders gesicherter Tunnel verbindet das Lutetia Hotel mit unterirdischen Anlagen und einer Bahntrasse.", "Unterwelt"),
            p("Saint-Louis General Hospital", "Paris", "sr6-final-bets-paris-grand-tour", "Saint-Louis General Hospital", "Das Krankenhaus ist ein zentraler medizinischer und forensischer Schauplatz des Grand-Tour-Plots.", "Medizin"),
            p("Link Club Paris", "Paris", "sr5-gestohlene-seelen", "Link Club", "Der Pariser Ableger gehört zur international vernetzten Link-Club-Kette.", "Bars und Clubs"),
        ],
        "people": [
            n("Anise Solange", "sr6-final-bets-paris-grand-tour", "Anise Solange", "Konzernberaterin", "Spinrad Industries", "Anise Solange war Johnny Spinrads langjährige Geschäftsberaterin und führte weite Teile des Konzerns von Lissabon aus."),
            n("Camille Berger", "sr6-final-bets-paris-grand-tour", "Who’s Who – Camille Berger", "Lokale Akteurin", "Paris", "Camille Berger gehört zum Personenbestand des Paris-Grand-Tour-Quellenstands."),
            n("Emil Dietrich", "sr6-final-bets-paris-grand-tour", "Who’s Who – Emil Dietrich", "Lokaler Akteur", "Paris", "Emil Dietrich ist im Pariser Personenbestand belegt."),
            n("Hannibal Aubert", "sr6-final-bets-paris-grand-tour", "Who’s Who – Hannibal Aubert", "Lokaler Akteur", "Paris", "Hannibal Aubert ist ein Pariser Akteur des Grand-Tour-Plots."),
            n("Jonas Quaid", "sr6-final-bets-paris-grand-tour", "Who’s Who – Jonas Quaid", "Lokaler Akteur", "Paris", "Jonas Quaid ist im Pariser Personenbestand belegt."),
            n("Kaori Osada", "sr6-final-bets-paris-grand-tour", "Who’s Who – Kaori Osada", "Lokale Akteurin", "Paris", "Kaori Osada ist im Pariser Personenbestand belegt."),
            n("Monsieur Gris", "sr6-final-bets-paris-grand-tour", "Who’s Who – Monsieur Gris", "Schattenakteur", "Paris", "Monsieur Gris ist ein Pariser Schattenkontakt."),
            n("Thomas Blanc", "sr6-final-bets-paris-grand-tour", "Who’s Who – Thomas Blanc", "Lokaler Akteur", "Paris", "Thomas Blanc ist eine zentrale Person des Paris-Grand-Tour-Quellenstands."),
            n("Hisoka Morita", "sr6-final-bets-paris-grand-tour", "Hisoka Morita", "Yakuza-Berater", "Mitsuhama/Yakuza", "Hisoka Morita ist ein erfahrener Saiko-komon im Umfeld der jüngsten Mitsuhama- und Yakuza-Konflikte."),
            n("House Bourbon-Anjou", "sr6-final-bets-paris-grand-tour", "House Bourbon-Anjou", "Adelshaus", "Frankreich", "Das Haus Bourbon-Anjou ist ein französisch-spanischer Adelszweig mit Anspruchs- und Machtinteressen.", "group"),
            n("House Rohan", "sr6-final-bets-paris-grand-tour", "House Rohan", "Adelshaus", "Bretagne/Paris", "Das wohlhabende Haus Rohan besitzt starke Wirtschaftsverbindungen und Einfluss in der Bretagne und in Paris.", "group"),
            n("MCT HTR Team Paris", "sr6-final-bets-paris-grand-tour", "MCT HTR Team", "High-Threat-Response-Team", "Mitsuhama", "Das achtköpfige MCT-HTR-Team ist eine hochprofessionelle Konzernsicherheitseinheit des Pariser Quellenstands.", "group"),
            n("Paris Vory", "sr6-final-bets-paris-grand-tour", "The Vory", "Verbrechersyndikat", "La Zone", "Die Pariser Vory operiert in La Zone vor allem mit Waffen, Drogen und Menschenhandel.", "group"),
        ],
    },
    "montreal": {
        "name": "Montréal", "year": 2063, "center": (45.5019, -73.5674),
        "bounds": [[45.30, -74.05], [45.75, -73.25]], "zoom": 9,
        "books": ["sr3-shadows-of-north-america"],
        "profile": {
            "SR3": ("sr3-shadows-of-north-america", "Shadows of North America", "Kapitel Québec/Montréal", "Montréal ist ein wichtiges urbanes Zentrum Québecs mit französisch geprägter Politik, Konzern- und Schattenwirtschaft."),
        },
        "districts": [
            ("Montréal Core", (45.502, -73.567), "Der Kernraum bündelt Verwaltung, Wirtschaft, Kultur und die wichtigsten Verkehrsachsen.", "SR3", "sr3-shadows-of-north-america", "Kapitel Montréal"),
        ],
        "places": [],
        "people": [],
    },
    "neo-tokio": {
        "name": "Neo-Tokio", "year": 2072, "center": (35.6762, 139.6503),
        "bounds": [[35.20, 138.90], [36.10, 140.40]], "zoom": 8,
        "books": ["sr3-shadows-of-asia", "sr4-corporate-enclaves",
                  "sr5-run-faster-1st-printing"],
        "profile": {
            "SR3": ("sr3-shadows-of-asia", "Shadows of Asia", "Kapitel Japan", "Der frühe Quellenstand beschreibt den japanischen Machtkern und die Entwicklung des Großraums Tokio."),
            "SR4": ("sr4-corporate-enclaves", "Corporate Enclaves", "Kapitel Neo-Tokyo", "Neo-Tokio ist ein hochverdichteter Konzern-, Regierungs- und Medienplex unter starkem Yakuza-Einfluss."),
        },
        "districts": [
            ("Bunkyō", (35.708, 139.752), "Bunkyō ist Bildungs- und Kulturbezirk und beherbergt den Sitz der Ranken-Ryū.", "SR4", "sr4-corporate-enclaves", "Bunkyo"),
            ("Chiba", (35.607, 140.106), "Chiba bildet einen östlichen Industrie-, Hafen- und Konzernraum des Neo-Tokio-Gebiets.", "SR4", "sr4-corporate-enclaves", "Kapitel Neo-Tokyo"),
            ("Yokohama", (35.444, 139.638), "Yokohama ist ein südlicher Hafen- und Konzernschwerpunkt des Großraums.", "SR4", "sr4-corporate-enclaves", "Kapitel Neo-Tokyo"),
            ("Kanda", (35.691, 139.771), "Kanda ist ein zentraler Geschäfts-, Bildungs- und Szenebezirk.", "SR4", "sr4-corporate-enclaves", "Kanda"),
            ("Minato", (35.658, 139.751), "Minato ist ein hochrangiger Konzern-, Diplomatie- und Hafenbezirk.", "SR4", "sr4-corporate-enclaves", "Minato"),
            ("Toshima", (35.726, 139.716), "Toshima ist ein dichter urbaner Teilraum und Standort des Neo-Tokyo Tower.", "SR4", "sr4-corporate-enclaves", "Toshima"),
            ("Sub-Tokyo", (35.680, 139.700), "Sub-Tokyo bezeichnet die unterirdische Stadt- und Schattenebene unter dem Oberflächenplex.", "SR4", "sr4-corporate-enclaves", "Sub-Tokyo"),
        ],
        "places": [
            p("Ranken-Ryū", "Bunkyō", "sr4-corporate-enclaves", "Ranken-Ryu (Bunkyo)", "Die Ranken-Ryū ist eine im Bezirk Bunkyō belegte Schule beziehungsweise Organisation.", "Bildung und Kultur"),
            p("The Cube Tokyo", "Neo-Tokio", "sr5-run-faster-1st-printing", "The Cube, Tokyo", "The Cube ist ein hochverdichteter urbaner Wohn- und Szenestandort.", "Sonstige Spots"),
            p("Yokogawa Incorporated", "Yokohama", "sr4-corporate-enclaves", "Yokogawa Incorporated", "Yokogawa ist als wichtiger Konzernakteur im Neo-Tokio-Plex belegt.", "Konzerne"),
            p("Chosun Alley", "Sub-Tokyo", "sr4-corporate-enclaves", "Chosun Alley (Sub-Tokyo)", "Chosun Alley ist ein benannter Schauplatz der unterirdischen Stadt.", "Unterwelt"),
            p("Gotoku-ji Temple", "Neo-Tokio", "sr4-corporate-enclaves", "Gotoku-ji Temple (Setagaya)", "Der Gotoku-ji ist ein Tempel- und Magieschauplatz in Setagaya.", "Religion und Magie", [139.647, 35.648]),
            p("Neo-Tokyo Tower", "Toshima", "sr4-corporate-enclaves", "Neo-Tokyo Tower (Toshima)", "Der Neo-Tokyo Tower ist ein markanter Konzern- und Stadtstandort in Toshima.", "Sichtseeing und Monumente"),
            p("Pachinko Street", "Bunkyō", "sr4-corporate-enclaves", "Pachinko Street (Bunkyo)", "Pachinko Street ist ein Vergnügungs- und Unterweltschwerpunkt in Bunkyō.", "Ausgehen"),
            p("Takonashi", "Kanda", "sr4-corporate-enclaves", "Takonashi (Kanda)", "Takonashi ist ein in Kanda belegter lokaler Schauplatz.", "Sonstige Spots"),
            p("The Brazilian Market", "Yokohama", "sr4-corporate-enclaves", "The Brazilian Market (Yokohama)", "Der Brazilian Market ist ein internationaler Markt- und Szenetreff in Yokohama.", "Einkaufen"),
            p("Ueno Park", "Neo-Tokio", "sr4-corporate-enclaves", "Ueno Park", "Ueno Park ist ein großer Kultur-, Freizeit- und öffentlicher Raum.", "Freizeit und Natur", [139.774, 35.715]),
        ],
        "people": [
            n("Kodachi-gumi", "sr4-corporate-enclaves", "Kodachi-gumi", "Yakuza-gumi", "Neo-Tokio", "Das Kodachi-gumi ist eine im Neo-Tokio-Quellenstand belegte Yakuza-Gruppe.", "group"),
            n("Watada-gumi", "sr4-corporate-enclaves", "Watada-gumi", "Yakuza-gumi", "Neo-Tokio", "Das Watada-gumi ist eine der einflussreichen Yakuza-Gruppen des Plexes.", "group"),
            n("Yomi Ryū", "sr4-corporate-enclaves", "Yomi Ryu", "Organisation", "Neo-Tokio", "Yomi Ryū ist eine im Quellenband benannte Neo-Tokio-Organisation.", "group"),
            n("Imperial Household Agency", "sr4-corporate-enclaves", "Imperial Household Agency", "Staatliche Organisation", "Neo-Tokio", "Die Imperial Household Agency ist eine zentrale Institution des imperialen Machtapparats.", "group"),
            n("Mita-gumi", "sr4-corporate-enclaves", "Mita-gumi", "Yakuza-gumi", "Neo-Tokio", "Das Mita-gumi ist eine im Unterweltkapitel belegte Yakuza-Gruppe.", "group"),
            n("Neo-Tokyo Metropolitan Police", "sr4-corporate-enclaves", "Neo-Tokyo Metropolitan Police", "Polizeiorganisation", "Neo-Tokio", "Die Metropolitan Police ist die zentrale öffentliche Sicherheitsorganisation des Plexes.", "group"),
            n("Neo-Tokyo Zoku", "sr4-corporate-enclaves", "Neo-Tokyo Zoku", "Straßengruppe", "Neo-Tokio", "Die Zoku gehören zur mobilen Straßen- und Gangszene des Plexes.", "group"),
            n("Red Ronin", "sr4-corporate-enclaves", "Red Ronin", "Lokale Gruppe", "Neo-Tokio", "Red Ronin ist eine im Quellenband benannte Gruppe.", "group"),
            n("Yakuza Incorporated", "sr4-corporate-enclaves", "Yakuza Incorporated", "Organisiertes Verbrechen", "Neo-Tokio", "Yakuza Incorporated beschreibt eine besonders eng mit Wirtschaft und Konzernen verflochtene Unterweltstruktur.", "group"),
        ],
    },
    "washington-fdc": {
        "name": "Washington FDC", "year": 2080,
        "center": (38.9072, -77.0369),
        "bounds": [[38.70, -77.25], [39.10, -76.80]], "zoom": 10,
        "books": ["sr6-cutting-black"],
        "profile": {
            "SR6": ("sr6-cutting-black", "Cutting Black", "Kapitel UCAS/Washington FDC", "Washington FDC ist politisches Zentrum der UCAS und ein Brennpunkt von Regierung, Geheimdiensten und Konzerninteressen."),
        },
        "districts": [
            ("Federal District of Columbia", (38.907, -77.037), "Der Bundesdistrikt bündelt die wichtigsten politischen und administrativen Institutionen der UCAS.", "SR6", "sr6-cutting-black", "Kapitel Washington FDC"),
        ],
        "places": [],
        "people": [],
    },
    "los-angeles": {
        "name": "Los Angeles", "year": 2072, "center": (34.0522, -118.2437),
        "bounds": [[33.45, -119.05], [34.60, -117.45]], "zoom": 8,
        "books": ["sr2-california-free-state", "sr4-corporate-enclaves",
                  "sr5-gestohlene-seelen", "sr5-schattenlaufer-auflage-1"],
        "profile": {
            "SR2": ("sr2-california-free-state", "California Free State", "Kapitel Los Angeles", "Los Angeles ist ein zersplitterter Medien-, Konzern- und Katastrophenplex der California Free State."),
            "SR4": ("sr4-corporate-enclaves", "Corporate Enclaves", "Kapitel Los Angeles", "Der spätere Stand zeigt Horizon als dominante Macht und den Plex als Bühne permanent vermarkteter Realität."),
        },
        "districts": [
            ("Downtown Los Angeles", (34.052, -118.244), "Downtown ist ein zentraler Verwaltungs-, Medien- und Konzernraum.", "SR4", "sr4-corporate-enclaves", "Kapitel Los Angeles"),
            ("Hollywood", (34.092, -118.329), "Hollywood ist Kern der Unterhaltungs- und SimSinn-Industrie.", "SR4", "sr4-corporate-enclaves", "Kapitel Hollywood"),
            ("San Onofre Radiation Zone", (33.368, -117.555), "San Onofre ist ein verstrahlter Sonder- und Gefahrenraum südlich des Plexes.", "SR4", "sr4-corporate-enclaves", "Kapitel Los Angeles"),
            ("East Los Angeles", (34.023, -118.172), "East Los Angeles ist ein eigenständiger östlicher Wohn-, Gewerbe- und Straßenraum.", "SR4", "sr4-corporate-enclaves", "East Los Angeles"),
            ("Long Beach and South Bay", (33.770, -118.194), "Long Beach und South Bay bilden den südlichen Hafen-, Industrie- und Küstenraum.", "SR4", "sr4-corporate-enclaves", "Long Beach and South Bay"),
            ("Escondido", (33.120, -117.086), "Escondido ist ein südlicher Rand- und Siedlungsraum im erweiterten Los-Angeles-Quellenstand.", "SR2", "sr2-california-free-state", "Escondido"),
        ],
        "places": [
            p("UCLA", "Los Angeles", "sr4-corporate-enclaves", "University of California – Los Angeles", "Die UCLA ist ein bedeutender Bildungs-, Forschungs- und Konzernkontaktpunkt.", "Bildung und Kultur", [-118.4452, 34.0689]),
            p("The Millennium Los Angeles", "Los Angeles", "sr5-schattenlaufer-auflage-1", "The Millennium, Los Angeles", "The Millennium ist ein im Quellenarchiv belegter Los-Angeles-Schauplatz.", "Hotels"),
            p("Amalgamated Studios", "Hollywood", "sr4-corporate-enclaves", "Amalgamated Studios", "Amalgamated Studios ist ein wichtiger Medien- und Produktionsstandort.", "Konzerne"),
            p("Angelic Entertainment", "Hollywood", "sr4-corporate-enclaves", "Angelic Entertainment", "Angelic Entertainment gehört zur Unterhaltungsindustrie des Plexes.", "Konzerne"),
            p("Link Club Los Angeles", "Los Angeles", "sr5-gestohlene-seelen", "Link Club", "Der Los-Angeles-Ableger gehört zur international vernetzten Link-Club-Kette.", "Bars und Clubs"),
        ],
        "people": [
            n("Horizon Group Los Angeles", "sr4-corporate-enclaves", "Kapitel Los Angeles", "Dominanter Medienkonzern", "Los Angeles", "Horizon prägt Wirtschaft, Medien und politische Wahrnehmung des Plexes.", "group"),
            n("California Rangers", "sr2-california-free-state", "California Rangers", "Sicherheitsorganisation", "California Free State", "Die California Rangers sind eine im Los-Angeles-Umfeld aktive Sicherheitsorganisation.", "group"),
        ],
    },
    "bogota": {
        "name": "Bogotá", "year": 2073, "center": (4.7110, -74.0721),
        "bounds": [[4.35, -74.45], [5.05, -73.70]], "zoom": 9,
        "books": ["sr4-war"],
        "profile": {
            "SR4": ("sr4-war", "War!", "Kapitel Bogotá", "Bogotá ist Kriegsschauplatz, Regierungszentrum und umkämpfter Knoten zwischen Konzernen, Militär und Aufständischen."),
        },
        "districts": [
            ("Bogotá War Zone", (4.711, -74.072), "Der Großraum ist von Frontverläufen, befestigten Zonen und wechselnder Kontrolle geprägt.", "SR4", "sr4-war", "Kapitel Bogotá"),
        ],
        "places": [
            p("Capitolio Nacional", "Bogotá", "sr4-war", "Capitolio National", "Das Capitolio Nacional ist ein zentraler politischer und militärischer Bezugspunkt.", "Behörden", [-74.076, 4.598]),
            p("El Hotel del Eldorado", "Bogotá", "sr4-war", "El Hotel del Eldorado", "Das Hotel del Eldorado ist ein im Kriegsquellenband belegter Schauplatz.", "Hotels"),
            p("Museo del Oro", "Bogotá", "sr4-war", "Museo del Oro", "Das Goldmuseum ist Kulturort und möglicher Operationsschauplatz.", "Bildung und Kultur", [-74.072, 4.601]),
            p("Aztechnology Business Complex", "Bogotá", "sr4-war", "Aztechnology Business Complex", "Der Aztechnology Business Complex ist ein befestigter Konzernstandort in der umkämpften Stadt.", "Konzerne"),
            p("Aztechnology Castillos", "Bogotá", "sr4-war", "Aztechnology Castillos", "Die Castillos sind gesicherte Aztechnology-Anlagen im Bogotá-Kriegsraum.", "Konzerne"),
            p("Bogotá Natural Gas Power Plant", "Bogotá", "sr4-war", "Bogotá Natural Gas Power Plant", "Das Erdgaskraftwerk ist ein strategischer Infrastrukturstandort.", "Infrastruktur"),
            p("El Dorado Airport", "Bogotá", "sr4-war", "El Dorado Airport", "El Dorado ist der wichtigste internationale Flughafen und ein strategischer Zugang zur Stadt.", "Verkehr", [-74.1469, 4.7016]),
            p("Guaymaral Airport", "Bogotá", "sr4-war", "Guaymaral Airport", "Der nördliche Flughafen Guaymaral ist ein weiterer taktisch wichtiger Luftverkehrsstandort.", "Verkehr"),
            p("Native Lands Street Clinic", "Bogotá", "sr4-war", "Native Lands Street Clinic", "Die Straßenklinik versorgt Bewohner innerhalb des umkämpften Stadtgebiets.", "Medizin"),
            p("Olaya Cartel Drug Labs", "Bogotá", "sr4-war", "Olaya Cartel Drug Labs", "Die Drogenlabore des Olaya-Kartells sind ein Standort der lokalen Unterwelt.", "Unterwelt"),
            p("Palace of Justice", "Bogotá", "sr4-war", "The Palace of Justice", "Der Justizpalast ist ein politischer, symbolischer und taktischer Ort.", "Behörden"),
            p("Pemex Arcology", "Bogotá", "sr4-war", "The Pemex Arcology", "Die Pemex-Arkologie ist ein großer Konzern- und Versorgungskomplex.", "Konzerne"),
            p("Pontificia Universidad Javeriana", "Bogotá", "sr4-war", "Pontifical Xavierian University", "Die päpstliche Universität ist ein bedeutender Bildungsstandort.", "Bildung und Kultur"),
            p("The Abyss", "Bogotá", "sr4-war", "The Abyss", "The Abyss ist ein im Kriegsquellenband benannter Gefahren- oder Unterweltschauplatz.", "Unterwelt"),
            p("KondOrchid Regional Shopping Center", "Bogotá", "sr4-war", "The KondOrchid Regional Shopping Center", "Das regionale Einkaufszentrum ist ein großer Handels- und Versorgungspunkt.", "Einkaufen"),
            p("War Temple", "Bogotá", "sr4-war", "War Temple", "Der War Temple ist ein religiös und militärisch aufgeladener Schauplatz.", "Religion und Magie"),
        ],
        "people": [
            n("Cauan Silveira", "sr4-war", "Cauan Silveira", "Lokaler Akteur", "Bogotá", "Cauan Silveira ist im Bogotá-Kapitel von War! belegt."),
            n("Carla Prieto", "sr4-war", "Carla Prieto", "Lokale Akteurin", "Bogotá", "Carla Prieto ist im Bogotá-Kriegsquellenstand belegt."),
            n("Raul Chavez", "sr4-war", "Raul Chavez", "Lokaler Akteur", "Bogotá", "Raul Chavez ist als Bogotá-bezogener Akteur belegt."),
            n("Sacred Life, Sacred Death", "sr4-war", "Sacred Life, Sacred Death", "Lokale Organisation", "Bogotá", "Sacred Life, Sacred Death ist eine im Quellenband benannte lokale Organisation.", "group"),
            n("Tsunami", "sr4-war", "Tsunami", "Einsatzgruppe", "Bogotá", "Tsunami ist als Gruppe im Bogotá-Kriegsraum belegt.", "group"),
        ],
    },
    "lagos": {
        "name": "Lagos", "year": 2072, "center": (6.5244, 3.3792),
        "bounds": [[6.20, 2.95], [6.90, 3.85]], "zoom": 9,
        "books": ["sr4-feral-cities", "sr4-street-legends"],
        "profile": {
            "SR4": ("sr4-feral-cities", "Feral Cities", "Kapitel Lagos", "Lagos ist ein riesiger, fragmentierter Küstenplex aus Märkten, Stammesgebieten, Slums, Häfen und gefährlichen Freiräumen."),
        },
        "districts": [
            ("Agege", (6.615, 3.323), "Agege ist ein dichter nördlicher Teilraum mit großen Märkten und ausgeprägter Straßenwirtschaft.", "SR4", "sr4-feral-cities", "Kapitel Agege"),
            ("Surulere", (6.500, 3.350), "Surulere ist ein zentraler urbaner Teilraum des Lagos-Plexes.", "SR4", "sr4-feral-cities", "Kapitel Surulere"),
            ("Lagos Island", (6.455, 3.394), "Lagos Island bildet einen wichtigen Handels-, Hafen- und Verwaltungsraum.", "SR4", "sr4-feral-cities", "Kapitel Lagos"),
            ("Apapa", (6.448, 3.360), "Apapa ist ein wichtiger Hafen-, Industrie- und Logistikraum.", "SR4", "sr4-feral-cities", "Kapitel Apapa"),
            ("Badagry", (6.416, 2.886), "Badagry bildet einen westlichen Küsten- und Grenzraum des Lagos-Plexes.", "SR4", "sr4-feral-cities", "Kapitel Badagry"),
            ("Eti Osa", (6.465, 3.585), "Eti Osa umfasst östliche Küsten-, Wohn- und Entwicklungsgebiete.", "SR4", "sr4-feral-cities", "Kapitel Eti Osa"),
            ("Shomolu", (6.540, 3.387), "Shomolu ist ein dicht besiedelter Festlandteil des Plexes.", "SR4", "sr4-feral-cities", "Kapitel Shomolu"),
            ("Victoria Island", (6.429, 3.421), "Victoria Island ist ein wohlhabender Geschäfts-, Hotel- und Touristenraum.", "SR4", "sr4-feral-cities", "Victoria Island Tourist Guide"),
        ],
        "places": [
            p("Dúdú Dúdú Ọjà", "Agege", "sr4-feral-cities", "Dúdú Dúdú Ọjà (Arms Market, Agege)", "Dúdú Dúdú Ọjà ist ein bedeutender Waffenmarkt in Agege.", "Einkaufen"),
            p("Apapa Medical Center", "Apapa", "sr4-feral-cities", "Apapa Medical Center (Apapa)", "Das Apapa Medical Center ist eine wichtige medizinische Einrichtung des Hafenbezirks.", "Medizin"),
            p("Aztechnology Africa", "Lagos", "sr4-feral-cities", "Aztechnology Africa", "Aztechnology Africa unterhält einen bedeutenden Standort im Lagos-Plex.", "Konzerne"),
            p("Porto Novo Luxury Hotel", "Apapa", "sr4-feral-cities", "The Porto Novo Luxury Hotel (Apapa)", "Das Porto Novo ist ein Luxushotel im Hafenraum Apapa.", "Hotels"),
            p("The Three Friends", "Lagos Mainland", "sr4-feral-cities", "The Three Friends (Lagos Mainland)", "The Three Friends ist ein lokaler Treffpunkt auf dem Festland.", "Bars und Kneipen"),
        ],
        "people": [
            n("Akuchi", "sr4-street-legends", "Akuchi", "Lokaler Akteur", "Lagos", "Akuchi ist als Lagos-bezogener Akteur im Quellenarchiv belegt."),
            n("Anwuma Bavole", "sr4-feral-cities", "Anwuma Bavole", "Lokale Akteurin", "Lagos", "Anwuma Bavole ist im Lagos-Kapitel von Feral Cities belegt."),
            n("Area Boys", "sr4-feral-cities", "Area Boys", "Straßengruppe", "Lagos", "Die Area Boys gehören zur Straßenszene und lokalen Machtlandschaft des Plexes.", "group"),
            n("Níròjú Ikú", "sr4-feral-cities", "Níròjú Ikú", "Lokale Gruppe", "Lagos", "Níròjú Ikú ist eine im Lagos-Quellenstand benannte Gruppe.", "group"),
            n("Why Not", "sr4-feral-cities", "Why Not (Victoria Island)", "Lokale Gruppe", "Victoria Island", "Why Not ist eine auf Victoria Island belegte lokale Gruppe.", "group", "Victoria Island"),
        ],
    },
    "detroit": {
        "name": "Detroit", "year": 2080, "center": (42.3314, -83.0458),
        "bounds": [[41.95, -83.55], [42.75, -82.55]], "zoom": 9,
        "books": ["sr2-target-ucas", "sr6-cutting-black"],
        "profile": {
            "SR2": ("sr2-target-ucas", "Target: UCAS", "Kapitel Detroit", "Detroit ist Automobil-, Industrie- und Ares-Machtzentrum der UCAS."),
            "SR6": ("sr6-cutting-black", "Cutting Black", "Kapitel Detroit", "Der spätere Stand zeigt Detroit im Zentrum der Blackout- und Ares-Krise."),
        },
        "districts": [
            ("Detroit Core", (42.331, -83.046), "Der Stadtkern bündelt Verwaltung, Industrie und die wichtigsten Ares-Einrichtungen.", "SR6", "sr6-cutting-black", "Kapitel Detroit"),
            ("Belle Isle", (42.340, -82.986), "Belle Isle ist ein Insel- und Parkraum im Detroit River mit eigener strategischer Bedeutung.", "SR6", "sr6-cutting-black", "Belle Isle"),
            ("Dearborn", (42.322, -83.176), "Dearborn ist ein westlicher Industrie- und Siedlungsschwerpunkt des Detroit-Plexes.", "SR6", "sr6-cutting-black", "Dearborn"),
            ("Windsor", (42.314, -83.036), "Windsor liegt auf der kanadischen Flussseite und ist eng mit Detroits Verkehrs- und Grenzlage verbunden.", "SR6", "sr6-cutting-black", "Windsor"),
        ],
        "places": [
            p("Ares Macrotechnology Detroit", "Detroit", "sr2-target-ucas", "Kapitel Detroit/Ares", "Detroit ist der historische Hauptmacht- und Industriestandort von Ares Macrotechnology.", "Konzerne"),
        ],
        "people": [
            n("Ares Macrotechnology", "sr2-target-ucas", "Kapitel Detroit", "Megakonzern", "Detroit", "Ares ist die prägende Konzernmacht Detroits.", "group", "Ares Macrotechnology Detroit"),
            n("Motor City Madmen", "sr6-cutting-black", "Motor City Madmen", "Lokale Gruppe", "Detroit", "Die Motor City Madmen sind eine im Detroit-Quellenstand benannte Gruppe.", "group"),
        ],
    },
    "atlanta": {
        "name": "Atlanta", "year": 2080, "center": (33.7490, -84.3880),
        "bounds": [[33.35, -84.85], [34.15, -83.90]], "zoom": 9,
        "books": ["sr1-the-neo-anarchist-s-guide-to-north-america",
                  "sr5-gestohlene-seelen", "sr6-cutting-black"],
        "profile": {
            "SR1": ("sr1-the-neo-anarchist-s-guide-to-north-america", "The Neo-Anarchist’s Guide to North America", "Kapitel Atlanta", "Atlanta ist Hauptstadt der CAS und ein Zentrum von Politik, Konzernen und südlicher Machtkultur."),
            "SR6": ("sr6-cutting-black", "Cutting Black", "Kapitel CAS/Atlanta", "Der Blackout-Stand ergänzt Krisenfolgen, politische Spannungen und aktuelle Akteure."),
        },
        "districts": [
            ("Atlanta Core", (33.749, -84.388), "Der Kern bündelt Regierung, Konzernzentralen und kulturelle Einrichtungen der CAS-Hauptstadt.", "SR1", "sr1-the-neo-anarchist-s-guide-to-north-america", "Kapitel Atlanta"),
            ("Buckhead", (33.838, -84.379), "Buckhead ist ein besonders wohlhabender und stark gesicherter Wohn- und Geschäftsbezirk.", "SR1", "sr1-the-neo-anarchist-s-guide-to-north-america", "Buckhead (AA)"),
            ("Decatur", (33.775, -84.296), "Decatur ist ein eigenständiger östlicher Teilraum des Atlanta-Plexes.", "SR1", "sr1-the-neo-anarchist-s-guide-to-north-america", "Decatur (B)"),
            ("Douglasville", (33.751, -84.747), "Douglasville bildet einen westlichen Rand- und Siedlungsraum.", "SR1", "sr1-the-neo-anarchist-s-guide-to-north-america", "Douglasville (C)"),
            ("Southtown", (33.680, -84.410), "Southtown ist ein südlicher, deutlich schwächer eingestufter Teilraum des Plexes.", "SR1", "sr1-the-neo-anarchist-s-guide-to-north-america", "Southtown (E)"),
        ],
        "places": [
            p("Link Club Atlanta", "Atlanta", "sr5-gestohlene-seelen", "Link Club", "Der Atlanta-Ableger gehört zur internationalen Link-Club-Kette.", "Bars und Clubs"),
            p("Atlanta Black Market", "Atlanta", "sr1-the-neo-anarchist-s-guide-to-north-america", "Black Market", "Der Schwarze Markt ist ein zentraler Umschlagplatz der lokalen Schattenwirtschaft.", "Einkaufen"),
        ],
        "people": [],
    },
    "portland": {
        "name": "Portland", "year": 2054, "center": (45.5152, -122.6784),
        "bounds": [[45.20, -123.05], [45.85, -122.25]], "zoom": 9,
        "books": ["sr2-tir-tairngire"],
        "profile": {
            "SR2": ("sr2-tir-tairngire", "Tír Tairngire", "Kapitel Portland", "Portland ist abgeschottetes Tor und wichtigster urbaner Macht- und Handelsraum des Tír Tairngire."),
        },
        "districts": [
            ("Portland Core", (45.515, -122.678), "Der Kernraum ist politisches, wirtschaftliches und logistisches Zentrum der abgeschotteten Stadt.", "SR2", "sr2-tir-tairngire", "Kapitel Portland"),
        ],
        "places": [
            p("Telestrian Industries Portland", "Portland", "sr2-tir-tairngire", "Telestrian Industries Corporation", "Telestrian Industries gehört zu den prägenden Konzernakteuren Portlands.", "Konzerne"),
            p("New Dawn Corporation", "Portland", "sr2-tir-tairngire", "New Dawn Corporation", "New Dawn ist als Portlander Konzernstandort belegt.", "Konzerne"),
            p("Pat O’Grady’s", "Portland", "sr2-tir-tairngire", "Pat O’Grady’s", "Pat O’Grady’s ist ein im Portland-Quellenstand benanntes Lokal.", "Bars und Kneipen"),
            p("Portland Civic Stadium", "Portland", "sr2-tir-tairngire", "Portland Civic Stadium", "Das Civic Stadium ist ein großer Sport- und Veranstaltungsort.", "Freizeit und Natur"),
            p("Portland Executel", "Portland", "sr2-tir-tairngire", "Portland Executel", "Das Executel ist ein Geschäfts- und Übernachtungsstandort.", "Hotels"),
            p("West Slope Inn", "Portland", "sr2-tir-tairngire", "West Slope Inn", "Das West Slope Inn ist eine im Stadtprofil benannte Unterkunft.", "Hotels"),
            p("Willamette Hospital", "Portland", "sr2-tir-tairngire", "Willamette Hospital", "Das Willamette Hospital ist eine wichtige medizinische Einrichtung.", "Medizin"),
            p("Willamette University", "Portland", "sr2-tir-tairngire", "Willamette University", "Die Willamette University ist ein Bildungs- und Forschungsstandort.", "Bildung und Kultur"),
        ],
        "people": [
            n("Telestrian Industries", "sr2-tir-tairngire", "Telestrian Industries Corporation", "Konzern", "Portland", "Telestrian Industries ist eine der wichtigsten lokalen Konzernmächte.", "group", "Telestrian Industries Portland"),
            n("Ares Macrotechnologies Tír Tairngire", "sr2-tir-tairngire", "Ares Macrotechnologies (Tír Tairngire)", "Konzernabteilung", "Portland", "Ares unterhält im Tír und in Portland eine eigene Konzernpräsenz.", "group"),
            n("Knight Errant Tír Tairngire", "sr2-tir-tairngire", "Knight Errant (Tír Tairngire)", "Sicherheitsorganisation", "Portland", "Knight Errant ist als Sicherheitsakteur im Portlander Quellenstand belegt.", "group"),
            n("Matsushima Computer", "sr2-tir-tairngire", "Matsushima Computer", "Konzern", "Portland", "Matsushima Computer gehört zu den im Quellenband aufgeführten Konzernakteuren.", "group"),
        ],
    },
    "wien": {
        "name": "Wien", "year": 2080, "center": (48.2082, 16.3738),
        "bounds": [[47.85, 15.95], [48.55, 16.85]], "zoom": 9,
        "books": ["sr2-walzer-punks-schwarzes-ice",
                  "sr4-euro-war-antiques", "sr5-datapuls-osterreich"],
        "profile": {
            "SR2": ("sr2-walzer-punks-schwarzes-ice", "Walzer, Punks & Schwarzes Ice", "Kapitel Wien", "Der frühe Quellenstand zeigt Wien als barocke, politische und zugleich subkulturelle Schattenmetropole."),
            "SR5": ("sr5-datapuls-osterreich", "Datapuls Österreich", "Kapitel Wien", "Der spätere Stand vertieft den Wiener Sprawl, Machtgruppen und besondere Institutionen."),
        },
        "districts": [
            ("Wiener Sprawl", (48.208, 16.374), "Der Wiener Sprawl verbindet historische Kernstadt, dichte Außenbezirke und stark unterschiedliche Sicherheitsräume.", "SR5", "sr5-datapuls-osterreich", "Der Wiener Sprawl"),
        ],
        "places": [
            p("Dr.-Singer-Schule", "Wien", "sr5-datapuls-osterreich", "Dr.-Singer-Schule", "Die Dr.-Singer-Schule ist eine im österreichischen Quellenstand belegte Institution.", "Bildung und Kultur"),
            p("Brimstone Memorial Battery", "Wiener Umland", "sr4-euro-war-antiques", "Brimstone", "Eine frühere Flugkörperbatterie nahe Wien wurde nach Ende ihrer Einsatzzeit Teil eines Gedenkparks.", "Sichtseeing und Monumente"),
        ],
        "people": [
            n("Glock Gruppe", "sr5-datapuls-osterreich", "Glock Gruppe", "Konzern- und Sicherheitsgruppe", "Österreich", "Die Glock Gruppe ist als österreichische Machtgruppe mit Wien-Bezug belegt.", "group"),
        ],
    },
}


def update_city_registry() -> None:
    path = ROOT / "data/cities.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    by_id = {city["id"]: city for city in registry["cities"]}
    for city_id, config in CONFIGS.items():
        by_id[city_id] = {
            "id": city_id,
            "name": config["name"],
            "manifest": f"data/{city_id}/manifest.json",
            "year": config["year"],
        }
    existing = [city["id"] for city in registry["cities"]]
    order = existing + [city_id for city_id in CONFIGS if city_id not in existing]
    registry["cities"] = [by_id[city_id] for city_id in order]
    write_json(path, registry)


def main() -> None:
    missing = {
        work_id
        for config in CONFIGS.values()
        for work_id in config["books"]
        if work_id not in WORKS
    }
    if missing:
        raise SystemExit(f"Unbekannte Werk-IDs: {sorted(missing)}")
    for city_id, config in CONFIGS.items():
        build_city(city_id, config)
        print(f"OK {city_id}")
    update_city_registry()


if __name__ == "__main__":
    main()
