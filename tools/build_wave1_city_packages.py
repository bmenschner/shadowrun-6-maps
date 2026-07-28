#!/usr/bin/env python3
"""Build the first six new city packages from verified city-focused sources.

Unmapped places remain catalogue-only (``geometry: null``).  District and
surviving landmark coordinates are explicit editorial anchors and never
randomly generated.
"""

from __future__ import annotations

import json
from pathlib import Path

from build_us_city_content import CityCatalogue, city_edition, name_key, write_json


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "data/source-registry.json").read_text(encoding="utf-8"))
WORKS = {work["id"]: work for work in REGISTRY["works"]}


def p(name, scope, book, citation, summary, category="Sonstige Spots", coordinates=None):
    return {
        "name": name, "scope": scope, "book": book, "citation": citation,
        "summary": summary, "category": category, "coordinates": coordinates,
    }


def n(name, book, citation, role, affiliation, summary, entity_type="person", location=None):
    return {
        "name": name, "book": book, "citation": citation, "role": role,
        "affiliation": affiliation, "summary": summary,
        "entity_type": entity_type, "location": location,
    }


CONFIGS = {
    "chicago": {
        "name": "Chicago", "year": 2082, "center": (41.8781, -87.6298),
        "bounds": [[41.55, -88.15], [42.15, -87.35]], "zoom": 9,
        "books": ["sr2-bug-city", "sr4-feral-cities", "sr5-mission-chicago",
                  "sr5-abenteuerband-schatten-uber-chicago", "sr5-anarchy-chicago-chaos"],
        "profile": {
            "SR2": ("sr2-bug-city", "Bug City", "gesamter Band", "Chicago wird nach der Insektengeist-Katastrophe zur abgeriegelten Containment Zone."),
            "SR4": ("sr4-feral-cities", "Feral Cities", "Kapitel Chicago", "Die verwilderte Stadt entwickelt Enklaven, neue Machtgruppen und gefährliche Freiräume."),
            "SR5": ("sr5-mission-chicago", "Mission Chicago", "gesamter Band", "Chicago öffnet sich wieder, bleibt aber ein zerrissener Plex voller Ruinen, Wiederaufbau und alter Schrecken."),
        },
        "districts": [
            ("The Zone", (41.865, -87.627), "Die frühere Containment Zone bildet den verwüsteten Kernraum mit Ruinen, Enklaven und Spuren der Insektengeist-Krise.", "SR4", "sr4-feral-cities", "Kapitel The Zone"),
            ("Northside", (41.965, -87.660), "Northside umfasst überlebende und neu organisierte Siedlungsräume nördlich des Kerns.", "SR4", "sr4-feral-cities", "Kapitel Northside"),
            ("Southside", (41.765, -87.625), "Southside ist ein weitläufiger südlicher Teilraum mit wechselnder lokaler Kontrolle.", "SR4", "sr4-feral-cities", "Kapitel Southside"),
            ("Westside", (41.875, -87.760), "Westside verbindet Ruinenzonen, Enklaven und wichtige Zugänge in den Plex.", "SR4", "sr4-feral-cities", "Kapitel Westside"),
            ("O’Hare Sub-Sprawl", (41.974, -87.907), "Der O’Hare-Teilplex bildet einen westlichen Verkehrs- und Siedlungsschwerpunkt.", "SR5", "sr5-anarchy-chicago-chaos", "Kapitel O’Hare Sub-Sprawl"),
            ("The Core", (41.883, -87.632), "Der Kern umfasst das verdichtete Zentrum Chicagos und zentrale Schauplätze der wechselnden Krisenstände.", "SR5", "sr5-mission-chicago", "Kapitel Der Kern"),
        ],
        "places": [
            p("Cermak Crater", "The Zone", "sr4-feral-cities", "Kapitel The Zone", "Der Cermak-Krater ist Ground Zero der Zerstörung und ein zentraler Gefahrenpunkt der Zone.", "Sondergebiete", [-87.6226, 41.8522]),
            p("Chicago Pedway", "The Zone", "sr4-feral-cities", "Kapitel The Zone", "Das unterirdische Pedway-Netz verbindet Teile des Zentrums und dient als Verkehrsweg, Rückzugsraum und Gefahrenzone.", "Verkehr"),
            p("Bryn Mawr Apartment Hotel", "Northside", "sr4-feral-cities", "Kapitel Northside", "Das Bryn Mawr Apartment Hotel ist als Schauplatz im Northside belegt.", "Hotels"),
            p("Fort Chicago", "Northside", "sr4-feral-cities", "Kapitel Northside", "Fort Chicago ist eine befestigte Enklave im nördlichen Stadtgebiet.", "Sicherheit und Justiz"),
            p("Freaktown", "The Zone", "sr4-feral-cities", "Kapitel The Zone", "Freaktown ist eine eigenständige Gemeinschaft innerhalb der Zone.", "Stadtteile"),
            p("Little Earth", "The Zone", "sr4-feral-cities", "Kapitel The Zone", "Little Earth liegt im Umfeld der University of Chicago und gehört zu den benannten Enklaven der Zone.", "Stadtteile"),
            p("Market Square", "Northside", "sr4-feral-cities", "Kapitel Northside", "Market Square ist ein Handelsplatz und sozialer Treffpunkt im Northside.", "Einkaufen"),
            p("Merle’s Grocery", "The Zone", "sr4-feral-cities", "Kapitel The Zone", "Merle’s Grocery ist ein lokaler Versorgungs- und Kontaktpunkt in der Zone.", "Einkaufen"),
            p("Open Enclave", "Westside", "sr4-feral-cities", "Kapitel Westside", "Die Open Enclave ist eine benannte Siedlung im Westside.", "Stadtteile"),
            p("The Maker Collective", "The Core", "sr5-mission-chicago", "Kapitel Maker Collective", "Das Maker Collective ist ein wichtiger Anlaufpunkt des wiederaufgebauten Chicago.", "Organisationen"),
            p("The Vault", "The Core", "sr5-mission-chicago", "Kapitel Die Vault", "The Vault ist ein gesicherter Schauplatz im Chicago-Quellenstand der fünften Edition.", "Sicherheit und Justiz"),
            p("Miller’s Pub", "The Core", "sr5-mission-chicago", "Kapitel Miller’s Pub", "Miller’s Pub ist ein Treffpunkt der lokalen Schatten- und Kneipenszene.", "Bars und Kneipen"),
            p("The Purple Pig", "The Core", "sr5-abenteuerband-schatten-uber-chicago", "Schauplatz Das Purple Pig", "The Purple Pig ist ein in Schatten über Chicago verwendeter Treffpunkt.", "Restaurants"),
            p("Valley Rose Pharmaceuticals", "The Core", "sr5-mission-chicago", "Kapitel Valley Rose", "Valley Rose Pharmaceuticals ist ein Konzernstandort im Chicago-Missionsmaterial.", "Konzerne"),
        ],
        "people": [
            n("Anne Ravenheart", "sr2-bug-city", "PDF-Seite 155", "Lokale Akteurin", "Chicago", "Anne Ravenheart gehört zum Personenbestand von Bug City."),
            n("Hanna Uljaken", "sr2-bug-city", "PDF-Seite 157", "Lokale Akteurin", "Chicago", "Hanna Uljaken ist im Personenkapitel von Bug City belegt."),
            n("Jerome Standish", "sr2-bug-city", "PDF-Seite 158", "Lokaler Akteur", "Chicago", "Jerome Standish ist im Personenkapitel von Bug City belegt."),
            n("Kyle Teller", "sr2-bug-city", "PDF-Seite 155", "Lokaler Akteur", "Chicago", "Kyle Teller ist im Personenkapitel von Bug City belegt."),
            n("Juan Xihuitl", "sr5-mission-chicago", "Personen und Kontakte", "Lokaler Akteur", "Chicago", "Juan Xihuitl ist als Akteur im Chicago-Missionsmaterial belegt."),
            n("Matt Wrath", "sr5-mission-chicago", "Personen und Kontakte", "Lokaler Akteur", "Chicago", "Matt Wrath ist als Akteur im Chicago-Missionsmaterial belegt."),
            n("Momma Dean", "sr5-anarchy-chicago-chaos", "Charaktere", "Neo-tribale Anführerin", "Chicago", "Momma Dean führt eine lokale neo-tribale Gemeinschaft."),
            n("Quantum Princess", "sr5-anarchy-chicago-chaos", "Charaktere", "Deckerin", "Chicago", "Quantum Princess ist als Chicagoer Deckerin belegt."),
            n("Sid Gambetti", "sr5-mission-chicago", "Personen und Kontakte", "Lokaler Akteur", "Chicago", "Sid Gambetti ist als Akteur im Chicago-Missionsmaterial belegt."),
            n("Chicago Anarchist Collective", "sr4-feral-cities", "Kapitel Chicago", "Anarchistisches Netzwerk", "Chicago", "Das Chicago Anarchist Collective vernetzt lokale anarchistische Strukturen.", "group"),
            n("Jolly Rogers", "sr2-bug-city", "PDF-Seite 129", "Gang", "Chicago", "Die Jolly Rogers sind eine in Bug City belegte Gang.", "group"),
            n("Desolation Angels", "sr5-anarchy-chicago-chaos", "Gangs", "Gang", "Chicago", "Die Desolation Angels gehören zur Ganglandschaft Chicagos.", "group"),
            n("The Ancients", "sr5-anarchy-chicago-chaos", "Gangs", "Go-Gang", "Chicago", "Die Ancients unterhalten eine Präsenz im Chicagoer Plex.", "group"),
            n("The Horde", "sr5-anarchy-chicago-chaos", "Gangs", "Gang", "Chicago", "The Horde ist als Chicagoer Gang belegt.", "group"),
        ],
    },
    "boston": {
        "name": "Boston", "year": 2076, "center": (42.3601, -71.0589),
        "bounds": [[42.15, -71.35], [42.58, -70.75]], "zoom": 10,
        "books": ["sr5-lockdown", "sr5-sperrzone-boston", "sr5-gefahr-in-boston",
                  "sr5-shadowrun-chronicles-boston-adventures"],
        "profile": {
            "SR5": ("sr5-sperrzone-boston", "Sperrzone Boston", "gesamter Band", "Boston wird nach der KFS-Krise abgeriegelt; Konzerne, Sicherheitskräfte und Überlebende ringen innerhalb der Sperrzone um Kontrolle."),
        },
        "districts": [
            ("Boston Lockdown Zone", (42.3601, -71.0589), "Die abgeriegelte Bostoner Zone bildet den räumlichen Rahmen der KFS-Krise.", "SR5", "sr5-sperrzone-boston", "Kapitel Sperrzone"),
            ("Cambridge", (42.3736, -71.1097), "Cambridge ist Wissenschafts- und Universitätszentrum sowie Brennpunkt der MIT&T-Ereignisse.", "SR5", "sr5-sperrzone-boston", "Kapitel Cambridge"),
            ("Fenway", (42.345, -71.099), "Fenway verbindet Sportstätten, Hochschulen und urbane Krisenschauplätze.", "SR5", "sr5-lockdown", "Kapitel Boston"),
            ("Four Corners", (42.294, -71.071), "Four Corners ist ein lokaler Siedlungs- und Konfliktraum innerhalb der Sperrzone.", "SR5", "sr5-lockdown", "Kapitel Four Corners"),
            ("Boston Harbor", (42.355, -70.99), "Der Hafen bleibt Verkehrsweg, Fluchtroute und Schauplatz konkurrierender Operationen.", "SR5", "sr5-sperrzone-boston", "Kapitel Hafen"),
            ("Chelsea", (42.3918, -71.0328), "Chelsea ist als eigener Teilraum im Bostoner Sperrzonenmaterial belegt.", "SR5", "sr5-lockdown", "Kapitel Chelsea"),
        ],
        "places": [
            p("Aqua Arcana", "Boston Harbor", "sr5-lockdown", "Orte in Boston", "Aqua Arcana ist ein benannter Bostoner Schauplatz.", "Magie und Erwachte"),
            p("Aurelius Academy", "Boston Lockdown Zone", "sr5-lockdown", "Orte in Boston", "Die Aurelius Academy ist ein Bildungs- und Forschungsschauplatz.", "Bildung und Kultur"),
            p("MIT&T Containment Zone", "Cambridge", "sr5-sperrzone-boston", "Kapitel MIT&T", "Die abgeschirmte MIT&T-Zone ist ein Zentrum der Bostoner KFS-Katastrophe.", "Sondergebiete", [-71.0935, 42.3591]),
            p("Enoch-Fuller House", "Boston Lockdown Zone", "sr5-sperrzone-boston", "Schauplatz Enoch-Fuller-Haus", "Das Enoch-Fuller-Haus ist ein benannter Missionsschauplatz.", "Sonstige Spots"),
            p("The Alabaster Maiden", "Boston Lockdown Zone", "sr5-sperrzone-boston", "Schauplatz Alabaster Maiden", "The Alabaster Maiden ist ein Treffpunkt im Sperrzonenmaterial.", "Bars und Kneipen"),
            p("The Beaded Shamrock", "Boston Lockdown Zone", "sr5-sperrzone-boston", "Schauplatz Beaded Shamrock", "The Beaded Shamrock ist ein Bostoner Treffpunkt.", "Bars und Kneipen"),
            p("The Braintrust", "Cambridge", "sr5-sperrzone-boston", "Schauplatz Braintrust", "The Braintrust ist ein in Sperrzone Boston belegter Schauplatz.", "Matrix und Technik"),
            p("The Nub", "Boston Lockdown Zone", "sr5-sperrzone-boston", "Schauplatz Der Nub", "The Nub ist ein lokaler Treffpunkt innerhalb der Zone.", "Bars und Kneipen"),
            p("Fenway Colleges", "Fenway", "sr5-lockdown", "Kapitel Universitäten", "Die Fenway Colleges bilden einen Hochschulkomplex in der Krisenzone.", "Bildung und Kultur"),
            p("Franklin Park", "Four Corners", "sr5-sperrzone-boston", "Kapitel Boston", "Franklin Park ist als geografischer und taktischer Schauplatz belegt.", "Freizeit und Natur", [-71.092, 42.305]),
            p("Knight Errant Station", "Boston Lockdown Zone", "sr5-sperrzone-boston", "Schauplatz Knight-Errant-Station", "Die Knight-Errant-Station ist ein Sicherheitsstandort in der Sperrzone.", "Sicherheit und Justiz"),
        ],
        "people": [
            n("Aaron Creech", "sr5-sperrzone-boston", "Charaktere", "Lokaler Akteur", "Boston", "Aaron Creech ist im Charakterbestand von Sperrzone Boston belegt."),
            n("Aiden Wagner", "sr5-sperrzone-boston", "Charaktere", "Knight-Errant-Angehöriger und Runner", "Boston", "Aiden Wagner bewegt sich zwischen Knight Errant und den Schatten."),
            n("Brandon Wilson", "sr5-lockdown", "Characters", "Lokaler Akteur", "Boston", "Brandon Wilson ist im Charakterbestand von Lockdown belegt."),
            n("Daniel James", "sr5-lockdown", "Characters", "Lokaler Akteur", "Boston", "Daniel James ist im Charakterbestand von Lockdown belegt."),
            n("Pendleton Wynn", "sr5-sperrzone-boston", "Charaktere", "Lokaler Akteur", "Boston", "Pendleton Wynn ist im Charakterbestand von Sperrzone Boston belegt."),
            n("Zoh Rothberg", "sr5-sperrzone-boston", "Charaktere", "Lokaler Akteur", "Boston", "Zoh Rothberg ist im Charakterbestand von Sperrzone Boston belegt."),
            n("Bane-Sidhe", "sr5-lockdown", "Fraktionen", "Organisation", "Boston", "Bane-Sidhe operiert während der Bostoner Krise als relevante Fraktion.", "group"),
            n("Mama’s Boyz", "sr5-lockdown", "Gangs", "Gang", "Boston", "Mama’s Boyz gehören zur lokalen Ganglandschaft.", "group"),
            n("Wicked", "sr5-sperrzone-boston", "Gangs", "Gang", "Boston", "Wicked ist eine in der Sperrzone aktive Gang.", "group"),
            n("Vory v Zakone", "sr5-lockdown", "Organisiertes Verbrechen", "Syndikat", "Boston", "Die Vory v Zakone ist im Bostoner Untergrund aktiv.", "group"),
        ],
    },
    "hong-kong": {
        "name": "Hongkong", "year": 2070, "center": (22.3193, 114.1694),
        "bounds": [[22.15, 113.80], [22.60, 114.50]], "zoom": 10,
        "books": ["sr4-runner-havens", "sr5-hong-kong-neon-contrails-2050"],
        "profile": {
            "SR4": ("sr4-runner-havens", "Runner Havens", "Kapitel Hong Kong", "Hongkong ist ein dichter, freier Konzern- und Schattenhafen mit Triaden, Geistern und internationalem Handel."),
            "SR5": ("sr5-hong-kong-neon-contrails-2050", "Hong Kong Neon Contrails (2050)", "gesamter Band", "Der historische 2050-Stand zeigt die frühere Machtordnung und Schauplätze des Plexes."),
        },
        "districts": [
            ("Central District", (22.2819, 114.1582), "Central ist das hochverdichtete Finanz- und Machtzentrum Hongkongs.", "SR4", "sr4-runner-havens", "Kapitel Central District"),
            ("Eastern District", (22.2841, 114.2241), "Eastern District verbindet dichte Wohn- und Geschäftsräume am Nordufer.", "SR4", "sr4-runner-havens", "Kapitel Eastern District"),
            ("Kowloon City", (22.3282, 114.1916), "Kowloon City ist ein dichter urbaner Teilraum mit Märkten, Werkstätten und Unterwelt.", "SR4", "sr4-runner-havens", "Kapitel Kowloon City"),
            ("Wanchai-Causeway", (22.2795, 114.1818), "Wanchai-Causeway verbindet Vergnügung, Handel und repräsentative Standorte.", "SR4", "sr4-runner-havens", "Kapitel Wanchai-Causeway"),
            ("Aberdeen Harbor", (22.248, 114.155), "Aberdeen Harbor ist ein südlicher Hafen- und Küstenraum.", "SR4", "sr4-runner-havens", "Kapitel Southern Coast"),
            ("Kwun Tong", (22.312, 114.226), "Kwun Tong ist ein östlicher Industrie- und Wohnbezirk.", "SR4", "sr4-runner-havens", "Kapitel Kwun Tong"),
            ("Yau Tsim Mong", (22.313, 114.170), "Yau Tsim Mong bildet einen dicht bebauten Teil Kowloons.", "SR4", "sr4-runner-havens", "Kapitel Yau Tsim Mong"),
            ("Tolo Harbor", (22.445, 114.214), "Tolo Harbor umfasst den nördlichen Hafen- und Anlagenraum.", "SR5", "sr5-hong-kong-neon-contrails-2050", "Kapitel Tolo Harbor Complex"),
        ],
        "places": [
            p("Chop-Chop Shop", "Kowloon City", "sr4-runner-havens", "Kapitel Kowloon City", "Der Chop-Chop Shop ist eine in Kowloon City belegte Schattenklinik.", "Medizin"),
            p("Cloud Nine", "Central District", "sr4-runner-havens", "Kapitel Central District", "Cloud Nine ist ein exklusiver Treffpunkt im Central District.", "Bars und Clubs"),
            p("Evolution", "Eastern District", "sr4-runner-havens", "Kapitel Eastern District", "Evolution ist ein benannter Schauplatz im Eastern District.", "Bars und Clubs"),
            p("Happy Valley Arena", "Wanchai-Causeway", "sr4-runner-havens", "Kapitel Wanchai-Causeway", "Die Happy Valley Arena ist ein großer Veranstaltungs- und Sportort.", "Freizeit und Natur", [114.184, 22.272]),
            p("Kai Tak Night Market", "Kowloon City", "sr4-runner-havens", "Kapitel Kowloon City", "Der Kai Tak Night Market ist ein bedeutender Nachtmarkt und Schattenkontaktpunkt.", "Einkaufen"),
            p("Luk Yu Teahouse", "Central District", "sr4-runner-havens", "Kapitel Central District", "Das Luk Yu Teahouse ist ein traditionsreicher Treffpunkt.", "Restaurants", [114.155, 22.282]),
            p("Shangri-La", "Aberdeen Harbor", "sr4-runner-havens", "Kapitel Southern Coast", "Shangri-La ist ein an der südlichen Küste belegter Schauplatz.", "Hotels"),
            p("The Whampoa", "Kowloon City", "sr4-runner-havens", "Kapitel Kowloon City", "The Whampoa ist ein markanter Handels- und Vergnügungskomplex.", "Einkaufen", [114.190, 22.305]),
            p("Tolo Harbor Complex", "Tolo Harbor", "sr5-hong-kong-neon-contrails-2050", "Kapitel Tolo Harbor Complex", "Der Tolo Harbor Complex ist ein zentraler Anlagen- und Hafenschauplatz des historischen Quellenstands.", "Konzerne"),
        ],
        "people": [
            n("Bradley McTaggart", "sr5-hong-kong-neon-contrails-2050", "Charaktere", "Lokaler Akteur", "Hongkong", "Bradley McTaggart ist im Personenbestand von Neon Contrails belegt."),
            n("Colonel James Zhang", "sr5-hong-kong-neon-contrails-2050", "Charaktere", "Militärischer Akteur", "Hongkong", "Colonel James Zhang ist im Personenbestand von Neon Contrails belegt."),
            n("Ma Bolin", "sr5-hong-kong-neon-contrails-2050", "Charaktere", "Lokaler Akteur", "Hongkong", "Ma Bolin ist im Personenbestand von Neon Contrails belegt."),
            n("Yu Longwei", "sr5-hong-kong-neon-contrails-2050", "Charaktere", "Lokaler Akteur", "Hongkong", "Yu Longwei ist im Personenbestand von Neon Contrails belegt."),
            n("The Tolo Vory", "sr4-runner-havens", "Kapitel Hong Kong", "Vory-Gruppe", "Tolo Harbor", "The Tolo Vory ist eine im Hongkonger Untergrund aktive Gruppe.", "group", "Tolo Harbor"),
        ],
    },
    "london": {
        "name": "London", "year": 2075, "center": (51.5074, -0.1278),
        "bounds": [[51.25, -0.65], [51.78, 0.35]], "zoom": 9,
        "books": ["sr1-london-sourcebook", "sr5-mission-london", "sr5-srmc-london-falling"],
        "profile": {
            "SR1": ("sr1-london-sourcebook", "London Sourcebook", "gesamter Band", "London ist ein streng geschichteter Plex aus Krone, Konzernen, toxischen Zonen, Unterplex und vielfältiger Unterwelt."),
            "SR5": ("sr5-mission-london", "Mission London", "gesamter Band", "Der spätere Missionsstand ergänzt London um aktuelle Akteure und konkrete Einsatzorte."),
        },
        "districts": [
            ("City of London", (51.5155, -0.0922), "Die City bildet das Finanz- und Konzernzentrum des Plexes.", "SR1", "sr1-london-sourcebook", "PDF-Seite 79"),
            ("West End", (51.511, -0.128), "Das West End ist Vergnügungs-, Kultur- und Geschäftsraum.", "SR5", "sr5-mission-london", "Kapitel West End"),
            ("Soho", (51.513, -0.132), "Soho ist ein dichtes Ausgeh- und Schattenviertel.", "SR5", "sr5-srmc-london-falling", "Kapitel Soho"),
            ("Westminster", (51.4995, -0.1248), "Westminster bildet das politische Zentrum Londons.", "SR5", "sr5-mission-london", "Kapitel Westminster"),
            ("Whitechapel", (51.516, -0.072), "Whitechapel ist ein östlicher Stadtteil mit eigener Unterwelt- und Straßenszene.", "SR1", "sr1-london-sourcebook", "Kapitel Whitechapel"),
            ("Wapping and Shadwell", (51.508, -0.057), "Wapping und Shadwell bilden einen östlichen Hafen- und Wohnraum.", "SR1", "sr1-london-sourcebook", "PDF-Seite 80"),
            ("Hampstead", (51.556, -0.178), "Hampstead und die Heath bilden einen nördlichen Grün- und Wohnraum.", "SR5", "sr5-mission-london", "Kapitel Hampstead"),
            ("Lambeth Containment Zone", (51.493, -0.112), "Die Lambeth Containment Zone ist ein abgeriegelter innerstädtischer Sonderraum.", "SR1", "sr1-london-sourcebook", "PDF-Seite 114"),
            ("The Underplex", (51.514, -0.141), "Der Underplex ist ein unterirdischer Handels-, Verkehrs- und Schattenraum.", "SR1", "sr1-london-sourcebook", "Kapitel Underplex"),
        ],
        "places": [
            p("British Industrial Arcology", "City of London", "sr1-london-sourcebook", "PDF-Seite 112", "Die British Industrial Arcology ist ein großer Konzernkomplex.", "Konzerne"),
            p("The British Museum", "West End", "sr1-london-sourcebook", "PDF-Seite 74", "Das British Museum ist Wahrzeichen, Kulturort und wiederkehrender Missionsschauplatz.", "Bildung und Kultur", [-0.1269, 51.5194]),
            p("Covent Garden Market", "West End", "sr1-london-sourcebook", "PDF-Seite 113", "Covent Garden Market ist ein zentraler Handels- und Vergnügungsort.", "Einkaufen", [-0.1228, 51.5117]),
            p("Euston Station", "The Underplex", "sr1-london-sourcebook", "PDF-Seite 65", "Euston Station ist ein wichtiger Verkehrszugang.", "Verkehr", [-0.1337, 51.5282]),
            p("Glenwood Primary School", "London", "sr5-srmc-london-falling", "Schauplatz Glenwood Primary School", "Die Glenwood Primary School ist ein Missionsschauplatz.", "Bildung und Kultur"),
            p("Hampstead Heath", "Hampstead", "sr5-mission-london", "Schauplatz Hampstead Heath", "Hampstead Heath ist Grünraum und Missionsschauplatz.", "Freizeit und Natur", [-0.1657, 51.5608]),
            p("Oxford Street Underplex Access", "The Underplex", "sr1-london-sourcebook", "PDF-Seite 41", "Der Zugang an der Oxford Street führt in den Underplex.", "Verkehr"),
            p("Temple Bar", "City of London", "sr1-london-sourcebook", "PDF-Seite 84", "Temple Bar ist ein benannter Ort im Machtzentrum der City.", "Sichtseeing und Monumente"),
            p("Zowie’s Bar Node", "The Underplex", "sr5-srmc-london-falling", "Schauplatz Zowie’s Bar Node", "Zowie’s Bar Node ist ein virtueller oder vernetzter Treffpunkt.", "Matrix und virtuelle Orte"),
        ],
        "people": [
            n("Addison Hughes", "sr5-mission-london", "Personen", "Lokaler Akteur", "London", "Addison Hughes ist im Personenbestand von Mission London belegt."),
            n("Agatha Hawthorne", "sr5-srmc-london-falling", "Characters", "Lokale Akteurin", "London", "Agatha Hawthorne ist im Personenbestand von London Falling belegt."),
            n("Bartholomew Johnson", "sr5-srmc-london-falling", "Characters", "Lokaler Akteur", "London", "Bartholomew Johnson ist im Personenbestand von London Falling belegt."),
            n("Charles Findley", "sr5-srmc-london-falling", "Characters", "Lokaler Akteur", "London", "Charles Findley ist im Personenbestand von London Falling belegt."),
            n("Dr. Richard Pelletiere", "sr5-srmc-london-falling", "Characters", "Wissenschaftler", "London", "Dr. Richard Pelletiere ist eine zentrale Person des London-Falling-Szenarios."),
            n("Lady Rhiannon Glendower", "sr5-srmc-london-falling", "Characters", "Adlige und druidische Akteurin", "London", "Lady Rhiannon Glendower ist im Londoner Macht- und Magieumfeld belegt."),
            n("Lord James Helling", "sr5-srmc-london-falling", "Characters", "Adliger Akteur", "London", "Lord James Helling ist im Personenbestand von London Falling belegt."),
            n("Nigel Patterson", "sr5-srmc-london-falling", "Characters", "Lokaler Akteur", "London", "Nigel Patterson ist im Personenbestand von London Falling belegt."),
            n("Walt Walker", "sr5-srmc-london-falling", "Characters", "Lokaler Akteur", "London", "Walt Walker ist im Personenbestand von London Falling belegt."),
            n("New Druidic Movement", "sr5-srmc-london-falling", "Fraktionen", "Druidische Organisation", "London", "Das New Druidic Movement ist eine einflussreiche magische Organisation.", "group"),
            n("Druidic Hidden Circles", "sr1-london-sourcebook", "PDF-Seite 40", "Druidische Netzwerke", "London", "Die verborgenen druidischen Zirkel sind Teil der britischen Magielandschaft.", "group"),
            n("The Templars", "sr1-london-sourcebook", "PDF-Seite 43", "Organisation", "London", "Die Templars sind als Londoner Organisation belegt.", "group"),
        ],
    },
    "muenchen": {
        "name": "München", "year": 2080, "center": (48.1374, 11.5755),
        "bounds": [[47.98, 11.28], [48.35, 11.90]], "zoom": 10,
        "books": ["sr4-munchen-noir", "sr6-datapuls-munchen"],
        "profile": {
            "SR4": ("sr4-munchen-noir", "München Noir", "gesamter Band", "München ist ein Medien-, Konzern- und Politplex mit scharfen sozialen Gegensätzen."),
            "SR6": ("sr6-datapuls-munchen", "Datapuls: München", "S. 2–29", "Der Stand von 2080 vertieft Stadtteile, Sonderverwaltungszonen, Konzerne und die lokale Szene."),
        },
        "districts": [
            ("Altstadt-Lehel", (48.140, 11.578), "Altstadt-Lehel umfasst das historische Zentrum, Einkaufsachsen und besonders teure Wohnlagen.", "SR6", "sr6-datapuls-munchen", "S. 5–8"),
            ("Schwabing", (48.166, 11.586), "Schwabing verbindet Universität, Szene, teure Wohnlagen und den Englischen Garten.", "SR6", "sr6-datapuls-munchen", "S. 7–8"),
            ("Bogenhausen", (48.154, 11.633), "Bogenhausen ist ein gehobener östlicher Wohn- und Konzernraum.", "SR4", "sr4-munchen-noir", "PDF-Seite 9"),
            ("Milbertshofen", (48.182, 11.575), "Milbertshofen ist stark von BMW, Industrie und großen Anlagen geprägt.", "SR6", "sr6-datapuls-munchen", "Kapitel Konzerne"),
            ("Sonderverwaltungszone Hasenbergl", (48.213, 11.555), "Hasenbergl ist eine abgeriegelte Problemzone im Münchner Norden.", "SR6", "sr6-datapuls-munchen", "S. 9"),
            ("Sonderverwaltungszone Perlach", (48.100, 11.630), "Perlach ist eine von Armut, Gewalt und harter Sicherheitsverwaltung geprägte Sonderzone.", "SR6", "sr6-datapuls-munchen", "S. 9"),
            ("Sonderverwaltungszone Großried", (48.108, 11.465), "Großried umfasst Großhadern, Klinik- und Universitätsanlagen sowie prekäre Wohnräume.", "SR6", "sr6-datapuls-munchen", "S. 9"),
            ("Laim Stadtkrieg-Arena", (48.140, 11.500), "Laim wurde in eine großflächige Stadtkrieg-Arena umgewandelt.", "SR6", "sr6-datapuls-munchen", "S. 9"),
            ("Freising", (48.402, 11.748), "Freising ist Regierungssitz Bayerns, bleibt aber eine eigenständige Gemeinde außerhalb des Münchner Sprawls.", "SR6", "sr6-datapuls-munchen", "S. 9"),
            ("Sperrgebiet Dachau", (48.270, 11.468), "Der Osten Dachaus ist seit dem Erwachen ein astral verseuchtes Sperrgebiet.", "SR6", "sr6-datapuls-munchen", "S. 8–9"),
        ],
        "places": [
            p("Bayrischer Hof", "Altstadt-Lehel", "sr6-datapuls-munchen", "S. 5", "Der Bayrische Hof ist eine Spitzenadresse und neutraler Treffpunkt für Reiche, Politiker und Manager.", "Hotels", [11.5701, 48.1405]),
            p("München Hosuto", "Altstadt-Lehel", "sr6-datapuls-munchen", "S. 5", "Das München Hosuto ist ein Luxushotel und bevorzugter Treffpunkt japanischer Geschäftsleute.", "Hotels"),
            p("Anna Excelsior Hotel", "Altstadt-Lehel", "sr6-datapuls-munchen", "S. 5", "Das Anna Excelsior bietet diskrete Unterbringung nahe dem Hauptbahnhof.", "Hotels"),
            p("Two Towers", "Milbertshofen", "sr6-datapuls-munchen", "S. 5", "Two Towers ist ein Geschäftshotel am Mittleren Ring.", "Hotels"),
            p("Englischer Garten", "Schwabing", "sr6-datapuls-munchen", "S. 7", "Der Englische Garten ist zentraler Grünraum, Sportort und Teil der Münchner Identität.", "Freizeit und Natur", [11.6035, 48.1642]),
            p("Schrannenhalle", "Altstadt-Lehel", "sr6-datapuls-munchen", "S. 6", "Die Schrannenhalle ist ein hochwertiger Lebensmittelmarkt und Informationsumschlagplatz der Oberschicht.", "Einkaufen", [11.576, 48.134]),
            p("Theatinerstraße", "Altstadt-Lehel", "sr6-datapuls-munchen", "S. 6", "Die Theatinerstraße ist eine exklusive Einkaufsachse.", "Einkaufen", [11.576, 48.142]),
            p("Hofbräuhaus", "Altstadt-Lehel", "sr4-munchen-noir", "PDF-Seite 40", "Das Hofbräuhaus ist Wahrzeichen, Gastronomie- und Touristentreffpunkt.", "Restaurants", [11.5803, 48.1376]),
            p("Kunstpark Nord", "Milbertshofen", "sr4-munchen-noir", "PDF-Seite 41", "Kunstpark Nord ist ein großer Ausgeh- und Szenekomplex.", "Bars und Clubs"),
            p("Medienpark", "München", "sr4-munchen-noir", "PDF-Seite 30", "Der Medienpark konzentriert Studios und Unternehmen der Münchner Medienindustrie.", "Konzerne"),
            p("Renraku Arkologie Europa", "München", "sr4-munchen-noir", "PDF-Seite 11", "Die Renraku-Arkologie Europa in Harlaching ist ein dominanter extraterritorialer Konzernstandort.", "Konzerne"),
            p("M-Airport", "Freising", "sr4-munchen-noir", "PDF-Seite 24", "Der Großflughafen bei Freising ist das internationale Luftverkehrstor des Plexes.", "Verkehr", [11.7861, 48.3538]),
            p("Café Käfer", "Altstadt-Lehel", "sr4-munchen-noir", "PDF-Seite 40", "Café Käfer ist ein Treffpunkt der gehobenen Münchner Szene.", "Restaurants"),
            p("Gorky Park", "München", "sr4-munchen-noir", "PDF-Seite 66", "Gorky Park ist ein benannter Münchner Szenetreff.", "Bars und Clubs"),
        ],
        "people": [
            n("Franz Büchner", "sr4-munchen-noir", "PDF-Seite 123", "Lokaler Akteur", "München", "Franz Büchner ist im Personenbestand von München Noir belegt."),
            n("Alexej", "sr4-munchen-noir", "PDF-Seite 90", "Straßensamurai", "München", "Alexej ist als Straßensamurai im Münchner Abenteuerteil belegt."),
            n("Bookingagentur mozART", "sr4-munchen-noir", "PDF-Seite 34", "Bookingagentur", "Münchner Medien- und Musikszene", "mozART vermittelt Künstler und Aufträge in der Münchner Medienlandschaft.", "group"),
            n("Chomjak", "sr4-munchen-noir", "PDF-Seite 82", "Vory-Gruppe", "München", "Chomjak ist im Münchner Vory-Umfeld belegt.", "group"),
            n("Vory an der Isar", "sr4-munchen-noir", "PDF-Seite 56", "Syndikat", "München", "Die Vory an der Isar ist eine zentrale Fraktion des organisierten Verbrechens.", "group"),
            n("USPD", "sr4-munchen-noir", "PDF-Seite 15", "Politische Untergrundorganisation", "München", "Die USPD ist im politischen Untergrund Münchens aktiv.", "group"),
        ],
    },
    "frankfurt": {
        "name": "Groß-Frankfurt", "year": 2078, "center": (50.1109, 8.6821),
        "bounds": [[49.2, 7.9], [50.65, 9.25]], "zoom": 8,
        "books": ["sr2-chrom-dioxin", "sr5-datapuls-frankfurt"],
        "profile": {
            "SR2": ("sr2-chrom-dioxin", "Chrom & Dioxin", "Kapitel Groß-Frankfurt", "Groß-Frankfurt wird als weit ausgreifender Plex mit Bezirken, Konzernen und toxischen Altlasten beschrieben."),
            "SR5": ("sr5-datapuls-frankfurt", "Datapuls Frankfurt", "gesamter Band", "Der spätere Quellenstand vertieft Banken, Politik, Unterwelt und die Teilräume des Plexes."),
        },
        "districts": [
            ("Frankfurt-City", (50.1109, 8.6821), "Frankfurt-City ist Banken-, Verwaltungs- und Verkehrskern des Plexes.", "SR2", "sr2-chrom-dioxin", "PDF-Seite 6"),
            ("Aschaffenburg", (49.977, 9.152), "Aschaffenburg bildet einen östlichen Bezirk Groß-Frankfurts.", "SR2", "sr2-chrom-dioxin", "PDF-Seite 6"),
            ("Bergstraße", (49.680, 8.620), "Bergstraße ist ein südlicher Bezirk zwischen Rhein-Main und Rhein-Neckar.", "SR2", "sr2-chrom-dioxin", "PDF-Seite 6"),
            ("Biblis", (49.691, 8.458), "Biblis ist ein westlicher Teilraum des Plexes mit industriellen und ökologischen Altlasten.", "SR2", "sr2-chrom-dioxin", "PDF-Seite 6"),
            ("Darmstadt", (49.8728, 8.6512), "Darmstadt ist Wissenschafts-, Technik- und Verwaltungsstandort.", "SR2", "sr2-chrom-dioxin", "PDF-Seite 6"),
            ("Hanau", (50.126, 8.929), "Hanau ist ein östlicher Industrie- und Siedlungsbezirk.", "SR2", "sr2-chrom-dioxin", "Kapitel Bezirk Hanau"),
            ("Heidelberg", (49.3988, 8.6724), "Heidelberg ist Universitätsstadt und südlicher Wissensstandort des Großraums.", "SR2", "sr2-chrom-dioxin", "Kapitel Heidelberg"),
            ("Ludwigshafen", (49.4774, 8.4452), "Ludwigshafen ist ein stark industriell und chemisch geprägter Teilraum.", "SR2", "sr2-chrom-dioxin", "Kapitel Ludwigshafen"),
            ("Mannheim", (49.4875, 8.4660), "Mannheim ist ein Industrie-, Hafen- und Verkehrszentrum.", "SR2", "sr2-chrom-dioxin", "Kapitel Mannheim"),
            ("Offenbach", (50.0956, 8.7761), "Offenbach ist ein dicht bebauter östlicher Bezirk des Kernplexes.", "SR2", "sr2-chrom-dioxin", "Kapitel Offenbach"),
            ("Mainz", (49.9929, 8.2473), "Mainz liegt am westlichen Rhein-Main-Rand und ist als eigener Teilraum belegt.", "SR5", "sr5-datapuls-frankfurt", "Kapitel Mainz"),
            ("Wiesbaden", (50.0782, 8.2398), "Wiesbaden ist Verwaltungs-, Kur- und Glücksspielstandort im westlichen Plex.", "SR5", "sr5-datapuls-frankfurt", "Kapitel Wiesbaden"),
        ],
        "places": [
            p("Commerzbank-Tower", "Frankfurt-City", "sr5-datapuls-frankfurt", "Kapitel Frankfurt-City", "Der Commerzbank-Tower ist ein markanter Banken- und Konzernstandort.", "Konzerne", [8.674, 50.110]),
            p("Hauptquartier der AG Chemie", "Ludwigshafen", "sr5-datapuls-frankfurt", "Kapitel Konzerne", "Das Hauptquartier der AG Chemie ist ein zentraler Konzernstandort im Plex.", "Konzerne"),
            p("Hotel Schlossblick", "Groß-Frankfurt", "sr5-datapuls-frankfurt", "Hotspots", "Hotel Schlossblick ist ein benannter Übernachtungs- und Treffpunkt.", "Hotels"),
            p("Jägerlatein", "Groß-Frankfurt", "sr5-datapuls-frankfurt", "Hotspots", "Jägerlatein ist ein im Datapuls belegtes Restaurant.", "Restaurants"),
            p("Spielbank Wiesbaden", "Wiesbaden", "sr5-datapuls-frankfurt", "Hotspots", "Die Spielbank Wiesbaden ist Casino, gesellschaftlicher Treffpunkt und möglicher Schattenkontakt.", "Ausgehen", [8.245, 50.086]),
            p("Ruprecht-Karls-Universität", "Heidelberg", "sr2-chrom-dioxin", "PDF-Seite 35", "Die Heidelberger Universität ist ein traditionsreicher Forschungs- und Bildungsstandort.", "Bildung und Kultur", [8.706, 49.410]),
            p("Frankfurter Hafen", "Frankfurt-City", "sr2-chrom-dioxin", "PDF-Seite 28", "Der Hafen ist ein Verkehrs-, Industrie- und Schmuggelraum des Plexes.", "Verkehr"),
            p("Gallusviertel", "Frankfurt-City", "sr2-chrom-dioxin", "PDF-Seite 26", "Das Gallusviertel ist als innerstädtischer Teilraum im frühen Quellenstand belegt.", "Stadtteile"),
            p("Niederrad", "Frankfurt-City", "sr2-chrom-dioxin", "PDF-Seite 26", "Niederrad ist ein südlicher Stadtteil im Kernraum Frankfurt.", "Stadtteile"),
        ],
        "people": [
            n("AG Chemie", "sr5-datapuls-frankfurt", "Kapitel Konzerne", "Megakonzern", "Groß-Frankfurt", "AG Chemie ist eine der prägenden Konzernmächte des Plexes.", "group", "Hauptquartier der AG Chemie"),
            n("Die Grauen Wölfe", "sr5-datapuls-frankfurt", "Kapitel Unterwelt", "Gang oder extremistische Gruppe", "Groß-Frankfurt", "Die Grauen Wölfe sind als lokale Gruppe im Frankfurter Quellenstand belegt.", "group"),
            n("Yakuza", "sr5-datapuls-frankfurt", "Kapitel Unterwelt", "Syndikat", "Groß-Frankfurt", "Die Yakuza unterhält Interessen im Groß-Frankfurter Plex.", "group"),
        ],
    },
}


