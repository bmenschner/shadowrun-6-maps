#!/usr/bin/env python3
"""Build the fourth city wave from the remaining verified source matrix."""

from __future__ import annotations

import json

from build_us_city_content import write_json
from build_wave1_city_packages import ROOT, WORKS, build_city, n, p


def city(
    name, year, center, bounds, book, title, summary, *,
    extra_books=(), places=(), people=(),
):
    edition = WORKS[book]["edition"]
    return {
        "name": name, "year": year, "center": center, "bounds": bounds, "zoom": 9,
        "books": [book, *extra_books],
        "profile": {
            edition: (book, title, "Stadt- oder Regionalkapitel", summary),
        },
        "districts": [
            (f"{name} Lore-Raum", center, summary, edition, book, "Stadt- oder Regionalkapitel"),
        ],
        "places": list(places),
        "people": list(people),
    }


CONFIGS = {
    "caracas": city(
        "Caracas", 2072, (10.4806, -66.9036), [[10.15, -67.25], [10.75, -66.55]],
        "sr4-shadowrun-4d-geisterkartelle", "Geisterkartelle",
        "Caracas verbindet den Hochlandsprawl mit dem Hafen La Guaira und ist ein Brennpunkt der Geisterkartell-Konflikte.",
        extra_books=("sr4-ghost-cartels", "sr4-dawn-of-the-artifacts-5-artifacts-unbound"),
        places=(
            p("Hafen La Guaira", "Caracas", "sr4-shadowrun-4d-geisterkartelle", "Hafen La Guaira (Caracas)", "Der Hafen ist Verkehrs-, Schmuggel- und Kartellschwerpunkt.", "Verkehr", [-66.933, 10.603]),
            p("Mesón Gordo Restaurant", "Caracas", "sr4-ghost-cartels", "Méson Gordo Restaurant", "Das Restaurant ist ein lokaler Treff- und Missionsort.", "Restaurants"),
            p("El Picaruelo", "La Guaira", "sr4-shadowrun-4d-geisterkartelle", "El Picaruelo", "El Picaruelo ist ein im Hafenraum belegter Schauplatz.", "Bars und Kneipen"),
            p("Ramos Villa", "El Ávila", "sr4-ghost-cartels", "Ramos Villa", "Die Villa liegt im El-Ávila-Raum und dient als Missionsschauplatz.", "Wohnen"),
            p("Caracas Cathedral", "Caracas", "sr4-dawn-of-the-artifacts-5-artifacts-unbound", "Caracas Cathedral", "Die Kathedrale ist religiöses Wahrzeichen und Abenteuerbezugspunkt.", "Religion und Magie", [-66.914, 10.506]),
        ),
        people=(
            n("Rayo", "sr4-ghost-cartels", "Rayo, Ork Gangboss", "Gangboss", "Caracas", "Rayo ist ein orkischer Ganganführer des Caracas-Quellenstands."),
        ),
    ),
    "st-louis": city(
        "St. Louis", 2050, (38.6270, -90.1994), [[38.35, -90.55], [38.95, -89.75]],
        "sr1-the-neo-anarchist-s-guide-to-north-america", "The Neo-Anarchist’s Guide to North America",
        "St. Louis ist ein bedeutender Mississippi-Verkehrsraum mit UCAS-, CAS- und Unterweltbezügen.",
    ),
    "santiago": city(
        "Nuevo Santiago", 2064, (-33.4489, -70.6693), [[-33.85, -71.15], [-33.05, -70.15]],
        "sr3-shadows-of-latin-america-v1-2", "Shadows of Latin America",
        "Nuevo Santiago ist Chiles politischer und wirtschaftlicher Kernsprawl, geprägt von Umweltbelastung und regionalen Machtkämpfen.",
        extra_books=("sr3-lateinamerika-in-den-schatten-v1-0",),
    ),
    "sydney": city(
        "Sydney", 2063, (-33.8688, 151.2093), [[-34.20, 150.65], [-33.45, 151.55]],
        "sr3-target-awakened-lands", "Target: Awakened Lands",
        "Sydney ist ein australischer Küstenplex mit starken Konzern-, Syndikats- und erwachten Einflüssen.",
        extra_books=("sr3-erwachte-lander", "sr5-gestohlene-seelen"),
        places=(
            p("Link Club Sydney", "Sydney", "sr5-gestohlene-seelen", "Link Club", "Der Sydney-Ableger gehört zur international vernetzten Clubkette.", "Bars und Clubs"),
        ),
        people=(
            n("Sydney Vory v Zakone", "sr3-target-awakened-lands", "Vory v Zakone", "Verbrechersyndikat", "Sydney", "Die Vory besitzt eine belegte Präsenz im australischen Plex.", "group"),
            n("Sydney Greek Mafia", "sr3-erwachte-lander", "Die griechische Mafia", "Mafiaorganisation", "Sydney", "Die griechische Mafia ist Teil der lokalen Unterwelt.", "group"),
        ),
    ),
    "austin": city(
        "Austin", 2053, (30.2672, -97.7431), [[29.95, -98.10], [30.60, -97.35]],
        "sr2-lone-star", "Lone Star",
        "Austin ist Regierungssitz des Freistaats Texas und eng mit Lone Star, Politik und regionaler Konzernwirtschaft verbunden.",
        people=(
            n("Lone Star Austin", "sr2-lone-star", "Power Structure", "Sicherheitskonzern", "Austin", "Lone Star ist ein zentraler Macht- und Sicherheitsakteur der Stadt.", "group"),
        ),
    ),
    "dublin": city(
        "Dublin", 2054, (53.3498, -6.2603), [[53.10, -6.70], [53.65, -5.85]],
        "sr2-tir-na-nog", "Tír na nÓg",
        "Dublin ist politisches, wirtschaftliches und touristisches Zentrum Tír na nÓgs unter strenger staatlicher und elfischer Kontrolle.",
        places=(
            p("Bar Flanagan", "Dublin", "sr2-tir-na-nog", "Bar Flanagan", "Bar Flanagan ist ein benannter Treffpunkt.", "Bars und Kneipen"),
            p("Saxon Hotel", "Dublin", "sr2-tir-na-nog", "Saxon Hotel", "Das Saxon Hotel ist ein Unterkunfts- und Geschäftsort.", "Hotels"),
            p("Davy Byrne’s", "Dublin", "sr2-tir-na-nog", "Davy Byrne’s", "Davy Byrne’s gehört zu den lokalen Gastronomie- und Kontaktorten.", "Bars und Kneipen"),
            p("Dublin International", "Dublin", "sr2-tir-na-nog", "Dublin International", "Der internationale Flughafen ist ein Hauptzugang der Insel.", "Verkehr", [-6.270, 53.421]),
            p("El Mocambo", "Dublin", "sr2-tir-na-nog", "El Mocambo", "El Mocambo ist ein lokaler Szenetreff.", "Bars und Clubs"),
            p("Fat Paddy’s", "Dublin", "sr2-tir-na-nog", "Fat Paddy’s", "Fat Paddy’s ist ein benannter Pub.", "Bars und Kneipen"),
            p("Leitrim Lodge", "Dublin", "sr2-tir-na-nog", "Leitrim Lodge", "Die Lodge ist als Unterkunft belegt.", "Hotels"),
            p("Monaghan’s Grill", "Dublin", "sr2-tir-na-nog", "Monaghan’s Grill", "Monaghan’s Grill ist ein lokaler Gastronomiestandort.", "Restaurants"),
        ),
        people=(
            n("Tír na nÓg Police", "sr2-tir-na-nog", "Police", "Staatliche Polizei", "Dublin", "Die Polizei setzt die strenge Ordnung des Tír in Dublin durch.", "group"),
            n("Dublin Street Gangs", "sr2-tir-na-nog", "Street Gangs", "Gangmilieu", "Dublin", "Mehrere Straßengangs bilden einen Teil der lokalen Unterwelt.", "group"),
        ),
    ),
    "dubai": city(
        "Dubai", 2072, (25.2048, 55.2708), [[24.75, 54.75], [25.60, 55.75]],
        "sr4-corporate-enclaves", "Corporate Enclaves",
        "Dubai ist eine luxuriöse Konzernenklave und globaler Geschäfts-, Reise- und Sicherheitsknoten.",
        extra_books=("sr4-boardroom-backstabs-1-damage-control",),
        people=(
            n("Mudaween / Dubai Police", "sr4-boardroom-backstabs-1-damage-control", "Mudaween / Dubai Police", "Polizei- und Sicherheitseinheit", "Dubai", "Die Mudaween gehören zur lokalen Polizeistruktur.", "group"),
        ),
    ),
    "las-vegas": city(
        "Las Vegas", 2073, (36.1699, -115.1398), [[35.75, -115.70], [36.55, -114.65]],
        "sr4-the-twilight-horizon", "The Twilight Horizon",
        "Las Vegas ist ein stark von Horizon, Casinos, Unterhaltung und organisierter Kriminalität geprägter Wüstenplex.",
        extra_books=("sr5-gestohlene-seelen",),
        places=(
            p("Desert Breeze Park", "Las Vegas", "sr4-the-twilight-horizon", "Desert Breeze Park", "Der Park ist ein öffentlicher Freizeit- und Missionsort.", "Freizeit und Natur", [-115.242, 36.130]),
            p("Fremont Street Experience", "Las Vegas", "sr4-the-twilight-horizon", "The Freemont Street Experience", "Fremont Street ist ein wichtiger Vergnügungs- und Tourismusraum.", "Ausgehen", [-115.143, 36.170]),
            p("University of Nevada Las Vegas", "Las Vegas", "sr4-the-twilight-horizon", "University of Nevada Las Vegas", "UNLV ist Bildungs-, Forschungs- und Veranstaltungsstandort.", "Bildung und Kultur", [-115.139, 36.108]),
            p("Link Club Las Vegas", "Las Vegas", "sr5-gestohlene-seelen", "Link Club", "Der lokale Ableger gehört zur internationalen Link-Club-Kette.", "Bars und Clubs"),
        ),
    ),
    "singapur": city(
        "Singapur", 2073, (1.3521, 103.8198), [[1.15, 103.55], [1.55, 104.10]],
        "sr3-shadows-of-asia", "Shadows of Asia",
        "Singapur ist ein hochkontrollierter asiatischer Handels-, Hafen-, Finanz- und Matrixknoten.",
        extra_books=("sr5-blutige-geschafte", "sr6-margin-calls-corporate-world-post-dis-plot"),
        places=(
            p("Marina Bay Orchid", "Singapur", "sr5-blutige-geschafte", "Marina Bay Orchid", "Die Marina Bay Orchid ist ein benannter Hotel- und Missionsstandort.", "Hotels"),
            p("Chid Ballroom, Fullerton Hotel", "Singapur", "sr6-margin-calls-corporate-world-post-dis-plot", "Chid Ballroom, The Fullerton Hotel, Singapore", "Der Ballsaal ist ein hochrangiger Veranstaltungs- und Geschäftsort.", "Hotels", [103.853, 1.286]),
        ),
    ),
    "kapstadt": city(
        "Kapstadt", 2072, (-33.9249, 18.4241), [[-34.35, 17.85], [-33.45, 19.05]],
        "sr4-vice", "Vice",
        "Kapstadt ist ein Hafen- und Tourismusplex der Azanischen Konföderation mit ausgeprägter Gang- und Konzernpräsenz.",
        extra_books=("sr4-unterwelten", "sr5-megakons-2078"),
        people=(
            n("Numbers Gang", "sr4-vice", "The Numbers Gang", "Gefängnis- und Straßengang", "Kapstadt", "Die Numbers Gang ist eine der prägenden Unterweltgruppen Kapstadts.", "group"),
            n("Saeder-Krupp Afrika", "sr5-megakons-2078", "S-K Afrika", "Konzernabteilung", "Kapstadt", "Saeder-Krupp unterhält starke regionale Interessen.", "group"),
        ),
    ),
    "nuernberg": city(
        "Nürnberg", 2074, (49.4521, 11.0767), [[49.20, 10.70], [49.75, 11.45]],
        "sr4-reisefuhrer-in-die-deutschen-schatten", "Reiseführer in die deutschen Schatten",
        "Nürnberg ist ein fränkisches Verwaltungs-, Industrie-, Kultur- und Verkehrszentrum der ADL.",
    ),
    "baltimore": city(
        "Baltimore", 2073, (39.2904, -76.6122), [[38.95, -77.05], [39.65, -76.15]],
        "sr4-conspiracy-theories", "Conspiracy Theories",
        "Baltimore ist ein Hafen- und Industrieraum im Washington-Baltimore-Korridor mit sumpfigen Randzonen und dichter Verkehrsinfrastruktur.",
        places=(
            p("Baltimore/Washington International", "Baltimore", "sr4-conspiracy-theories", "Baltimore Washington International", "Der Flughafen verbindet Baltimore und Washington FDC.", "Verkehr", [-76.668, 39.177]),
            p("Victory Chain Store", "Baltimore", "sr4-corporate-intrigue", "Victory Chain Store", "Der Laden ist ein im Abenteuerbestand benannter Schauplatz.", "Einkaufen"),
        ),
        extra_books=("sr4-corporate-intrigue",),
    ),
    "nairobi": city(
        "Nairobi", 2072, (-1.2921, 36.8219), [[-1.60, 36.45], [-0.95, 37.20]],
        "sr4-corporate-enclaves", "Corporate Enclaves",
        "Nairobi ist ein ostafrikanischer Konzern-, Diplomatie-, Logistik- und Geheimdienstknoten.",
        extra_books=("sr4-spy-games", "sr4-vice"),
        people=(
            n("International Police Nairobi", "sr4-vice", "International Police", "Internationale Polizeistruktur", "Nairobi", "Internationale Polizeikräfte sind im Stadtquellenstand belegt.", "group"),
        ),
    ),
    "manaus": city(
        "Manaus", 2064, (-3.1190, -60.0217), [[-3.45, -60.45], [-2.75, -59.55]],
        "sr3-shadows-of-latin-america-v1-2", "Shadows of Latin America",
        "Manaus ist ein amazonischer Fluss-, Industrie- und Logistikknoten am Rand dichter erwachter Wildnis.",
    ),
    "bruessel": city(
        "Brüssel", 2063, (50.8503, 4.3517), [[50.55, 3.95], [51.15, 4.75]],
        "sr3-shadows-of-europe", "Shadows of Europe",
        "Brüssel ist ein europäisches Politik-, Diplomatie-, Konzern- und Lobbyzentrum.",
    ),
    "perth": city(
        "Perth", 2073, (-31.9523, 115.8613), [[-32.35, 115.35], [-31.45, 116.30]],
        "sr3-target-awakened-lands", "Target: Awakened Lands",
        "Perth ist ein isolierter westaustralischer Küstenplex mit Bergbau-, Konzern- und Unterweltbezügen.",
        extra_books=("sr5-no-future", "sr5-lifestyle-2080", "sr5-megakons-2078"),
        places=(
            p("Mindarie Water Tower", "Perth", "sr5-lifestyle-2080", "Mindarie Water Tower", "Der Wasserturm ist ein markanter lokaler Veranstaltungs- und Szenestandort.", "Sichtseeing und Monumente"),
        ),
    ),
    "sarajevo": city(
        "Sarajevo", 2071, (43.8563, 18.4131), [[43.55, 18.05], [44.15, 18.80]],
        "sr4-dawn-of-the-artifacts-3-darkest-hour", "Dawn of the Artifacts: Darkest Hour",
        "Sarajevo ist ein vom Balkankonflikt geprägter urbaner Knoten und Schauplatz militärischer und artefaktbezogener Operationen.",
    ),
    "vancouver": city(
        "Vancouver", 2063, (49.2827, -123.1207), [[48.85, -123.55], [49.65, -122.55]],
        "sr3-shadows-of-north-america", "Shadows of North America",
        "Vancouver ist ein salish-shidischer Küstenplex mit Hafen, Biotechnologie, Schmuggel und starker indigener Politik.",
        places=(
            p("Kyuusei Medical", "Vancouver", "sr3-shadows-of-north-america", "Kyuusei Medical", "Kyuusei Medical ist ein belegter Biotech- und Medizinkonzernstandort.", "Medizin"),
            p("Pacific Cybernetics Incorporated", "Vancouver", "sr3-nordamerika-in-den-schatten", "Pacific Cybernetics Incorporated", "Pacific Cybernetics ist ein lokaler Technologie- und Konzernakteur.", "Konzerne"),
        ),
        extra_books=("sr3-nordamerika-in-den-schatten",),
    ),
    "san-diego": city(
        "San Diego-Tijuana", 2064, (32.7157, -117.1611), [[32.15, -117.45], [33.15, -116.65]],
        "sr3-shadows-of-latin-america-v1-2", "Shadows of Latin America",
        "Der grenzüberschreitende San-Diego-Tijuana-Sprawl verbindet Kalifornien und Aztlan mit Handel, Konzernen und organisierter Kriminalität.",
        extra_books=("sr3-lateinamerika-in-den-schatten-v1-0",),
    ),
    "lima": city(
        "Lima", 2080, (-12.0464, -77.0428), [[-12.45, -77.45], [-11.65, -76.55]],
        "sr3-shadows-of-latin-america-v1-2", "Shadows of Latin America",
        "Lima ist Perus Küsten-, Regierungs- und Konzernzentrum mit starken sozialen und politischen Gegensätzen.",
        extra_books=("sr5-lifestyle-2080",),
        places=(
            p("The Bar Lima", "Lima", "sr5-lifestyle-2080", "Die Bar (Lima, Peru)", "The Bar ist ein ausdrücklich benannter lokaler Szenetreff.", "Bars und Kneipen"),
        ),
        people=(
            n("Shining Path", "sr3-shadows-of-latin-america-v1-2", "Shining Path", "Untergrundorganisation", "Peru", "Shining Path ist als regionaler Akteur belegt.", "group"),
        ),
    ),
    "buenos-aires": city(
        "Buenos Aires", 2064, (-34.6037, -58.3816), [[-35.05, -58.90], [-34.15, -57.75]],
        "sr3-shadows-of-latin-america-v1-2", "Shadows of Latin America",
        "Buenos Aires ist Argentiniens politischer, kultureller, Hafen- und Wirtschaftskern.",
    ),
    "havanna": city(
        "Havanna", 2078, (23.1136, -82.3666), [[22.75, -82.80], [23.45, -81.95]],
        "sr5-hard-targets", "Hard Targets",
        "Havanna ist Hauptstadt der Karibischen Liga, Tourismus-, Geheimdienst- und Unterweltzentrum.",
        extra_books=("sr5-harte-ziele", "sr4-vice"),
        places=(
            p("Avery Tower", "Havanna", "sr5-hard-targets", "Avery Tower", "Der Avery Tower ist ein markanter Hochhaus- und Konzernstandort.", "Konzerne"),
            p("Barrens am Guachinango", "Havanna", "sr5-harte-ziele", "Barrens am Guachinango", "Die Barrens bilden einen prekären und gefährlichen Stadtraum.", "Sondergebiete"),
            p("Hotel Nacional", "Havanna", "sr5-hard-targets", "Hotel Nacional", "Das Hotel Nacional ist ein traditionsreicher Hotel- und Geschäftstreff.", "Hotels", [-82.396, 23.144]),
            p("Havana International Airport", "Havanna", "sr5-hard-targets", "International Airport", "Der internationale Flughafen ist der wichtigste Luftverkehrszugang.", "Verkehr", [-82.409, 22.989]),
            p("Boyer(os) National Park", "Havanna", "sr5-hard-targets", "The Boyeros National Park", "Der Park ist ein benannter Natur- und Freizeitstandort.", "Freizeit und Natur"),
            p("Tropicana Club", "Havanna", "sr5-hard-targets", "Tropicana Club", "Das Tropicana ist ein weltbekannter Unterhaltungs- und Kontaktort.", "Bars und Clubs", [-82.449, 23.097]),
        ),
        people=(
            n("Mareno Family", "sr4-vice", "The Mareno Family", "Mafiafamilie", "Havanna", "Die Mareno-Familie ist eine wichtige lokale Unterweltmacht.", "group"),
            n("Havanna Vory", "sr5-harte-ziele", "Vory", "Verbrechersyndikat", "Havanna", "Die Vory besitzt eine lokale Präsenz.", "group"),
        ),
    ),
    "dallas-fort-worth": city(
        "Dallas/Fort Worth", 2082, (32.850, -97.00), [[32.35, -97.65], [33.35, -96.35]],
        "sr1-the-neo-anarchist-s-guide-to-north-america", "The Neo-Anarchist’s Guide to North America",
        "Der DFW-Sprawl ist ein weitläufiger texanischer Wirtschafts-, Luftfahrt-, Sicherheits- und Verkehrsknoten.",
        extra_books=("sr2-nordamerika-quellenbuch", "sr5-gestohlene-seelen"),
        places=(
            p("D/FW Airport", "Dallas/Fort Worth", "sr2-nordamerika-quellenbuch", "D/FW Airport", "Der Großflughafen ist das zentrale Verkehrsdrehkreuz des Sprawls.", "Verkehr", [-97.040, 32.899]),
            p("Link Club Dallas/Fort Worth", "Dallas/Fort Worth", "sr5-gestohlene-seelen", "Link Club", "Der DFW-Ableger gehört zur internationalen Link-Club-Kette.", "Bars und Clubs"),
        ),
        people=(
            n("Dallas/Fort Worth Police Department", "sr1-the-neo-anarchist-s-guide-to-north-america", "Dallas/Fort Worth Police Department", "Polizeiorganisation", "Dallas/Fort Worth", "Das Police Department ist die lokale öffentliche Sicherheitsorganisation.", "group"),
        ),
    ),
    "prag": city(
        "Prag", 2063, (50.0755, 14.4378), [[49.75, 14.00], [50.40, 14.90]],
        "sr3-shadows-of-europe", "Shadows of Europe",
        "Prag ist ein mitteleuropäisches Kultur-, Magie-, Handel- und Unterweltzentrum.",
    ),
    "miami": city(
        "Miami", 2075, (25.7617, -80.1918), [[25.35, -80.65], [26.15, -79.75]],
        "sr4-vice", "Vice",
        "Miami ist ein Hafen-, Tourismus-, Schmuggel- und Unterweltzentrum der Karibischen Liga.",
        extra_books=("sr5-gestohlene-seelen", "sr4-10-mercs"),
        places=(
            p("Link Club Miami", "Miami", "sr5-gestohlene-seelen", "Link Club", "Der Miami-Ableger gehört zur internationalen Link-Club-Kette.", "Bars und Clubs"),
        ),
        people=(
            n("Team Zero", "sr4-10-mercs", "Team Zero", "Söldnerteam", "Miami", "Team Zero ist als militärische Gruppe mit Miami-Bezug belegt.", "group"),
        ),
    ),
    "teheran": city(
        "Teheran", 2062, (35.6892, 51.3890), [[35.30, 50.85], [36.05, 52.00]],
        "sr3-survival-of-the-fittest", "Survival of the Fittest",
        "Teheran ist ein politisch, religiös und magisch aufgeladener iranischer Großraum und Abenteuerschauplatz.",
    ),
    "melbourne": city(
        "Melbourne", 2063, (-37.8136, 144.9631), [[-38.25, 144.35], [-37.35, 145.55]],
        "sr3-target-awakened-lands", "Target: Awakened Lands",
        "Melbourne ist ein südostaustralischer Kultur-, Konzern- und Unterweltplex.",
        people=(
            n("Melbourne Yakuza", "sr3-target-awakened-lands", "The Yakuza", "Verbrechersyndikat", "Melbourne", "Die Yakuza ist im lokalen Unterweltstand belegt.", "group"),
            n("Melbourne Vory v Zakone", "sr3-target-awakened-lands", "Vory v Zakone", "Verbrechersyndikat", "Melbourne", "Die Vory unterhält eine lokale Präsenz.", "group"),
        ),
    ),
    "salt-lake-city": city(
        "Salt Lake City", 2051, (40.7608, -111.8910), [[40.35, -112.35], [41.15, -111.35]],
        "sr1-native-american-nations-volume-one", "Native American Nations, Volume One",
        "Salt Lake City ist ein urbaner Knoten der Ute Nation mit starkem religiösem und regionalpolitischem Erbe.",
    ),
    "manila": city(
        "Manila", 2063, (14.5995, 120.9842), [[14.20, 120.55], [15.05, 121.45]],
        "sr3-shadows-of-asia", "Shadows of Asia",
        "Manila ist ein dichter philippinischer Hafen-, Medien-, Industrie- und Machtplex.",
        extra_books=("sr2-cyberpirates", "sr2-cyberpiraten"),
        people=(
            n("Carlos Consuni", "sr3-shadows-of-asia", "Carlos Consuni", "Politischer oder wirtschaftlicher Akteur", "Manila", "Carlos Consuni ist im philippinischen Quellenstand belegt."),
            n("Bahay ng Isda", "sr2-cyberpiraten", "Bahay ng Isda", "Lokale Gruppe", "Manila", "Bahay ng Isda ist eine im Cyberpiraten-Quellenstand belegte Gruppe.", "group"),
        ),
    ),
    "johannesburg": city(
        "Johannesburg", 2075, (-26.2041, 28.0473), [[-26.65, 27.45], [-25.65, 28.75]],
        "sr5-better-than-bad", "Better Than Bad",
        "Johannesburg ist ein südafrikanischer Megaplex aus reichen Konzernräumen, Townships und stark gemischten Bevölkerungszentren.",
        places=(
            p("Ekurhuleni / West Rand", "Johannesburg", "sr5-better-than-bad", "Ekurhuleni, West Rand", "Ekurhuleni und West Rand bilden wichtige Teilräume des Megaplexes.", "Stadtteile"),
        ),
    ),
    "phoenix": city(
        "Phoenix", 2075, (33.4484, -112.0740), [[32.95, -112.70], [34.05, -111.35]],
        "sr1-the-neo-anarchist-s-guide-to-north-america", "The Neo-Anarchist’s Guide to North America",
        "Phoenix ist ein weitläufiger Wüstensprawl mit Konzern-, Syndikats- und Schmuggelbezügen.",
    ),
    "brisbane": city(
        "Brisbane", 2063, (-27.4698, 153.0251), [[-27.90, 152.55], [-27.05, 153.50]],
        "sr3-target-awakened-lands", "Target: Awakened Lands",
        "Brisbane ist ein ost­australischer Küsten-, Konzern- und Verkehrsknoten.",
        people=(
            n("Tanamyre Resources Brisbane", "sr3-target-awakened-lands", "Tanamyre Resources", "Rohstoffkonzern", "Brisbane", "Tanamyre Resources ist als regionaler Konzernakteur belegt.", "group"),
        ),
    ),
    "bangkok": city(
        "Bangkok", 2073, (13.7563, 100.5018), [[13.35, 100.05], [14.15, 101.00]],
        "sr4-state-of-the-art-2073", "State of the Art 2073",
        "Bangkok ist ein dichtes südostasiatisches Handels-, Vergnügungs-, Militär- und Unterweltzentrum.",
        extra_books=("sr4-99-bottles",),
        people=(
            n("Bangkok Military Police", "sr4-99-bottles", "Bangkok Military Police", "Militärpolizei", "Bangkok", "Die Militärpolizei ist ein zentraler Sicherheitsakteur.", "group"),
            n("Yellow Lotus Triad Bangkok", "sr4-99-bottles", "Yellow Lotus Triad", "Triade", "Bangkok", "Die Yellow Lotus besitzt eine lokale Präsenz.", "group"),
            n("Kuroiban-gumi", "sr4-99-bottles", "Kuroiban-gumi", "Yakuza-gumi", "Bangkok", "Das Kuroiban-gumi ist eine lokale Unterweltgruppe.", "group"),
        ),
    ),
}


def update_city_registry() -> None:
    path = ROOT / "data/cities.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    by_id = {entry["id"]: entry for entry in registry["cities"]}
    order = [entry["id"] for entry in registry["cities"]]
    for city_id, config in CONFIGS.items():
        by_id[city_id] = {
            "id": city_id, "name": config["name"],
            "manifest": f"data/{city_id}/manifest.json", "year": config["year"],
        }
        if city_id not in order:
            order.append(city_id)
    registry["cities"] = [by_id[city_id] for city_id in order]
    write_json(path, registry)


def main() -> None:
    referenced = set()
    for config in CONFIGS.values():
        referenced.update(config["books"])
        referenced.update(item[0] for item in config["profile"].values())
        referenced.update(item[4] for item in config["districts"])
        referenced.update(item["book"] for item in config["places"])
        referenced.update(item["book"] for item in config["people"])
    missing = referenced - WORKS.keys()
    if missing:
        raise SystemExit(f"Unbekannte Werk-IDs: {sorted(missing)}")
    for city_id, config in CONFIGS.items():
        build_city(city_id, config)
        print(f"OK {city_id}")
    update_city_registry()


if __name__ == "__main__":
    main()
