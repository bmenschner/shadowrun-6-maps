#!/usr/bin/env python3
"""Build city packages for the third source-import wave.

The package deliberately publishes only stable names supported by a
city-focused or regional source. District coordinates are navigation anchors;
places without a reliable address remain catalogue-only.
"""

from __future__ import annotations

import json

from build_us_city_content import write_json
from build_wave1_city_packages import ROOT, WORKS, build_city, n, p


def profile(edition, book, title, summary):
    return {edition: (book, title, "Stadt- oder Regionalkapitel", summary)}


CONFIGS = {
    "kairo": {
        "name": "Kairo", "year": 2083, "center": (30.0444, 31.2357),
        "bounds": [[29.65, 30.75], [30.35, 31.85]], "zoom": 9,
        "books": ["sr6-risk-rewards-cairo-campaign", "sr4-dawn-of-the-artifacts-5-artifacts-unbound"],
        "profile": profile("SR6", "sr6-risk-rewards-cairo-campaign", "Risk & Rewards: Cairo Campaign",
                           "Kairo ist ein weit ausgreifender Sprawl zwischen Konzernen, staatlichen Sicherheitsorganen, verbotenen Kulten und einer lebhaften Schattenwirtschaft."),
        "districts": [
            ("Ein Shams", (30.131, 31.324), "Ein Shams liegt nordwestlich des Flughafens und ist ein dicht bebautes Gebiet mit niedrigen Einkommen und starker Gangpräsenz.", "SR6", "sr6-risk-rewards-cairo-campaign", "Ein Shams"),
            ("El Korba", (30.091, 31.323), "El Korba verbindet historische und moderne Architektur und gilt als besonders markantes Stadtviertel.", "SR6", "sr6-risk-rewards-cairo-campaign", "El Korba"),
            ("Mokattam", (30.020, 31.304), "Mokattam liegt auf den Höhen östlich des Zentrums und besitzt starke magische Bezüge.", "SR6", "sr6-risk-rewards-cairo-campaign", "Mokattam"),
            ("Old Cairo", (30.006, 31.230), "Old Cairo fasst die historisch gewachsenen Viertel und ihre religiösen und kulturellen Konflikte zusammen.", "SR6", "sr6-risk-rewards-cairo-campaign", "Old Cairo"),
            ("Wust El Balad", (30.046, 31.239), "Wust El Balad bildet den verdichteten Innenstadtbereich Kairos.", "SR6", "sr6-risk-rewards-cairo-campaign", "Wust El Balad"),
            ("Zamalek", (30.061, 31.219), "Zamalek ist ein wohlhabender Inselbezirk mit Diplomatie, Hotels und gehobenem Nachtleben.", "SR6", "sr6-risk-rewards-cairo-campaign", "Zamalek"),
        ],
        "places": [
            p("Alhak Hospital", "Ein Shams", "sr6-risk-rewards-cairo-campaign", "Alhak Hospital", "Das geschlossene Krankenhaus war Mitsuhamas erster großer Vorstoß in den nordafrikanischen Medizinmarkt.", "Medizin"),
            p("Al-Hayat Althaania Market", "Kairo", "sr6-risk-rewards-cairo-campaign", "Althaania Market", "Der auch Second Life Market genannte wandernde Markt bleibt jeweils nur wenige Tage in einem Stadtteil.", "Einkaufen"),
            p("EmSat Nasr City Office", "Nasr City", "sr6-risk-rewards-cairo-campaign", "EmSat Nasr City Office", "Der hoch aufragende EmSat-Standort ist ein regionales Kommunikationszentrum.", "Konzerne"),
            p("Equinox", "Kairo", "sr6-risk-rewards-cairo-campaign", "Equinox", "Equinox ist ein rund um die Uhr geöffneter, mehrgeschossiger Untergrundclub am Rand des Kernsprawls.", "Bars und Clubs"),
            p("Gnostic Medicine", "Kairo", "sr6-risk-rewards-cairo-campaign", "Gnostic Medicine", "Die kleine medizinische Sammlung dokumentiert die Geschichte gnostischer Heilkunst.", "Medizin"),
            p("Golden Frond Hotel", "Nasr City", "sr6-risk-rewards-cairo-campaign", "Golden Frond Hotel", "Das Resort- und Konferenzhotel richtet sich an wohlhabende und einflussreiche Gäste.", "Hotels"),
            p("Grand Nile Tower", "Kairo", "sr6-risk-rewards-cairo-campaign", "Grand Nile Tower", "Der traditionsreiche Luxushotelturm ist ein Wahrzeichen am Nilufer.", "Hotels", [31.232, 30.034]),
            p("Museum of Cairo", "Kairo", "sr6-risk-rewards-cairo-campaign", "Museum of Cairo", "Das Museum bewahrt bedeutende Relikte der ägyptischen Geschichte.", "Bildung und Kultur"),
            p("Ptah’s Spire", "El Khalafawy", "sr6-risk-rewards-cairo-campaign", "Ptah’s Spire", "Der gesicherte Wohnturm besitzt ein Landedeck und liegt nahe dem El-Khalafawy-Platz.", "Wohnen"),
            p("Ramses Plate", "Kairo", "sr6-risk-rewards-cairo-campaign", "Ramses Plate", "Das Restaurant verfügt über private Speiseräume und dient als diskreter Treffpunkt.", "Restaurants"),
            p("Ramses Station", "Kairo", "sr4-dawn-of-the-artifacts-5-artifacts-unbound", "Ramses Station", "Der zentrale Bahnhof ist ein wichtiger Verkehrs- und Übergangspunkt.", "Verkehr", [31.247, 30.063]),
            p("Red Sunrise Bar", "Al Marj", "sr6-risk-rewards-cairo-campaign", "Casanova’s Job", "Die Red Sunrise Bar ist ein Treffpunkt für Fixer und Auftraggeber im nördlichen Sprawl.", "Bars und Kneipen"),
            p("Sphinx Airport", "Westkairo", "sr6-risk-rewards-cairo-campaign", "Sphinx Airport", "Der westliche internationale Flughafen bedient Linien-, Privat- und Frachtverkehr.", "Verkehr", [30.8957, 30.1081]),
            p("The Garden of Plenty", "Kairo", "sr6-risk-rewards-cairo-campaign", "The Garden of Plenty", "Der Garten ist ein benannter Schauplatz der Kairo-Kampagne.", "Freizeit und Natur"),
            p("The Night Souk", "Kairo", "sr6-risk-rewards-cairo-campaign", "The Night Souk", "Der Nachtmarkt gehört zu den wichtigen Handels- und Kontaktorten des Sprawls.", "Einkaufen"),
            p("The Well of Ptah", "Mit Rahina", "sr6-risk-rewards-cairo-campaign", "The Well of Ptah", "Ein ehemaliges Versteck des Isis-Kults wurde zu einem kleinen Ptah-Tempel umgebaut.", "Religion und Magie"),
            p("Treats of the Nile", "Kairo", "sr6-risk-rewards-cairo-campaign", "Treats of the Nile", "Treats of the Nile ist ein in der Kampagne belegter Gastronomiestandort.", "Restaurants"),
        ],
        "people": [
            n("Egyptian National Police", "sr6-risk-rewards-cairo-campaign", "Egyptian National Police", "Staatliche Sicherheitsorganisation", "Ägypten", "Mehrere eng verzahnte Ministerien bilden die nationale Polizei.", "group"),
            n("Cairo Police", "sr6-risk-rewards-cairo-campaign", "The Cairo Police", "Lokale Polizeistruktur", "Kairo", "Kairos Polizeiarbeit verteilt sich auf staatliche Aufsicht und private Anbieter.", "group"),
            n("Cult of Isis", "sr6-risk-rewards-cairo-campaign", "The Cult of Isis", "Verbotener magischer Kult", "Kairo", "Der Isis-Kult folgt verbotenen alten Wegen und arbeitet deshalb im Untergrund.", "group"),
            n("Sphinx Kings", "sr6-risk-rewards-cairo-campaign", "Telling Timothy", "Gang", "Kairo", "Die Sphinx Kings sind eine im Kampagnenmaterial belegte lokale Gang.", "group"),
            n("Timothy Telestrian", "sr6-risk-rewards-cairo-campaign", "Timothy Telestrian", "Konzernakteur", "Telestrian Industries", "Timothy Telestrian verfolgt in Kairo eigene Konzern- und Familieninteressen."),
            n("Leilani Acheampong", "sr6-risk-rewards-cairo-campaign", "Leilani Acheampong", "Fixerin und Konzernverbindung", "Telestrian Technologies", "Leilani Acheampong arbeitet in Kairo als hochrangige Fixerin und Johnson."),
            n("Yoon Yu-Na", "sr6-risk-rewards-cairo-campaign", "Yoon Yu-Na", "Lokale Akteurin", "Kairo", "Yoon Yu-Na gehört zum Personenbestand der Kairo-Kampagne."),
            n("Nafakh Alrimal", "sr6-risk-rewards-cairo-campaign", "Part One", "Gang", "Kairo", "Die als Blowing Sand bezeichnete Gang setzt lokale Fixer unter Druck.", "group"),
        ],
    },
    "metropole": {
        "name": "Metrópole", "year": 2078, "center": (-23.20, -45.25),
        "bounds": [[-24.10, -47.20], [-21.80, -42.50]], "zoom": 7,
        "books": ["sr3-lateinamerika-in-den-schatten-v1-0", "sr5-shadows-in-focus-city-by-shadow-metropole"],
        "profile": {
            "SR3": ("sr3-lateinamerika-in-den-schatten-v1-0", "Lateinamerika in den Schatten", "Kapitel Amazonien", "Der südostbrasilianische Megasprawl verbindet die früher getrennten Metropolen São Paulo und Rio de Janeiro."),
            "SR5": ("sr5-shadows-in-focus-city-by-shadow-metropole", "City by Shadow: Metrópole", "gesamter Band", "Metrópole ist ein riesiger, sozial zerrissener Sprawl mit Amazonien, Konzernen, Gangs und stark ausgeprägten lokalen Machtzentren."),
        },
        "districts": [
            ("São Paulo", (-23.5505, -46.6333), "São Paulo ist der westliche Wirtschafts-, Industrie- und Konzernschwerpunkt von Metrópole.", "SR5", "sr5-shadows-in-focus-city-by-shadow-metropole", "São Paulo"),
            ("Rio de Janeiro", (-22.9068, -43.1729), "Rio de Janeiro ist Küsten-, Medien-, Tourismus- und Machtzentrum des Sprawls.", "SR5", "sr5-shadows-in-focus-city-by-shadow-metropole", "Rio de Janeiro"),
            ("Eastern Centro", (-22.94, -43.12), "Eastern Centro ist ein eigener politischer Teilraum innerhalb des östlichen Plexes.", "SR5", "sr5-shadows-in-focus-city-by-shadow-metropole", "Mayor of Eastern Centro"),
        ],
        "places": [
            p("Grand Palm Hotel", "Metrópole", "sr5-shadows-in-focus-city-by-shadow-metropole", "Grand Palm Hotel", "Das Grand Palm Hotel ist ein im Stadtquellenband benannter Unterkunfts- und Treffpunkt.", "Hotels"),
            p("Quimbanda Street", "Metrópole", "sr5-shadows-in-focus-city-by-shadow-metropole", "Quimbanda Street", "Quimbanda Street ist ein stark magisch und subkulturell geprägter Straßenzug.", "Religion und Magie"),
            p("University of São Paulo", "São Paulo", "sr5-shadows-in-focus-city-by-shadow-metropole", "University of Sao Paulo", "Die Universität ist ein bedeutender Bildungs- und Forschungsstandort.", "Bildung und Kultur", [-46.730, -23.559]),
            p("Paredão", "Metrópole", "sr5-shadows-in-focus-city-by-shadow-metropole", "Paredão", "Paredão ist ein benannter lokaler Schauplatz.", "Sonstige Spots"),
        ],
        "people": [
            n("César Moreira", "sr5-shadows-in-focus-city-by-shadow-metropole", "César Moreira", "Lokaler Akteur", "Metrópole", "César Moreira gehört zu den wichtigen Personen des Stadtquellenbands."),
            n("Kalina Stoykovska", "sr5-shadows-in-focus-city-by-shadow-metropole", "Kalina Stoykovska", "Lokale Akteurin", "Metrópole", "Kalina Stoykovska gehört zum Personenbestand des Plexes."),
            n("Lazaro Machado", "sr5-shadows-in-focus-city-by-shadow-metropole", "Lazaro Machado", "Lokaler Akteur", "Metrópole", "Lazaro Machado ist ein im Stadtquellenband belegter Akteur."),
            n("Nelson Bastos", "sr5-shadows-in-focus-city-by-shadow-metropole", "Nelson Bastos", "Lokaler Akteur", "Metrópole", "Nelson Bastos gehört zu den Movers and Shakers des Plexes."),
            n("Comando Verde", "sr5-shadows-in-focus-city-by-shadow-metropole", "Comando Verde", "Unterweltorganisation", "Metrópole", "Comando Verde ist eine bedeutende kriminelle Macht des Sprawls.", "group"),
            n("Irmandade Quiumbandista", "sr3-lateinamerika-in-den-schatten-v1-0", "Irmandade Quiumbandista", "Magische Bruderschaft", "Amazonien", "Die Bruderschaft ist eng mit der regionalen Quimbanda-Tradition verbunden.", "group"),
        ],
    },
    "butte": {
        "name": "Butte", "year": 2078, "center": (46.0038, -112.5348),
        "bounds": [[45.80, -112.80], [46.22, -112.25]], "zoom": 10,
        "books": ["sr5-shadows-in-focus-city-by-shadow-butte", "sr5-mission-sioux-nation"],
        "profile": profile("SR5", "sr5-shadows-in-focus-city-by-shadow-butte", "City by Shadow: Butte",
                           "Butte ist eine kompakte Bergbau- und Industriestadt der Sioux Nation mit klar geschichteten Bezirken und starker Unterwelt."),
        "districts": [
            ("Emerald District", (46.018, -112.525), "Der Emerald District ist einer der benannten sozialen und wirtschaftlichen Stadtbereiche.", "SR5", "sr5-shadows-in-focus-city-by-shadow-butte", "Emerald District"),
            ("Granite District", (46.009, -112.545), "Der Granite District bewahrt den rauen Bergbau- und Arbeitercharakter Buttes.", "SR5", "sr5-shadows-in-focus-city-by-shadow-butte", "Granite District"),
            ("Platinum District", (45.995, -112.522), "Der Platinum District ist der wohlhabendere und stärker kontrollierte Teilraum.", "SR5", "sr5-shadows-in-focus-city-by-shadow-butte", "Platinum District"),
        ],
        "places": [
            p("Arizona Marketplace", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "Arizona Marketplace", "Der Marketplace ist ein lokaler Handels- und Versorgungspunkt.", "Einkaufen"),
            p("Big Cheese", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "Big Cheese", "Big Cheese ist ein benannter Gastronomie- und Treffpunkt.", "Restaurants"),
            p("Copper Stadium", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "Copper Stadium", "Das Stadion ist ein Sport- und Veranstaltungszentrum.", "Freizeit und Natur"),
            p("Finlen Hotel", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "Finlen Hotel", "Das Finlen ist ein traditionsreicher Hotelstandort.", "Hotels", [-112.536, 46.013]),
            p("Montana Tech", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "Montana Tech", "Montana Tech ist Buttes wichtiger Bildungs- und Forschungsstandort.", "Bildung und Kultur", [-112.558, 46.012]),
            p("Moon Rise Tavern", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "Moon Rise Tavern", "Die Moon Rise Tavern ist ein lokaler Schatten- und Szenetreff.", "Bars und Kneipen"),
            p("Phantasmagoria", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "Phantasmagoria", "Phantasmagoria ist ein benannter Vergnügungsort.", "Bars und Clubs"),
            p("Proving Grounds", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "Proving Grounds", "Die Proving Grounds dienen Tests, Training und Wettbewerb.", "Sicherheit und Justiz"),
            p("Shiawase Medical", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "Shiawase Medical", "Shiawase betreibt einen medizinischen Konzernstandort in Butte.", "Medizin"),
            p("Summit Valley Airport", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "Summit Valley Airport", "Der Flughafen bindet die Bergbaustadt an regionale und überregionale Verkehrswege an.", "Verkehr", [-112.497, 45.955]),
            p("The Cabbage Patch", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "The Cabbage Patch", "The Cabbage Patch ist ein lokaler Schauplatz.", "Sonstige Spots"),
            p("The Mai Wah", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "The Mai Wah", "Das Mai Wah ist ein historischer und kultureller Standort.", "Bildung und Kultur"),
            p("The Mineral Museum", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "The Mineral Museum", "Das Mineral Museum dokumentiert Bergbau, Geologie und Stadtgeschichte.", "Bildung und Kultur"),
            p("The Rabbit Hole", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "The Rabbit Hole", "The Rabbit Hole ist ein lokaler Szenetreff.", "Bars und Clubs"),
            p("Tilt", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "Tilt", "Tilt ist ein benannter Vergnügungsstandort.", "Bars und Clubs"),
            p("White Buffalo", "Butte", "sr5-shadows-in-focus-city-by-shadow-butte", "White Buffalo", "White Buffalo ist ein lokaler Treffpunkt.", "Bars und Kneipen"),
        ],
        "people": [
            n("Lakota Mafia", "sr5-shadows-in-focus-city-by-shadow-butte", "Lakota Mafia", "Verbrechersyndikat", "Butte", "Die Lakota Mafia ist eine zentrale Unterweltmacht der Stadt.", "group"),
            n("Butte Vory", "sr5-shadows-in-focus-city-by-shadow-butte", "Vory", "Verbrechersyndikat", "Butte", "Die Vory unterhält eine lokale Präsenz.", "group"),
            n("Druid’s Wolves", "sr5-shadows-in-focus-city-by-shadow-butte", "Druid’s Wolves", "Lokale Gruppe", "Butte", "Druid’s Wolves ist eine im Stadtquellenband benannte Gruppe.", "group"),
            n("The Lost", "sr5-shadows-in-focus-city-by-shadow-butte", "The Lost", "Lokale Gruppe", "Butte", "The Lost gehört zur lokalen Gruppen- und Ganglandschaft.", "group"),
            n("Butte Street Gangs", "sr5-shadows-in-focus-city-by-shadow-butte", "The Street Gangs", "Gangmilieu", "Butte", "Mehrere Straßengangs konkurrieren um Einfluss in Butte.", "group"),
        ],
    },
    "casablanca-rabat": {
        "name": "Casablanca-Rabat", "year": 2078, "center": (33.78, -7.10),
        "bounds": [[33.40, -8.05], [34.20, -6.35]], "zoom": 8,
        "books": ["sr5-shadows-in-focus-casablanca-rabat", "sr5-shadows-in-focus-morocco"],
        "profile": profile("SR5", "sr5-shadows-in-focus-casablanca-rabat", "Shadows in Focus: Casablanca-Rabat",
                           "Der Doppelplex verbindet Marokkos Wirtschaftsmetropole Casablanca mit dem politischen Zentrum Rabat und den dazwischenliegenden Küstenräumen."),
        "districts": [
            ("Casablanca", (33.5731, -7.5898), "Casablanca ist Wirtschafts-, Hafen- und Konzernzentrum des Doppelplexes.", "SR5", "sr5-shadows-in-focus-casablanca-rabat", "Casablanca"),
            ("Rabat", (34.0209, -6.8416), "Rabat bildet den politischen, diplomatischen und königlichen Schwerpunkt.", "SR5", "sr5-shadows-in-focus-casablanca-rabat", "Rabat"),
            ("Al Irfane Quarter", (33.978, -6.866), "Al Irfane ist ein Bildungs- und Verwaltungsviertel im Rabater Teil des Plexes.", "SR5", "sr5-shadows-in-focus-casablanca-rabat", "Al Irfane Quarter"),
            ("New Medina", (33.575, -7.615), "New Medina verbindet dichte Wohn-, Handels- und Kulturräume.", "SR5", "sr5-shadows-in-focus-casablanca-rabat", "New Medina"),
            ("Temara Barrens", (33.927, -6.906), "Die Temara Barrens sind ein prekärer und schwach kontrollierter Randraum zwischen den Zentren.", "SR5", "sr5-shadows-in-focus-casablanca-rabat", "Temara Barrens"),
            ("The Corniche", (33.598, -7.665), "Die Corniche ist Casablancas Küsten-, Hotel- und Vergnügungsstreifen.", "SR5", "sr5-shadows-in-focus-casablanca-rabat", "The Corniche"),
        ],
        "places": [
            p("Café Alba", "Casablanca", "sr5-shadows-in-focus-casablanca-rabat", "Café Alba", "Café Alba ist ein lokaler Gastronomie- und Kontaktort.", "Restaurants"),
            p("Club Pitt", "Casablanca", "sr5-shadows-in-focus-casablanca-rabat", "Club Pitt", "Club Pitt gehört zum Nachtleben des Doppelplexes.", "Bars und Clubs"),
            p("Hassan II Mosque", "Casablanca", "sr5-shadows-in-focus-casablanca-rabat", "Hassan II Mosque", "Die große Moschee ist ein religiöses und weithin sichtbares Wahrzeichen.", "Religion und Magie", [-7.6327, 33.6084]),
            p("Hassan Tower", "Rabat", "sr5-shadows-in-focus-casablanca-rabat", "Hassan Tower", "Der Hassan-Turm ist ein bedeutendes historisches Wahrzeichen Rabats.", "Sichtseeing und Monumente", [-6.8227, 34.0241]),
            p("Ketsuni Tower", "Casablanca", "sr5-shadows-in-focus-casablanca-rabat", "Ketsuni Tower", "Der Ketsuni Tower ist ein benannter Hochhaus- und Konzernstandort.", "Konzerne"),
            p("Morocco Mall", "Casablanca", "sr5-shadows-in-focus-casablanca-rabat", "Morocco Mall", "Das Einkaufszentrum ist ein großer Handels- und Freizeitkomplex.", "Einkaufen", [-7.6997, 33.5758]),
            p("Rabat International Airport", "Rabat", "sr5-shadows-in-focus-casablanca-rabat", "Rabat International Airport", "Der internationale Flughafen ist ein Hauptzugang des nördlichen Plexes.", "Verkehr", [-6.7515, 34.0515]),
            p("Rick’s Café", "Casablanca", "sr5-shadows-in-focus-casablanca-rabat", "Rick’s Café", "Rick’s Café ist ein traditionsbewusster Gastronomie- und Treffpunkt.", "Restaurants", [-7.6200, 33.6068]),
            p("Shady-Ass Café", "Casablanca", "sr5-shadows-in-focus-casablanca-rabat", "Shady-Ass Café", "Das Café ist ein deutlich schattennaher Kontaktort.", "Bars und Kneipen"),
            p("Souk Derb Ghallef", "Casablanca", "sr5-shadows-in-focus-casablanca-rabat", "Souk Derb Ghallef", "Der Souk ist ein bedeutender Markt für Elektronik, Reparaturen und graue Waren.", "Einkaufen"),
            p("Temple Beth-El Synagogue", "Casablanca", "sr5-shadows-in-focus-morocco", "Temple Beth El Synagogue", "Die Synagoge ist ein historischer religiöser Standort.", "Religion und Magie"),
            p("Badra Skytower", "Casablanca-Rabat", "sr5-shadows-in-focus-casablanca-rabat", "Badra Skytower", "Badra ist einer der prägenden Skytower des Doppelplexes.", "Konzerne"),
            p("Kenza Skytower", "Casablanca-Rabat", "sr5-shadows-in-focus-casablanca-rabat", "Kenza Skytower", "Kenza gehört zur charakteristischen Hochhauslandschaft.", "Konzerne"),
            p("Red Minaret of Mohammed VI", "Rabat", "sr5-shadows-in-focus-casablanca-rabat", "Red Minaret of Mohammed VI", "Das rote Minarett ist ein markantes religiös-politisches Wahrzeichen.", "Religion und Magie"),
        ],
        "people": [
            n("Royal Family of Morocco", "sr5-shadows-in-focus-casablanca-rabat", "Royal Family", "Königshaus", "Marokko", "Die königliche Familie prägt Politik, Wirtschaft und Sicherheitsordnung.", "group"),
            n("Chef Faquad Rasheed", "sr5-shadows-in-focus-casablanca-rabat", "Chef Faquad Rasheed", "Gastronom und lokaler Akteur", "Casablanca-Rabat", "Faquad Rasheed ist ein im Stadtquellenband belegter Akteur."),
            n("Nina", "sr5-shadows-in-focus-casablanca-rabat", "Nina", "Lokale Akteurin", "Casablanca-Rabat", "Nina gehört zum Personenbestand des Stadtquellenbands."),
            n("Al Necira", "sr5-shadows-in-focus-casablanca-rabat", "Al Necira (Ares)", "Ares-Tochter", "Casablanca-Rabat", "Al Necira bildet eine regionale Ares-Struktur.", "group"),
            n("Dar es Salaam", "sr5-shadows-in-focus-casablanca-rabat", "Dar es Salaam", "Lokale Organisation", "Casablanca-Rabat", "Dar es Salaam ist als lokale Organisation im Quellenband belegt.", "group"),
        ],
    },
    "vladivostok": {
        "name": "Vladivostok", "year": 2078, "center": (43.1155, 131.8855),
        "bounds": [[42.75, 131.35], [43.55, 132.35]], "zoom": 9,
        "books": ["sr1-shadowrun-corporate-download", "sr2-target-smuggler-havens",
                  "sr3-shadows-of-asia", "sr4-vice", "sr5-gestohlene-seelen",
                  "sr5-enhanced-fiction-the-vladivostok-gauntlet"],
        "profile": {
            "SR2": ("sr2-target-smuggler-havens", "Target: Smuggler Havens", "Kapitel Vladivostok", "Vladivostok ist ein rauer Pazifikhafen, Schmugglerknoten und Machtzentrum konkurrierender Vory-Fraktionen."),
            "SR5": ("sr5-enhanced-fiction-the-vladivostok-gauntlet", "The Vladivostok Gauntlet", "gesamter Text", "Der spätere Erzählstand ergänzt konkrete Treffpunkte, Vory-Akteure und Konzerninteressen."),
        },
        "districts": [
            ("Vladivostok Harbor", (43.105, 131.875), "Der Hafen ist logistisches Herz, Schmuggelroute und zentraler Konfliktraum.", "SR2", "sr2-target-smuggler-havens", "Kapitel Vladivostok"),
            ("Vladivostok Core", (43.117, 131.889), "Der Stadtkern bündelt Verwaltung, Geschäftswelt, Unterwelt und Nachtleben.", "SR2", "sr2-target-smuggler-havens", "Kapitel Vladivostok"),
        ],
        "places": [
            p("Titty Coffee Bar", "Vladivostok Core", "sr5-enhanced-fiction-the-vladivostok-gauntlet", "Titty Coffee Bar", "Die Coffee Bar ist ein Treffpunkt des späteren Vladivostok-Quellenstands.", "Bars und Kneipen"),
            p("Dyadya Yarov’s", "Vladivostok Core", "sr5-enhanced-fiction-the-vladivostok-gauntlet", "Dyadya Yarov’s", "Dyadya Yarov’s ist ein lokaler Treff- und Kontaktort.", "Bars und Kneipen"),
            p("Evo Aphrodite", "Vladivostok", "sr5-enhanced-fiction-the-vladivostok-gauntlet", "Evo Aphrodite", "Evo Aphrodite ist ein in der Erzählquelle belegter Konzernstandort.", "Konzerne"),
            p("Yamatetsu Naval Technologies", "Vladivostok Harbor", "sr1-shadowrun-corporate-download", "Yamatetsu Naval Technologies", "Der historische Yamatetsu-Standort verbindet Konzern- und Marinetechnologie.", "Konzerne"),
            p("Link Club Vladivostok", "Vladivostok Core", "sr5-gestohlene-seelen", "Link Club", "Der Vladivostoker Ableger gehört zur internationalen Link-Club-Kette.", "Bars und Clubs"),
        ],
        "people": [
            n("Byelmodin Faction", "sr2-target-smuggler-havens", "The Byelmodin Faction", "Vory-Fraktion", "Vladivostok", "Byelmodin führt eine der prägenden lokalen Vory-Fraktionen.", "group"),
            n("Kovalenka Faction", "sr2-target-smuggler-havens", "The Kovalenka Faction", "Vory-Fraktion", "Vladivostok", "Die Kovalenka-Fraktion ist eine lokale Macht der Vory.", "group"),
            n("Yunggart Faction", "sr2-target-smuggler-havens", "The Yunggart Faction", "Vory-Fraktion", "Vladivostok", "Die Yunggart-Fraktion gehört zur lokalen Vory-Machtordnung.", "group"),
            n("Vladivostok Vory v Zakone", "sr2-target-smuggler-havens", "Vory v Zakone", "Verbrechersyndikat", "Vladivostok", "Die Vory dominiert wesentliche Teile des Schmuggels und der Unterwelt.", "group"),
            n("Vladivostok Yakuza", "sr2-target-smuggler-havens", "The Yakuza", "Verbrechersyndikat", "Vladivostok", "Die Yakuza konkurriert im pazifischen Hafen um Einfluss.", "group"),
            n("Lyubov Kirilskaya", "sr4-vice", "Bojevik Lyubov Kirilskaya", "Vory-Bojevik", "Vladivostok", "Lyubov Kirilskaya ist eine im Unterweltmaterial belegte Vory-Akteurin."),
        ],
    },
    "zuerich": {
        "name": "Zürich", "year": 2080, "center": (47.3769, 8.5417),
        "bounds": [[47.15, 8.15], [47.65, 8.90]], "zoom": 9,
        "books": ["sr2-chrom-dioxin", "sr2-schattenlichter",
                  "sr3-europa-in-den-schatten", "sr4-shadowrun-4d-konzerndossier",
                  "sr5-datapuls-schweiz",
                  "sr5-schattenload-05-swissmetro-bahnhof-zurich-west"],
        "profile": {
            "SR2": ("sr2-chrom-dioxin", "Chrom & Dioxin", "Kapitel Schweiz/Zürich", "Zürich ist Finanz-, Forschungs- und Verkehrszentrum einer stark kontrollierten Schweizer Stadtlandschaft."),
            "SR5": ("sr5-datapuls-schweiz", "Datapuls Schweiz", "Kapitel Zürich", "Der spätere Stand vertieft die Sonderzonen, Inseln, Konzern- und Sicherheitsinteressen Zürichs."),
        },
        "districts": [
            ("Zürich City", (47.3769, 8.5417), "Zürich City bildet den Finanz-, Verwaltungs- und Kulturkern.", "SR5", "sr5-datapuls-schweiz", "Kapitel Zürich"),
            ("Zürich-West", (47.390, 8.510), "Zürich-West verbindet ehemalige Industrieflächen, Verkehr, Nachtleben und neue Konzernnutzungen.", "SR5", "sr5-schattenload-05-swissmetro-bahnhof-zurich-west", "SwissMetro-Bahnhof Zürich-West"),
            ("Escher-Bürkli-Insel", (47.367, 8.542), "Die Escher-Bürkli-Insel ist ein besonderer innerstädtischer Lore-Raum.", "SR5", "sr5-datapuls-schweiz", "Die Escher-Bürkli-Insel"),
        ],
        "places": [
            p("Alter Bahnhof", "Zürich", "sr2-chrom-dioxin", "Alter Bahnhof (Z)", "Der Alte Bahnhof ist ein im frühen Schweizer Quellenstand benannter Ort.", "Verkehr"),
            p("SwissMetro-Bahnhof Zürich-West", "Zürich-West", "sr5-schattenload-05-swissmetro-bahnhof-zurich-west", "gesamter Artikel", "Der Bahnhof ist ein wichtiger Zugang zum schweizerischen Hochgeschwindigkeitsnetz.", "Verkehr"),
            p("Paracelsus-Klinik", "Zürich", "sr2-chrom-dioxin", "Paracelsus-Klinik", "Die Paracelsus-Klinik ist ein bedeutender medizinischer Standort.", "Medizin"),
            p("Zürich Investments", "Zürich", "sr3-europa-in-den-schatten", "Zürich Investments", "Zürich Investments ist ein wichtiger Finanz- und Konzernakteur der Stadt.", "Konzerne"),
            p("Zenit AG", "Zürich", "sr4-shadowrun-4d-konzerndossier", "Zenit AG", "Zenit ist ein in Zürich belegter Konzernstandort.", "Konzerne"),
            p("Hermetische Hochschulen Zürich", "Zürich", "sr2-chrom-dioxin", "Hermetische Hochschulen", "Zürich besitzt bedeutende Einrichtungen hermetischer Forschung und Ausbildung.", "Bildung und Kultur"),
        ],
        "people": [
            n("Bernhard Gasser", "sr5-datapuls-schweiz", "Bernhard Gasser", "Lokaler Akteur", "Zürich", "Bernhard Gasser gehört zum Personenbestand des Schweizer Quellenstands."),
            n("Daniela Ladina Cavegn", "sr2-schattenlichter", "Daniela Ladina Cavegn", "Lokale Akteurin", "Zürich", "Daniela Ladina Cavegn ist im Zürcher Quellenmaterial belegt."),
            n("Hans Homberger", "sr2-schattenlichter", "Hans Homberger", "Lokaler Akteur", "Zürich", "Hans Homberger ist ein Akteur des frühen Zürcher Quellenstands."),
            n("Richard Bührle", "sr5-datapuls-schweiz", "Richard Bührle", "Lokaler Akteur", "Zürich", "Richard Bührle gehört zum Personenbestand des Schweizer Quellenstands."),
        ],
    },
    "leipzig-halle": {
        "name": "Leipzig-Halle", "year": 2081, "center": (51.42, 12.10),
        "bounds": [[51.15, 11.60], [51.70, 12.65]], "zoom": 9,
        "books": ["sr3-deutschland-in-den-schatten-ii", "sr4-reisefuhrer-in-die-deutschen-schatten", "sr5-auf-dunklen-pfaden"],
        "profile": {
            "SR3": ("sr3-deutschland-in-den-schatten-ii", "Deutschland in den Schatten II", "Kapitel Leipzig-Halle", "Der Doppelplex verbindet Industrie, Logistik, Chemie, Kultur und stark unterschiedliche Sicherheitsräume."),
            "SR4": ("sr4-reisefuhrer-in-die-deutschen-schatten", "Reiseführer in die deutschen Schatten", "Kapitel Leipzig-Halle", "Der Reiseführer ergänzt aktuelle Treffpunkte, Infrastruktur und lohnende Ziele."),
        },
        "districts": [
            ("Leipzig", (51.3397, 12.3731), "Leipzig bildet den östlichen Kultur-, Handels- und Dienstleistungskern.", "SR3", "sr3-deutschland-in-den-schatten-ii", "Kapitel Leipzig"),
            ("Halle", (51.4969, 11.9688), "Halle ist der westliche Industrie-, Chemie- und Siedlungsschwerpunkt.", "SR3", "sr3-deutschland-in-den-schatten-ii", "Kapitel Halle"),
            ("Leipzig-Halle Industrieband", (51.43, 12.18), "Das Industrie- und Logistikband verbindet die beiden alten Städte.", "SR4", "sr4-reisefuhrer-in-die-deutschen-schatten", "Kapitel Leipzig-Halle"),
        ],
        "places": [
            p("Aggravex Center", "Leipzig-Halle", "sr5-auf-dunklen-pfaden", "Aggravex Center", "Das Aggravex Center ist ein im Quellenmaterial benannter Schauplatz.", "Konzerne"),
            p("AIRobic", "Leipzig-Halle", "sr5-auf-dunklen-pfaden", "AIRobic", "AIRobic ist ein lokaler Treff- oder Veranstaltungsort.", "Freizeit und Natur"),
            p("Club Fight", "Leipzig-Halle", "sr5-auf-dunklen-pfaden", "Club Fight", "Club Fight ist ein Schauplatz der lokalen Musik- und Clubszene.", "Bars und Clubs"),
            p("Jogoya", "Leipzig-Halle", "sr5-auf-dunklen-pfaden", "Jogoya", "Jogoya ist ein im Stadtumfeld belegter Ort.", "Sonstige Spots"),
            p("The Factory", "Leipzig-Halle", "sr5-auf-dunklen-pfaden", "The Factory", "The Factory ist ein Industrie- und Missionsschauplatz.", "Industrie"),
            p("The Filthy Dragon", "Leipzig-Halle", "sr5-auf-dunklen-pfaden", "The Filthy Dragon", "The Filthy Dragon ist ein lokaler Szenetreff.", "Bars und Kneipen"),
            p("Magische Bibliotheken Leipzig-Halle", "Leipzig-Halle", "sr4-reisefuhrer-in-die-deutschen-schatten", "Magische Bibliotheken", "Die Hochschulen des Plexes verfügen über zugängliche magische Bibliotheksbestände.", "Bildung und Kultur"),
        ],
        "people": [
            n("Cherkezov", "sr5-auf-dunklen-pfaden", "Cherkezov", "Lokaler Akteur", "Leipzig-Halle", "Cherkezov ist ein im Quellenmaterial belegter Akteur."),
            n("Gargari-Organizatsi Leipzig-Halle", "sr5-auf-dunklen-pfaden", "Gargari-Organizatsi", "Vory-Organisation", "Leipzig-Halle", "Die westliche Vory unterhält eine Präsenz im Plex.", "group"),
            n("Ratspräsident Yilmaz Wojenko", "sr5-auf-dunklen-pfaden", "Ratspräsident Yilmaz Wojenko", "Politiker", "Leipzig-Halle", "Yilmaz Wojenko ist ein politischer Akteur des Plexes."),
            n("Club Fight", "sr5-auf-dunklen-pfaden", "Club Fight", "Musikgruppe", "Leipzig-Halle", "Club Fight ist eine bewusst skandalorientierte lokale Band.", "group", "Club Fight"),
        ],
    },
    "quebec": {
        "name": "Québec", "year": 2063, "center": (46.8139, -71.2080),
        "bounds": [[46.55, -71.65], [47.15, -70.65]], "zoom": 9,
        "books": ["sr2-nordamerika-quellenbuch", "sr2-underworld-sourcebook",
                  "sr3-shadows-of-north-america", "sr3-nordamerika-in-den-schatten"],
        "profile": {
            "SR3": ("sr3-nordamerika-in-den-schatten", "Nordamerika in den Schatten", "Der Québec-City-Metroplex", "Québec City ist Hauptstadt, Unternehmensstandort und Symbol einer Republik zwischen Öffnung und Abschottung."),
        },
        "districts": [
            ("Québec City Metroplex", (46.8139, -71.2080), "Der Hauptstadtplex verbindet historische Stadt, Regierungssitz und stark umkämpfte Unternehmenszonen.", "SR3", "sr3-nordamerika-in-den-schatten", "Der Québec City Metroplex"),
            ("Québec Corporate Zones", (46.82, -71.25), "Zwölf Unternehmenszonen bündeln einen wesentlichen Teil der Konzernmacht im Hauptstadtgebiet.", "SR3", "sr3-shadows-of-north-america", "Québec City Metroplex"),
        ],
        "places": [
            p("Château Frontenac", "Québec City Metroplex", "sr3-nordamerika-in-den-schatten", "Der Québec City Metroplex", "Das Château Frontenac dient im Quellenstand als repräsentativer Sitz der politischen Mehrheitsführung.", "Behörden", [-71.2048, 46.8119]),
            p("Hilton International Quebec", "Québec City Metroplex", "sr2-nordamerika-quellenbuch", "Hilton International Quebec", "Das Hilton ist ein bedeutender Hotel- und Geschäftstreffpunkt.", "Hotels"),
            p("Hôtel Auberge des Gouverneurs", "Québec City Metroplex", "sr2-nordamerika-quellenbuch", "Hôtel Auberge des Gouverneurs", "Das Hotel ist als Unterkunft und lokaler Treffpunkt belegt.", "Hotels"),
        ],
        "people": [
            n("Démocrates Mondains", "sr3-shadows-of-north-america", "Démocrates Mondains", "Politische Partei", "Québec", "Die Partei treibt eine Öffnung der Republik voran.", "group"),
            n("Hélène Bard", "sr3-shadows-of-north-america", "Démocrates Mondains", "Präsidentin der Démocrates Mondains", "Québec", "Hélène Bard ist die treibende politische Kraft hinter dem Öffnungskurs."),
            n("Québec Unité", "sr2-underworld-sourcebook", "Québec Unité", "Politische oder Untergrundorganisation", "Québec", "Québec Unité ist eine im Quellenbestand belegte Organisation.", "group"),
        ],
    },
    "bremen": {
        "name": "Bremen", "year": 2080, "center": (53.0793, 8.8017),
        "bounds": [[52.90, 8.45], [53.30, 9.15]], "zoom": 9,
        "books": ["sr1-deutschland-in-den-schatten", "sr3-deutschland-in-den-schatten-ii"],
        "profile": {
            "SR1": ("sr1-deutschland-in-den-schatten", "Deutschland in den Schatten", "Kapitel Bremen", "Bremen ist Hafen-, Handels-, Universitäts- und Industriestadt des Norddeutschen Bundes."),
            "SR3": ("sr3-deutschland-in-den-schatten-ii", "Deutschland in den Schatten II", "Kapitel Bremen", "Der spätere Stand vertieft Stadtteile, soziale Brüche und die norddeutsche Unterwelt."),
        },
        "districts": [
            ("Bremen-Stadt", (53.0793, 8.8017), "Bremen-Stadt bildet Verwaltungs-, Handels- und Kulturkern.", "SR3", "sr3-deutschland-in-den-schatten-ii", "Kapitel Bremen"),
            ("Horn/Lehe", (53.105, 8.875), "Horn/Lehe ist das Universitätsviertel mit Hochschulen für Technik, Nautik und Informatik.", "SR3", "sr3-deutschland-in-den-schatten-ii", "Horn/Lehe (B)"),
            ("Kattenturm", (53.035, 8.827), "Kattenturm wurde nach schweren Unruhen zum Sonderbezirk und ist sozial stark ausgegrenzt.", "SR3", "sr3-deutschland-in-den-schatten-ii", "Kattenturm (F)"),
            ("Bremerhaven", (53.5396, 8.5809), "Bremerhaven bildet den nördlichen Hafen- und Logistikteil des Stadtstaates.", "SR3", "sr3-deutschland-in-den-schatten-ii", "Kapitel Bremen/Bremerhaven"),
        ],
        "places": [
            p("Universität Bremen", "Horn/Lehe", "sr3-deutschland-in-den-schatten-ii", "Horn/Lehe (B)", "Die Universität prägt den Wissenschafts- und Bildungsstandort Horn/Lehe.", "Bildung und Kultur", [8.853, 53.106]),
            p("Bremer Hafen", "Bremen-Stadt", "sr1-deutschland-in-den-schatten", "Kapitel Bremen", "Der Hafen ist ein zentraler Wirtschafts-, Verkehrs- und Schmuggelraum.", "Verkehr"),
        ],
        "people": [
            n("Lobatchevski-Vory Bremen", "sr3-deutschland-in-den-schatten-ii", "Unterwelt Bremen", "Vory-Organisation", "Bremen", "Die westliche Vory ist in Bremens Unterwelt präsent.", "group"),
            n("Bremer Bikerszene", "sr3-deutschland-in-den-schatten-ii", "Biker und die erwachte Welt", "Bikergruppen", "Bremen", "Bikergruppen sind ein eigenständiger Teil der Bremer Schatten- und Straßenszene.", "group"),
        ],
    },
    "hannover": {
        "name": "Hannover", "year": 2080, "center": (52.3759, 9.7320),
        "bounds": [[52.15, 9.35], [52.65, 10.10]], "zoom": 9,
        "books": ["sr2-deutschland-in-den-schatten",
                  "sr4-machtspiele-handbuch-fur-spione", "sr5-datapuls"],
        "profile": {
            "SR4": ("sr4-machtspiele-handbuch-fur-spione", "Machtspiele: Handbuch für Spione", "Kapitel Hannover", "Hannover ist Allianzhauptstadt, Regierungszentrum und Schauplatz intensiver Geheimdienst- und Unterweltaktivität."),
            "SR5": ("sr5-datapuls", "Datapuls", "Hannover", "Die Hauptstadt beherbergt Bundestag, Bundesrat, Ministerien und Institutionen unter hoher staatlicher Sicherheit."),
        },
        "districts": [
            ("Regierungsviertel Hannover", (52.370, 9.735), "Das Regierungsviertel bündelt die zentralen Institutionen der Allianz.", "SR5", "sr5-datapuls", "Hannover"),
            ("Mühlenberg", (52.342, 9.666), "Mühlenberg ist ein Schwerpunkt der Vory-Aktivitäten im Stadtgebiet.", "SR4", "sr4-machtspiele-handbuch-fur-spione", "Vory v Zakone"),
            ("Gümmer", (52.422, 9.510), "Gümmer liegt knapp außerhalb der Stadt und beherbergt einen wichtigen Offizierstreff.", "SR4", "sr4-machtspiele-handbuch-fur-spione", "Die italienische Mafia"),
        ],
        "places": [
            p("Flughafen Hannover-Langenhagen", "Hannover", "sr4-machtspiele-handbuch-fur-spione", "Drehkreuz der Politik", "Der Flughafen ist vor allem für Politik, Verwaltung, Diplomatie und Konzernverkehr bedeutend.", "Verkehr", [9.685, 52.461]),
            p("Scharnhorst Lounge", "Gümmer", "sr4-machtspiele-handbuch-fur-spione", "Die italienische Mafia", "Die elitäre Offizierslounge ist ein diskreter Treffpunkt für Militär und Polizei.", "Bars und Clubs"),
            p("Bundestag der ADL", "Regierungsviertel Hannover", "sr5-datapuls", "Hannover", "Der Bundestag gehört zu den zentralen politischen Institutionen der Allianzhauptstadt.", "Behörden"),
            p("Bundesrat der ADL", "Regierungsviertel Hannover", "sr5-datapuls", "Hannover", "Der Bundesrat ist eine der zentralen Institutionen im Regierungszentrum.", "Behörden"),
            p("Shadowtech-Shop Hannover", "Hannover", "sr2-deutschland-in-den-schatten", "Shadowtech-Shop", "Der Shop ist ein im frühen Quellenstand belegter Ausrüstungs- und Szenestandort.", "Einkaufen"),
        ],
        "people": [
            n("Staatliche Polizei Hannover", "sr4-machtspiele-handbuch-fur-spione", "Staatliche Polizei", "Polizeiorganisation", "Hannover", "Die staatliche Polizei besitzt die Hoheit in der Allianzhauptstadt.", "group"),
            n("Hannover Vory v Zakone", "sr4-machtspiele-handbuch-fur-spione", "Vory v Zakone", "Verbrechersyndikat", "Hannover", "Die Vory ist das zahlenmäßig stärkste Syndikat im Einzugsgebiet.", "group", "Mühlenberg"),
            n("Graue Wölfe Hannover", "sr4-machtspiele-handbuch-fur-spione", "Ethnische Minderheiten und Gangs", "Unterweltgruppe", "Hannover", "Türkische und albanische Akteure bilden eine eigenständige lokale Gruppierung.", "group"),
            n("Enrico Zorn", "sr4-machtspiele-handbuch-fur-spione", "Enrico Zorn", "Geheimdienst- und Schattenakteur", "Hannover", "Enrico Zorn ist ein unter fragwürdiger Identität auftretender Akteur der Machtspiele."),
        ],
    },
    "istanbul": {
        "name": "Istanbul", "year": 2075, "center": (41.0082, 28.9784),
        "bounds": [[40.75, 28.45], [41.35, 29.55]], "zoom": 9,
        "books": ["sr3-shadows-of-asia", "sr4-runner-havens",
                  "sr4-strassenmagie", "sr5-cutting-aces",
                  "sr5-gestohlene-seelen", "sr5-mit-tricks-und-finesse"],
        "profile": {
            "SR3": ("sr3-shadows-of-asia", "Shadows of Asia", "Free City of Constantinople", "Die freie Stadt kontrolliert den Bosporus und verbindet Europa, Asien, Handel und politische Rivalitäten."),
            "SR5": ("sr5-mit-tricks-und-finesse", "Mit Tricks und Finesse", "Istanbul/Konstantinopel", "Der spätere Stand vertieft Bezirke, Unterwelt, Sehnsüchte und Schattenkontakte."),
        },
        "districts": [
            ("Galata", (41.0256, 28.9741), "Galata umfasst Galata und Beyoğlu und verbindet alte Handels-, Bank-, Hafen- und Vergnügungsräume.", "SR5", "sr5-mit-tricks-und-finesse", "Galata"),
            ("Beyoğlu", (41.037, 28.977), "Beyoğlu ist ein moderner, nach Erdbeben teilweise neu errichteter Bezirk mit hyperaktivem Nachtleben.", "SR4", "sr4-runner-havens", "Beyoglu"),
            ("Yenikapı", (41.005, 28.951), "Yenikapı ist ein Küsten-, Verkehrs- und Großveranstaltungsraum.", "SR5", "sr5-cutting-aces", "Yenikapi Square"),
        ],
        "places": [
            p("House of Justice", "Istanbul", "sr5-cutting-aces", "House of Justice", "Das große Justizgebäude beherbergt Gerichte, Genehmigungsstellen und eine eigene Sicherheitseinheit.", "Behörden"),
            p("Yenikapı Square", "Yenikapı", "sr5-cutting-aces", "Yenikapi Square", "Der sehr große Küstenplatz dient Kundgebungen und Feiern mit bis zu einer Million Menschen.", "Freizeit und Natur", [28.951, 41.005]),
            p("Link Club Istanbul", "Istanbul", "sr5-gestohlene-seelen", "Link Club", "Der lokale Ableger gehört zur internationalen Link-Club-Kette.", "Bars und Clubs"),
        ],
        "people": [
            n("Berrak Sensoy", "sr5-cutting-aces", "Berrak Sensoy", "Fixer", "Istanbul", "Berrak Sensoy ist eine der ersten Anlaufstellen für Schattenarbeit in der Stadt."),
            n("Grey Wolves", "sr5-cutting-aces", "Grey Wolves", "Nationalistische Söldnerorganisation", "Istanbul", "Die Grey Wolves entwickelten sich aus radikalen Zellen zu einer geschlosseneren Söldnergruppe.", "group"),
            n("Dead Warlocks", "sr4-strassenmagie", "Dead Warlocks", "Magische Gruppe", "Istanbul", "Die Dead Warlocks sind als magische Gruppe mit Istanbul-Bezug belegt.", "group"),
        ],
    },
    "tenochtitlan": {
        "name": "Tenochtitlán", "year": 2073, "center": (19.4326, -99.1332),
        "bounds": [[19.05, -99.55], [19.75, -98.70]], "zoom": 9,
        "books": ["sr2-aztlan", "sr3-lateinamerika-in-den-schatten-v1-0",
                  "sr3-shadows-of-latin-america-v1-2", "sr4-jet-set",
                  "sr5-book-of-the-lost", "sr5-gestohlene-seelen"],
        "profile": {
            "SR2": ("sr2-aztlan", "Aztlan", "Kapitel Tenochtitlán", "Tenochtitlán ist Hauptstadt Aztlans, Aztechnology-Machtzentrum und hochverdichtete verkabelte Metropole."),
            "SR3": ("sr3-lateinamerika-in-den-schatten-v1-0", "Lateinamerika in den Schatten", "Kapitel Aztlan", "Der spätere Stand betont die Verbindung aus Staat, Konzern, Tempeln und dem Tezcatlipoca-Kult."),
        },
        "districts": [
            ("Corporate Core Tenochtitlán", (19.433, -99.141), "Der Konzernkern ist besonders stark vernetzt, kontrolliert und von Aztechnology geprägt.", "SR2", "sr2-aztlan", "Communications"),
            ("University District", (19.333, -99.188), "Der Universitätsbezirk ist Bildungsraum und Bezugspunkt mehrerer lokaler Schauplätze.", "SR2", "sr2-aztlan", "The Pedegral"),
            ("Zócalo", (19.4326, -99.1332), "Der Zócalo ist politisches, zeremonielles und symbolisches Zentrum.", "SR2", "sr2-aztlan", "National Palace"),
        ],
        "places": [
            p("Café de Montevideo", "Tenochtitlán", "sr2-aztlan", "Café de Montevideo", "Das Café an der Avenida Insurgentes Norte ist vor allem ein sozialer Treffpunkt.", "Restaurants"),
            p("Cero Cero", "Tenochtitlán", "sr2-aztlan", "Cero Cero", "Der Nachtclub liegt im Camino Real Hotel.", "Bars und Clubs"),
            p("National Palace", "Zócalo", "sr2-aztlan", "National Palace", "Der große Bau am Zócalo ist Regierungssitz und starkes Machtsymbol.", "Behörden", [-99.131, 19.433]),
            p("Aztechnology World Headquarters", "Corporate Core Tenochtitlán", "sr4-jet-set", "Aztechnology World Headquarters", "Das Welt-Hauptquartier bündelt die Macht des Megakonzerns.", "Konzerne"),
            p("Teocallis", "Tenochtitlán", "sr3-shadows-of-latin-america-v1-2", "Teocallis, House of the Gods", "Die Tempel prägen Skyline, Straßenbild und religiöse Machtordnung.", "Religion und Magie"),
            p("The Pedregal", "University District", "sr2-aztlan", "The Pedegral", "Der Pedregal liegt westlich des Universitätsbezirks und ist ein besonderer lokaler Schauplatz.", "Sonstige Spots"),
            p("Link Club Tenochtitlán", "Tenochtitlán", "sr5-gestohlene-seelen", "Link Club", "Der lokale Ableger gehört zur internationalen Link-Club-Kette.", "Bars und Clubs"),
            p("Taco Temple", "Tenochtitlán", "sr5-book-of-the-lost", "Taco Temple", "Taco Temple ist ein im späteren Quellenstand belegter Gastronomiestandort.", "Restaurants"),
        ],
        "people": [
            n("Cult of Tezcatlipoca", "sr3-shadows-of-latin-america-v1-2", "The Cult of Tezcatlipoca", "Religiöser Machtkult", "Aztlan", "Der Kult verbindet Staats-, Konzern- und Priesterherrschaft mit Opfertraditionen.", "group"),
            n("Aztechnology", "sr2-aztlan", "Kapitel Tenochtitlán", "Megakonzern", "Tenochtitlán", "Aztechnology dominiert Wirtschaft, Sicherheit und Politik der Hauptstadt.", "group", "Aztechnology World Headquarters"),
            n("Tarascan", "sr2-aztlan", "Tarascan", "Ethnische Gemeinschaft", "Aztlan", "Die Tarascan bilden eine sprachlich und kulturell eigenständige Gemeinschaft.", "group"),
        ],
    },
    "stuttgart": {
        "name": "Stuttgart", "year": 2080, "center": (48.7758, 9.1829),
        "bounds": [[48.50, 8.75], [49.05, 9.65]], "zoom": 9,
        "books": ["sr3-deutschland-in-den-schatten-ii", "sr4-reisefuhrer-in-die-deutschen-schatten", "sr5-datapuls"],
        "profile": {
            "SR3": ("sr3-deutschland-in-den-schatten-ii", "Deutschland in den Schatten II", "Stuttgart heute", "Der Ballungsraum Mittlerer Neckar verbindet Konzerne, Automobilindustrie, wohlhabende Kesselzonen und ausgegrenzte Randviertel."),
            "SR5": ("sr5-datapuls", "Datapuls", "Stuttgart", "Der spätere Stand ergänzt Konzerne, Unterwelt, Sicherheitskräfte und besondere lokale Schauplätze."),
        },
        "districts": [
            ("Stuttgarter Kessel", (48.7758, 9.1829), "Der Kessel ist dichter Verwaltungs-, Konzern- und Kulturkern des Plexes.", "SR3", "sr3-deutschland-in-den-schatten-ii", "Stuttgart heute"),
            ("Mühlhausen", (48.843, 9.229), "Mühlhausen und angrenzende Viertel sind sozial benachteiligt und werden vom Sternschutz weitgehend gemieden.", "SR3", "sr3-deutschland-in-den-schatten-ii", "Mühlhausen"),
            ("Degerloch", (48.749, 9.171), "Degerloch ist im Quellenstand ein besonders heruntergekommener und unsicherer Teilraum.", "SR3", "sr3-deutschland-in-den-schatten-ii", "Mühlhausen"),
        ],
        "places": [
            p("Das Schwarze Haus", "Stuttgart", "sr5-datapuls", "Das Schwarze Haus", "Um das Gebäude ranken sich seit Jahrzehnten kuriose und erschreckende Geschichten.", "Religion und Magie"),
            p("Horizon Group Stuttgart", "Stuttgart", "sr5-datapuls", "Horizon Group", "Stuttgart ist Hauptsitz der regionalen Horizon Group.", "Konzerne"),
            p("Stuttgarter Transrapid", "Stuttgart", "sr3-deutschland-in-den-schatten-ii", "Bahn", "Der Transrapid verbindet Stuttgart mit Karlsruhe, Mannheim, Frankfurt und Hannover.", "Verkehr"),
        ],
        "people": [
            n("Generalleutnant Daniel Culp", "sr5-datapuls", "Generalleutnant Daniel Culp", "Militärischer Leiter von Argus", "MET2000/Argus", "Der in Stuttgart geborene Daniel Culp ist Generalleutnant der MET2000 und militärischer Argus-Leiter."),
            n("Gasperi-Familie Stuttgart", "sr5-datapuls", "Die Unterwelt", "Mafiafamilie", "Stuttgart", "Die Gasperi-Familie kontrolliert einen großen Teil der illegalen Geschäfte.", "group"),
            n("Michaela Semenszato", "sr5-datapuls", "Die Unterwelt", "Mafiaoberhaupt", "Gasperi-Familie", "Michaela Semenszato führt die Stuttgarter Gasperi-Familie."),
            n("Sternschutz Stuttgart", "sr4-reisefuhrer-in-die-deutschen-schatten", "Sternschutz Security", "Privater Sicherheitsdienst", "Stuttgart", "Der Sternschutz übernimmt wesentliche Polizeiaufgaben im Plex.", "group"),
            n("Horizon Group Stuttgart", "sr5-datapuls", "Horizon Group", "Medien- und PR-Konzern", "Stuttgart", "Die lokale Horizon Group ist ein bedeutender Konzernakteur.", "group", "Horizon Group Stuttgart"),
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
    order = [city["id"] for city in registry["cities"]]
    order.extend(city_id for city_id in CONFIGS if city_id not in by_id or city_id not in order)
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