def book_entry(work_id: str) -> dict:
    work = WORKS[work_id]
    return {
        "id": work_id,
        "registryWorkId": work_id,
        "title": work["title"],
        "edition": work["edition"],
    }


def empty_collection(name: str, topology: dict | None = None) -> dict:
    result = {"type": "FeatureCollection", "name": name, "features": []}
    if topology is not None:
        result["topology"] = topology
    return result


def ensure_package(city_id: str, config: dict) -> None:
    city_dir = ROOT / "data" / city_id
    city_dir.mkdir(parents=True, exist_ok=True)
    for filename, payload in {
        "atlas.json": [],
        "zones.geojson": empty_collection(
            f"{config['name']} Gebietsstatus",
            {"model": "exclusive-partition", "priority": ["corporate", "normal"], "unresolved_overlap_area_degrees_squared": 0},
        ),
        "exterritorial.geojson": empty_collection(f"{config['name']} Extraterritorialität"),
        "districts.geojson": empty_collection(f"{config['name']} Lore-Distrikte"),
        "neighborhoods.geojson": empty_collection(f"{config['name']} Stadtteile"),
        "outskirts.geojson": empty_collection(f"{config['name']} Umland"),
        "city-boundary.geojson": empty_collection(f"{config['name']} Kartengrenze"),
    }.items():
        write_json(city_dir / filename, payload)
    manifest = {
        "schemaVersion": 1, "id": city_id, "name": config["name"],
        "year": config["year"], "dataVersion": 1, "availableEditions": [],
        "center": list(config["center"]), "zoom": config["zoom"],
        "overlayBounds": config["bounds"], "cityBounds": config["bounds"],
        "regionBounds": config["bounds"], "scopeLabel": config["name"],
        "atlasIntro": "", "summary": {},
        "files": {
            "places": "places.geojson", "people": "people.json", "atlas": "atlas.json",
            "zones": "zones.geojson", "exterritorial": "exterritorial.geojson",
            "districts": "districts.geojson", "neighborhoods": "neighborhoods.geojson",
            "outskirts": "outskirts.geojson", "boundary": "city-boundary.geojson",
            "labels": "labels.json", "sources": "sources.json",
        },
    }
    write_json(city_dir / "manifest.json", manifest)


