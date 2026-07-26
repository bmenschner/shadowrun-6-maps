#!/usr/bin/env python3
"""Build the first two US city content packages: Denver and Manhattan.

The source lists are editorial catalogues derived from the supplied books and
maps.  Modern coordinates are used where a landmark survives.  Fictional or
changed places are deliberately distributed around a documented district
anchor and labelled as approximate.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = Path("/mnt/c/Users/Privat/Documents/Shadowrun/txtexports")


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii").casefold()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def name_key(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii").casefold()
    value = re.sub(r"^(the|das|der|die)\s+", "", value)
    key = re.sub(r"[^a-z0-9]+", "", value)
    return {
        "capnkluge": "capnkludge",
        "elizabethbettykalheim": "elizabethkalheim",
        "marablain": "marablaine",
        "samuelpiphalbert": "samuelhalbert",
        "tabithatabbymorgan": "tabby",
        "happycanyonshoppingcenter": "happycanyonmall",
        "rockymountainarsenal": "rockymountainarsenalpark",
        "rockymountainarsenalnationalwildliferefuge": "rockymountainarsenalpark",
        "auroravillagesportsmedicalcenter": "auroravillagemedicalcenter",
        "raquelsandysands": "rachelsands",
        "mikhailpetrov": "mikaelpetrov",
        "kazuyathedragonhotomi": "kazuyahotomi",
        "prometheustower": "prometheusspire",
        "grandcentralstation": "grandcentralstationundarkologie",
        "grandcentral": "grandcentralstationundarkologie",
        "minpakring": "minparkring",
    }.get(key, key)


def source(book_id: str, title: str, edition: str, citation: str, purpose: str = "description") -> dict:
    return {
        "bookId": book_id,
        "title": title,
        "edition": edition,
        "citation": citation,
        "purpose": purpose,
    }


def infer_place_category(name: str) -> str:
    low = name.casefold()
    rules = [
        (("airport", "flughafen", "station", "bahnhof", "union station"), "Verkehr"),
        (("hotel", "inn", "resort", "cheap sleeps", "quik-e-nap", "apartments"), "Hotels"),
        (("hospital", "clinic", "medical", "recovery", "gerontology"), "Medizin"),
        (("bar", "club", "pub", "lunar", "denim", "grind", "vibe", "nowhere", "church"), "Bars und Clubs"),
        (("restaurant", "grill", "café", "cafe", "food", "feed trough", "marcel", "sylvia"), "Restaurants"),
        (("mall", "market", "pawn", "emporium", "imports", "square"), "Einkaufen"),
        (("university", "college", "school", "museum", "gallery", "foundation", "library"), "Bildung und Kultur"),
        (("park", "zoo", "garden", "reservoir", "refuge", "amusement"), "Freizeit und Natur"),
        (("police", "nypd", "prison", "correctional", "judicial", "military", "air force", "fort "), "Sicherheit und Justiz"),
        (("office", "headquarters", "factory", "complex", "spire", "arcology", "arkologie", "plaza", "bank", "holdings"), "Konzerne"),
        (("temple", "jinja", "holy", "dragon reborn", "house of wonders"), "Magie und Religion"),
        (("district", "warrens", "harlem", "city", "heights", "village", "side", "parkside", "terminal", "the hub"), "Bezirke"),
        (("matrix", "null", "data haven", "virtual", "metaplane", "metaebene"), "Matrix und Metaplanes"),
    ]
    for needles, category in rules:
        if any(needle in low for needle in needles):
            return category
    return "Sonstige Spots"


def infer_people_category(name: str, role: str, entity_type: str) -> str:
    low = f"{name} {role}".casefold()
    if entity_type == "group":
        if any(word in low for word in ("gang", "ancients", "cutters", "bloods", "zombies", "fronts", "domes", "riders", "sons")):
            return "Gangs"
        return "Organisationen und Gruppen"
    if any(word in low for word in ("doctor", "dr.", "professor", "medical")):
        return "Wissenschaft und Medizin"
    if any(word in low for word in ("council", "mayor", "representative", "senator", "administration")):
        return "Politik und Verwaltung"
    if any(word in low for word in ("dragon", "spirit", "mage", "shaman", "awakened", "adept")):
        return "Magie und Erwachte"
    if any(word in low for word in ("ceo", "executive", "corporate", "company")):
        return "Konzerne"
    if any(word in low for word in ("decker", "hacker", "technomancer", "matrix", "data haven")):
        return "Matrix und Technik"
    if any(word in low for word in ("police", "security", "agent", "soldier")):
        return "Sicherheit und Justiz"
    return "Schatten und Szene"


def jitter(anchor: tuple[float, float], key: str, scale: float = 0.018) -> list[float]:
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    dx = (int.from_bytes(digest[:2], "big") / 65535 - 0.5) * scale
    dy = (int.from_bytes(digest[2:4], "big") / 65535 - 0.5) * scale
    return [round(anchor[1] + dx, 6), round(anchor[0] + dy, 6)]


class CityCatalogue:
    def __init__(
        self,
        city_id: str,
        name: str,
        default_anchor: tuple[float, float],
        anchors: dict[str, tuple[float, float]],
        books: list[dict],
    ) -> None:
        self.city_id = city_id
        self.name = name
        self.default_anchor = default_anchor
        self.anchors = anchors
        self.books = books
        self.places: OrderedDict[str, dict] = OrderedDict()
        self.people: OrderedDict[str, dict] = OrderedDict()
        self.map_marker_ids: list[int] = []

    def add_place(
        self,
        name: str,
        scope: str,
        edition: str,
        book_id: str,
        title: str,
        citation: str,
        *,
        category: str | None = None,
        summary: str | None = None,
        coordinates: list[float] | None = None,
        map_number: int | None = None,
        exact: bool = False,
    ) -> None:
        key = name_key(name)
        src = source(book_id, title, edition, citation)
        supplied_summary = summary
        if key in self.places:
            props = self.places[key]["properties"]
            if name != props["name"] and name not in props["aliases"]:
                props["aliases"].append(name)
            if edition not in props["editions"]:
                props["editions"].append(edition)
            if not any(existing["bookId"] == book_id and existing["citation"] == citation for existing in props["sources"]):
                props["sources"].append(src)
            edition_data = props["edition_descriptions"].get(edition)
            if edition_data is None:
                edition_data = {
                    "kind": "Quellennachweis",
                    "preview": f"{name} ist für {edition} in {title} belegt.",
                    "full": (
                        f"{name} ist für {edition} in {title} belegt. "
                        "Der Eintrag wird editionsübergreifend mit demselben Ort zusammengeführt."
                    ),
                    "hasMore": True,
                    "hasExcerpt": False,
                    "sources": [],
                }
                props["edition_descriptions"][edition] = edition_data
            if not any(
                existing["bookId"] == book_id and existing["citation"] == citation
                for existing in edition_data["sources"]
            ):
                edition_data["sources"].append(src)
            if supplied_summary:
                edition_data.update(
                    {
                        "kind": "Ortsprofil",
                        "preview": supplied_summary,
                        "full": (
                            f"{supplied_summary} Die Position folgt einem erhaltenen heutigen Bezugspunkt."
                            if exact
                            else (
                                f"{supplied_summary} Die Position ist auf den belegten Stadt- oder "
                                "Teilraum angenähert; eine hausgenaue Lage ist aus dem Datenmaterial "
                                "nicht sicher ableitbar."
                            )
                        ),
                        "hasMore": True,
                        "hasExcerpt": True,
                    }
                )
            if map_number is not None:
                props[f"map_number_{edition.casefold()}"] = map_number
                if props["id"] not in self.map_marker_ids:
                    self.map_marker_ids.append(props["id"])
            return

        place_id = len(self.places) + 1
        anchor = self.anchors.get(scope, self.default_anchor)
        coords = coordinates or jitter(anchor, f"{self.city_id}:{scope}:{name}")
        category = category or infer_place_category(name)
        summary = summary or (
            f"{name} ist ein in {title} belegter Schauplatz im Bereich {scope}."
        )
        full = (
            f"{summary} Die Position folgt einem erhaltenen heutigen Bezugspunkt."
            if exact
            else f"{summary} Die Position ist auf den belegten Stadt- oder Teilraum angenähert; eine hausgenaue Lage ist aus dem Datenmaterial nicht sicher ableitbar."
        )
        props = {
            "id": place_id,
            "global_id": f"{self.city_id}:place:{place_id}-{slug(name)}",
            "name": name,
            "aliases": [],
            "category": category,
            "detail_map": scope,
            "source_pages": citation,
            "map_source": title,
            "placement_note": "Erhaltener geographischer Bezugspunkt" if exact else f"Nach Quellenbezug im Teilraum {scope} angenähert",
            "accuracy": "Geographischer Bezugspunkt" if exact else "Teilraumzuordnung; Feinposition vorläufig",
            "source_map": f"{self.city_id}-content",
            "source_panel": scope,
            "description_preview": summary,
            "description_full": full,
            "description_source": citation,
            "description_kind": "Ortsprofil",
            "description_has_more": True,
            "detail_plans": [],
            "alternate_locations": [],
            "sources": [src],
            "map_sources": [],
            "editions": [edition],
            "edition_descriptions": {
                edition: {
                    "kind": "Ortsprofil",
                    "preview": summary,
                    "full": full,
                    "hasMore": True,
                    "hasExcerpt": True,
                    "sources": [src],
                }
            },
        }
        if map_number is not None:
            props[f"map_number_{edition.casefold()}"] = map_number
            self.map_marker_ids.append(place_id)
        self.places[key] = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": coords},
            "properties": props,
        }

    def enrich_district(self, name: str, edition: str, summary: str) -> None:
        place = self.places.get(name_key(name))
        if not place:
            raise ValueError(f"{self.city_id}: Bezirksdossier fehlt: {name}")
        props = place["properties"]
        full = (
            f"{summary} Die Zusammenfassung folgt dem Bezirkskapitel der "
            "angegebenen Edition; heutige Grenzen dienen nur der geografischen "
            "Einordnung."
        )
        props["category"] = "Bezirke"
        props["description_preview"] = summary
        props["description_full"] = full
        props["description_kind"] = "Bezirksprofil"
        props["description_has_more"] = True
        props["placement_note"] = f"Lore-Bezirkszentrum {name}"
        props["accuracy"] = "Lore-Bezirk; Grenzebene separat geprüft"
        edition_data = props.get("edition_descriptions", {}).get(edition)
        if edition_data:
            edition_data.update(
                {
                    "kind": "Bezirksprofil",
                    "preview": summary,
                    "full": full,
                    "hasMore": True,
                    "hasExcerpt": True,
                }
            )

    def add_district_version(
        self,
        name: str,
        edition: str,
        book_id: str,
        title: str,
        citation: str,
        summary: str,
    ) -> None:
        self.add_place(
            name,
            name,
            edition,
            book_id,
            title,
            citation,
            category="Bezirke",
            summary=summary,
            coordinates=[
                self.anchors.get(name, self.default_anchor)[1],
                self.anchors.get(name, self.default_anchor)[0],
            ],
        )
        props = self.places[name_key(name)]["properties"]
        edition_data = props["edition_descriptions"][edition]
        edition_data["kind"] = "Bezirksprofil"
        edition_data["full"] = (
            f"{summary} Die Beschreibung folgt dem Lore-Stand der angegebenen "
            "Edition; die separat schaltbare Grenzebene bildet den jüngsten "
            "georeferenzierten Arbeitsstand ab."
        )

    def add_person(
        self,
        name: str,
        edition: str,
        book_id: str,
        title: str,
        citation: str,
        *,
        role: str = "Lokaler Akteur",
        affiliation: str = "",
        summary: str | None = None,
        entity_type: str = "person",
        location_name: str | None = None,
    ) -> None:
        key = name_key(name)
        src = source(book_id, title, edition, citation)
        supplied_summary = summary
        if key in self.people:
            person = self.people[key]
            if name != person["name"] and name not in person["aliases"]:
                person["aliases"].append(name)
                if len(name) > len(person["name"]) + 3:
                    person["aliases"].append(person["name"])
                    person["aliases"] = list(dict.fromkeys(person["aliases"]))
                    person["name"] = name
            if edition not in person["editions"]:
                person["editions"].append(edition)
            if not any(existing["bookId"] == book_id and existing["citation"] == citation for existing in person["sources"]):
                person["sources"].append(src)
            edition_data = person["edition_descriptions"].get(edition)
            if edition_data is None:
                edition_data = {
                    "kind": "Quellennachweis",
                    "preview": f"{name} ist für {edition} in {title} belegt.",
                    "full": (
                        f"{name} ist für {edition} in {title} belegt. Das gemeinsame Dossier "
                        "vermeidet einen zweiten Eintrag derselben Person oder Gruppe."
                    ),
                    "hasMore": True,
                    "hasExcerpt": False,
                    "sources": [],
                }
                person["edition_descriptions"][edition] = edition_data
            if not any(
                existing["bookId"] == book_id and existing["citation"] == citation
                for existing in edition_data["sources"]
            ):
                edition_data["sources"].append(src)
            if supplied_summary:
                edition_data.update(
                    {
                        "kind": "Gruppendossier" if entity_type == "group" else "Personendossier",
                        "preview": supplied_summary,
                        "full": (
                            supplied_summary
                            + " Das Dossier ist eine redaktionelle Zusammenfassung des belegten Quellenstands."
                        ),
                        "hasMore": True,
                        "hasExcerpt": True,
                    }
                )
                if person["summary"].startswith(f"{name} wird in "):
                    person["summary"] = supplied_summary
                    person["description"] = (
                        supplied_summary
                        + " Das Dossier ist eine redaktionelle Zusammenfassung des belegten Quellenstands."
                    )
            if location_name and name_key(location_name) in self.places:
                place = self.places[name_key(location_name)]["properties"]
                if not any(
                    location.get("global_id") == place["global_id"]
                    for location in person.get("locations", [])
                ):
                    person.setdefault("locations", []).append(
                        {
                            "id": place["id"],
                            "relation": f"Bezug zu {location_name}",
                            "global_id": place["global_id"],
                        }
                    )
            return

        summary = summary or f"{name} wird in {title} als für {self.name} relevante Person oder Gruppe geführt."
        locations = []
        if location_name and name_key(location_name) in self.places:
            place = self.places[name_key(location_name)]["properties"]
            locations.append(
                {
                    "id": place["id"],
                    "relation": f"Bezug zu {location_name}",
                    "global_id": place["global_id"],
                }
            )
        person_id = slug(name)
        self.people[key] = {
            "id": person_id,
            "global_id": f"{self.city_id}:person:{person_id}",
            "name": name,
            "aliases": [],
            "category": infer_people_category(name, role, entity_type),
            "entity_type": entity_type,
            "role": role,
            "affiliation": affiliation or self.name,
            "status": "Quellenstand beachten",
            "summary": summary,
            "description": summary + " Das Dossier ist eine redaktionelle Zusammenfassung des belegten Quellenstands.",
            "source": citation,
            "locations": locations,
            "scope": self.name,
            "sources": [src],
            "editions": [edition],
            "edition_descriptions": {
                edition: {
                    "kind": "Gruppendossier" if entity_type == "group" else "Personendossier",
                    "preview": summary,
                    "full": summary + " Das Dossier ist eine redaktionelle Zusammenfassung des belegten Quellenstands.",
                    "hasMore": True,
                    "hasExcerpt": True,
                    "sources": [src],
                }
            },
        }

    def finish(self, year: int, atlas_intro: str, bounds: list[list[float]] | None = None, zoom: int | None = None) -> None:
        city_dir = ROOT / "data" / self.city_id
        features = sorted(self.places.values(), key=lambda item: item["properties"]["name"].casefold())
        people = sorted(self.people.values(), key=lambda item: item["name"].casefold())
        write_json(
            city_dir / "places.geojson",
            {"type": "FeatureCollection", "name": f"{self.name} Orte", "features": features},
        )
        write_json(city_dir / "people.json", people)
        citations = []
        for feature in features:
            citations.extend(feature["properties"]["sources"])
        for person in people:
            citations.extend(person["sources"])
        unique_citations = []
        seen = set()
        for item in citations:
            signature = (item["bookId"], item["citation"], item["purpose"])
            if signature not in seen:
                seen.add(signature)
                unique_citations.append(item)
        write_json(
            city_dir / "sources.json",
            {"schemaVersion": 1, "books": self.books, "citations": unique_citations},
        )
        manifest_path = city_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["year"] = year
        # Version 6 adds source-based district summaries and direct district
        # polygon interaction.
        manifest["dataVersion"] = 7
        manifest["availableEditions"] = sorted(
            {edition for feature in features for edition in feature["properties"]["editions"]}
            | {edition for person in people for edition in person["editions"]}
        )
        manifest["atlasIntro"] = atlas_intro
        if bounds:
            manifest["overlayBounds"] = bounds
            manifest["cityBounds"] = bounds
            manifest["regionBounds"] = bounds
        if zoom:
            manifest["zoom"] = zoom
        manifest["summary"] = {
            "entities": len(features) + len(people),
            "marker_instances": len(features),
            "overview_marker_instances": len(features),
            "detail_marker_instances": len(self.map_marker_ids),
            "gangs": sum(person["category"] == "Gangs" for person in people),
            "corporations": sum(feature["properties"]["category"] == "Konzerne" for feature in features),
        }
        write_json(manifest_path, manifest)
        atlas_path = city_dir / "atlas.json"
        atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
        if atlas:
            atlas[0]["markerIds"] = self.map_marker_ids
        write_json(atlas_path, atlas)


DENVER_ANCHORS = {
    "The Hub": (39.7392, -104.9903),
    "Arvada": (39.8028, -105.0875),
    "Aurora Warrens": (39.7294, -104.8319),
    "Boulder": (40.0150, -105.2705),
    "Brighton": (39.9853, -104.8205),
    "Broomfield": (39.9205, -105.0867),
    "Castle Rock": (39.3722, -104.8561),
    "Centennial": (39.5807, -104.8772),
    "Colorado Springs": (38.8339, -104.8214),
    "Commerce City": (39.8083, -104.9339),
    "Elbert": (39.2194, -104.5372),
    "Englewood": (39.6478, -104.9878),
    "Front Range": (39.708, -105.230),
    "Lakewood": (39.7047, -105.0814),
    "Lowry": (39.7167, -104.9008),
    "Stapleton": (39.7794, -104.8814),
    "The Gap": (39.44, -104.94),
    "Thornton": (39.8680, -104.9719),
    "Westminster": (39.8367, -105.0372),
    "Aztlan Sector": (39.735, -104.985),
    "CAS Sector": (39.635, -104.965),
    "Pueblo Sector": (39.695, -105.105),
    "Sioux Sector": (39.80, -104.89),
    "UCAS Sector": (39.755, -104.98),
    "Ute Sector": (39.72, -105.13),
}

DENVER_BOOKS = [
    {"id": "denver-city-shadows-sr2", "title": "Denver: The City of Shadows", "edition": "SR2"},
    {"id": "shadows-north-america-sr3", "title": "Shadows of North America", "edition": "SR3"},
    {"id": "year-comet-sr3", "title": "Year of the Comet", "edition": "SR3"},
    {"id": "welcome-denver-sr4", "title": "Welcome to Denver", "edition": "SR4"},
    {"id": "srm02-sr4", "title": "Shadowrun Missions Season 2", "edition": "SR4"},
    {"id": "spy-games-sr4", "title": "Spy Games", "edition": "SR4"},
    {"id": "storm-front-sr4", "title": "Storm Front", "edition": "SR4"},
    {"id": "denver-trilogy-sr5", "title": "Denver Adventure Trilogy", "edition": "SR5"},
    {"id": "third-parallel-sr6", "title": "The Third Parallel", "edition": "SR6"},
]

DENVER_SR6_PLACES = {
    "Arvada": ["Arvada", "Atlantean Foundation Offices", "KMAG Headquarters", "Lakeside Amusement Park", "Mesametric Factory", "Table Mountain Prison Complex"],
    "Aurora Warrens": ["Aurora Warrens", "Aurora Village Medical Center", "Meat Market", "Paradise Lane", "Quincy Reservoir", "Smoky Hill Marketplace"],
    "Boulder": ["Boulder", "Fox Theatre", "Halferville", "Heritage Museum", "Horizon Office Complex", "SpiriTech Headquarters", "University of Colorado"],
    "Brighton": ["Brighton", "Change the Range Solar Farm", "Horse Trot Ranch", "Pearson Park", "Safiya’s Critter Care", "Sitting Bull Shooting Range", "VOR Robotics Office"],
    "Broomfield": ["Broomfield", "Cerebrotech Factory", "HyperSense Headquarters", "Newlife Medical", "Sedalia Airport", "Towne Center Mall"],
    "Castle Rock": ["Castle Rock", "Castle Rock Fusion Plant", "Pradera Resort", "Stonegate Judicial Complex"],
    "Centennial": ["Centennial", "Aegis Cognito Office", "Centennial Airport", "Chamberlain Airport", "Cherry Creek Country Club", "Free Zone Voice Offices", "FTL Technologies Headquarters", "Novatech Matrix Services Office", "The Tipsy Chip", "University of Denver", "Warpdrive Systems Headquarters", "Wuxing Cherry Park"],
    "Colorado Springs": ["Colorado Springs", "Cheyenne Mountain", "Church of the Holy Word", "Colorado College", "Denver Data Haven Ruins", "Energia Viva Solar Farm", "Fort Carson", "Garden of the Gods", "Peterson Airport", "Shrine of the Sun", "Tesla Experimental Station", "Zebulon’s Revenge"],
    "Commerce City": ["Commerce City", "Krupp Chemicals Refinery", "The Solution", "Truman Distribution Networks Office", "Tsuruga International Warehouse"],
    "Elbert": ["Elbert", "Grassy Knoll Ranch", "Little Wolf Nursery"],
    "Englewood": ["Englewood", "Ketring Park", "Knight Errant Training Facility"],
    "Front Range": ["Front Range", "Blackhawk Resort and Casino", "Echo Mountain", "Red Rocks Amphitheater", "ZDF Station Front Range"],
    "Lakewood": ["Lakewood", "All the World’s a Stage", "Ares Arms Factory", "Casa Bonita", "Compri Hotel", "Denim", "Joe’s Drop Off", "Lakewood Correctional Institute"],
    "Lowry": ["Lowry", "Ascending Star", "Happy Canyon Mall", "Lowry International Airport", "Klub Karma", "Ming Solutions Office", "Nu Shen Massage", "Rusty’s Garage", "Three Delights", "Wings Over the Rockies Air & Space Museum"],
    "Stapleton": ["Stapleton", "Brainwave, Inc. Office", "Buckley Air Force Base", "Casquilho Imports", "Children of the Dragon Headquarters", "Denver International Airport", "Denver Sports Complex", "Front Range Space Port", "Marcel’s", "Rocky Mountain Arsenal Park", "Stapleton Airport"],
    "The Gap": ["The Gap"],
    "The Hub": ["The Hub", "Anasazi Holding Company Headquarters", "Ares-McAuliffe International School", "Ares Spire", "Brown Palace Hotel", "Church of the Dragon Reborn Headquarters", "Council Hall", "Daniels & Fisher Clock Tower", "Denver Administration Building", "Denver Zoo", "Draco Foundation Office", "Evo Gardens", "Feed Trough", "Fillmore Auditorium", "Five by Five", "Focused Consulting and Brokerage Headquarters", "Gadgeteer’s Electronics", "Ghostwalker’s Liaison Office", "Goodfriends", "Hargreaves Clinic", "Idyll Recovery Center", "Inari Jinja", "Lunar Noctum", "Mile High Limo and Taxi Service", "Pam’s Pawn", "Patterson Mansion", "Rocky Mountain Post Headquarters", "Sakura Square", "Sal’s Cheap Sleeps", "The Church", "The Grind", "Tower of Babel", "Truman Tech Tower", "Union Station", "Weekday Eclipse Memorial"],
    "Thornton": ["Thornton", "Apex Plasmids Complex", "Carnimore", "Hardpan", "Overmon-Aberny", "Shiawase Plaza"],
    "Westminster": ["Westminster", "Iris Firmware Office", "Native American Broadcasting Service", "Northern Lights Enchanting", "Rattlesnake Grill"],
}

DENVER_DISTRICT_SUMMARIES = {
    "Arvada": "Arvada ist eine überwiegend urbane Pendler- und Schlafstadt nordwestlich des Zentrums; der Westen wird ländlicher, während sich die Bebauung zum Hub hin stark verdichtet.",
    "Aurora Warrens": "Die Aurora Warrens sind ein dicht bevölkertes Elendsgebiet mit zerfallender Infrastruktur, starker Gangkontrolle und einer wachsenden Untergrundbevölkerung.",
    "Boulder": "Boulder bildet den nördlichen Abschluss der FRFZ und verbindet strenge Umweltauflagen mit Universität, Kunstszene und einer vergleichsweise geringen Konzernpräsenz.",
    "Brighton": "Brighton liegt als dünn besiedelter Agrardistrikt am nordöstlichen Zonenrand zur Sioux Nation; Farmen, Solaranlagen und abgelegene Konzernstandorte prägen die Ebene.",
    "Broomfield": "Broomfield ist ein wohlhabender Vorstadtdistrikt mit teuren Wohnlagen, zahlreichen Konzernenklaven, niedriger Kriminalität und besonders schnellen ZDF-Reaktionen.",
    "Castle Rock": "Castle Rock konzentriert seine kritische Infrastruktur entlang der Interstate 25; abseits dieses Korridors ist der Distrikt dünn besiedelt und weitgehend ländlich.",
    "Centennial": "Centennial ist das Technologiezentrum der FRFZ, Sitz zahlreicher Matrixfirmen und der University of Denver; nach der Reclamation übernahm es zudem Teile des zerstörten Englewood.",
    "Colorado Springs": "Colorado Springs ist die südlichste Großstadt der FRFZ und leidet nach wiederholten Machtwechseln zwischen Aztlan, CAS, PCC und Ghostwalker unter Abwanderung und schwacher Verwaltung.",
    "Commerce City": "Commerce City ist ein dichtes Arbeitergebiet nördlich des Zentrums, wirtschaftlich stark von Industrie, Raffinerien und dem Güterumschlag abhängig.",
    "Elbert": "Elbert umfasst die ländlichen Ebenen östlich der Interstate 25 zwischen Denver und Colorado Springs; nomadische Gruppen und Go-Gangs kontrollieren viele Schmuggelwege.",
    "Englewood": "Englewood wurde während der Reclamation nahezu vollständig zerstört und besitzt keinen Ratssitz mehr; wenige Überlebende halten sich vor allem um Ketring Park zwischen Ruinen und gefährlichen Geistern.",
    "Front Range": "Der Front-Range-Distrikt ist das größte und westlichste Gebiet der Zone: schwer zugängliches Gebirge zwischen Boulder und Colorado Springs mit Resorts, Casinos und Schmuggelrouten.",
    "Lakewood": "Lakewood ist eine eher bodenständige, blaukragengeprägte Vorstadt westlich des Hub; die Nähe zum zerstörten Englewood belastet insbesondere die magische Sicherheit.",
    "Lowry": "Lowry ist ein kleiner Industrie- und Arbeiterdistrikt östlich des Hub, entstanden aus einem ehemaligen Luftwaffenstützpunkt und geprägt von Werkstätten, Maschinenkultur und Chinatown.",
    "Stapleton": "Stapleton ist der große, dünn besiedelte Ostdistrikt der FRFZ; außerhalb des stadtnahen Vorstadtbereichs dominieren abgeschirmte Konzernanlagen, Flughäfen und Forschungsstandorte.",
    "The Gap": "The Gap ist der fast menschenleere Korridor zwischen Castle Rock und Colorado Springs, im Wesentlichen von der Interstate 25, wilden Geistern und mobilen Go-Gangs geprägt.",
    "The Hub": "The Hub ist Ghostwalkers dichtes politisches, wirtschaftliches und spirituelles Machtzentrum mit Zonenrat, Verwaltung, Konzernniederlassungen und außergewöhnlich vielfältiger Geisterpräsenz.",
    "Thornton": "Thornton liegt zwischen Westminster und Brighton und bewahrt deutliche Einflüsse der früheren Sioux-Verwaltung; offene Bewaffnung und ehemalige Sioux-Sicherheitskräfte sind alltäglich.",
    "Westminster": "Westminster ist ein kleiner Vorstadtdistrikt nordwestlich des Hub, dessen Verkehr und Unruhe häufig über die Grenze schwappen; ZDF und Überwachung reagieren hier besonders aggressiv.",
}

DENVER_MAP_NAMES = [
    "Anasazi Holding Company Headquarters", "Apex Plasmids Complex", "Atlantean Foundation Offices",
    "Casquilho Imports", "Children of the Dragon Headquarters", "Church of the Dragon Reborn Headquarters",
    "Council Hall", "Denim", "Denver Administration Building", "Denver Sports Complex", "Draco Foundation Office",
    "Fox Theatre", "Ghostwalker’s Liaison Office", "Happy Canyon Mall", "Horizon Office Complex", "Inari Jinja",
    "Joe’s Drop Off", "Ketring Park", "Lunar Noctum", "Northern Lights Enchanting", "Pam’s Pawn",
    "Paradise Lane", "Patterson Mansion", "Rocky Mountain Arsenal Park", "Sakura Square",
    "Smoky Hill Marketplace", "Tower of Babel",
]

DENVER_SR2_PLACES = {
    "Aztlan Sector": ["Burnsley Hotel", "Days Inn Capitol Hill", "Chinampas", "The Serpent’s Feather", "Boettcher Memorial Conservatory", "Anahuac University", "Aztechnology Building", "State Capitol Building"],
    "CAS Sector": ["Melbourne Hotel", "Stouffer Concourse Hotel", "Regency Tech Center", "Grassroots", "Goodfriends", "Rock Solid", "Denver Tech Center", "Ketring Park"],
    "Pueblo Sector": ["Compri Hotel", "Golden Days Inn", "The Raintree Inn", "Tablelands Restaurant", "The Rattlesnake Grill", "Hard Target", "Lakewood Correctional Institution", "Fort Logan Medical Center", "Fort Carson Military Reservation"],
    "Sioux Sector": ["Overmon-Aberny", "Hyatt-Star Regency", "Comfort Inn", "The Front Range", "Eyrie", "Hardpan", "Denver Foodstuffs Inc.", "Denver Union Stockyards"],
    "UCAS Sector": ["Brown Palace Hotel", "Conner-Westin Hotel", "Radisson Hotel", "Cambridge Hotel", "Holiday Inn", "Augusta", "Café Giovanni", "The New McCormick’s Seafood House", "The Digs", "Aurora Warrens", "Denver Sports Complex", "Broncomania Stadium", "Rocky Mountain Arsenal", "Universal Brotherhood Chapterhouse"],
    "Ute Sector": ["Holiday Inn Denver Sports Center", "Denver Marriott West", "The Rack", "Adirondack", "The Buckhorn", "Denim", "Lakeside Amusement Park", "University of Colorado"],
    "The Hub": ["Denver Data Haven", "The Nexus", "Council Hall"],
}

DENVER_GROUPS_SR6 = [
    "Koshari", "Nahmana Circle", "Ohanzee Circle", "Wahchinksapa Circle", "Outer Circle", "Komun’go",
    "Chavez Family", "Casquilho Family", "Tamanous", "Golden Triangle Triad", "White Lotus Triad",
    "Kirillov Vory", "Karemasu Clan", "Ancients", "Chrome Domes", "Cutters", "Dogmen", "Durin’s Sons",
    "First Nation", "Fronts", "Aurora Angels", "Dambusters", "Three Kings", "Ghost Riders",
    "Ironsiders MC", "Nocturna", "Silver Thorns", "Smooth Criminals", "West Side Bloods", "Zombies",
]

DENVER_PEOPLE_SR6 = [
    ("Alexis Glimmerscale", "Vertreterin der Draco Foundation", "Draco Foundation"),
    ("Charles Lightfoot", "Konzernmanager", "FTL Technologies"),
    ("Dean Costello", "Hacker und Unterweltkontakt", "Casquilho Family"),
    ("Lester Truman", "Geschäftsmann", "Truman Distribution Networks"),
    ("Nicholas Whitebird", "Liaison Ghostwalkers", "Denver Administration"),
    ("Rhinegold", "Schattenakteur", "Denver"),
    ("Silver Streak", "Rigger und Schattenakteur", "Denver"),
    ("Steven Ridgemont", "Programmierer und Unternehmer", "Warpdrive Systems"),
    ("Arcane", "Fae und Schattenakteur", "Denver"),
    ("Carol “Cat” McTavish", "Fixerin und Johnson", "Denver-Schatten"),
    ("Cap’n Kludge", "Nexus-Administrator", "Denver Data Haven"),
    ("Goldsmoke", "Schattenakteur", "Denver"),
    ("Kangee Ohanze", "Agent und Informationssammler", "Denver"),
    ("Mr. K", "Mr. Johnson", "Denver"),
    ("Masque", "Magischer Agent", "Aztechnology"),
    ("Magnum", "Schattenakteur", "Denver"),
    ("Perri", "Sysop", "Denver Data Haven"),
    ("The Refugee", "Gestaltwandler und Forscher", "Denver"),
    ("Stiletto", "Runnerin", "Denver"),
    ("Thomas White Feather", "Koshari-Akteur", "Koshari"),
    ("Vishala", "Magische Forscherin", "Denver"),
]

DENVER_PEOPLE_SR2 = [
    ("Hector Ramirez", "Aztlan-Vertreter im Council of Denver", "Aztlan"),
    ("Elizabeth “Betty” Kalheim", "CAS-Vertreterin im Council of Denver", "CAS"),
    ("Jonathan Popé", "Pueblo-Vertreter im Council of Denver", "Pueblo Corporate Council"),
    ("Mary Cat Dancing", "Sioux-Vertreterin im Council of Denver", "Sioux Nation"),
    ("William Huhuseca", "Ute-Vertreter im Council of Denver", "Ute Nation"),
    ("Jeremy Falloon", "UCAS-Vertreter im Council of Denver", "UCAS"),
    ("Cap’n Kluge", "Mitglied des Denver Data Haven", "Denver Data Haven"),
    ("Shiva", "Mitglied des Denver Data Haven", "Denver Data Haven"),
    ("Nahid Mostafavi", "Mitglied des Denver Data Haven", "Denver Data Haven"),
    ("Tom Kwan", "Mitglied des Denver Data Haven", "Denver Data Haven"),
    ("Kasigi Toda", "Yakuza-Oyabun", "Yakuza"),
    ("Francisco “Paco” Valdez", "Sektormanager", "Aztlan"),
    ("Rachel Sands", "Wirtin des Hardpan", "Hardpan"),
    ("Amazing Grace Rutan", "Lokale Persönlichkeit", "Ute Sector"),
]

DENVER_GROUPS_SR2 = [
    "BBs", "Braineaters", "Fronts", "Godz", "Hudson Hawks", "Trey Eights", "Cutters",
    "Golden Triangle Triad", "Red Dragon Triad", "White Lotus Triad", "Dreamland Syndicate",
]

DENVER_SPY_GAMES_PLACES = [
    ("Five by Five", "The Hub", "Bars und Clubs", "Five by Five ist eine nur über Tunnel und unterirdische Zugänge erreichbare Bar für Schmuggler und Coyoten; Geschäfte werden dort angebahnt, aber nicht offen verhandelt."),
    ("Klub Karma", "Lowry", "Bars und Clubs", "Klub Karma ist ein langjähriger Treffpunkt der Schatten in Chinatown und zugleich Territorium der Mafia; private Räume dienen diskreten Verhandlungen."),
    ("Mystic Curiosities", "Lowry", "Einkaufen", "Mystic Curiosities ist Zhang Wongs Taliskrämerladen in Chinatown, bekannt für zweifelhafte Massenware ebenso wie seltene Stücke und fundiertes arkanes Wissen."),
    ("University of Denver", "Centennial", "Bildung und Kultur", "Die University of Denver ist ein politisch aktiver Campus; die Penrose Library des psychologischen Instituts besitzt ein nicht öffentliches magisches Archiv."),
    ("Ketring Park", "Englewood", "Freizeit und Natur", "Ketring Park wandelte sich vom Gang-Schlachtfeld zu einem geduldeten neutralen Verhandlungsort, an dem Unterweltakteure Konflikte ohne offene Gewalt regeln."),
    ("Goodfriends", "The Hub", "Bars und Clubs", "Goodfriends ist ein wechselhaft geführter Treffpunkt für schnelle Kontakte und diskrete Begegnungen mit kleinen privaten Räumen."),
    ("Tower of Babel", "The Hub", "Bars und Clubs", "Der Tower of Babel ist ein populärer Club im Hub mit Unterweltpublikum, aufwendigen AR-Installationen und einer verborgenen Etage als CAS-Safehouse."),
    ("Altitude", "The Hub", "Bars und Clubs", "Altitude ist eine unaufgeregte Bar im Hub und einer der wenigen öffentlich bekannten Aufenthaltsorte von Nicholas Whitebird."),
    ("Wonderland", "The Hub", "Bars und Clubs", "Wonderland ist ein Club im Hub, der über verschachtelte Firmenkonstruktionen der freien Geistfrau Alyss gehört und von Diplomaten sowie Informationshändlern besucht wird."),
    ("Lakeside Amusement Park", "Arvada", "Freizeit und Natur", "Der zum Casino umgebaute Lakeside Amusement Park dient der Chavez-Familie als operative Basis."),
    ("Denim", "Lakewood", "Bars und Clubs", "Denim ist ein Hopi-thematisierter Nachtclub der Koshari, in dem auch Angehörige der Pueblo-Sicherheit verkehren."),
    ("Rattlesnake Grill", "Westminster", "Restaurants", "Der Rattlesnake Grill ist wegen seiner südwestlichen Küche ein beliebter, offener Treffpunkt für Runner und reguläre Gäste."),
    ("DocWagon Hospital Complex", "The Hub", "Medizin", "Der größte DocWagon-Komplex der FRFZ verbindet ein hochklassiges Traumazentrum mit einer inoffiziellen Straßenklinik in Raum 4-203."),
    ("Compri Hotel", "Lakewood", "Hotels", "Das Compri Hotel wirbt mit außergewöhnlicher Diskretion und meldet zugleich jeden Verdacht auf Spionage an Ghostwalkers Behörden."),
    ("Lakewood Correctional Institute", "Lakewood", "Sicherheit und Justiz", "Das Lakewood Correctional Institute experimentiert mit BTL-gestützten Methoden zur Rückfallvermeidung und nimmt tödliche Folgen billigend in Kauf."),
    ("Horse Trot Ranch", "Brighton", "Konzerne", "Die weitläufige Horse Trot Ranch von Falcone Corporate Consultants dient als abgeschirmter Rückzugs- und Verhandlungsort für Konzernführungskräfte."),
    ("Overmon-Aberny", "Thornton", "Hotels", "Das rustikale Overmon-Aberny setzt auf militärisch erfahrenes Personal und besitzt für ein Hotel außergewöhnlich starke physische Sicherheit."),
    ("Apex Plasmids Complex", "Thornton", "Konzerne", "Der rasch gewachsene Hauptkomplex von Apex Plasmids gilt wegen hinterherhinkender Sicherheitsabläufe als häufiges Ziel von Runs."),
    ("Hardpan", "Thornton", "Bars und Clubs", "Das abgelegene Hardpan ist Raquel Sands’ Bar nahe Algenbecken, Kläranlage und Friedhof und ein wichtiger Treffpunkt harter Sioux-Straßenkontakte."),
    ("Brown Palace Hotel", "The Hub", "Hotels", "Das Brown Palace schützt seine wertvolle Kunst besser als seine Matrix und eignet sich daher besonders zum Platzieren langfristiger Überwachungstechnik."),
    ("Marcel’s", "Stapleton", "Restaurants", "Marcel’s ist ein italienisches Restaurant, Geldwaschanlage und Stammhaus der Casquilho-Familie mit überwachten privaten Räumen."),
    ("Rocky Mountain Arsenal Park", "Stapleton", "Freizeit und Natur", "Das ehemalige Arsenal wurde zum Wildschutzgebiet; erwachte Tiere und Nester großer Critter machen das Gelände zugleich wertvoll und gefährlich."),
    ("Hargreaves Clinic", "The Hub", "Medizin", "Die Hargreaves Clinic gehört zu den spezialisierten medizinischen Einrichtungen der FRFZ und wird auch von politisch oder geheimdienstlich exponierten Personen genutzt."),
    ("Aurora Village Medical Center", "Aurora Warrens", "Medizin", "Das Aurora Village Sports Medical Center versorgt Sportler und zahlungskräftige Klienten am Rand der Warrens."),
    ("Apex Plasmids Complex", "Thornton", "Konzerne", "Apex Plasmids ist ein einheimischer A-Konzern mit Ghostwalkers Wohlwollen, dessen Hauptkomplex trotz schneller Expansion verwundbar geblieben ist."),
    ("Focused Consulting and Brokerage Headquarters", "The Hub", "Konzerne", "Focused Consulting and Brokerage gehört zu Denvers einflussreichen A-Konzernen und vermittelt diskret zwischen Wirtschaft, Politik und Nachrichtendiensten."),
    ("Mesametric Factory", "Arvada", "Konzerne", "Mesametric zählt zu den bedeutenden einheimischen Konzernen der FRFZ und unterhält in Denver zentrale Produktions- und Verwaltungsanlagen."),
    ("Native American Broadcasting Service", "Westminster", "Konzerne", "Der Native American Broadcasting Service prägt Denvers Medienlandschaft und dient zugleich als politischer Einflusskanal der NAN."),
    ("SpiriTech Headquarters", "Boulder", "Konzerne", "SpiriTech verbindet in Denver arkanes Fachwissen mit Konzernforschung und gehört zu den lokal bedeutenden A-Konzernen."),
    ("Warpdrive Systems Headquarters", "Centennial", "Konzerne", "Warpdrive Systems ist ein einheimischer Technologiekonzern, dessen Denver-Geschäft eng mit Matrix- und Verkehrsinfrastruktur verbunden ist."),
]

DENVER_SPY_GAMES_PEOPLE = [
    ("Ghostwalker", "Großer Drache und Herrscher der FRFZ", "Front Range Free Zone", "Ghostwalker beherrscht Denver kraft Vertrag und persönlicher Macht; Verwaltung, Geisterpolitik und Sicherheitsapparat richten sich letztlich nach seinem Willen."),
    ("Johann Castle", "CAS-Vertreter im Council of Denver", "CAS", "Johann Castle ist ein wohlhabender, öffentlich flamboyanter CAS-Vertreter, dessen Auftreten ihn leichtfertiger erscheinen lässt, als seine politische Stellung vermuten lässt."),
    ("Istas Catori", "PCC-Vertreterin im Council of Denver", "Pueblo Corporate Council", "Istas Catori ist eine zurückhaltende Hopi-Elfe und PCC-Vertreterin, um deren Vergangenheit und mögliche erwachte Natur zahlreiche Gerüchte kreisen."),
    ("Lucinda Gray Arrow", "Sioux-Vertreterin im Council of Denver", "Sioux Nation", "Lucinda Gray Arrow ist eine langjährige Katzenschamanin im Council und eine der sichtbarsten Unterstützerinnen Ghostwalkers."),
    ("Nicholas Whitebird", "Stimme Ghostwalkers", "Denver Administration", "Nicholas Whitebird ist Ghostwalkers orkischer Sprecher und politischer Vermittler; er verlässt den Hub nur selten."),
    ("Iain Lesker", "UCAS-Vertreter im Council of Denver", "UCAS", "Iain Lesker vertritt einen nationalistischen und metamenschenfeindlichen UCAS-Kurs und stützt sich auf ein engmaschiges Sicherheitsumfeld."),
    ("Alyss", "Freier Geist und Informationsakteurin", "Wonderland", "Alyss tritt als elfische freie Geistfrau und gesellschaftliche Begleiterin auf, besitzt jedoch Zugang zu Diplomaten, Behörden und einem weitreichenden Informationsnetz."),
    ("Eddie “Mustang” Vass", "Informationsbroker und ehemaliger Runner", "Raintree Inn", "Eddie Vass, früher Mustang, führt das Raintree Inn und steht im Zentrum eines informellen Netzwerks aus Fixern, Auftraggebern und Runnern."),
    ("Eric Talbert", "Leiter Metahuman Resources", "UCAS Sector", "Eric Talbert kontrolliert die Personalentscheidungen der UCAS-Sektorverwaltung und vermittelt verdeckte Aufträge an kurzfristige Kräfte."),
    ("Jorge Molinera", "Präsident der Anáhuac University", "Anahuac University", "Jorge Molinera verbindet akademischen Einfluss, Aztlan-Loyalitäten und ein Netz ehemaliger Studierender in Denvers Politik und Wirtschaft."),
    ("Jan Drysik", "Magier, Entertainer und Informationsbroker", "The Hub", "Jan Drysik nutzt seine Auftritte bei der Elite als Deckmantel für ein einträgliches Informations- und Vermittlungsgeschäft."),
    ("Juanita Iglala", "PCC-Politikerin und Koshari-Kontakt", "Pueblo Corporate Council", "Juanita Iglala bleibt nach ihrem Rückzug aus dem Council eine einflussreiche PCC-Akteurin mit mutmaßlichen Verbindungen zu den Koshari."),
    ("Riley Chaska", "Unternehmer und Schmuggelkontakt", "Denver", "Riley Chaska betreibt mit Rocko die sektorübergreifende Baumarktkette Sock-n-Wrench und vermittelt über sie Safehouses, Material und Kontakte."),
    ("Rocko", "Freier Geist und Geschäftspartner", "Sock-n-Wrench", "Rocko führt die Bücher von Sock-n-Wrench und nutzt gemeinsam mit Riley Chaska Kontakte in die Schmugglerszene."),
    ("Roger Soaring Owl", "Sicherheitsberater", "Sioux Nation", "Der frühere Knight-Errant-CEO Roger Soaring Owl hält sich wiederholt in Denver auf und berät die Sioux in Sicherheitsfragen."),
    ("Tabitha “Tabby” Morgan", "Konzernfixerin", "CAS Sector", "Tabby ist eine unverwechselbare Changeling-Fixerin, die Runner, ehemalige Militärangehörige und Konzernkunden zusammenbringt."),
    ("Tess McCartle", "Politikwissenschaftlerin und Kontakt", "University of Denver", "Tess McCartle leitet die Politikwissenschaften der University of Denver und kennt Strömungen, Akteure und Kampagnen der Stadtpolitik."),
    ("Zany Zuni", "Matrix-Informationsakteur", "Denver Data Haven", "Zany Zuni ist eine ungeklärte Matrixidentität mit Zugriff auf umfangreiche öffentliche Daten und erheblichem Einfluss auf den Denver Exchange."),
    ("Zhang Wong", "Taliskrämer", "Mystic Curiosities", "Zhang Wong verkauft in Mystic Curiosities sowohl billige Ware als auch seltene Telesma und besitzt umfangreiches arkanes Wissen."),
    ("Lydia McDaniel", "Forscherin und Archivkontakt", "University of Denver", "Dr. Lydia McDaniel vermittelt unter strengen Bedingungen Zugang zum magischen Archiv der Penrose Library."),
    ("Raquel “Sandy” Sands", "Wirtin und Straßenkontakt", "Hardpan", "Raquel Sands führt das Hardpan und ist eine zentrale Ansprechpartnerin für Informationen und Personal aus den Sioux-Straßen."),
    ("Miguel Yatokya", "PCC-Sektorpolitiker", "Pueblo Corporate Council", "Miguel Yatokya ist Präsident pro tempore des PCC-Sektors und steht in engem Austausch mit Juanita Iglala."),
    ("Jaron Falcone", "Konzernberater und ehemaliger Runner", "Horse Trot Ranch", "Jaron Falcone, früher als Decker HammerJack aktiv, betreibt abgeschirmte Konzernretreats und hilft Runnern nur mit belastbarer Abstreitbarkeit."),
    ("Gob", "Gangvermittler", "Fronts", "Gob vertritt die Fronts bei Unterweltverhandlungen im Ketring Park und koordiniert dort unter anderem den CalHots-Handel."),
]

DENVER_SPY_GAMES_CRIME_PEOPLE = [
    ("Miguel “Caesar” Chavez", "Don der Chavez-Familie", "Chavez Family", "Miguel Chavez führt die einflussreichste Mafiafamilie Denvers und wahrt deren Macht durch Bündnisse, Patronage und gezielte Gewalt.", "Lakeside Amusement Park"),
    ("Carlos Chavez", "Mafia-Capo", "Chavez Family", "Carlos Chavez gehört zur Führung der Chavez-Familie und beaufsichtigt einen Teil ihrer Geschäfte und Vollstrecker.", "Lakeside Amusement Park"),
    ("Joseph “Big Joe” Lovato", "Mafia-Capo", "Chavez Family", "Big Joe Lovato zählt zu den leitenden Capos der Chavez-Familie und besitzt eigene Kontakte in Denvers Unterwelt.", "Lakeside Amusement Park"),
    ("Jorge Chavez", "Mafia-Capo", "Chavez Family", "Jorge Chavez ist Mitglied der engeren Familienführung und für einen Teil der operativen Geschäfte verantwortlich.", "Lakeside Amusement Park"),
    ("Mark Sanchez", "Mafia-Capo", "Chavez Family", "Mark Sanchez gehört als Capo zum Führungskreis der Chavez-Familie.", "Lakeside Amusement Park"),
    ("Stephen Rodriguez", "Mafia-Capo", "Chavez Family", "Stephen Rodriguez ist ein weiterer leitender Akteur der Chavez-Familie.", "Lakeside Amusement Park"),
    ("Emilio Chavez", "Mafia-Nachwuchs und Runnerkontakt", "Chavez Family", "Emilio Chavez verbindet die jüngere Generation der Familie mit Denvers Runner- und Straßenszene.", "Lakeside Amusement Park"),
    ("Lucho Casquilho", "Don der Casquilho-Familie", "Casquilho Family", "Lucho Casquilho führt die Casquilho-Familie und ihr von Marcel’s ausgehendes Netz aus legalen Fassaden und kriminellen Geschäften.", "Marcel’s"),
    ("Lester “Scarface” Scrabulitelli", "Mafia-Capo", "Casquilho Family", "Scarface Scrabulitelli gehört zu den erfahrenen und gefürchteten Capos der Casquilho-Familie.", "Marcel’s"),
    ("Vasco Casquilho", "Mafia-Capo", "Casquilho Family", "Vasco Casquilho ist Teil der Familienführung und überwacht operative Geschäfte.", "Marcel’s"),
    ("Dean Costello", "Mafia-Capo", "Casquilho Family", "Dean Costello gehört zum Führungskreis der Casquilho-Familie.", "Marcel’s"),
    ("Peder Vasquez", "Mafia-Capo", "Casquilho Family", "Peder Vasquez koordiniert als Capo einen Teil des Casquilho-Netzwerks.", "Marcel’s"),
    ("Miguel Sanchez", "Mafia-Capo", "Casquilho Family", "Miguel Sanchez ist ein leitender Akteur der Casquilho-Familie.", "Marcel’s"),
    ("Juliette “Sparks” Junipero", "Mafia-Technikspezialistin", "Casquilho Family", "Sparks Junipero unterstützt die Casquilhos mit technischem und operativem Fachwissen.", "Marcel’s"),
    ("Tahaum Soyoko", "Führungspersönlichkeit der Koshari", "Koshari", "Tahaum Soyoko gehört zur Führung des Denver-Zweigs der Koshari.", "Denim"),
    ("Nata-aska", "Koshari-Akteur", "Koshari", "Nata-aska ist ein namentlich genannter Akteur im Denver-Netzwerk der Koshari.", "Denim"),
    ("Elambr", "Koshari-Akteur", "Koshari", "Elambr arbeitet für den Denver-Zweig der Koshari.", "Denim"),
    ("Joshua Kawaibatunya", "Koshari-Akteur", "Koshari", "Joshua Kawaibatunya gehört zum operativen Personal der Koshari in Denver.", "Denim"),
    ("Johnny Backstreet", "Koshari-Straßenkontakt", "Koshari", "Johnny Backstreet verbindet die Koshari mit Kontakten und Geschäften auf der Straße.", "Denim"),
    ("Mark Longfeather", "Führungspersönlichkeit des Wahchinksapa Circle", "Wahchinksapa Circle", "Mark Longfeather gehört zur Leitung des Sioux-Unterweltnetzwerks Wahchinksapa Circle.", None),
    ("James Greytail", "Wahchinksapa-Akteur", "Wahchinksapa Circle", "James Greytail ist ein namentlich genannter Akteur des Wahchinksapa Circle.", None),
    ("Johnny Ono", "Oyabun des Yamato-Clans", "Yamato Clan", "Johnny Ono führt den Yamato-Clan in Denver und muss seine geschwächte Organisation gegen mehrere Syndikate behaupten.", None),
    ("Kazuya “The Dragon” Hotomi", "Yakuza-Führungskraft", "Yamato Clan", "Kazuya Hotomi gehört zur verbliebenen Führung des Yamato-Clans.", None),
    ("Setto Karemaru", "Yakuza-Führungskraft", "Yamato Clan", "Setto Karemaru zählt zum leitenden Personal des Yamato-Clans.", None),
    ("Mikko Toyama", "Yakuza-Führungskraft", "Yamato Clan", "Mikko Toyama ist ein namentlich genannter Führungskader des Yamato-Clans.", None),
    ("Katsuo Sawaruma", "Yakuza-Führungskraft", "Yamato Clan", "Katsuo Sawaruma gehört zur Führung des Denver-Yamato-Clans.", None),
    ("Yue Fe", "Triadenführer", "Golden Triangle Triad", "Yue Fe ist ein führender Akteur der Golden Triangle Triad in Denver.", None),
    ("Hu Yan Zhuo", "Triadenführer", "Golden Triangle Triad", "Hu Yan Zhuo gehört zur Leitung der Golden Triangle Triad.", None),
    ("Li Zicheng", "Triadenführer", "Golden Triangle Triad", "Li Zicheng ist Teil des Führungskreises der Golden Triangle Triad.", None),
    ("Hai Feng", "Triadenführer", "White Lotus Triad", "Hai Feng gehört zu den führenden Mitgliedern der White Lotus Triad.", None),
    ("Chen Seng-ho", "Triadenführer", "White Lotus Triad", "Chen Seng-ho ist ein leitender Akteur der White Lotus Triad.", None),
    ("An Peng", "Triadenführer", "White Lotus Triad", "An Peng gehört zum Führungskreis der White Lotus Triad.", None),
    ("Vladimir Kirillov", "Zar der Kirillov Vory", "Kirillov Vory", "Vladimir Kirillov führt die nach ihm benannte Vory-Organisation in Denver.", None),
    ("Mikhail Petrov", "Vory-Führungskraft", "Kirillov Vory", "Mikhail Petrov gehört zur Führung der Kirillov Vory.", None),
    ("Nikolai Kirillov", "Vory-Führungskraft", "Kirillov Vory", "Nikolai Kirillov ist Teil des leitenden Familien- und Organisationskreises der Kirillov Vory.", None),
    ("Vasilli Fomin", "Vory-Führungskraft", "Kirillov Vory", "Vasilli Fomin ist ein leitender Akteur der Kirillov Vory.", None),
    ("Alexei Klavikov", "Vory-Führungskraft", "Kirillov Vory", "Alexei Klavikov gehört zum Führungspersonal der Kirillov Vory.", None),
    ("Irina Klavikova", "Vory-Führungskraft", "Kirillov Vory", "Irina Klavikova ist eine namentlich genannte Führungskraft der Kirillov Vory.", None),
]

DENVER_SPY_GAMES_GROUPS = [
    ("Chavez Family", "Mafiafamilie", "Die Chavez-Familie ist eine der dominierenden Mafiaorganisationen Denvers und kontrolliert ihre Geschäfte von Lakeside aus."),
    ("Casquilho Family", "Mafiafamilie", "Die Casquilho-Familie arbeitet von Marcel’s und dem Hub aus und konkurriert mit Chavez, Koshari und weiteren Syndikaten."),
    ("Koshari", "Pueblo-Syndikat", "Die Koshari verbinden organisierte Kriminalität mit Pueblo-Politik und kontrollieren unter anderem Denim."),
    ("Wahchinksapa Circle", "Sioux-Syndikat", "Der Wahchinksapa Circle ist ein Sioux-Unterweltnetzwerk mit eigenständigen politischen und wirtschaftlichen Interessen."),
    ("Yamato Clan", "Yakuza-Clan", "Der Yamato-Clan war nach 2062 Denvers verbliebene Yakuza-Struktur und geriet 2074 durch koordinierte Angriffe an den Rand des Zusammenbruchs."),
    ("Golden Triangle Triad", "Triade", "Die Golden Triangle Triad gehört zu den etablierten chinesischen Syndikaten der FRFZ."),
    ("White Lotus Triad", "Triade", "Die White Lotus Triad ist eine bedeutende Denver-Triade und war in den Syndikatskrieg um den Dragon Stone verwickelt."),
    ("Kirillov Vory", "Vory-Syndikat", "Die Kirillov Vory nutzt die Instabilität zwischen Denvers Syndikaten, um Personal, Territorium und Geschäfte zu übernehmen."),
    ("Fronts", "Go-Gang", "Die Fronts gehören zu Denvers größten Go-Gangs und sind zugleich als bewaffnete Dienstleister der Unterwelt aktiv."),
    ("Godz", "Go-Gang", "Die Godz sind eine der älteren großen Go-Gangs Denvers und treten häufig als Konkurrenten der Fronts auf."),
    ("Aurora Angels", "Gang", "Die Aurora Angels gehören zu den einflussreichen Gangs der Warrens und kontrollieren lokale Wege und Geschäfte."),
    ("Ghost Riders", "Go-Gang", "Die Ghost Riders operieren auf Denvers Straßen und Schmuggelachsen."),
    ("Three Kings", "Gang", "Die Three Kings sind eine benannte Gang der FRFZ mit lokalem Revier und Unterweltkontakten."),
    ("Dambusters", "Gang", "Die Dambusters zählen zu den etablierten bewaffneten Gruppen der Denver-Straßen."),
    ("Zombies", "Gang", "Die Zombies sind eine gewaltbereite Denver-Gang, die 2074 zeitweise Harlekin-Schminke als Erkennungszeichen trug."),
    ("Komun’go", "Seoulpa-Ring", "Komun’go ist Teil eines koreanischen Unterweltnetzwerks, das gemeinsam mit Dogmen und First Nation in Denver auftritt."),
    ("Dogmen", "Unterweltgruppe", "Die Dogmen bilden mit Komun’go und First Nation ein verbundenes kriminelles Netzwerk."),
    ("First Nation", "Unterweltgruppe", "First Nation arbeitet im Verbund mit Komun’go und den Dogmen im Denver-Untergrund."),
    ("Denver Data Haven", "Matrixgemeinschaft", "Der Denver Data Haven beziehungsweise Nexus ist ein offener Schattenknoten, Zuflucht für Technomancer und eines der wichtigsten Informationsnetze der Stadt."),
]

DENVER_STORM_FRONT_PEOPLE = [
    ("Ghostwalker", "Großer Drache und Herrscher der FRFZ", "Front Range Free Zone", "Im Herbst 2074 reagiert Ghostwalker auf Anschläge, Matrixangriffe und spirituelle Unruhen mit Ausgangssperren, Grenzschließungen und massiver Gewalt."),
    ("Perianwyr", "Drache, Musiker und Clubmanager", "Weekday Eclipse", "Perianwyr wird 2074 wegen verbotener Geisterbeschwörung festgesetzt; seine Inhaftierung und die Zerstörung des Weekday Eclipse treiben den Protest gegen Ghostwalker an."),
    ("Alyss", "Freier Geist und Informationsakteurin", "The Hub", "Alyss stirbt beim Anschlag auf Lucinda Gray Arrow im Hub, wodurch Ghostwalkers gesellschaftliches und geheimdienstliches Netzwerk einen wichtigen Knoten verliert."),
    ("Lucinda Gray Arrow", "Sioux-Vertreterin im Council of Denver", "Sioux Nation", "Lucinda Gray Arrow wird 2074 bei einem Anschlag im Hub getötet, der zugleich Ghostwalkers politische Ordnung erschüttert."),
    ("Nicholas Whitebird", "Stimme Ghostwalkers", "Denver Administration", "Whitebird entgeht dem Anschlag auf Gray Arrow nur durch eine kurzfristige Reise und verkündet später Ghostwalkers Notstandsmaßnahmen."),
    ("Zebulon", "Großer Geist von Denver", "Denver", "Zebulon, auch She of the City genannt, steht im Zentrum des Konflikts zwischen Ghostwalker, freien Geistern und Denvers erwachter Bevölkerung."),
]

DENVER_STORM_FRONT_PLACES = [
    ("Weekday Eclipse Memorial", "The Hub", "Bars und Clubs", "Der Weekday Eclipse war Perianwyrs Musikclub und ein Zentrum des Protests gegen Ghostwalker, bevor er 2074 durch einen Brandanschlag zerstört wurde."),
    ("Dragon’s Lair", "The Hub", "Matrix und Metaplanes", "Dragon’s Lair bezeichnet Ghostwalkers privaten Knoten im Denver Data Haven; 2074 wurden daraus kompromittierte Daten in die Matrix gestreut."),
    ("Denver GridGuide", "The Hub", "Matrix und Metaplanes", "Denvers GridGuide wird im Oktober 2074 stadtweit kompromittiert und legt Verkehr, Flughäfen und sektorübergreifende Bewegungen lahm."),
]


MANHATTAN_ANCHORS = {
    "Washington Heights": (40.8417, -73.9394),
    "New Harlem": (40.8116, -73.9465),
    "Parkside": (40.7903, -73.9597),
    "Central Park": (40.7829, -73.9654),
    "Times Square": (40.7580, -73.9855),
    "Midtown": (40.7549, -73.9840),
    "West End": (40.7736, -73.9890),
    "Stuyvesant": (40.7317, -73.9779),
    "City Center": (40.7411, -73.9897),
    "Heritage": (40.7282, -73.9942),
    "Downtown": (40.7135, -74.0066),
    "Terminal": (40.7465, -74.0038),
    "Financial District": (40.7075, -74.0113),
    "Villages": (40.7336, -74.0027),
    "International District": (40.7158, -73.9970),
    "Battery City": (40.7116, -74.0155),
    "Inwood": (40.8677, -73.9212),
    "Upper West Side": (40.7870, -73.9754),
    "Upper East Side": (40.7736, -73.9566),
    "Westside": (40.7870, -73.9754),
    "Upper Eastside": (40.7736, -73.9566),
    "Lower Westside": (40.7465, -74.0010),
    "The Village": (40.7336, -74.0027),
    "Lower East Side": (40.7150, -73.9843),
    "Southside": (40.7200, -74.0020),
    "SoHo": (40.7233, -74.0030),
    "Chinatown": (40.7158, -73.9970),
    "Governors Island": (40.6895, -74.0168),
    "Randalls Island": (40.7957, -73.9227),
    "New York Harbor Islands": (40.6990, -74.0250),
    "Manhattan": (40.7580, -73.9855),
}

MANHATTAN_BOOKS = [
    {"id": "nagna-sr1", "title": "The Neo-Anarchist’s Guide to North America", "edition": "SR1"},
    {"id": "shadows-north-america-sr3", "title": "Shadows of North America", "edition": "SR3"},
    {"id": "rotten-apple-sr4", "title": "The Rotten Apple: Manhattan", "edition": "SR4"},
    {"id": "srm03-sr4", "title": "Shadowrun Missions Season 3", "edition": "SR4"},
    {"id": "corporate-enclaves-manhattan-sr4", "title": "Konzernenklaven: Manhattan", "edition": "SR4"},
    {"id": "stolen-souls-sr5", "title": "Gestohlene Seelen / Stolen Souls", "edition": "SR5"},
    {"id": "bloody-business-sr5", "title": "Blutige Geschäfte / Bloody Business", "edition": "SR5"},
    {"id": "battle-manhattan-sr5", "title": "Krieg um Manhattan / Battle of Manhattan", "edition": "SR5"},
    {"id": "fluesternetze-sr6", "title": "Flüsternetze", "edition": "SR6"},
]

MANHATTAN_DISTRICT_SUMMARIES = {
    "Inwood": "Inwood inszeniert am Nordende Manhattans eine grüne, vorstädtische Idylle für Führungskräfte, doch verschwundene Kinder und Zugänge zum Untergrund stören die sorgfältige Fassade.",
    "Washington Heights": "Washington Heights verbindet Kliniken, Hochschulen, Parks und historische Orte mit wachsender antikonzernlicher Unruhe, die von Newtown nach Norden ausstrahlt.",
    "Newtown": "Das vollständig neu errichtete ehemalige Harlem sollte die konzernfreundliche Zukunft verkörpern; hinter der Fassade wachsen jedoch Neo-Anarchismus und kurzlebige Gangs aus Konzernjugendlichen.",
    "Westside": "Die Westside ist ein überwiegend von Konzernangestellten bewohnter Mittelschichtsstreifen am Hudson mit Einkaufsmöglichkeiten und einzelnen Geschäftskomplexen aus Midtown.",
    "Upper Eastside": "Die Upper Eastside enthält einige der teuersten Wohnlagen der Stadt sowie den dominanten Hauptsitz des Manhattan Development Consortium.",
    "Central Park": "Central Park ist eine von Shiawase gepflegte Naturkulisse unter permanenter PAN- und Drohnenkontrolle; die angrenzenden Luxusstreifen dienen Konzerneliten und repräsentativen Veranstaltungen.",
    "Midtown": "Midtown erstreckt sich zwischen 14th und 59th Street und bildet mit seinen Skyrakern, Verkehrsknoten, Medienhäusern und Geschäften das hell glänzende kommerzielle Zentrum der UCAS.",
    "Times Square": "Times Square ist Manhattans ikonische Bühne aus Theater, AR-Werbung und lückenloser Profilerfassung; im nahen Neon City konsumieren Konzernbürger kontrolliert inszenierte Verruchtheit.",
    "Lower Westside": "Die Lower Westside fällt vom Glanz Midtowns zu dichtem Niedriglohnwohnen, Docks und Ganggebieten am Rand von Terminal ab und beherbergt vor allem Personal kleinerer Konzerne.",
    "Terminal": "Terminal rund um Penn Station und Port Authority ist Manhattans kontrollierte Schattenzone für billige Unterkünfte, Drogen, Sexarbeit und Schmuggel, gesichert durch Chokepoints statt flächiger Ordnung.",
    "Stuyvesant": "Stuyvesant ist ein extrem wohlhabendes Villenviertel, dessen scheinbar dekorative Gebäude, Gärten und Tiere vielfach als bewaffnete Sicherheits- und Überwachungssysteme dienen.",
    "The Village": "The Village vermarktet eine konzernkompatible Nachbildung seiner früheren Bohème; NYCU, genehmigte Gegenkultur und touristische Geschäfte dominieren das Quartier.",
    "The Pit": "The Pit bezeichnet die Lower Eastside jenseits verlässlicher NYPD-Kontrolle: eine eingedämmte Grenzzone aus Gangs, Squats und Sanierungsprojekten, in der zunehmend die Cutters auftreten.",
    "SoHo": "SoHo verbindet Galerien, Arkanshops und echte lokale Kultur mit sorgfältig inszenierter Konzernfolklore; je weiter südlich, desto weniger glatt wird die Fassade.",
    "Southside": "Southside mischt kleinere Konzerne, Wohnungen und Gewerbe; zum angrenzenden Terminal hin werden Sicherheitsnetz und Ordnung schwächer und kurzlebige Thrillgangs häufiger.",
    "City Center": "City Center beherbergt Stadtverwaltung, NYPD, Gerichte und die wiederaufgebaute East Coast Stock Exchange im unmittelbaren Macht- und Matrixschatten der Towers.",
    "Chinatown": "Chinatown bewahrt hinter seiner touristischen Oberfläche eine widerstandsfähige lokale Kultur, einen lebhaften Graumarkt und wichtige Verbindungen zu Triaden und Telesmahändlern.",
    "The Towers": "Die drei ehemaligen Fuchi-Türme sind der irdische Hauptsitz des Konzerngerichtshofs und gelten nach ihrer Sanierung als eines der am stärksten gesicherten Konzernareale der Welt.",
    "Battery City": "Battery City am Südende dient vor allem als enges Wohngebiet für kulturelle und blaukragengeprägte Konzernarbeitskräfte, deren Hausgemeinschaften eine ungewöhnlich starke lokale Identität entwickelt haben.",
    "New York Harbor Islands": "Die Hafeninseln bilden getrennte Konzernräume: Governors Island ist ein Ares-Ausbildungs- und Testgelände, während Horizon Ellis und Liberty Island zum Virtual World Liberty Park umbaut.",
    "Roosevelt Island": "Roosevelt Island heißt inzwischen Penitentiary Island und trägt Manhattans Gefängnisse mittlerer bis maximaler Sicherheitsstufe, geschützt durch Zäune, Drohnen, Geister und Brückenstellungen.",
    "Randall’s and Ward’s Islands": "Randall’s Island beherbergt Gefängnisse niedrigerer und mittlerer Sicherheitsstufe; das durch Aufschüttung verbundene Ward’s Island dient Horizon als Rehabilitations- und Psychiatriezentrum.",
}

MANHATTAN_SR4_PLACES = {
    "Inwood": ["Inwood"],
    "Washington Heights": ["Washington Heights"],
    "New Harlem": ["Newtown"],
    "Upper West Side": ["Riverside", "Freedom Tunnel", "Prometheus Spire", "MDC Building", "FDR Drive", "Sea of Fools"],
    "Randalls Island": ["Randall’s and Ward’s Islands"],
    "Central Park": ["Central Park", "Belvedere Castle", "Obelisk"],
    "Midtown": ["Theater District", "Museum of Modern Art", "Grand Central", "Penn Station", "Some Assembly Required", "Zoé"],
    "Lower East Side": ["Eleemosynary Children’s Clinic", "Roosevelt Island", "Pizza Now"],
    "Times Square": ["Times Square", "Neon City"],
    "Downtown": ["Empire State Building", "Bowling Green", "Waldorf-Astoria", "Choke Points", "Apple Press", "Firesale"],
    "Stuyvesant": ["Stuyvesant"],
    "Terminal": ["Terminal"],
    "Southside": ["The Marquee", "Corson Place Hotel"],
    "Villages": ["Washington Square Park / NYCU Campus", "The Cypress Tree"],
    "Heritage": ["The Pit", "Orchard Street", "C-Squat"],
    "SoHo": ["SoHo", "Saints and SINners"],
    "City Center": ["The Towers", "City Center", "East Coast Stock Exchange", "Frankfurt Bank Association"],
    "Chinatown": ["Chinatown", "Lucky Star 99"],
    "Battery City": ["Battery City", "The Green Building", "Castle Clinton"],
    "Manhattan": ["The Underground", "Night Markets"],
}

MANHATTAN_MAP_PLACES = [
    ("Flughafen La Guardia", "Manhattan"),
    ("Governors Island", "Governors Island"),
    ("Randalls Island", "Randalls Island"),
    ("Grand Central Station und Arkologie", "Midtown"),
    ("Penn Station", "Midtown"),
    ("Lincoln Center", "Upper West Side"),
    ("Sylvia’s", "New Harlem"),
    ("Sony Plaza", "Midtown"),
    ("Tough Tony’s", "Midtown"),
    ("Al-Hazad’s House of Wonders", "Midtown"),
    ("Shogunate Club", "Midtown"),
    ("Vibe", "Midtown"),
    ("Heritage House", "Heritage"),
    ("Goldwater Club", "Manhattan"),
    ("Railspur-Apartments", "Manhattan"),
    ("Hudson Pawn", "Manhattan"),
    ("Mitsuhama-Arkologie", "New Harlem"),
    ("Dump Sh0ck", "Manhattan"),
    ("Nowhere", "Terminal"),
    ("Kente Royal Gallery", "New Harlem"),
    ("Alice-in-Wonderland-Spielplatz", "Central Park"),
    ("NYPD-Revier 10", "Lower East Side"),
    ("Corner Swing", "Manhattan"),
    ("Columbia University", "Washington Heights"),
    ("Knickerbocker Club", "Manhattan"),
    ("Bailey’s Pub", "Manhattan"),
    ("Das Oktagon", "Manhattan"),
    ("Lagerhaus von Ilhuicaatl Holdings", "Manhattan"),
    ("Union Square", "City Center"),
]

MANHATTAN_SR6_EXTRA = {
    "Lower East Side": ["Fluffy Duck’s Gourmet Chicken Bisquits", "Arcanna’s Cabana", "Quik-E-Nap", "U-Bahnhof an der 18th Street"],
    "New Harlem": ["Shibata Consulting", "Fundament-Archiv", "Nullknoten"],
    "Villages": ["Blind Pig", "Virtueller Aufenthaltsraum der NYU Medical School", "NYU Medical School"],
    "City Center": ["Commerzbank-Café", "44 Union Square"],
    "Manhattan": ["Animus Construction: Clinical Operations", "Topside", "Die Metaebene von Dis", "Die Fabrik"],
    "Governors Island": ["Die Höhlen", "Die Luftschleuse"],
}

MANHATTAN_PEOPLE_SR6 = [
    ("Abyssa", "Drachin und Machtakteurin", "Erwachte"),
    ("Becky Wu Ping", "Galeristin und Informationsquelle", "Kente Royal Gallery"),
    ("Carol “Cat” McTavish", "Fixerin und Johnson", "Schatten"),
    ("Donovan James Eastling (DJ)", "Konzernakteur", "Manhattan"),
    ("Eager", "Runner und Kontakt", "Schatten"),
    ("El Guapo (Jay Houston)", "Unterweltkontakt", "Manhattan"),
    ("Fluffy Duck", "Gastronom und Kontakt", "Fluffy Duck’s Gourmet Chicken Bisquits"),
    ("Gerald Ramius (Gramius)", "Konzern- und Forschungsakteur", "Manhattan"),
    ("Gu Guanyu", "Unterweltakteur", "Triaden"),
    ("Hadrian Williams-Lee", "Galerie- und Konzernkontakt", "Manhattan"),
    ("Indica Meiers", "Journalistin und Informationsquelle", "Freie Presse"),
    ("Jonathan Blake", "Konzernakteur", "Manhattan"),
    ("Malcolm Jamal Sutton", "Auftraggeber und lokaler Kontakt", "Manhattan"),
    ("MCT-Monadenjäger", "Spezialeinheit", "Mitsuhama", "group"),
    ("Die Nullsekte", "Matrix- und Monadengruppe", "Nullsekte", "group"),
    ("Piper Jane", "Journalistin", "Unabhängige Presse"),
    ("Rikki Nguyen", "Lokaler Akteur", "Manhattan"),
    ("Silver Nail", "Runner und Fahrer", "Schatten"),
    ("Spyder", "Informationsspezialist", "Schatten"),
    ("Sully", "Lokaler Akteur", "Manhattan"),
    ("Vida Nova", "Monade und Konzernakteurin", "Evo"),
]

MANHATTAN_GROUPS_SR6 = [
    ("Toki-gumi", "Yakuza-Syndikat"),
    ("Honjowara-gumi", "Yakuza-Syndikat"),
    ("Grüne Schlangengarde", "Yakuza-nahe Gruppe"),
    ("Oni Do Kai", "Attentätergruppe"),
    ("Young Dragons", "Yakuza-nahe Jugendgang"),
    ("Honor Society", "Yakuza-nahe Jugendgang"),
    ("Großer-Kreis-Liga", "Triade"),
    ("Bund des Roten Drachen", "Triade"),
    ("Min-Park-Ring", "Seoulpa-Ring"),
    ("Gangjun-Ring", "Seoulpa-Ring"),
    ("Yeong-Ring", "Seoulpa-Ring"),
    ("Ancients", "Straßengang"),
    ("Slaughterhouse", "Straßengang"),
    ("Battery Boys", "Straßengang"),
    ("Axemen", "Straßengang"),
    ("Cutters", "Gang und Syndikat"),
]

MANHATTAN_MAGIC_GROUPS = [
    "Illuminates of the New Dawn", "Magical Investors Group", "Ordo Maximus",
    "Dunkelzahn-Institut für Magische Forschung", "Gesellschaft der Falken",
    "Der Heilige Orden des Heiligen Franziskus", "Donnervogel-Vorhut",
]

MANHATTAN_SR1_DISTRICT_SUMMARIES = {
    "Inwood": "Inwood bildet 2050 den dünner bebauten Nordrand Manhattans mit überwiegend niedrigen Wohnhäusern und einer deutlich geringeren Konzernpräsenz als Midtown.",
    "Washington Heights": "Washington Heights gehört zum nördlichen Wohnband der Insel und liegt außerhalb des glitzernden Konzernkerns.",
    "Newtown": "Newtown ersetzt das weitgehend ausgelöschte Harlem durch neu errichtete Wohnquartiere; Apollo Theater, Cloisters und Columbia bewahren einzelne historische und kulturelle Anker.",
    "Westside": "Die Westside ist ein teures Wohngebiet für Konzernangestellte entlang des Hudson mit einzelnen aus Midtown übergreifenden Geschäftstürmen.",
    "Upper Eastside": "Die Upper Eastside ist ein gehobenes Wohngebiet; an ihrer Ostkante liegt Gracie Mansion als stark bewachter Amtssitz des Bürgermeisters.",
    "Central Park": "Die Wohnstreifen östlich und westlich des Central Park sind 2050 den reichsten und einflussreichsten Einwohnern vorbehalten und werden extrem dicht überwacht.",
    "Midtown": "Midtown ist 2050 das monumentale Konzernzentrum New Yorks mit Skyrakern, Arkologien, exklusiven Clubs und der höchsten Dichte multinationaler Niederlassungen.",
    "Times Square": "Times Square konzentriert Theater und Hochkultur, während Neon City eine kontrollierte, stark gesicherte Simulation des Rotlicht- und Unterhaltungsviertels bietet.",
    "Lower Westside": "Die Lower Westside fällt vom Reichtum Midtowns zu dichtem Wohnen, Hafenanlagen und Gangterritorien am Rand von Terminal ab.",
    "Terminal": "Terminal bündelt Penn Station und Port Authority, billige Unterkünfte, Schwarzmärkte und fast tägliche Straßengewalt hinter kontrollierten Chokepoints.",
    "Stuyvesant": "Stuyvesant besteht 2050 fast ausschließlich aus niedrig bebauten Einzelresidenzen der reichen und ultrareichen Oberschicht.",
    "The Village": "The Village verkauft eine bereinigte und teure Version seiner früheren Gegenkultur mit Galerien, Buchläden, Lofts und nächtlichen Modegruppen.",
    "The Pit": "Die Lower East Side beziehungsweise The Pit ist eine weitgehend aufgegebene Z-Zone, in der Gangs und Straßenregeln die staatliche Ordnung ersetzen.",
    "SoHo": "SoHo bewahrt im Gegensatz zum Village eine glaubwürdigere Kunst- und Subkultur und beherbergt hinter geschlossenen Fassaden mehrere magische Orden.",
    "Southside": "Southside mischt Gewerbe, Wohnen und Hafenanlagen; im Norden liegt ein elfenstämmiges Viertel, das von Ancients und Axemen umkämpft wird.",
    "City Center": "City Center enthält Rathaus, Gerichte, UCAS-Behörden und diplomatische Einrichtungen außerhalb der exklusivsten Konzernzonen.",
    "Chinatown": "Chinatown hält an eigener Bauweise und Kultur fest, widersetzt sich Aufkäufen durch Konzerne und leidet unter zahlreichen Jugendgangs.",
    "The Towers": "Fuchi-Town erhebt sich 2050 als dreiteiliger, schwarzer Arkologiekomplex auf den Ruinen des World Trade Center und steht vollständig unter Fuchi-Recht.",
    "Battery City": "Battery City ist ein verarmtes Wohngebiet am Südende Manhattans und festes Revier der Battery Boys.",
    "New York Harbor Islands": "Governors Island dient 2050 als stark bewaffneter Port-Authority-Komplex; die übrigen Hafeninseln bleiben wichtige Zugangspunkte und Symbole der Stadt.",
    "Roosevelt Island": "Roosevelt Island wird als Penitentiary Island für Haftanstalten mittlerer bis höchster Sicherheitsstufe genutzt.",
    "Randall’s and Ward’s Islands": "Randall’s Island beherbergt 2050 Manhattans Gefängnisse niedrigerer und mittlerer Sicherheitsstufe.",
}

MANHATTAN_SR5_DISTRICT_SUMMARIES = {
    "Inwood": "Inwood ist 2076 nach einem Stadterneuerungsprogramm eine scheinbar idyllische, flächendeckend überwachte Wohnlage für die wohlhabende Elite.",
    "Washington Heights": "Washington Heights bleibt ein Wohn- und Klinikbezirk mittlerer Sicherheitsstufe, in dem soziale Spannungen und antikonzernliche Aktivitäten wachsen.",
    "Newtown": "Newtown ist das konzerngeprägte Nachfolgeviertel Harlems; Zwangsräumungen und neue Luxusarkologien verstärken den neo-anarchistischen Widerstand.",
    "Westside": "Westside ist ein hochpreisiges Wohngebiet für einflussreiche Konzernbürger und wird je nach Teilgebiet von NYPD und Knight Errant geschützt.",
    "Upper Eastside": "Die Upper Eastside verbindet elitäres Wohnen mit dem MDC-Gebäude und weiteren politischen sowie wirtschaftlichen Machtzentren.",
    "Central Park": "Central Park und seine Luxuswohnungen bilden 2076 eine der teuersten Wohnlagen der Welt; Shiawase pflegt den Park unter engmaschiger NYPD-Überwachung.",
    "Midtown": "Midtown ist ein dichter Irrgarten konkurrierender exterritorialer Konzernflächen, Arkologien, Theater und Verkehrsknoten.",
    "Times Square": "Times Square bleibt eine streng gesicherte Theater- und Werbezone, in der Konzerne Unterhaltung, Tourismus und öffentliche Wahrnehmung kontrollieren.",
    "Lower Westside": "Die Lower Westside nimmt verdrängte Mittel- und Geringverdiener auf und leidet unter Überbelegung, Identitätsdiebstahl und Kämpfen zwischen mehreren Gangs.",
    "Terminal": "Terminal ist eine von Winter Systems abgeschottete Armuts- und Transitregion mit Sarghotels, Schmuggel und einem großen Anteil SINloser Bevölkerung.",
    "Stuyvesant": "Stuyvesant bleibt ein streng geschütztes Villen- und Luxuswohngebiet für die wohlhabendsten Bewohner Manhattans.",
    "The Village": "The Village ist ein kommerzialisierter Kulturbezirk mit teurem Wohnen, Gastronomie und einer weitgehend konzernverträglichen Bohème.",
    "The Pit": "Die Grube ist 2076 eine teilweise aufgegebene C- bis Z-Zone, in der Gangs, Neo-Anarchisten und Syndikate große Teile des Alltags bestimmen.",
    "SoHo": "SoHo verbindet Galerien, gehobene Subkultur und magische Geschäfte mit einem weiterhin sichtbaren lokalen Widerstand gegen vollständige Konzernkontrolle.",
    "Southside": "Southside ist ein gemischtes Wohn-, Gewerbe- und Hafengebiet mit wachsender Kriminalität und mehreren konkurrierenden Sicherheitsinteressen.",
    "City Center": "City Center bündelt Rathaus, Gerichte, NYPD-Hauptsitz, Botschaften und die East Coast Stock Exchange.",
    "Chinatown": "Chinatown bewahrt sein kulturelles Profil, während Glücksspiel, Schwarzmarkt, Skimmer und die Große-Kreis-Liga das kriminelle Umfeld prägen.",
    "The Towers": "Die sanierten ehemaligen Fuchi-Türme beherbergen 2076 den terrestrischen Konzerngerichtshof und die weltweit wohl stärkste Gebäudesicherheit.",
    "Battery City": "Battery City wird zum überfüllten Auffanggebiet für verdrängte Arbeiter- und Mittelschichtshaushalte und bleibt Territorium der Battery Boys.",
    "New York Harbor Islands": "Governors Island gehört Ares; Ellis und Liberty Island bilden Horizons Virtual World Liberty Park mit Museum, Freizeitpark und unterirdischer Schnellbahn.",
    "Roosevelt Island": "Roosevelt Island ist weiterhin Gefängnisinsel und zusätzlich Standort von Internierungseinrichtungen für KFS-Fragmentierte.",
    "Randall’s and Ward’s Islands": "Randall’s Island trägt Gefängnis- und Konzernanlagen, während Ward’s Island mit dem Horizon Rehabilitation and Psychiatric Center verbunden ist.",
}

MANHATTAN_SR1_PLACES = [
    ("The Cloisters", "Inwood", "Bildung und Kultur", "The Cloisters beherbergt mittelalterliche Kunst und dient den Children of the New Crusade zugleich als Wohn-, Arbeits- und Ritualort."),
    ("Apollo Theater", "New Harlem", "Bildung und Kultur", "Das Apollo Theater wurde als einer der wenigen kulturellen Anker Harlems beim Aufbau von Newtown erhalten."),
    ("Columbia University", "Washington Heights", "Bildung und Kultur", "Columbia University überstand das Beben teilweise und ist 2050 besonders für Geisteswissenschaften, Wirtschaftsrecht und Parapsychologie bekannt."),
    ("US Tower", "Midtown", "Konzerne", "Der US Tower gehört zu den markanten Konzernhochhäusern am Nordrand des Central Park."),
    ("Sony Dataworks", "Midtown", "Konzerne", "Sony Dataworks unterhält 2050 einen bedeutenden Komplex an der Fifth Avenue."),
    ("Netlink", "Midtown", "Konzerne", "Netlink zählt zu den großen Daten- und Kommunikationskonzernen im Midtown-Korridor."),
    ("UCAS Data Systems", "Midtown", "Konzerne", "UCAS Data Systems besitzt 2050 einen wichtigen Midtown-Standort nahe Park Avenue."),
    ("Villiers International", "Midtown", "Konzerne", "Villiers International ist mit einem hochrangigen Konzernkomplex in Midtown vertreten."),
    ("Saeder-Krupp Midtown", "Midtown", "Konzerne", "Saeder-Krupp betreibt 2050 einen großen Midtown-Komplex an Third Avenue und East 72nd Street."),
    ("Ares Macrotech Midtown", "Midtown", "Konzerne", "Ares Macrotech liegt 2050 am südwestlichen Rand des Central Park."),
    ("Aztechnology Midtown", "Midtown", "Konzerne", "Aztechnology unterhält 2050 einen repräsentativen Konzernstandort an Fifth Avenue."),
    ("Eastern Financial", "Midtown", "Konzerne", "Eastern Financial gehört zu den prägenden Finanzkonzernen des Midtown-Kerns."),
    ("Kesai & Wilhelm", "Midtown", "Konzerne", "Kesai & Wilhelm ist 2050 mit einem Midtown-Hochhaus nahe Columbus Avenue vertreten."),
    ("TransOrbital Midtown", "Midtown", "Konzerne", "TransOrbital besitzt 2050 einen wichtigen Standort im südlichen Midtown."),
    ("Lincoln Center", "Upper West Side", "Bildung und Kultur", "Das Lincoln Center bündelt klassische Kultur und moderne japanisch gestützte Produktionen, darunter Metropolitan Opera und Kobo Playhouse."),
    ("Manhattan Club", "Central Park", "Bars und Clubs", "Der Manhattan Club ist ein exklusiver Mitgliederclub für die politischen und wirtschaftlichen Entscheidungsträger der Stadt."),
    ("Prometheus Spire", "Upper West Side", "Konzerne", "Die spiralförmige Prometheus-Arkologie verbindet Forschung, Büros und abgeschirmte Wohnbereiche in einem ungewöhnlichen Hochhaus."),
    ("MDC Building", "Upper East Side", "Politik und Verwaltung", "Am späteren Standort des MDC-Gebäudes liegt 2050 Gracie Mansion, der stark bewachte Amtssitz des Bürgermeisters."),
    ("Port Authority Transit Terminal", "Terminal", "Verkehr", "Das Port Authority Transit Terminal ist einer der beiden wichtigsten Ankunftspunkte für die ärmere Pendler- und Besucherbevölkerung."),
    ("Penn Station", "Midtown", "Verkehr", "Penn Station verbindet PATH-, Fern- und Vorortlinien und bildet zusammen mit Port Authority den Kern von Terminal."),
    ("Grand Central", "Midtown", "Verkehr", "Grand Central dient den wohlhabenderen Reisenden als kontrollierter Verkehrsknoten außerhalb der schlimmsten Terminal-Zonen."),
    ("Empire State Building", "Downtown", "Konzerne", "Das Empire State Building war das einzige große Hochhaus, das das Beben von 2005 überstand, und besitzt weiterhin abgeschirmte obere Etagen."),
    ("The Towers", "City Center", "Konzerne", "Fuchi-Town besteht 2050 aus drei 250-stöckigen schwarzen Türmen auf den Ruinen des World Trade Center."),
    ("City Hall", "City Center", "Politik und Verwaltung", "City Hall ist der nominelle Sitz der städtischen Regierung innerhalb der von Konzernen kontrollierten Insel."),
    ("Criminal Courts", "City Center", "Sicherheit und Justiz", "Die Strafgerichte liegen gemeinsam mit weiteren UCAS- und Stadtbehörden in City Center."),
    ("Governors Island Port Authority Complex", "Governors Island", "Sicherheit und Justiz", "Governors Island ist 2050 ein bewaffneter Port-Authority-Komplex mit deutlich sichtbarer Luft- und Hafensicherung."),
]

MANHATTAN_SR1_GROUPS = [
    ("Children of the New Crusade", "Magischer Orden", "Die Children of the New Crusade besitzen The Cloisters und bewahren dort Kunst, magische Arbeitsräume und möglicherweise einen jungen östlichen Drachen."),
    ("Blood Monkeys", "Straßengang", "Die Blood Monkeys kontrollieren Teile der Lower Westside und ziehen für Raubzüge bis Downtown und Southside."),
    ("Wrathchildes", "Straßengang", "Die Wrathchildes sind eine Downtown-Gang, die regelmäßig mit Blood Monkeys und Ancients zusammenstößt."),
    ("Ancients", "Elfische Straßengang", "Die Ancients operieren von Southside und The Pit aus und gehören zu den sichtbarsten Gangs der Insel."),
    ("Axemen", "Ork- und Trollgang", "Die Axemen fordern im elfenstämmigen Norden von Southside die Ancients heraus."),
    ("Duelists", "Straßengang", "Die Duelists gehören zu den zahlreichen gewalttätigen Gangs der Lower East Side."),
    ("Merlyn’s Pride", "Straßengang", "Merlyn’s Pride ist eine der Gangs, die in The Pit nach eigenen Straßenregeln operieren."),
    ("Sisters Sinister", "Straßengang", "Die Sisters Sinister gehören zum zersplitterten Gangmilieu von The Pit."),
    ("Night-Spawn", "Straßengang", "Night-Spawn kontrolliert einen Teil der Lower East Side und beteiligt sich an den nächtlichen Revierkämpfen."),
    ("Billyboys", "Thrill-Kill-Gang", "Die Billyboys gelten als besonders unberechenbare und gewalttätige Gang in The Pit."),
    ("Battery Boys", "Straßengang", "Die Battery Boys kontrollieren Straßen, Parks und Teile des alten Tunnels in Battery City."),
]

MANHATTAN_CORPORATE_ENCLAVES_PLACES = [
    ("Matador", "Midtown", "Bars und Clubs", "Matador ist einer der angesagten Midtown-Clubs, in denen Konzernbürger Kontakte pflegen und halblegale Drogen konsumieren."),
    ("Wright’s", "Midtown", "Bars und Clubs", "Wright’s gehört zu den exklusiven Midtown-Clubs der Konzernszene."),
    ("Old Post near Penn Station", "Terminal", "Sonstige Spots", "Die alte Post nahe Penn Station ist ein lebendiger Treffpunkt von Kurieren, Dieben, Abhängigen und Neo-Anarchisten."),
]

MANHATTAN_CORPORATE_ENCLAVES_GROUPS = [
    ("Rat Pack", "Schmugglergruppe", "Das Rat Pack vermittelt illegale Wege, Waren und Personen nach Manhattan."),
    ("Janeski Vor", "Vory-Gruppe", "Die Janeski Vor in Queens besitzt Kontakte für Schmuggel und verdeckte Zugänge nach Manhattan."),
]

MANHATTAN_STOLEN_SOULS_PLACES = [
    ("East Coast Stock Exchange", "City Center", "Konzerne", "Die East Coast Stock Exchange steht am historischen Börsenplatz und betreibt einen der bestgesicherten Finanzhosts Nordamerikas."),
    ("S-K North America", "Midtown", "Konzerne", "S-K North America ist eine 175-stöckige Arkologie mit Büros zahlreicher Industrie-, Medien- und Finanzsparten."),
    ("S-K Prime", "City Center", "Konzerne", "S-K Prime gegenüber den Towers bündelt Anwälte, Lobbyisten, MDC-Angelegenheiten und einen erheblichen Teil der Schattenoperationen Saeder-Krupps."),
    ("The Towers", "City Center", "Konzerne", "Die drei sanierten Fuchi-Türme beherbergen NeoNET-Anteile und den terrestrischen Konzerngerichtshof mit extrem hoher Sicherheit."),
    ("MDC Building", "Upper East Side", "Politik und Verwaltung", "Das MDC-Gebäude besteht aus gemeinsamen Verwaltungsstockwerken, dreizehn Mitgliedstürmen und einem abgeschirmten Sitzungsgeschoss."),
    ("Malmstein Building", "Midtown", "Konzerne", "Das Malmstein Building ist NeoNETs 140-stöckiger Manhattan-Hauptsitz und wartet große Teile der lokalen Matrix- und Gerichtshofinfrastruktur."),
    ("Condatis Tower", "Midtown", "Konzerne", "Condatis Tower gehört zu den markanten Konzernwahrzeichen Manhattans und beherbergt hochrangige Unternehmensfunktionen."),
    ("Prometheus Spire", "Upper West Side", "Konzerne", "Der Prometheus Tower ist ein zentraler Forschungs- und Verwaltungsstandort von Prometheus Engineering."),
    ("Empire State Building", "Downtown", "Konzerne", "Das Empire State Building bleibt Wahrzeichen und bedeutender Bürostandort unter engmaschiger Konzernsicherheit."),
    ("NYPD, Inc. Headquarters", "City Center", "Sicherheit und Justiz", "Der Hauptsitz von NYPD, Inc. liegt in City Center und koordiniert den größten Anteil des Sicherheitsvertrags der Insel."),
    ("Grand Central", "Midtown", "Verkehr", "Grand Central ist der bevorzugte Bahn- und Stadtbahnknoten für Inhaber hochrangiger Einwohner- und Besucherpässe."),
    ("Horizon Manhattan Headquarters", "Midtown", "Konzerne", "Horizons Manhattan-Hauptsitz bündelt Medien-, Unterhaltungs- und KFS-bezogene Aktivitäten des Konzerns."),
    ("Shiawase Manhattan Arcology", "New Harlem", "Konzerne", "Shiawases Manhattan-Arkologie beherbergt Wohnungen, Büros, Forschung und umfangreiche Konzernversorgung."),
    ("Horizon Rehabilitation and Psychiatric Center", "Randalls Island", "Medizin", "Das frühere Manhattan Psychiatric Center wird von Horizon als Rehabilitations-, Psychiatrie- und Forschungsanlage betrieben."),
    ("Shiawase Bellevue Hospital", "Stuyvesant", "Medizin", "Shiawase Bellevue Hospital gehört zu den wichtigsten medizinischen Einrichtungen Manhattans und arbeitet an KFS-bezogenen Fällen."),
    ("Evo Office Complex", "Randalls Island", "Konzerne", "Evo unterhält auf Randall’s Island einen abgeschirmten Büro- und Forschungskomplex."),
    ("Rikers Island", "New York Harbor Islands", "Sicherheit und Justiz", "Rikers Island bleibt Teil des Gefängnis- und Internierungssystems der New Yorker Region."),
    ("Governors Island", "Governors Island", "Sicherheit und Justiz", "Governors Island ist Ares-exterritoriales Ausbildungszentrum für Knight Errant, Firewatch und möglicherweise Söldnereinheiten."),
    ("Liberty Island", "New York Harbor Islands", "Freizeit und Natur", "Liberty Island gehört Horizon und bildet mit Ellis Island den Virtual World Liberty Park."),
    ("Ellis Island", "New York Harbor Islands", "Bildung und Kultur", "Ellis Island wurde von Horizon restauriert und als Museum sowie Teil des Virtual World Liberty Park wiedereröffnet."),
    ("Renraku Tower", "Downtown", "Konzerne", "Der 280-stöckige Renraku Tower enthält Wohnungen, Büros, Finanzsparten und abgeschirmte Technomancer- sowie KI-Forschung."),
    ("Mitsuhama-Arkologie", "New Harlem", "Konzerne", "Die öffentlich zugänglichen Bereiche der MCT-Arkologie verdecken mutmaßliche unterirdische Technomancerforschung."),
    ("Link Club", "Times Square", "Bars und Clubs", "Der global vernetzte Link Club in Neon City bietet sichere private Räume, hat aber seinen früheren Status als Trendzentrum verloren."),
    ("!?! Club", "Central Park", "Bars und Clubs", "Der namenlose !?! Club an der West 61st Street setzt auf provokative erwachte, künstliche und technomantische Künstler."),
    ("Club Möbius", "Manhattan", "Matrix und Metaplanes", "Club Möbius ist ein nur auf Einladung zugänglicher virtueller Treffpunkt für Decker, Technomancer und KIs."),
    ("Aztechnology Pyramid", "Midtown", "Konzerne", "Die Aztechnology-Pyramide ist ein öffentlich teilweise zugänglicher Wohn-, Bildungs-, Einkaufs- und Bürokomplex in mittelamerikanischem Stil."),
    ("Wuxing Manhattan Building", "Downtown", "Konzerne", "Wuxings gold-karmesinroter Manhattan-Komplex beherbergt Finanzsparten, Ming Solutions und führende magische Forscher."),
    ("The Marquee", "Southside", "Bars und Clubs", "Das Marquee ist ein gehobener Club für erfolgreiche Konzernbürger und Prominente mit abgeschirmten VIP-Räumen."),
    ("Lucky Star 99", "Chinatown", "Einkaufen", "Lucky Star 99 ist Teehaus, Markt, Umschlagplatz illegaler Importwaren und Kontaktpunkt der Großen-Kreis-Liga."),
    ("Studio 74", "Midtown", "Bars und Clubs", "Studio 74 rekonstruiert das historische Studio 54 als Horizon-Nachtclub und Theater mit Konzerten und VIP-Suiten."),
    ("Red Light Lounge", "Downtown", "Bars und Clubs", "Die lizenzierte Red Light Lounge inszeniert Prohibitionskriminalität für zahlende Gäste und dient Konzernkontakten als diskreter Treffpunkt."),
    ("Tough Tony’s", "Midtown", "Bars und Clubs", "Tough Tony’s ist ein nur über Mafia-Verbindungen erreichbares illegales Lokal der Lucchese-Familie mit Zugang zum Untergrund."),
]

MANHATTAN_STOLEN_SOULS_PEOPLE = [
    ("Dominique Vittoria", "Ares-Managerin und frühere Manhattan-Leiterin", "Ares Macrotechnology"),
    ("Benjamin Lopez-Garcia", "MDC-Vertreter", "Aztechnology"),
    ("Madison Dover", "MDC-Vertreterin", "Citigroup"),
    ("Michael Andrews", "MDC-Vertreter", "Horizon"),
    ("Emma Porter", "MDC-Vertreterin", "NeoNET"),
    ("Mason Andersen", "MDC-Vertreter", "NYPD, Incorporated"),
    ("Ethan Miles", "MDC-Vertreter", "Prometheus Engineering"),
    ("Yutaka Taiga", "MDC-Vertreter", "Renraku"),
    ("Brent Lucas", "MDC-Vertreter", "Saeder-Krupp"),
    ("Mineyo Kotari", "MDC-Vertreterin", "Shiawase"),
    ("Junpei Sakura", "MDC-Vertreter", "Sony"),
    ("Katie Brookes", "MDC-Vertreterin", "Spinrad Industries"),
    ("Thomas Warren", "MDC-Vertreter", "Trans-Orbital"),
    ("Christopher Arkins", "MDC-Pressesprecher", "Manhattan Development Consortium"),
    ("Denise Fairborn", "MDC-Sicherheitschefin", "Manhattan Development Consortium"),
    ("David Jacobs", "Leiter der East Coast Stock Exchange", "East Coast Stock Exchange"),
    ("Thalia Falkner", "Bürgermeisterin", "Manhattan City Government"),
    ("Eric Padovano", "Stadtrat des ersten Bezirks", "Manhattan City Government"),
    ("Kathryn Gates", "Stadträtin des zweiten Bezirks", "Manhattan City Government"),
    ("Nicolas Stanford", "Stadtrat des dritten Bezirks", "Manhattan City Government"),
    ("Lucia Osgood", "Stadträtin des vierten Bezirks", "Manhattan City Government"),
    ("Viviana Hill", "Stadträtin des fünften Bezirks", "Manhattan City Government"),
    ("Abe Giordano", "Stadtrat des sechsten Bezirks", "Manhattan City Government"),
    ("Ayla Hamilton", "Stadträtin des siebten Bezirks", "Manhattan City Government"),
    ("Xarles Poirier", "Stadtrat des achten Bezirks", "Manhattan City Government"),
    ("Brian Jahnsen", "Stadtrat des neunten Bezirks", "Manhattan City Government"),
    ("Kenneth Plant", "Stadtrat des zehnten Bezirks", "Manhattan City Government"),
    ("Stephen Aachen", "Kommissarischer Leiter S-K Nordamerika", "Saeder-Krupp"),
    ("Nadine Reinhard", "Cybernetikforscherin", "Advanced Frontier Cybernetics"),
    ("René Fitzgerald", "Nanotechnologe und KFS-Forscher", "Morgen-Tek"),
    ("Maximilian Seiler", "Magischer KFS-Forscher", "Spellweaver Consortium"),
    ("Kerstin Müller", "Magische KFS-Forscherin", "Awakened World Research"),
    ("Michael Hubbard", "Cybertechnologe", "Mindstorm Neurotechnologies"),
    ("Alexandra Sosa", "Cybertechnologin", "Mindstorm Neurotechnologies"),
    ("Gifford Garceau", "Neurowissenschaftler", "Transys Neuronet"),
    ("Holly Garceau", "Neurowissenschaftlerin", "Transys Neuronet"),
    ("Aiden Howell", "Leiter Produktkontrolle Manhattan", "NeoNET"),
    ("Serrato Nevarez", "Magischer KFS-Forscher", "Mystics and Magicks"),
    ("Boleslao Roybal", "Magischer KFS-Forscher", "Mystics and Magicks"),
    ("Hui K’ung", "Magieforscher", "Ming Solutions"),
    ("Qiao Niu", "Magieforscher", "Ming Solutions"),
    ("Yue You Lu", "Magieforscher", "Ming Solutions"),
    ("Shing Hsü", "Magieforscher", "Ming Solutions"),
]

MANHATTAN_STOLEN_SOULS_GROUPS = [
    ("Manhattan Development Consortium", "Konzernkonsortium", "Das MDC besitzt und verwaltet den größten Teil Manhattans durch dreizehn stimmberechtigte Konzernmitglieder."),
    ("Carnetti Family", "Mafiafamilie", "Die Carnetti-Familie gehört zu den fünf wichtigsten Mafiafamilien New Yorks."),
    ("Colombo Family", "Mafiafamilie", "Die Colombo-Familie gehört zu den wichtigsten New Yorker Mafiaorganisationen."),
    ("Genovese Family", "Mafiafamilie", "Die Genovese-Familie ist ein bedeutendes Syndikat der New Yorker Unterwelt."),
    ("Lucchese Family", "Mafiafamilie", "Die Lucchese-Familie kontrolliert unter anderem Tough Tony’s und besitzt starke Kontakte in Häfen und Schmuggel."),
    ("Bonnano Family", "Mafiafamilie", "Die Bonnano-Familie gehört zu den etablierten Mafiafamilien der Region."),
    ("Großer-Kreis-Liga", "Triade", "Die Große-Kreis-Liga dominiert Teile Chinatowns, betreibt Glücksspiel und nutzt Lucky Star 99 als Kontaktpunkt."),
    ("Toki-gumi", "Yakuza-Syndikat", "Das Toki-gumi vertritt das Shotozumi-rengo in Manhattan."),
    ("Gangjun-Ring", "Seoulpa-Ring", "Der Gangjun-Ring zählt über 250 Mitglieder und gehört zu den größeren Seoulpa-Strukturen der Stadt."),
    ("Min-Park-Ring", "Seoulpa-Ring", "Der Min-Park-Ring ist mit rund 300 Mitgliedern der größte benannte Seoulpa-Ring Manhattans."),
    ("Yeong-Ring", "Seoulpa-Ring", "Der Yeong-Ring ist ein kleinerer, aber etablierter Seoulpa-Verbund."),
    ("Freedom Patriots", "Neo-Anarchisten-Zelle", "Freedom Patriots ist eine von den Konzernen als kriminell eingestufte Neo-Anarchisten-Zelle."),
    ("Domino Effect", "Neo-Anarchisten-Zelle", "Domino Effect führt verdeckte Aktionen gegen Konzernkontrolle und Überwachung durch."),
    ("Shatter Wave", "Neo-Anarchisten-Zelle", "Shatter Wave gehört zum zersplitterten neo-anarchistischen Netzwerk Manhattans."),
    ("Revolution Now!", "Neo-Anarchisten-Zelle", "Revolution Now! tritt offen gegen die Ordnung des MDC auf."),
    ("Fighters for Individuality and Compassion", "Neo-Anarchisten-Zelle", "Die Fighters for Individuality and Compassion verbinden antikonzernliche Politik mit lokalen Unterstützungsstrukturen."),
    ("New York Mets", "Sportmannschaft", "Die New York Mets sind Renrakus Baseballmannschaft im MDC-Sportsystem."),
    ("Manhattan Yankees", "Sportmannschaft", "Die Manhattan Yankees sind das Baseballteam von NYPD, Inc."),
    ("Brooklyn Giants", "Sportmannschaft", "Die Brooklyn Giants gehören Horizon."),
    ("New York Jets", "Sportmannschaft", "Die New York Jets gehören Citigroup."),
    ("Manhattan Islanders", "Sportmannschaft", "Die Manhattan Islanders sind das Hockeyteam von Prometheus Engineering."),
    ("New York Rangers", "Sportmannschaft", "Die New York Rangers gehören Shiawase."),
    ("The Quake", "Sportmannschaft", "The Quake ist Sonys Hurling-Team."),
    ("New York Nets", "Sportmannschaft", "Die New York Nets sind NeoNETs Basketballmannschaft."),
    ("Lightning", "Sportmannschaft", "Lightning ist das Fußballteam von Saeder-Krupp."),
    ("New York Marauders", "Sportmannschaft", "Die New York Marauders fahren Combatbiking für Spinrad."),
    ("New York Slashers", "Sportmannschaft", "Die New York Slashers sind Ares’ Urban-Brawl-Team."),
    ("Manhattan Kraak", "Sportmannschaft", "Manhattan Kraak tritt im Urban Brawl für Trans-Orbital an."),
    ("The Warriors", "Sportmannschaft", "The Warriors vertreten Aztechnology im Court Ball."),
]

MANHATTAN_SRM03_PLACES = [
    ("MDC Matrix Node", "Manhattan", "Matrix und Metaplanes", "Der zentrale MDC-Knoten verwaltet Zugangs-, Verwaltungs- und Konzerninformationen und ist wiederholt Ziel der dritten Missionsstaffel.", "Everyone’s Your Friend"),
    ("Museum of Modern Art", "Midtown", "Bildung und Kultur", "Das Museum of Modern Art ist Schauplatz des Diebstahls der transgenen Installation Starry Night.", "Ready, Set, Gogh!"),
    ("Deltona’s Penthouse", "Midtown", "Hotels", "Gary Deltonas Penthouse beherbergt seine private Sammlung transgener Kunst und wird Ziel eines zweiten Einbruchs.", "Ready, Set, Gogh!"),
    ("Ignensys Office", "Downtown", "Konzerne", "Die Büros von Ignensys sind Ziel einer verdeckten Sabotageaktion im Konkurrenzkampf kleiner Manhattan-Unternehmen.", "Block War"),
    ("Corson Place Hotel", "Southside", "Hotels", "Das Corson Place Hotel stellt Konferenzräume für kurzfristige Geschäftstreffen und dient Klubbs als neutraler Treffpunkt.", "Block War"),
    ("Free Your Mind", "Manhattan", "Einkaufen", "Free Your Mind ist Peace Mans New-Age-, Telesma- und Headshop und ein Ausgangspunkt mehrerer Aufträge.", "Burning Bridges"),
    ("Inara Indian Restaurant", "Manhattan", "Restaurants", "Das Inara Indian Restaurant in Brooklyn dient Karl Gahley und seinem Team als Treffpunkt.", "Burning Bridges"),
    ("Brooklyn Bridge", "Manhattan", "Verkehr", "Die Brooklyn Bridge ist Ziel eines Sabotageplans, der einen Neubauvertrag erzwingen soll.", "Burning Bridges"),
    ("KG Construction", "Manhattan", "Konzerne", "KG Construction lagert die Sprengstoffe, die Karl Gahley gegen die Brooklyn Bridge einsetzen lassen will.", "Burning Bridges"),
    ("Scientia Labs", "Midtown", "Konzerne", "Scientia Labs an der Tenth Avenue beherbergt Horizon Project Paracelsus, eine Ares-Anlage und den KI-Akteur Phrex.", "Monkeywrench"),
    ("NYPD, Inc. Holding Facility", "Randalls Island", "Sicherheit und Justiz", "Die Haftanlage von NYPD, Inc. auf Randall’s Island ist Ziel einer verdeckten Kontakt- und Befreiungsoperation.", "In and Out"),
    ("Some Assembly Required", "Midtown", "Restaurants", "Some Assembly Required ist eine kleine Restaurantkette, die im Streit um Karl und Anna Gahley unter Druck gerät.", "In and Out"),
    ("Throgs Neck Tunnel", "Manhattan", "Verkehr", "Der stillgelegte Throgs Neck Tunnel unter der Bronx ist eine matrixfreie Gangzone und Schauplatz eines Überfalls auf einen Transport.", "Jackknifed!"),
    ("Metropolitan Opera House", "Upper West Side", "Bildung und Kultur", "Die Metropolitan Opera im Lincoln Center wird Schauplatz der Entführung von Damien Knight während einer Premiere.", "Knight at the Opera"),
    ("Staten Island Safehouse", "Manhattan", "Sonstige Spots", "Ein privates Safehouse auf Staten Island dient während der Entführung Damien Knights als Zwischenstation.", "Knight at the Opera"),
    ("Central Park Aqueduct Squat", "Central Park", "Sonstige Spots", "Ein verborgener Squat in alten Wasseranlagen unter dem Central Park bildet den Kern des Firestorm-Schauplatzes.", "Firestorm"),
    ("Guggenheim Museum", "Upper East Side", "Bildung und Kultur", "Das Guggenheim wird während einer Ausstellungseröffnung von belebten Statuen und einer außer Kontrolle geratenen Performance heimgesucht.", "Something Completely Different"),
    ("Canaan-on-the-Water", "Manhattan", "Matrix und Metaplanes", "Canaan-on-the-Water ist der metaplanare Zielraum der Astralqueste gegen Mister Dada.", "Something Completely Different"),
    ("Jordan Aerodynamics Building", "Terminal", "Konzerne", "Das aufgegebene Jordan-Aerodynamics-Gebäude verbirgt ein CIA- und Ares-Projekt mit insektoiden Geistern hinter einer Gangfassade.", "Spin Control"),
    ("Pulaski FTC Soyosset Facility", "Manhattan", "Konzerne", "Pulaski Food Technology betreibt nördlich der Stadt eine Produktions- und Forschungsanlage, in der Kenji Vlastimil versteckt wird.", "Food Poisoning"),
    ("Meyerson Building", "Downtown", "Konzerne", "Das Meyerson Building beherbergt Secure Data Storage und belastende Daten über das vergiftete Nahrungsmittelprojekt.", "Food Poisoning"),
    ("Secure Data Storage", "Downtown", "Matrix und Metaplanes", "Secure Data Storage ist ein unabhängiger Langzeit-Datenspeicher im Meyerson Building.", "Food Poisoning"),
]

MANHATTAN_SRM03_GROUPS = [
    ("Switchblades", "Verdeckte Militäreinheit", "Die scheinbare Terminal-Gang Switchblades tarnt UCAS Army Rangers, die das geheime Jordan-Aerodynamics-Projekt sichern."),
    ("Kings", "Straßengang", "Die Kings kontrollieren ein Ganggebiet in Terminal und handeln mit gefälschten Identitäten."),
    ("Tridents", "Straßengang", "Die Tridents gehören zu den konkurrierenden Terminal-Gangs rund um das Jordan-Aerodynamics-Gebäude."),
    ("Slaughterhouse", "Straßengang", "Slaughterhouse ist die größte lokale Gang des untersuchten Terminal-Gebiets und arbeitet mit Tamanous zusammen."),
    ("Sharks", "Straßengang", "Die Sharks kontrollieren Teile des alten Throgs Neck Tunnel."),
    ("The Minibosses", "Chaosmagier-Gruppe", "Die Minibosses inszenieren im Guggenheim eine magische Performance, die außer Kontrolle gerät."),
]

MANHATTAN_BLOODY_BUSINESS_PLACES = [
    ("Rocket Records Manhattan Office", "Midtown", "Konzerne", "Rocket Records dient Johnny Spinrad als Ausgangspunkt für seine Manhattan-Verhandlungen und die anschließende Benefizveranstaltung."),
    ("Belvedere Castle", "Central Park", "Magie und Religion", "Belvedere Castle beherbergt eine Benefizveranstaltung und den Hauptsitz der Gesellschaft des Falken."),
    ("Arcanum Manhattan", "Midtown", "Konzerne", "Das Arcanum in Midtown wird Schauplatz einer Operation gegen den Verzauberer Kilian Lester inmitten zahlreicher exterritorialer Korridore."),
]

MANHATTAN_BLOODY_BUSINESS_PEOPLE = [
    ("Johnny Spinrad", "Konzernchef und Auftraggeber", "Spinrad Industries", "Johnny Spinrad reist für Verhandlungen und eine Benefizveranstaltung nach Manhattan und beschäftigt dafür ein Runnerteam als Schutz."),
    ("Kilian Lester", "Verzauberer und Zielperson", "Arcanum", "Kilian Lester ist ein orkischer Verzauberer und Ziel einer verdeckten Austauschoperation im Manhattan-Arkanum."),
    ("Jayden Riley", "Auftraggeber unter falscher Identität", "Manadyne", "Jayden Riley steuert eine Reihe von Aufträgen und schickt das Team für den Abschluss nach Manhattan."),
]


CAST_STOPWORDS = {
    "AFTERMATH", "CAST OF SHADOWS", "PICKING UP THE PIECES", "LEGWORK", "DEBUGGING",
    "GEAR", "WEAPONS", "QUALITIES", "SKILLS", "ACTIVE SKILLS", "KNOWLEDGE SKILLS",
    "CONDITION MONITOR", "ARMOR", "INITIATIVE", "MATRIX", "PHYSICAL", "MENTAL",
    "SOCIAL", "EDGE", "ESSENCE", "MOVEMENT", "CONTACTS", "NOTES", "KARMA",
    "FALSE FLAG", "RIPPING REALITY", "SERRATED EDGE", "BLOCK WAR", "PERSONAL INFO",
    "VALIDATION", "DESSERTS", "ENTREES", "SALADS", "BACKGROUND", "VENGEANCE",
}

CAST_FORBIDDEN_WORDS = {
    "after", "aftermath", "adventure", "and", "arrival", "arrive", "arrives", "at",
    "awarding", "background", "before", "begin", "begins", "current", "debriefing",
    "did", "edition", "facility", "for", "garage", "got", "guards", "guard", "have",
    "house", "in", "location", "money", "of", "outskirts", "pieces", "players",
    "patrols", "priests", "ready", "reach", "rifts", "rules", "scenarios", "shattered",
    "someone", "those", "their", "this", "to", "tower", "validation", "warned", "week",
    "what", "when", "where", "wildlife", "with", "won", "you", "minibosses", "biodrones",
    "rangers", "drone", "gangers", "contacts", "items", "gained", "lost", "info",
    "behind", "cards", "choice", "commlink", "cyberware", "finale", "explanation",
    "hooks", "hospitality", "locals", "opportunity", "other", "picking", "player",
    "plot", "programs", "security", "setup", "snipers", "spell", "spells", "statement",
    "step", "southern", "system", "matrix", "basic", "flood", "hard", "broken",
    "realm", "businesses", "toys", "lunch", "november", "ground", "something",
    "jackknifed", "operator", "host", "topography", "event", "synopsis", "handouts",
    "legwork", "destroyed", "raises", "relax", "amusing", "celebration", "crash",
    "party", "conference", "earlier", "today", "during", "destruction", "inside",
    "outside", "searching", "side", "marks", "up", "point",
}

TOC_CAST_GENERIC = {
    "mr. johnson", "mafia thugs", "rmd corporate hacker", "typical css guard",
    "css security mage", "typical gang member", "mossberg super shorty assault shotgun",
    "prisoners", "gangers", "thug/enforcer", "front lieutenant", "lone star mage",
    "lone star swat", "yakuza guards", "casquilho agents", "dwarf drone rigger",
    "ork bodyguards", "human mage", "human kick artist", "brent’s guards", "the emts",
    "typical gangers", "feral ghouls", "doc wagon htr team", "ghoul enforcers", "triad",
    "triad riggers", "home guard", "lonestar", "squad member", "lonestar mage",
    "lonestar swat", "vory enforcer one", "vory enforcer two", "ghoul mage", "smugglers",
    "vory mage trainee", "house guards", "mafia security hackers", "mafia agents",
    "yakuza thugs", "triad bodyguards", "koshari soldiers", "typical ganger",
}

TOC_CAST_GROUPS = {
    "the black cats", "irina’s neo-fascists", "blood and mayhem", "h-team",
    "tamanous", "fronts", "base-13", "lin’s assassins", "triad emissaries",
    "vory v zakone",
}


def extract_toc_cast_names(path: Path) -> list[tuple[str, str]]:
    """Read the compact Cast of Shadows list printed in SRM02 contents."""
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()[:220]
    try:
        start = next(index for index, line in enumerate(lines) if "CAST OF SHADOWS" in line.upper())
    except StopIteration:
        return []
    raw_entries = []
    buffer = ""
    for raw in lines[start + 1:]:
        line = re.sub(r"\s+", " ", raw.strip())
        if not line:
            continue
        if "CREDITS" in line.upper() or line.upper() in {"WRITER", "ART"}:
            break
        buffer = f"{buffer} {line}".strip()
        if re.search(r"(?:\.{2,}|\s)\d+\s*$", line):
            raw_entries.append(buffer)
            buffer = ""
    results = []
    for raw in raw_entries:
        candidate = re.sub(r"\.{2,}\s*\d+\s*$", "", raw).strip()
        candidate = re.sub(r"\s+\d+\s*$", "", candidate).strip()
        candidate = re.sub(r"\s*\([^)]*\)\s*", " ", candidate).strip()
        candidate = re.sub(r"\s+", " ", candidate)
        candidate = re.sub(r"^SOTTOCAPO\s+O\s*MAR\s+CHAVEZ$", "OMAR CHAVEZ", candidate, flags=re.I)
        candidate = re.sub(r"^SOTTOCAPO\s+O\s*MAR\s+", "", candidate, flags=re.I)
        candidate = re.sub(r"^SOTTOCAPO\s+", "", candidate, flags=re.I)
        candidate = re.sub(r",\s*(?:MAFIA ENFORCER|SOLDIER)\s*$", "", candidate, flags=re.I)
        candidate = candidate.replace("YOSHIRO- SAN", "YOSHIRO-SAN")
        if (
            not candidate
            or candidate.casefold() in TOC_CAST_GENERIC
            or "@" in candidate
            or candidate.casefold().startswith(("find us online", "303 91st ave"))
        ):
            continue
        candidate = candidate.rstrip(" .")
        if len(candidate) > 65 or any(word in candidate.upper() for word in ("CREDITS", "DEVELOPER", "PROOFREADER")):
            continue
        display = candidate.title().replace("’S", "’s").replace("'S", "'s")
        display = re.sub(r"\bMc([a-z])", lambda match: "Mc" + match.group(1).upper(), display)
        entity_type = "group" if candidate.casefold() in TOC_CAST_GROUPS else "person"
        results.append((display, entity_type))
    return list(dict.fromkeys(results))


def extract_cast_names(path: Path) -> list[str]:
    """Conservatively collect prominent all-caps Cast of Shadows headings."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    marker = text.upper().find("CAST OF SHADOWS")
    if marker < 0:
        return []
    lines = text[marker:].splitlines()
    results = []
    for index, raw in enumerate(lines):
        candidate = re.sub(r"\s+", " ", raw.strip())
        candidate = re.sub(r"^O\s+(?=[A-Z])", "", candidate)
        candidate = re.split(r"\s+-\s+(?=(?:MALE|FEMALE)\b)", candidate, maxsplit=1)[0]
        candidate = candidate.rstrip(" ,")
        if not candidate or candidate in CAST_STOPWORDS or len(candidate) > 62:
            continue
        if candidate.startswith(("(", ">>", "•", "-", "“")) or candidate.endswith((":", "–", "...", "?")):
            continue
        if any(char.isdigit() for char in candidate):
            continue
        letters = [char for char in candidate if char.isalpha()]
        if len(letters) < 4 or not all(char.isupper() for char in letters):
            continue
        words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ’']+", candidate.casefold())
        if len(words) > 6 or any(len(word) == 1 for word in words):
            continue
        if set(words) & CAST_FORBIDDEN_WORDS:
            continue
        following = " ".join(lines[index + 1:index + 7])
        if sum(char.islower() for char in following) < 45:
            continue
        identity_tokens = [
            word for word in words
            if word not in {"the", "a", "an", "dr", "lt", "colonel", "general", "chief", "mr", "mrs", "ms"}
        ]
        if not identity_tokens:
            continue
        prose_start = re.sub(r"[^a-z0-9’']+", " ", following.casefold()).strip()[:180]
        if identity_tokens[0] not in prose_start:
            continue
        if any(word in candidate for word in ("SHADOWRUN", "MISSION", "TABLE", "CREDITS", "CHARACTER")):
            continue
        results.append(candidate.title().replace("’S", "’s").replace("'S", "'s"))
    return list(dict.fromkeys(results))

