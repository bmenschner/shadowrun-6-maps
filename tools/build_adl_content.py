#!/usr/bin/env python3
"""Build the ADL overview package from the supplied German source archive.

The ADL map is an overview, not a substitute for the detailed Berlin,
Hamburg, or Rhein-Ruhr packages.  Coordinates therefore identify documented
cities and broad lore regions.  No house-level positions are inferred.
"""

from __future__ import annotations

import json
from pathlib import Path

from build_us_city_content import CityCatalogue, city_edition, write_json


ROOT = Path(__file__).resolve().parents[1]
CITY_ID = "adl-2082"

BOOKS = [
    {"id": "sr1-deutschland-in-den-schatten", "registryWorkId": "sr1-deutschland-in-den-schatten", "title": "Deutschland in den Schatten", "edition": "SR1"},
    {"id": "sr2-deutschland-in-den-schatten", "registryWorkId": "sr2-deutschland-in-den-schatten", "title": "Deutschland in den Schatten", "edition": "SR2"},
    {"id": "sr3-deutschland-in-den-schatten-ii", "registryWorkId": "sr3-deutschland-in-den-schatten-ii", "title": "Deutschland in den Schatten II", "edition": "SR3"},
    {"id": "sr3-brennpunkt-adl", "registryWorkId": "sr3-brennpunkt-adl", "title": "Brennpunkt ADL", "edition": "SR3"},
    {"id": "sr4-reisefuhrer-in-die-deutschen-schatten", "registryWorkId": "sr4-reisefuhrer-in-die-deutschen-schatten", "title": "Reiseführer in die deutschen Schatten", "edition": "SR4"},
    {"id": "sr5-datapuls-adl", "registryWorkId": "sr5-datapuls-adl", "title": "Datapuls ADL", "edition": "SR5"},
    {"id": "sr5-datapuls-frankfurt", "registryWorkId": "sr5-datapuls-frankfurt", "title": "Datapuls Frankfurt", "edition": "SR5"},
    {"id": "sr5-datapuls-karlsruhe", "registryWorkId": "sr5-datapuls-karlsruhe", "title": "Datapuls Karlsruhe", "edition": "SR5"},
    {"id": "sr5-datapuls-sox", "registryWorkId": "sr5-datapuls-sox", "title": "Datapuls SOX", "edition": "SR5"},
    {"id": "sr5-datapuls-trollrepublik-schwarzwald", "registryWorkId": "sr5-datapuls-trollrepublik-schwarzwald", "title": "Datapuls Trollrepublik & Schwarzwald", "edition": "SR5"},
    {"id": "sr6-datapuls-alpen", "registryWorkId": "sr6-datapuls-alpen", "title": "Datapuls: Alpen", "edition": "SR6"},
    {"id": "sr6-datapuls-harz", "registryWorkId": "sr6-datapuls-harz", "title": "Datapuls: Harz", "edition": "SR6"},
    {"id": "sr6-datapuls-marienbad", "registryWorkId": "sr6-datapuls-marienbad", "title": "Datapuls: Marienbad", "edition": "SR6"},
    {"id": "sr6-datapuls-munchen", "registryWorkId": "sr6-datapuls-munchen", "title": "Datapuls: München", "edition": "SR6"},
    {"id": "sr6-datapuls-pomorya", "registryWorkId": "sr6-datapuls-pomorya", "title": "Datapuls: Pomorya", "edition": "SR6"},
    {"id": "sr6-datapuls-westphalen", "registryWorkId": "sr6-datapuls-westphalen", "title": "Datapuls: Westphalen", "edition": "SR6"},
]


# Latitude/longitude anchors.  Regional entries deliberately use a broad
# geographic centre and are labelled as such in the generated place data.
ANCHORS = {
    "ADL": (51.1657, 10.4515),
    "Berlin": (52.5200, 13.4050),
    "Brandenburg": (52.4125, 12.5316),
    "Freistaat Bayern": (48.9468, 11.4039),
    "Freistaat Sachsen": (51.1045, 13.2017),
    "Freistaat Thüringen": (50.9848, 11.0299),
    "Freistaat Westphalen": (51.9624, 7.6257),
    "Groß-Frankfurt": (50.1109, 8.6821),
    "Großherzogtum Westrhein-Luxemburg": (49.7560, 6.6410),
    "Hamburg": (53.5511, 9.9937),
    "Hannover": (52.3759, 9.7320),
    "Harz": (51.7500, 10.6333),
    "Hessen-Nassau": (50.4074, 8.0000),
    "Karlsruhe": (49.0069, 8.4037),
    "Leipzig-Halle": (51.3880, 12.2000),
    "Marienbad": (49.9646, 12.7012),
    "München": (48.1374, 11.5755),
    "Norddeutscher Bund": (53.2000, 10.1500),
    "Nordrhein-Ruhr": (51.4556, 7.0116),
    "Pomorya": (54.0500, 13.4000),
    "SOX": (49.1200, 6.8000),
    "Trollrepublik Schwarzwald": (48.1500, 8.1500),
    "Württemberg": (48.7758, 9.1829),
    "Alpen": (47.5000, 11.0000),
}