def build_city(city_id: str, config: dict) -> None:
    ensure_package(city_id, config)
    anchors = {name: coordinates for name, coordinates, *_ in config["districts"]}
    anchors[config["name"]] = config["center"]
    catalogue = CityCatalogue(
        city_id, config["name"], config["center"], anchors,
        [book_entry(work_id) for work_id in config["books"]],
    )
    editions = {}
    for edition, (book_id, title, citation, summary) in config["profile"].items():
        editions[edition] = city_edition(
            edition, book_id, title, citation, summary,
            summary + " Die Zusammenfassung trennt Editionsstände und verweist auf die jeweilige Stadtquelle.",
        )
    catalogue.set_city_profile(
        f"{config['name']} gehört zu den eigenständig erschlossenen Schauplätzen der Sechsten Welt.",
        f"Dieses Kartenpaket bündelt belastbare Bezirke, Orte, Personen und Gruppen für {config['name']}. Nicht exakt georeferenzierbare Einträge bleiben ohne erfundene Kartenposition im Katalog.",
        editions,
    )

    district_names = set()
    for name, coordinates, summary, edition, book_id, citation in config["districts"]:
        district_names.add(name)
        title = WORKS[book_id]["title"]
        catalogue.add_place(
            name, name, edition, book_id, title, citation,
            category="Bezirke", summary=summary,
            coordinates=[coordinates[1], coordinates[0]],
        )
        props = catalogue.places[name_key(name)]["properties"]
        props["accuracy"] = "Lore-Bezirkszentrum; Grenzpolygon noch nicht georeferenziert"
        props["placement_note"] = f"Geografischer Bezugspunkt des Lore-Distrikts {name}"

    exact_names = set()
    for item in config["places"]:
        work = WORKS[item["book"]]
        catalogue.add_place(
            item["name"], item["scope"], work["edition"], item["book"], work["title"],
            item["citation"], category=item["category"], summary=item["summary"],
            coordinates=item["coordinates"], exact=item["coordinates"] is not None,
        )
        if item["coordinates"] is not None:
            exact_names.add(item["name"])

    for item in config["people"]:
        work = WORKS[item["book"]]
        catalogue.add_person(
            item["name"], work["edition"], item["book"], work["title"], item["citation"],
            role=item["role"], affiliation=item["affiliation"], summary=item["summary"],
            entity_type=item["entity_type"], location_name=item["location"],
        )

    catalogue.finish(
        config["year"],
        f"Quellenbasierter Arbeitsstand für {config['name']}; ungenaue Orte bleiben ausschließlich im Katalog.",
        config["bounds"],
        config["zoom"],
    )
    city_dir = ROOT / "data" / city_id
    places = json.loads((city_dir / "places.geojson").read_text(encoding="utf-8"))
    labels = []
    for feature in places["features"]:
        props = feature["properties"]
        if props["name"] not in district_names and props["name"] not in exact_names:
            feature["geometry"] = None
            props["accuracy"] = "Nur Stadt oder Lore-Teilraum belegt"
            props["placement_note"] = "Keine belastbare Einzelposition; Eintrag bleibt im Katalog"
        if props["name"] in district_names:
            lon, lat = feature["geometry"]["coordinates"]
            labels.append({"name": props["name"], "lat": lat, "lon": lon, "type": "district", "entity_id": props["id"]})
    write_json(city_dir / "places.geojson", places)
    write_json(city_dir / "labels.json", labels)


def update_city_registry() -> None:
    path = ROOT / "data/cities.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    by_id = {city["id"]: city for city in registry["cities"]}
    for city_id, config in CONFIGS.items():
        by_id[city_id] = {
            "id": city_id, "name": config["name"],
            "manifest": f"data/{city_id}/manifest.json", "year": config["year"],
        }
    preferred = [
        "berlin-2080", "hamburg-2080", "seattle", "rhein-ruhr-2082",
        "toronto-2080", "denver", "manhattan", "adl-2082",
        "chicago", "boston", "hong-kong", "london", "muenchen", "frankfurt",
    ]
    registry["cities"] = [by_id[city_id] for city_id in preferred if city_id in by_id]
    write_json(path, registry)


def main() -> None:
    for city_id, config in CONFIGS.items():
        build_city(city_id, config)
        print(f"OK {city_id}")
    update_city_registry()


if __name__ == "__main__":
    main()