DENVER_CAST_EXCLUDE = {
    "add-elf-metatype-adjustments", "add-ork-metatype-adjustments", "add-troll-metatype-adjustments",
    "archer-heights", "docwagon-hospital-complex", "first-pit-stop", "hacker-technomancer",
    "hardpan-bar", "hot-potato", "if-the-runners-take", "lone-star-substation",
    "lone-star-law-enforcement", "mhcd", "mile-high-stadium", "paladin-group-llc",
    "paladin-health", "paladin-hospital", "paladin-nodes", "rocky-mountain-arsenal-national",
    "second-pit-stop", "shadow-reich-male-human", "team-karma", "the-clinic", "the-doctor",
    "the-meet", "the-ramsay-building-the-hub", "the-sectors", "thundercloud-morgan-atv",
}

MANHATTAN_CAST_EXCLUDE = {
    "breham-unlimited", "gold-whale-vehicle", "ic-none", "manhattan-island", "mercenary",
    "new-york-city-archives", "pushing-the-envelope", "restaurant-hijinks", "seats",
    "sky-sled", "stone-homunculus", "team-zero-body-bag-mk-ii", "water-blossom",
    "weapons-under-pressure", "zuckermans",
}


def build_denver() -> CityCatalogue:
    city = CityCatalogue("denver", "Denver", DENVER_ANCHORS["The Hub"], DENVER_ANCHORS, DENVER_BOOKS)
    map_numbers = {name_key(name): index for index, name in enumerate(DENVER_MAP_NAMES, 1)}
    exact_sites = {
        "Fox Theatre": [-105.2709, 40.0191],
        "Red Rocks Amphitheater": [-105.2057, 39.6654],
        "Casa Bonita": [-105.0708, 39.7415],
        "Denver International Airport": [-104.6737, 39.8561],
        "Denver Zoo": [-104.9508, 39.7508],
        "Brown Palace Hotel": [-104.9878, 39.7441],
        "Fillmore Auditorium": [-104.9752, 39.7404],
        "Union Station": [-105.0008, 39.7527],
        "Garden of the Gods": [-104.8864, 38.8730],
        "Cheyenne Mountain": [-104.8675, 38.7441],
        "Sakura Square": [-104.9945, 39.7503],
    }
    for scope, names in DENVER_SR6_PLACES.items():
        for name in names:
            number = map_numbers.get(name_key(name))
            city.add_place(
                name, scope, "SR6", "third-parallel-sr6", "The Third Parallel",
                "The Third Parallel, S. 10-39" if number is None else f"The Third Parallel - Denver Map, Nr. {number}",
                coordinates=exact_sites.get(name), map_number=number, exact=name in exact_sites,
            )
    for scope, names in DENVER_SR2_PLACES.items():
        for name in names:
            city.add_place(
                name, scope, "SR2", "denver-city-shadows-sr2", "Denver: The City of Shadows",
                f"Denver: The City of Shadows, Abschnitt {scope}",
            )
    city.add_place(
        "Front Range",
        "Front Range",
        "SR3",
        "shadows-north-america-sr3",
        "Shadows of North America",
        "Shadows of North America, Denver, S. 195",
        category="Bezirke",
        summary=(
            "Die Front Range Free Zone bleibt nach Ghostwalkers Machtübernahme eine "
            "geteilte Stadt und ein zentraler Umschlagplatz für Schmuggel, Politik und "
            "Informationen."
        ),
    )
    city.add_place(
        "Denver Data Haven",
        "The Hub",
        "SR3",
        "shadows-north-america-sr3",
        "Shadows of North America",
        "Shadows of North America, Denver Matrix, S. 195",
        category="Matrix und Metaplanes",
        summary=(
            "Der Nexus ist in SR3 das größte Data Haven Nordamerikas und ein "
            "entscheidender Informationsknoten der Denver-Schatten."
        ),
    )
    for name, scope, category, summary in DENVER_SPY_GAMES_PLACES:
        city.add_place(
            name,
            scope,
            "SR4",
            "spy-games-sr4",
            "Spy Games",
            "Spy Games, Denver-Kapitel S. 6-86",
            category=category,
            summary=summary,
        )
    for name, scope, category, summary in DENVER_STORM_FRONT_PLACES:
        city.add_place(
            name,
            scope,
            "SR4",
            "storm-front-sr4",
            "Storm Front",
            "Storm Front, Lightning in Denver S. 87-111",
            category=category,
            summary=summary,
        )
    for name in ("The Hardpan", "The Splatter Bar", "Little D’s Gourmet Emporium", "Marcel’s", "Happy Canyon Shopping Center", "Rocky Mountain Dynamics", "The Meat Market"):
        scope = "Aurora Warrens" if "Meat" in name else "The Hub"
        city.add_place(name, scope, "SR4", "welcome-denver-sr4", "Welcome to Denver", "Welcome to Denver, Making the Scene")
    for name, scope, category in [
        ("Archer Heights", "The Hub", "Konzerne"),
        ("DocWagon Hospital Complex", "The Hub", "Medizin"),
        ("First Pit Stop", "The Hub", "Bars und Clubs"),
        ("Hardpan Bar", "Thornton", "Bars und Clubs"),
        ("Lone Star Substation", "The Hub", "Sicherheit und Justiz"),
        ("Mile High Stadium", "The Hub", "Freizeit und Natur"),
        ("Paladin Group LLC", "The Hub", "Konzerne"),
        ("Paladin Health", "The Hub", "Medizin"),
        ("Paladin Hospital", "The Hub", "Medizin"),
        ("The Ramsay Building", "The Hub", "Konzerne"),
    ]:
        city.add_place(
            name, scope, "SR5", "denver-trilogy-sr5", "Denver Adventure Trilogy",
            "Denver Adventure Trilogy, Kampagnenschauplätze", category=category,
        )
    for name in ("Denver Metaplane", "The Black Canyon", "The Broken Heart", "The Iron Horse Nation", "The Mile High Realm", "The Shattered Lands"):
        edition = "SR6" if name == "Denver Metaplane" else "SR5"
        book_id = "third-parallel-sr6" if edition == "SR6" else "denver-trilogy-sr5"
        title = "The Third Parallel" if edition == "SR6" else "Denver Adventure Trilogy"
        city.add_place(
            name, "The Hub", edition, book_id, title,
            f"{title}, metaplanare Schauplätze", category="Matrix und Metaplanes",
        )
    for name, summary in DENVER_DISTRICT_SUMMARIES.items():
        city.enrich_district(name, "SR6", summary)

    for name in DENVER_GROUPS_SR6:
        city.add_person(
            name, "SR6", "third-parallel-sr6", "The Third Parallel",
            "The Third Parallel, S. 42-50", role="Lokale Organisation oder Gang",
            affiliation="Denver", entity_type="group",
        )
    for name, role, affiliation in DENVER_PEOPLE_SR6:
        city.add_person(
            name, "SR6", "third-parallel-sr6", "The Third Parallel",
            "The Third Parallel, S. 42-50 und Kampagnenanhang", role=role, affiliation=affiliation,
            location_name="The Hub" if name in {"Nicholas Whitebird", "Carol “Cat” McTavish"} else None,
        )
    for name in DENVER_GROUPS_SR2:
        city.add_person(
            name, "SR2", "denver-city-shadows-sr2", "Denver: The City of Shadows",
            "Denver: The City of Shadows, Unterwelt- und Gruppenregister", role="Lokale Organisation oder Gang",
            affiliation="Denver", entity_type="group",
        )
    for name, role, affiliation in DENVER_PEOPLE_SR2:
        city.add_person(
            name, "SR2", "denver-city-shadows-sr2", "Denver: The City of Shadows",
            "Denver: The City of Shadows, Personenregister", role=role, affiliation=affiliation,
            location_name="Hardpan" if name == "Rachel Sands" else None,
        )
    for name, role, affiliation in [
        ("Elizabeth Kalheim", "CAS-Vertreterin", "CAS"),
        ("Juanita Iglala", "PCC-Vertreterin", "Pueblo Corporate Council"),
        ("Miguel Sanchez", "Unterwelt- und Straßenkontakt", "Casquilho Family"),
        ("Lucinda Gray Arrow", "Sioux-Vertreterin", "Sioux Nation"),
        ("Iain Lesker", "UCAS-Vertreter", "UCAS"),
        ("Tabby", "Fixerin", "Denver-Schatten"),
        ("Wheezer", "Informationskontakt", "Denver"),
    ]:
        city.add_person(name, "SR4", "welcome-denver-sr4", "Welcome to Denver", "Welcome to Denver, Who’s Who", role=role, affiliation=affiliation)
    city.add_person(
        "Ghostwalker",
        "SR3",
        "year-comet-sr3",
        "Year of the Comet",
        "Year of the Comet, The Dragon Takes Denver",
        role="Großer Drache und Herrscher der FRFZ",
        affiliation="Front Range Free Zone",
        summary=(
            "Ghostwalker erscheint 2061 aus dem Watergate-Spalt, erzwingt den Abzug "
            "Aztlans und etabliert sich als oberste Macht der Front Range Free Zone."
        ),
        location_name="The Hub",
    )
    city.add_person(
        "Zebulon",
        "SR3",
        "year-comet-sr3",
        "Year of the Comet",
        "Year of the Comet, Denver und Ghostwalker",
        role="Großer Geist von Denver",
        affiliation="Denver",
        summary=(
            "Zebulon ist der große Stadtgeist Denvers und eng mit Ghostwalkers "
            "Rückkehr sowie der spirituellen Ordnung der FRFZ verbunden."
        ),
        location_name="The Hub",
    )
    city.add_person(
        "Los Espejos",
        "SR3",
        "shadows-north-america-sr3",
        "Shadows of North America",
        "Shadows of North America, Denver - Los Espejos, S. 195",
        role="Aztlanische Widerstandsbewegung",
        affiliation="Denver",
        summary=(
            "Los Espejos ist eine zellenförmig organisierte aztlanische Bewegung, "
            "die Personal und Waffen in die FRFZ schmuggelt und von der ZDF verfolgt wird."
        ),
        entity_type="group",
    )
    for name, role, affiliation, summary in DENVER_SPY_GAMES_PEOPLE:
        location_name = {
            "Alyss": "Wonderland",
            "Eddie “Mustang” Vass": "The Raintree Inn",
            "Jorge Molinera": "Anahuac University",
            "Nicholas Whitebird": "The Hub",
            "Raquel “Sandy” Sands": "Hardpan",
            "Tess McCartle": "University of Denver",
            "Zhang Wong": "Mystic Curiosities",
            "Lydia McDaniel": "University of Denver",
            "Jaron Falcone": "Horse Trot Ranch",
            "Gob": "Ketring Park",
            "Ghostwalker": "The Hub",
        }.get(name)
        city.add_person(
            name,
            "SR4",
            "spy-games-sr4",
            "Spy Games",
            "Spy Games, Denvers Machtspieler und Stadtprofile S. 6-86",
            role=role,
            affiliation=affiliation,
            summary=summary,
            location_name=location_name,
        )
    for name, role, affiliation, summary, location_name in DENVER_SPY_GAMES_CRIME_PEOPLE:
        city.add_person(
            name,
            "SR4",
            "spy-games-sr4",
            "Spy Games",
            "Spy Games, Criminal Elements S. 72-86",
            role=role,
            affiliation=affiliation,
            summary=summary,
            location_name=location_name,
        )
    for name, role, summary in DENVER_SPY_GAMES_GROUPS:
        location_name = {
            "Chavez Family": "Lakeside Amusement Park",
            "Casquilho Family": "Marcel’s",
            "Koshari": "Denim",
            "Fronts": "Ketring Park",
            "Denver Data Haven": "Denver Data Haven",
        }.get(name)
        city.add_person(
            name,
            "SR4",
            "spy-games-sr4",
            "Spy Games",
            "Spy Games, Criminal Elements S. 72-86",
            role=role,
            affiliation="Denver",
            summary=summary,
            entity_type="group",
            location_name=location_name,
        )
    for name, role, affiliation, summary in DENVER_STORM_FRONT_PEOPLE:
        city.add_person(
            name,
            "SR4",
            "storm-front-sr4",
            "Storm Front",
            "Storm Front, Lightning in Denver S. 87-111",
            role=role,
            affiliation=affiliation,
            summary=summary,
            location_name=(
                "Weekday Eclipse Memorial"
                if name == "Perianwyr"
                else "The Hub"
            ),
        )
    city.add_person(
        "Yamato Clan",
        "SR4",
        "storm-front-sr4",
        "Storm Front",
        "Storm Front, On Denver’s Yamato Clan",
        role="Yakuza-Clan",
        affiliation="Denver",
        summary=(
            "Der Yamato-Clan verliert 2074 nach Matrixangriffen, Verrat und einer "
            "koordinierten Offensive fast seine gesamte Handlungsfähigkeit in Denver."
        ),
        entity_type="group",
    )

    mission_dir = CORPUS / "Shadowrun 4"
    for path in sorted(mission_dir.glob("Shadowrun 4E - SRM02-??A - *.txt")):
        title = path.stem.split(" - ", 2)[-1]
        for name, entity_type in extract_toc_cast_names(path):
            name = re.sub(r"\s+\((?:CAS|PCC|Sioux|UCAS|Ute) Sector(?:,\s*FRFZ)?\)$", "", name, flags=re.I)
            if name_key(name) in city.places:
                continue
            role = "Gang oder benannte Gruppe" if entity_type == "group" else f"NSC aus {title}"
            city.add_person(
                name, "SR4", "srm02-sr4", "Shadowrun Missions Season 2",
                f"{title}, Cast of Shadows", role=role,
                affiliation="Denver", entity_type=entity_type,
            )
    trilogy_dir = CORPUS / "Shadowrun 5" / "07 - Englisch"
    for path in sorted(trilogy_dir.glob("Shadowrun 5E - Denver Adventure *.txt")):
        title = path.stem.split(" - ", 2)[-1]
        for name in extract_cast_names(path):
            name = re.sub(r"\s+\((?:CAS|PCC|Sioux|UCAS|Ute) Sector(?:,\s*FRFZ)?\)$", "", name, flags=re.I)
            if (
                name in {"Candice “Candy Cane”", "Kainbridge"}
                or slug(name) in DENVER_CAST_EXCLUDE
                or name_key(name) in city.places
            ):
                continue
            group_names = {
                "blinkers", "dark-amoebas", "doorkickers", "fuzz-spiders",
                "greed-monkeys", "rabbids", "scratchers", "shadow-claws",
            }
            entity_type = "group" if slug(name) in group_names else "person"
            role = "Gang oder benannte Gruppe" if entity_type == "group" else f"NSC aus {title}"
            city.add_person(
                name, "SR5", "denver-trilogy-sr5", "Denver Adventure Trilogy",
                f"{title}, Cast of Shadows", role=role,
                affiliation="Denver-Kampagne", entity_type=entity_type,
            )
    for name in (
        "Alexander “Xando” Obilon", "Candice “Candy Cane” Kainbridge",
        "Trent “Touchdown” Dade", "Scott “D-Day” Taug",
    ):
        city.add_person(
            name, "SR5", "denver-trilogy-sr5", "Denver Adventure Trilogy",
            "Serrated Edge, Cast of Shadows", role="Kampagnenfigur", affiliation="Denver-Kampagne",
        )
    return city