REGIONS = [
    ("Berlin", "SR5", "sr5-datapuls-adl", "Datapuls ADL", "Kapitel Berlin", "Das geteilte Berlin verbindet anarchistische Kieze, Konzernbezirke und extraterritoriale Enklaven; die Stadt besitzt eine eigene Detailkarte.", "berlin-2080"),
    ("Brandenburg", "SR5", "sr5-datapuls-adl", "Datapuls ADL", "Kapitel Brandenburg", "Brandenburg umschließt Berlin als dünner besiedeltes Flächenland und ist durch die Verwerfungen zwischen Hauptstadtregion, Wildnis und lokalen Machtzentren geprägt.", None),
    ("Freistaat Bayern", "SR5", "sr5-datapuls-adl", "Datapuls ADL", "Kapitel Freistaat Bayern", "Der Freistaat Bayern ist ein eigenständiges, wirtschaftsstarkes Allianzbundesland; München bildet sein dominierendes urbanes Zentrum.", None),
    ("Freistaat Sachsen", "SR5", "sr5-datapuls-adl", "Datapuls ADL", "Kapitel Freistaat Sachsen", "Sachsen ist ein östliches Allianzbundesland mit Leipzig-Halle als wichtigstem Ballungsraum und eigenen politischen sowie industriellen Konfliktlinien.", None),
    ("Freistaat Thüringen", "SR5", "sr5-datapuls-adl", "Datapuls ADL", "Kapitel Freistaat Thüringen", "Thüringen ist ein zentral gelegenes Allianzbundesland zwischen urbanen Korridoren, bewaldeten Rückzugsräumen und erwachten Besonderheiten.", None),
    ("Freistaat Westphalen", "SR6", "sr6-datapuls-westphalen", "Datapuls: Westphalen", "S. 2–31", "Westphalen ist ein stark von der Deutsch-Katholischen Kirche geprägter Freistaat, dessen Ordnung, Theurgie und Sicherheitsapparat das öffentliche Leben bestimmen.", None),
    ("Groß-Frankfurt", "SR5", "sr5-datapuls-frankfurt", "Datapuls Frankfurt", "gesamter Band", "Groß-Frankfurt ist ein finanz- und konzerngeprägter Plex, in dem Banken, Börse, Flughafen und Schattenwirtschaft eng miteinander verflochten sind.", None),
    ("Großherzogtum Westrhein-Luxemburg", "SR5", "sr5-datapuls-adl", "Datapuls ADL", "Kapitel Westrhein-Luxemburg", "Das Großherzogtum Westrhein-Luxemburg bildet einen westlichen Grenzraum der ADL mit eigener monarchischer Ordnung und starker europäischer Verflechtung.", None),
    ("Hamburg", "SR5", "sr5-datapuls-adl", "Datapuls ADL", "Kapitel Hamburg", "Hamburg ist ein überfluteter Hafenplex, Medienzentrum und Tor zur Nordsee; die Stadt besitzt eine eigene Detailkarte.", "hamburg-2080"),
    ("Hessen-Nassau", "SR5", "sr5-datapuls-adl", "Datapuls ADL", "Kapitel Hessen-Nassau", "Hessen-Nassau verbindet ländliche Räume, alte Zentren und den Einfluss des benachbarten Groß-Frankfurt.", None),
    ("Norddeutscher Bund", "SR5", "sr5-datapuls-adl", "Datapuls ADL", "Kapitel Norddeutscher Bund", "Der Norddeutsche Bund umfasst große Teile des Nordens und wird von Hafenwirtschaft, Landwirtschaft, Küstengefahren und dem politischen Zentrum Hannover geprägt.", None),
    ("Nordrhein-Ruhr", "SR5", "sr5-datapuls-adl", "Datapuls ADL", "Kapitel Nordrhein-Ruhr", "Nordrhein-Ruhr ist der dicht bebaute Industrie- und Konzernraum der ADL, überragt von Saeder-Krupp in Neu-Essen; der Plex besitzt eine eigene Detailkarte.", "rhein-ruhr-2082"),
    ("Pomorya", "SR6", "sr6-datapuls-pomorya", "Datapuls: Pomorya", "S. 2–29", "Pomorya ist ein elfisch geprägtes Herzogtum an der Ostseeküste mit ausgeprägter Naturorientierung, höfischer Politik und kontrollierten Zugängen.", None),
    ("SOX", "SR5", "sr5-datapuls-sox", "Datapuls SOX", "gesamter Band", "Die SOX ist eine toxisch und radioaktiv verseuchte Sonderzone im Westen, deren abgeschirmte Anlagen, Ruinen und Gefahren nur eingeschränkt zugänglich sind.", None),
    ("Trollrepublik Schwarzwald", "SR5", "sr5-datapuls-trollrepublik-schwarzwald", "Datapuls Trollrepublik & Schwarzwald", "gesamter Band", "Die Trollrepublik Schwarzwald ist ein erwachter, überwiegend von Trollen und Orks geprägter Sonderraum mit eigener politischer Ordnung.", None),
    ("Württemberg", "SR5", "sr5-datapuls-adl", "Datapuls ADL", "Kapitel Württemberg", "Württemberg ist ein südwestliches Allianzbundesland mit Stuttgart als urbanem und industriellem Schwerpunkt.", None),
]

CITY_AND_SPECIAL = [
    ("Hannover", "SR5", "sr5-datapuls-adl", "Datapuls ADL", "Kapitel Politik und Hannover", "Hannover ist Hauptstadt der ADL und Sitz zentraler Allianzbehörden.", "Städte"),
    ("Harz", "SR6", "sr6-datapuls-harz", "Datapuls: Harz", "gesamter Band", "Der Harz ist eine erwachte Gebirgsregion mit Hexentraditionen, magischen Orten und zahlreichen lokalen Gefahren.", "Sondergebiete"),
    ("Karlsruhe", "SR5", "sr5-datapuls-karlsruhe", "Datapuls Karlsruhe", "gesamter Band", "Karlsruhe ist ein wichtiges Verwaltungs-, Justiz- und Technologierzentrum im Südwesten der ADL.", "Städte"),
    ("Leipzig-Halle", "SR5", "sr5-datapuls-adl", "Datapuls ADL", "Kapitel Sachsen", "Leipzig-Halle bildet einen zusammengewachsenen mitteldeutschen Ballungsraum mit Verkehr, Industrie und eigener Schattenökonomie.", "Städte"),
    ("Marienbad", "SR6", "sr6-datapuls-marienbad", "Datapuls: Marienbad", "gesamter Band", "Marienbad ist eine traditionsreiche Kurstadt im böhmischen Grenzraum und ein Knotenpunkt für Politik, Magie und diskrete Geschäfte.", "Städte"),
    ("München", "SR6", "sr6-datapuls-munchen", "Datapuls: München", "S. 2–29", "München ist Bayerns überfüllte Medien- und Konzernmetropole, geprägt von Geschichte, Erwachen und einem eigenwilligen lokalen Schattenmilieu.", "Städte"),
    ("Alpen", "SR6", "sr6-datapuls-alpen", "Datapuls: Alpen", "gesamter Band", "Der Alpenraum verbindet schwer zugängliche Hochgebirge, arkane Phänomene, Tourismus, Schmuggelwege und grenzüberschreitende Interessen.", "Sondergebiete"),
]


def add_region(
    catalogue: CityCatalogue,
    row: tuple[str, str, str, str, str, str, str | None],
) -> None:
    name, edition, book_id, title, citation, summary, linked_city = row
    lat, lon = ANCHORS[name]
    catalogue.add_place(
        name,
        name,
        edition,
        book_id,
        title,
        citation,
        category="Allianzländer und Regionen",
        summary=summary,
        coordinates=[lon, lat],
        exact=False,
    )
    props = catalogue.places[next(key for key, item in catalogue.places.items() if item["properties"]["name"] == name)]["properties"]
    props["accuracy"] = "Regionaler Bezugspunkt; keine flächengenaue Grenze"
    props["placement_note"] = f"Geografisches Zentrum des Lore-Raums {name}"
    if linked_city:
        props["linked_city_id"] = linked_city