def build_manhattan() -> CityCatalogue:
    city = CityCatalogue("manhattan", "Manhattan", MANHATTAN_ANCHORS["Manhattan"], MANHATTAN_ANCHORS, MANHATTAN_BOOKS)
    exact_sites = {
        "Governors Island": [-74.0168, 40.6895],
        "Randalls Island": [-73.9227, 40.7957],
        "Penn Station": [-73.9935, 40.7506],
        "Lincoln Center": [-73.9835, 40.7725],
        "Sylvia’s": [-73.9448, 40.8089],
        "Columbia University": [-73.9626, 40.8075],
        "Union Square": [-73.9903, 40.7359],
        "Central Park": [-73.9654, 40.7829],
        "Belvedere Castle": [-73.9690, 40.7794],
        "Museum of Modern Art": [-73.9776, 40.7614],
        "Empire State Building": [-73.9857, 40.7484],
        "Washington Square Park / NYCU Campus": [-73.9973, 40.7308],
        "Castle Clinton": [-74.0168, 40.7034],
    }
    for scope, names in MANHATTAN_SR4_PLACES.items():
        for name in names:
            city.add_place(
                name, scope, "SR4", "rotten-apple-sr4", "The Rotten Apple: Manhattan",
                f"The Rotten Apple: Manhattan, Abschnitt {scope}",
                coordinates=exact_sites.get(name), exact=name in exact_sites,
            )
    for name in (
        "Westside", "Upper Eastside", "Midtown", "Lower Westside",
        "The Village", "Southside", "New York Harbor Islands",
    ):
        lat, lon = MANHATTAN_ANCHORS[name]
        city.add_place(
            name,
            name,
            "SR4",
            "rotten-apple-sr4",
            "The Rotten Apple: Manhattan",
            f"The Rotten Apple: Manhattan, Viertelbeschreibung {name}, S. 13-23",
            category="Bezirke",
            summary=(
                f"{name} ist ein eigenständiger Lore-Teilraum der "
                "Manhattan Development Consortium Zone."
            ),
            coordinates=[lon, lat],
        )
    for name, summary in MANHATTAN_SR1_DISTRICT_SUMMARIES.items():
        city.add_district_version(
            name,
            "SR1",
            "nagna-sr1",
            "The Neo-Anarchist’s Guide to North America",
            "The Neo-Anarchist’s Guide to North America, New York City S. 114-128",
            summary,
        )
    for name, scope, category, summary in MANHATTAN_SR1_PLACES:
        city.add_place(
            name,
            scope,
            "SR1",
            "nagna-sr1",
            "The Neo-Anarchist’s Guide to North America",
            "The Neo-Anarchist’s Guide to North America, New York City S. 114-128",
            category=category,
            summary=summary,
            coordinates=exact_sites.get(name),
            exact=name in exact_sites,
        )
    for name, role, summary in MANHATTAN_SR1_GROUPS:
        location_name = {
            "Children of the New Crusade": "The Cloisters",
            "Blood Monkeys": "Lower Westside",
            "Wrathchildes": "City Center",
            "Ancients": "Southside",
            "Axemen": "Southside",
            "Duelists": "The Pit",
            "Merlyn’s Pride": "The Pit",
            "Sisters Sinister": "The Pit",
            "Night-Spawn": "The Pit",
            "Billyboys": "The Pit",
            "Battery Boys": "Battery City",
        }.get(name)
        city.add_person(
            name,
            "SR1",
            "nagna-sr1",
            "The Neo-Anarchist’s Guide to North America",
            "The Neo-Anarchist’s Guide to North America, New York City S. 114-128",
            role=role,
            affiliation="New York",
            summary=summary,
            entity_type="group",
            location_name=location_name,
        )
    city.add_person(
        "Manhattan Development Consortium",
        "SR3",
        "shadows-north-america-sr3",
        "Shadows of North America",
        "Shadows of North America, New York City S. 173-174",
        role="Konzernkonsortium",
        affiliation="Manhattan",
        summary=(
            "Das in SR3 noch Manhattan, Inc. genannte Konsortium besitzt den "
            "wiederaufgebauten Stadtgrund und kontrolliert den Zugang zur Insel."
        ),
        entity_type="group",
        location_name="The Towers",
    )
    for name, scope, category, summary in MANHATTAN_CORPORATE_ENCLAVES_PLACES:
        city.add_place(
            name,
            scope,
            "SR4",
            "corporate-enclaves-manhattan-sr4",
            "Konzernenklaven: Manhattan",
            "Konzernenklaven: Manhattan, S. 1-4",
            category=category,
            summary=summary,
        )
    for name, role, summary in MANHATTAN_CORPORATE_ENCLAVES_GROUPS:
        city.add_person(
            name,
            "SR4",
            "corporate-enclaves-manhattan-sr4",
            "Konzernenklaven: Manhattan",
            "Konzernenklaven: Manhattan, S. 1-4",
            role=role,
            affiliation="New York",
            summary=summary,
            entity_type="group",
        )
    for name, summary in MANHATTAN_SR5_DISTRICT_SUMMARIES.items():
        city.add_district_version(
            name,
            "SR5",
            "stolen-souls-sr5",
            "Gestohlene Seelen / Stolen Souls",
            "Gestohlene Seelen, New Yorker Konzernidyll S. 118-147",
            summary,
        )
    for name, scope, category, summary in MANHATTAN_STOLEN_SOULS_PLACES:
        city.add_place(
            name,
            scope,
            "SR5",
            "stolen-souls-sr5",
            "Gestohlene Seelen / Stolen Souls",
            "Gestohlene Seelen, New Yorker Konzernidyll S. 118-147",
            category=category,
            summary=summary,
            coordinates=exact_sites.get(name),
            exact=name in exact_sites,
        )
    for name, role, affiliation in MANHATTAN_STOLEN_SOULS_PEOPLE:
        city.add_person(
            name,
            "SR5",
            "stolen-souls-sr5",
            "Gestohlene Seelen / Stolen Souls",
            "Gestohlene Seelen, New Yorker Konzernidyll S. 118-147",
            role=role,
            affiliation=affiliation,
            summary=(
                f"{name} wird im Manhattan-Kapitel als {role.lower()} im Umfeld "
                f"von {affiliation} geführt."
            ),
        )
    for name, role, summary in MANHATTAN_STOLEN_SOULS_GROUPS:
        location_name = {
            "Manhattan Development Consortium": "MDC Building",
            "Großer-Kreis-Liga": "Lucky Star 99",
            "Toki-gumi": "Chinatown",
            "Gangjun-Ring": "Lower Westside",
            "Min-Park-Ring": "Lower Westside",
            "Yeong-Ring": "Lower Westside",
            "New York Mets": "Manhattan",
            "Manhattan Yankees": "Manhattan",
            "Brooklyn Giants": "Manhattan",
            "New York Jets": "Manhattan",
            "Manhattan Islanders": "Manhattan",
            "New York Rangers": "Manhattan",
            "The Quake": "Manhattan",
            "New York Nets": "Manhattan",
            "Lightning": "Manhattan",
            "New York Marauders": "Manhattan",
            "New York Slashers": "Manhattan",
            "Manhattan Kraak": "Manhattan",
            "The Warriors": "Manhattan",
        }.get(name)
        city.add_person(
            name,
            "SR5",
            "stolen-souls-sr5",
            "Gestohlene Seelen / Stolen Souls",
            "Gestohlene Seelen, New Yorker Konzernidyll S. 118-147",
            role=role,
            affiliation="New York",
            summary=summary,
            entity_type="group",
            location_name=location_name,
        )
    for name, scope, category, summary, mission in MANHATTAN_SRM03_PLACES:
        city.add_place(
            name,
            scope,
            "SR4",
            "srm03-sr4",
            "Shadowrun Missions Season 3",
            f"{mission}, Schauplätze",
            category=category,
            summary=summary,
            coordinates=exact_sites.get(name),
            exact=name in exact_sites,
        )
    for name, role, summary in MANHATTAN_SRM03_GROUPS:
        location_name = {
            "Switchblades": "Jordan Aerodynamics Building",
            "Kings": "Terminal",
            "Tridents": "Terminal",
            "Slaughterhouse": "Terminal",
            "Sharks": "Throgs Neck Tunnel",
            "The Minibosses": "Guggenheim Museum",
        }.get(name)
        city.add_person(
            name,
            "SR4",
            "srm03-sr4",
            "Shadowrun Missions Season 3",
            "Shadowrun Missions Season 3, Missionsschauplätze und Gruppen",
            role=role,
            affiliation="New York",
            summary=summary,
            entity_type="group",
            location_name=location_name,
        )
    for name, scope, category, summary in MANHATTAN_BLOODY_BUSINESS_PLACES:
        city.add_place(
            name,
            scope,
            "SR5",
            "bloody-business-sr5",
            "Blutige Geschäfte / Bloody Business",
            "Blutige Geschäfte, Manhattan-Schauplätze",
            category=category,
            summary=summary,
            coordinates=exact_sites.get(name),
            exact=name in exact_sites,
        )
    for name, role, affiliation, summary in MANHATTAN_BLOODY_BUSINESS_PEOPLE:
        city.add_person(
            name,
            "SR5",
            "bloody-business-sr5",
            "Blutige Geschäfte / Bloody Business",
            "Blutige Geschäfte, Manhattan-Abenteuer",
            role=role,
            affiliation=affiliation,
            summary=summary,
        )
    for number, (name, scope) in enumerate(MANHATTAN_MAP_PLACES, 1):
        city.add_place(
            name, scope, "SR6", "fluesternetze-sr6", "Flüsternetze",
            f"Flüsternetze - Manhattankarte, Nr. {number}",
            coordinates=exact_sites.get(name), map_number=number, exact=name in exact_sites,
        )
    for scope, names in MANHATTAN_SR6_EXTRA.items():
        for name in names:
            city.add_place(name, scope, "SR6", "fluesternetze-sr6", "Flüsternetze", "Flüsternetze, Kampagne S. 41-143")
    for name, scope, category in [
        ("Zuckerman’s", "Midtown", "Restaurants"),
        ("New York City Archives", "Downtown", "Bildung und Kultur"),
        ("Water Blossom", "Manhattan", "Verkehr"),
        ("Wheels Up, Art’s Bar", "Manhattan", "Bars und Clubs"),
    ]:
        city.add_place(
            name, scope, "SR5", "battle-manhattan-sr5",
            "Krieg um Manhattan / Battle of Manhattan",
            "Krieg um Manhattan, Schauplätze", category=category,
        )
    for name, summary in MANHATTAN_DISTRICT_SUMMARIES.items():
        city.enrich_district(name, "SR4", summary)

    for item in MANHATTAN_PEOPLE_SR6:
        name, role, affiliation, *kind = item
        city.add_person(
            name, "SR6", "fluesternetze-sr6", "Flüsternetze",
            "Flüsternetze, Charakterfundgrube S. 150-162", role=role, affiliation=affiliation,
            entity_type=kind[0] if kind else "person",
            location_name=affiliation if name in {"Becky Wu Ping", "Fluffy Duck"} else None,
        )
    for name, role in MANHATTAN_GROUPS_SR6:
        city.add_person(
            name, "SR6", "fluesternetze-sr6", "Flüsternetze",
            "Flüsternetze, Das kriminelle Netzwerk S. 35-36",
            role=role, affiliation="New York", entity_type="group",
        )
    for name in MANHATTAN_MAGIC_GROUPS:
        city.add_person(
            name, "SR6", "fluesternetze-sr6", "Flüsternetze",
            "Flüsternetze, Das Erwachte New York S. 36-37",
            role="Magische Gesellschaft", affiliation="New York", entity_type="group",
        )

    mission_dir = CORPUS / "Shadowrun 4"
    for path in sorted(mission_dir.glob("Shadowrun 4E - SRM03-?? - *.txt")):
        title = path.stem.split(" - ", 2)[-1]
        for name in extract_cast_names(path):
            name = {
                "Hal Newspring, Prometheus": "Hal Newspring",
                "Master Wu, Elf Male Mage": "Master Wu",
            }.get(name, name)
            if slug(name) in MANHATTAN_CAST_EXCLUDE or name_key(name) in city.places:
                continue
            city.add_person(name, "SR4", "srm03-sr4", "Shadowrun Missions Season 3", f"{title}, Cast of Shadows", role=f"NSC aus {title}", affiliation="Manhattan")
    battle_sources = [
        CORPUS / "Shadowrun 5" / "04 - Abenteuerbände" / "Shadowrun 5D - Abenteuerband - Krieg um Manhattan.txt",
        CORPUS / "Shadowrun 5" / "07 - Englisch" / "Shadowrun 5E - Boardroom Backstabs 3 - Battle of Manhattan.txt",
    ]
    for path in battle_sources:
        if not path.exists():
            continue
        for name in extract_cast_names(path):
            name = {
                "Hal Newspring, Prometheus": "Hal Newspring",
                "Master Wu, Elf Male Mage": "Master Wu",
            }.get(name, name)
            if slug(name) in MANHATTAN_CAST_EXCLUDE or name_key(name) in city.places:
                continue
            city.add_person(name, "SR5", "battle-manhattan-sr5", "Krieg um Manhattan / Battle of Manhattan", "Krieg um Manhattan, Dramatis Personae", role="NSC aus Krieg um Manhattan", affiliation="Manhattan")
    for name, role in (
        ("Sully", "Schattenakteur und Kampagnenfigur"),
        ("Zarah", "Technomancerin und Kampagnenfigur"),
    ):
        city.add_person(
            name, "SR5", "battle-manhattan-sr5",
            "Krieg um Manhattan / Battle of Manhattan",
            "Krieg um Manhattan, Cast of Shadows", role=role, affiliation="Manhattan",
        )
    return city


def update_registry_years() -> None:
    path = ROOT / "data" / "cities.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    years = {"denver": 2081, "manhattan": 2083}
    for city in registry["cities"]:
        if city["id"] in years:
            city["year"] = years[city["id"]]
    write_json(path, registry)


def main() -> None:
    denver = build_denver()
    denver.finish(
        2081,
        "Denver/Front Range aus SR2 bis SR6 mit historischen Sektoren, aktuellen Distrikten, Kartenorten, Personen und Gruppen.",
        bounds=[[38.65, -105.75], [40.30, -104.15]],
        zoom=8,
    )
    manhattan = build_manhattan()
    manhattan.finish(
        2083,
        "Manhattan aus SR4 bis SR6 mit Konzernstadt-Bezirken, Missionsschauplätzen, Kartenlegende, Personen und Gruppen.",
        bounds=[[40.67, -74.05], [40.89, -73.90]],
        zoom=12,
    )
    update_registry_years()
    print(f"Denver: {len(denver.places)} Orte, {len(denver.people)} Personen/Gruppen")
    print(f"Manhattan: {len(manhattan.places)} Orte, {len(manhattan.people)} Personen/Gruppen")


if __name__ == "__main__":
    main()