def main() -> None:
    catalogue = CityCatalogue(CITY_ID, "ADL", ANCHORS["ADL"], ANCHORS, BOOKS)
    catalogue.set_city_profile(
        "Die Allianz Deutscher Länder ist ein politisch und kulturell stark gegliederter Staatenbund im Herzen Europas.",
        "Die ADL-Karte dient als regionaler Einstieg in die deutschen Schatten. Sie zeigt Allianzländer, große Plexe und Sonderräume; flächengenaue Grenzen werden nur übernommen, wenn das Kartenmaterial sie belastbar stützt.",
        {
            "SR1": city_edition("SR1", "sr1-deutschland-in-den-schatten", "Deutschland in den Schatten", "gesamter Band", "Die erste deutsche Regionaldarstellung etabliert das zersplitterte Deutschland der Sechsten Welt.", "Deutschland in den Schatten führt die politische Neuordnung, zentrale Plexe und Konflikträume des deutschsprachigen Settings ein."),
            "SR2": city_edition("SR2", "sr2-deutschland-in-den-schatten", "Deutschland in den Schatten", "gesamter Band", "Der SR2-Stand führt die deutschen Regionen und ihre Schatten weiter.", "Die zweite Edition übernimmt und erweitert den regionalen Quellenstand für das Deutschland der Sechsten Welt."),
            "SR3": city_edition("SR3", "sr3-brennpunkt-adl", "Brennpunkt ADL", "gesamter Band", "Brennpunkt ADL verdichtet Politik, Wirtschaft und Konflikte der Allianz.", "Brennpunkt ADL und Deutschland in den Schatten II bilden den zentralen deutschen Regionalstand der dritten Edition."),
            "SR4": city_edition("SR4", "sr4-reisefuhrer-in-die-deutschen-schatten", "Reiseführer in die deutschen Schatten", "gesamter Band", "Der Reiseführer erschließt zahlreiche Städte und Regionen der ADL.", "Der Reiseführer in die deutschen Schatten aktualisiert den regionalen Stand und ergänzt lokale Schauplätze."),
            "SR5": city_edition("SR5", "sr5-datapuls-adl", "Datapuls ADL", "gesamter Band", "Datapuls ADL liefert den Überblick für 2078.", "Datapuls ADL fasst Allianzländer, große Städte, Politik, Konzerne und Gefahren des Jahres 2078 zusammen."),
            "SR6": city_edition("SR6", "sr6-datapuls-munchen", "Datapuls: München", "Reihe Datapuls", "Die SR6-Datapulse vertiefen einzelne Städte und Regionen.", "Die sechste Edition ergänzt den Überblick durch regionale Datapulse zu München, Pomorya, Westphalen, Harz, Marienbad und dem Alpenraum."),
        },
    )

    for row in REGIONS:
        add_region(catalogue, row)
    for name, edition, book_id, title, citation, summary, category in CITY_AND_SPECIAL:
        lat, lon = ANCHORS[name]
        catalogue.add_place(
            name,
            name,
            edition,
            book_id,
            title,
            citation,
            category=category,
            summary=summary,
            coordinates=[lon, lat],
            exact=name in {"Hannover", "Karlsruhe", "Leipzig-Halle", "Marienbad", "München"},
        )

    # Editions that establish the same recurring regions are attached to the
    # existing entity instead of producing duplicate markers.
    for edition, book_id, title in [
        ("SR1", "sr1-deutschland-in-den-schatten", "Deutschland in den Schatten"),
        ("SR2", "sr2-deutschland-in-den-schatten", "Deutschland in den Schatten"),
        ("SR3", "sr3-deutschland-in-den-schatten-ii", "Deutschland in den Schatten II"),
        ("SR4", "sr4-reisefuhrer-in-die-deutschen-schatten", "Reiseführer in die deutschen Schatten"),
    ]:
        for name in ("Berlin", "Hamburg", "Hannover", "Nordrhein-Ruhr", "München"):
            catalogue.add_place(
                name,
                name,
                edition,
                book_id,
                title,
                f"Kapitel {name}",
                category="Städte" if name in {"Hannover", "München"} else "Allianzländer und Regionen",
            )

    for name, role, affiliation in [
        ("Anikka Beloit", "Bundeskanzlerin", "Bundesregierung der ADL / BVP"),
        ("Thomas Rosenstein", "Chef des Bundeskanzleramtes", "Bundesregierung der ADL / CVP"),
        ("Aron Nebbe", "Außenminister und Vizekanzler", "Bundesregierung der ADL"),
    ]:
        catalogue.add_person(
            name,
            "SR5",
            "sr5-datapuls-adl",
            "Datapuls ADL",
            "Kapitel Bundesregierung",
            role=role,
            affiliation=affiliation,
            summary=f"{name} wird im Regierungsüberblick des Datapuls ADL als {role} geführt.",
            location_name="Hannover",
        )

    catalogue.finish(
        2082,
        "Überblick über Allianzländer, Metropolregionen und Sondergebiete der ADL. Marker kennzeichnen regionale Bezugspunkte; Detailkarten bleiben eigenständige Kartenpakete.",
        [[47.0, 5.5], [55.4, 15.5]],
        6,
    )

    city_dir = ROOT / "data" / CITY_ID
    places = json.loads((city_dir / "places.geojson").read_text(encoding="utf-8"))
    labels = []
    for feature in places["features"]:
        props = feature["properties"]
        lon, lat = feature["geometry"]["coordinates"]
        labels.append(
            {
                "name": props["name"],
                "lat": lat,
                "lon": lon,
                "type": "district" if props["category"] == "Allianzländer und Regionen" else "neighborhood",
                "entity_id": props["id"],
            }
        )
    write_json(city_dir / "labels.json", labels)


if __name__ == "__main__":
    main()
