#!/usr/bin/env python3
"""Validate all static Shadowrun city packages before publication."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/cities.json"
VALID_EDITIONS = {f"SR{number}" for number in range(1, 7)}
VALID_COVERAGE_STATUSES = {
    "importiert",
    "zusammengeführt",
    "geprüft-ohne-relevanten-inhalt",
    "dublette",
    "übersetzung-eines-geprüften-werks",
    "nichtoffiziell-ausgeschlossen",
    "unlesbar-pdf-gegenprüfung-erforderlich",
    "offen",
    "nur-volltexttreffer",
    "noch-zu-prüfen",
}
OPEN_COVERAGE_STATUSES = {"offen", "nur-volltexttreffer", "noch-zu-prüfen"}


def merge_unique(first, second, key=lambda value: json.dumps(value, sort_keys=True, ensure_ascii=False)):
    result = []
    seen = set()
    for value in [*(first or []), *(second or [])]:
        signature = key(value)
        if signature in seen:
            continue
        seen.add(signature)
        result.append(value)
    return result


def apply_augmentations(entries: list, augmentations: list, *, properties: bool = False) -> None:
    by_id = {entry["id"]: entry for entry in augmentations}
    found = set()
    for entry in entries:
        target = entry.get("properties", {}) if properties else entry
        augmentation = by_id.get(target.get("id"))
        if not augmentation:
            continue
        found.add(target["id"])
        for key, value in augmentation.items():
            if key in {"id", "global_id"}:
                continue
            if key in {"aliases", "editions", "sources", "map_sources", "locations"}:
                target[key] = merge_unique(
                    target.get(key),
                    value,
                    key=(lambda item: item if isinstance(item, str) else json.dumps(item, sort_keys=True, ensure_ascii=False)),
                )
            elif key == "edition_descriptions":
                target[key] = {**target.get(key, {}), **value}
            else:
                target[key] = value
    missing = sorted(set(by_id) - found, key=str)
    if missing:
        raise ValueError(f"Erweiterungen verweisen auf unbekannte IDs: {', '.join(map(str, missing))}")


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Ungültige JSON-Datei {path.relative_to(ROOT)}: {error}") from error


def validate_coordinates(coordinates, label: str) -> None:
    if not isinstance(coordinates, list) or not coordinates:
        raise ValueError(f"{label}: Koordinaten fehlen")
    if isinstance(coordinates[0], (int, float)):
        if len(coordinates) < 2:
            raise ValueError(f"{label}: Koordinatenpaar ist unvollständig")
        lon, lat = coordinates[:2]
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError(f"{label}: ungültige Koordinaten {lon}, {lat}")
        return
    for item in coordinates:
        validate_coordinates(item, label)


def point_in_ring(point: tuple[float, float], ring: list[list[float]]) -> bool:
    x, y = point
    inside = False
    for first, second in zip(ring, ring[1:]):
        x1, y1 = first[:2]
        x2, y2 = second[:2]
        if (y1 > y) != (y2 > y):
            crossing_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < crossing_x:
                inside = not inside
    return inside


def point_in_geometry(point: tuple[float, float], geometry: dict) -> bool:
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    return any(
        point_in_ring(point, polygon[0])
        and not any(point_in_ring(point, hole) for hole in polygon[1:])
        for polygon in polygons
    )


def validate_feature_collection(payload: dict, label: str, *, allow_null_geometry: bool = False) -> None:
    if payload.get("type") != "FeatureCollection" or not isinstance(payload.get("features"), list):
        raise ValueError(f"{label}: keine gültige FeatureCollection")
    for index, feature in enumerate(payload["features"]):
        geometry = feature.get("geometry")
        if geometry is None and allow_null_geometry:
            continue
        geometry = geometry or {}
        validate_coordinates(geometry.get("coordinates"), f"{label}, Feature {index + 1}")


def validate_edition_data(entry: dict, label: str) -> set[str]:
    editions = entry.get("editions")
    if not isinstance(editions, list) or not editions:
        raise ValueError(f"{label}: keine Spielversion zugeordnet")
    edition_set = set(editions)
    unknown = sorted(edition_set - VALID_EDITIONS)
    if unknown:
        raise ValueError(f"{label}: unbekannte Spielversion(en): {', '.join(unknown)}")
    if len(editions) != len(edition_set):
        raise ValueError(f"{label}: doppelte Spielversion")

    descriptions = entry.get("edition_descriptions")
    if not isinstance(descriptions, dict) or set(descriptions) != edition_set:
        raise ValueError(f"{label}: Editionsbeschreibungen passen nicht zu den Spielversionen")
    for edition, description in descriptions.items():
        if not isinstance(description, dict):
            raise ValueError(f"{label}: ungültige Beschreibung für {edition}")
        if not description.get("preview") or not description.get("full"):
            raise ValueError(f"{label}: leerer Beschreibungstext für {edition}")
        sources = description.get("sources")
        if not isinstance(sources, list) or not sources:
            raise ValueError(f"{label}: kein Quellenbeleg für {edition}")
        if any(source.get("edition") != edition for source in sources):
            raise ValueError(f"{label}: Quellenbeleg ist der falschen Edition zugeordnet")

    sources = entry.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError(f"{label}: strukturierte Quellen fehlen")
    for source in sources:
        if source.get("edition") not in edition_set or source.get("edition") not in VALID_EDITIONS:
            raise ValueError(f"{label}: unklassifizierte oder unpassende Quelle {source.get('citation')}")
        if not source.get("citation") or not source.get("bookId"):
            raise ValueError(f"{label}: unvollständige Quellenangabe")
    return edition_set


def validate_city(
    city: dict,
    global_ids: set[str],
    registry_works: dict[str, dict],
    coverage_by_work: dict[str, dict],
) -> tuple[int, int]:
    manifest_path = ROOT / city["manifest"]
    manifest = read_json(manifest_path)
    if manifest.get("id") != city.get("id"):
        raise ValueError(f"{manifest_path.relative_to(ROOT)}: Stadt-ID stimmt nicht mit cities.json überein")
    city_dir = manifest_path.parent
    required = {"places", "people", "atlas", "zones", "districts", "neighborhoods", "outskirts", "boundary", "labels", "sources"}
    missing = sorted(required - set(manifest.get("files", {})))
    if missing:
        raise ValueError(f"{city['id']}: fehlende Dateiverweise: {', '.join(missing)}")
    for path in manifest["files"].values():
        if not (city_dir / path).exists():
            raise ValueError(f"{city['id']}: Datei fehlt: {path}")

    places = read_json(city_dir / manifest["files"]["places"])
    validate_feature_collection(places, f"{city['id']} Orte", allow_null_geometry=True)
    for key, label in (
        ("virtualPlaces", "virtuelle Orte"),
        ("historicalPlaces", "historische Orte"),
        ("sourcePlaces", "zusätzliche Quellenorte"),
    ):
        supplemental_path = manifest.get("files", {}).get(key)
        if supplemental_path:
            supplemental = read_json(city_dir / supplemental_path)
            validate_feature_collection(supplemental, f"{city['id']} {label}", allow_null_geometry=True)
            places["features"].extend(supplemental["features"])
    place_augmentations_path = manifest.get("files", {}).get("placeAugmentations")
    if place_augmentations_path:
        apply_augmentations(
            places["features"],
            read_json(city_dir / place_augmentations_path),
            properties=True,
        )
    archive_place_augmentations_path = manifest.get("files", {}).get(
        "archivePlaceAugmentations"
    )
    if archive_place_augmentations_path:
        apply_augmentations(
            places["features"],
            read_json(city_dir / archive_place_augmentations_path),
            properties=True,
        )
    place_ids: set[object] = set()
    city_editions: set[str] = set()
    referenced_book_ids: set[str] = set()
    for feature in places["features"]:
        properties = feature.get("properties") or {}
        place_id = properties.get("id")
        if place_id in place_ids:
            raise ValueError(f"{city['id']}: doppelte Orts-ID {place_id}")
        place_ids.add(place_id)
        global_id = properties.get("global_id")
        if not global_id or global_id in global_ids:
            raise ValueError(f"{city['id']}: fehlende oder doppelte globale Orts-ID {global_id}")
        global_ids.add(global_id)
        if not properties.get("name") or not properties.get("category"):
            raise ValueError(f"{city['id']}: Ort {place_id} ohne Name oder Kategorie")
        city_editions.update(validate_edition_data(properties, f"{city['id']}: Ort {place_id}"))
        referenced_book_ids.update(source["bookId"] for source in properties["sources"])

    people = read_json(city_dir / manifest["files"]["people"])
    historical_people_path = manifest.get("files", {}).get("historicalPeople")
    if historical_people_path:
        people.extend(read_json(city_dir / historical_people_path))
    source_people_path = manifest.get("files", {}).get("sourcePeople")
    if source_people_path:
        people.extend(read_json(city_dir / source_people_path))
    person_augmentations_path = manifest.get("files", {}).get("personAugmentations")
    if person_augmentations_path:
        apply_augmentations(people, read_json(city_dir / person_augmentations_path))
    archive_person_augmentations_path = manifest.get("files", {}).get(
        "archivePersonAugmentations"
    )
    if archive_person_augmentations_path:
        apply_augmentations(
            people,
            read_json(city_dir / archive_person_augmentations_path),
        )
    person_ids: set[object] = set()
    for person in people:
        person_id = person.get("id")
        if person_id in person_ids:
            raise ValueError(f"{city['id']}: doppelte Personen-ID {person_id}")
        person_ids.add(person_id)
        global_id = person.get("global_id")
        if not global_id or global_id in global_ids:
            raise ValueError(f"{city['id']}: fehlende oder doppelte globale Personen-ID {global_id}")
        global_ids.add(global_id)
        city_editions.update(validate_edition_data(person, f"{city['id']}: Person {person_id}"))
        referenced_book_ids.update(source["bookId"] for source in person["sources"])
        for link in person.get("locations", []):
            if link.get("id") not in place_ids:
                raise ValueError(f"{city['id']}: {person.get('name')} verweist auf unbekannten Ort {link.get('id')}")

    for key in ("zones", "exterritorial", "districts", "neighborhoods", "outskirts", "boundary"):
        payload = read_json(city_dir / manifest["files"][key])
        validate_feature_collection(payload, f"{city['id']} {key}")
        if key == "zones":
            topology = payload.get("topology", {})
            if topology.get("model") != "exclusive-partition":
                raise ValueError(f"{city['id']}: Gebietsstatus ist keine exklusive Flächenpartition")
            unresolved = topology.get("unresolved_overlap_area_degrees_squared")
            if not isinstance(unresolved, (int, float)) or unresolved > 1e-9:
                raise ValueError(f"{city['id']}: ungeklärte Gebietsüberlappung {unresolved}")
            if any(feature.get("properties", {}).get("topology") != "disjoint" for feature in payload["features"]):
                raise ValueError(f"{city['id']}: mindestens eine Gebietsfläche ist nicht als disjunkt markiert")
            if city["id"] == "berlin-2080":
                labels = {feature.get("properties", {}).get("label") for feature in payload["features"]}
                required_corporate = {
                    "Exterritoriales Konzerngebiet · AZT Schönwalde",
                    "Exterritoriales Konzerngebiet · Z-IC Tegel",
                    "Exterritoriales Konzerngebiet · AGC Siemensstadt",
                    "Exterritoriales Konzerngebiet · Renrakusan",
                    "Exterritoriales Konzerngebiet · S-K Tempelhof",
                }
                if missing := required_corporate - labels:
                    raise ValueError(
                        f"{city['id']}: getrennte Konzerngebiete fehlen: {', '.join(sorted(missing))}"
                    )
                anarcho = next(
                    feature
                    for feature in payload["features"]
                    if feature.get("properties", {}).get("status") == "anarcho"
                )
                renrakusan_neighbors = {
                    "Caligariplatz/Pankower Dreamland": (13.453143, 52.550202),
                    "Nordostrand Renrakusan": (13.465, 52.557),
                    "Ostrand Renrakusan": (13.474, 52.54),
                    "Südostrand/Kreuzhain": (13.474, 52.515),
                }
                for name, point in renrakusan_neighbors.items():
                    if not point_in_geometry(point, anarcho["geometry"]):
                        raise ValueError(f"{city['id']}: {name} ist nicht dem Anarchogebiet zugeordnet")
        if key == "exterritorial" and city["id"] == "berlin-2080":
            reviewed = {
                feature.get("properties", {}).get("label")
                for feature in payload["features"]
                if feature.get("properties", {}).get("boundary_review_status") == "reviewed"
            }
            if "Exterritoriales Konzerngebiet · Renrakusan" not in reviewed:
                raise ValueError(f"{city['id']}: Renrakusan ist nicht als geprüfte EXTER-Fläche markiert")
    for key in ("security", "special"):
        supplemental_path = manifest.get("files", {}).get(key)
        if supplemental_path:
            validate_feature_collection(
                read_json(city_dir / supplemental_path),
                f"{city['id']} {key}",
            )

    atlas = read_json(city_dir / manifest["files"]["atlas"])
    atlas_ids = set()
    for plan in atlas:
        if plan.get("key") in atlas_ids:
            raise ValueError(f"{city['id']}: doppelte Detailkarten-ID {plan.get('key')}")
        atlas_ids.add(plan.get("key"))
        image_path = (city_dir / plan["image"]).resolve()
        if not image_path.exists():
            raise ValueError(f"{city['id']}: Detailkarte fehlt: {plan['image']}")

    offline_base = manifest.get("assets", {}).get("offlineBase")
    if offline_base and not (city_dir / offline_base).resolve().exists():
        raise ValueError(f"{city['id']}: Offline-Kartenbasis fehlt: {offline_base}")

    manifest_editions = manifest.get("availableEditions")
    if not isinstance(manifest_editions, list) or set(manifest_editions) != city_editions:
        raise ValueError(f"{city['id']}: availableEditions stimmt nicht mit den Stadtinhalten überein")

    sources_payload = read_json(city_dir / manifest["files"]["sources"])
    books = sources_payload.get("books")
    citations = sources_payload.get("citations")
    if not isinstance(books, list) or not isinstance(citations, list):
        raise ValueError(f"{city['id']}: Quellenkatalog ist unvollständig")
    book_ids = [book.get("id") for book in books]
    if len(book_ids) != len(set(book_ids)) or any(book.get("edition") not in VALID_EDITIONS for book in books):
        raise ValueError(f"{city['id']}: Quellenkatalog enthält doppelte Bücher oder ungültige Editionen")
    missing_books = sorted(referenced_book_ids - set(book_ids))
    if missing_books:
        raise ValueError(
            f"{city['id']}: Entitäten verweisen auf unbekannte Quellen-IDs: "
            + ", ".join(missing_books[:12])
        )
    for book in books:
        registry_work_id = book.get("registryWorkId")
        if not registry_work_id:
            continue
        work = registry_works.get(registry_work_id)
        if not work:
            raise ValueError(
                f"{city['id']}: Quellenkatalog verweist auf unbekanntes Registerwerk "
                f"{registry_work_id}"
            )
        if work["edition"] != book["edition"]:
            raise ValueError(
                f"{city['id']}: Edition des Registerwerks {registry_work_id} stimmt nicht"
            )
    if manifest.get("sourceCoverageComplete"):
        open_work_ids = [
            work_id
            for work_id, row in coverage_by_work.items()
            if row.get("cities", {}).get(city["id"], {}).get("status")
            in OPEN_COVERAGE_STATUSES
        ]
        if open_work_ids:
            raise ValueError(
                f"{city['id']}: als vollständig markiert, aber "
                f"{len(open_work_ids)} Werk-/Stadt-Prüfungen sind offen"
            )
        incomplete_entity_work_ids = [
            work_id
            for work_id, row in coverage_by_work.items()
            if city["id"] in row.get("cities", {})
            if row.get("cities", {}).get(city["id"], {}).get(
                "entityExtraction", {}
            ).get("status") not in {
                "vollständig-extrahiert",
                "keine-lokalen-dossiers",
                "nichtoffiziell-ausgeschlossen",
            }
        ]
        if incomplete_entity_work_ids:
            raise ValueError(
                f"{city['id']}: als vollständig markiert, aber "
                f"{len(incomplete_entity_work_ids)} werkweise "
                "Entitätsprüfungen sind offen"
            )
    return len(place_ids), len(person_ids)


def validate_source_registry() -> tuple[dict[str, dict], dict[str, dict]]:
    registry = read_json(ROOT / "data/source-registry.json")
    coverage = read_json(ROOT / "data/source-coverage.json")
    works = registry.get("works")
    if not isinstance(works, list) or not works:
        raise ValueError("data/source-registry.json enthält keine Werke")
    work_ids = [work.get("id") for work in works]
    if len(work_ids) != len(set(work_ids)) or any(not work_id for work_id in work_ids):
        raise ValueError("data/source-registry.json enthält fehlende oder doppelte Werk-IDs")
    files = []
    for work in works:
        if work.get("edition") not in VALID_EDITIONS:
            raise ValueError(f"Registerwerk {work.get('id')} hat keine gültige Edition")
        if not work.get("title") or not isinstance(work.get("files"), list) or not work["files"]:
            raise ValueError(f"Registerwerk {work.get('id')} ist unvollständig")
        for file in work["files"]:
            if not file.get("path") or not re.fullmatch(r"[0-9a-f]{64}", file.get("sha256", "")):
                raise ValueError(f"Registerwerk {work.get('id')} enthält eine ungültige Datei")
            files.append(file["path"])
    if len(files) != len(set(files)):
        raise ValueError("data/source-registry.json ordnet eine Datei mehreren Werken zu")
    summary = registry.get("summary", {})
    if summary.get("files") != len(files) or summary.get("works") != len(works):
        raise ValueError("Zusammenfassung des Quellenregisters stimmt nicht")

    matrix = coverage.get("matrix")
    if not isinstance(matrix, list) or len(matrix) != len(works):
        raise ValueError("data/source-coverage.json deckt nicht jedes Registerwerk ab")
    coverage_by_work = {row.get("workId"): row for row in matrix}
    if set(coverage_by_work) != set(work_ids):
        raise ValueError("Abdeckungsmatrix und Quellenregister besitzen verschiedene Werk-IDs")
    city_ids = [city.get("id") for city in coverage.get("cities", [])]
    if len(city_ids) != len(set(city_ids)) or not city_ids:
        raise ValueError("Abdeckungsmatrix enthält fehlende oder doppelte Stadt-IDs")
    counted_statuses = Counter()
    for row in matrix:
        unknown_cities = set(row.get("cities", {})) - set(city_ids)
        if unknown_cities:
            raise ValueError(
                f"Abdeckungsmatrix enthält unbekannte Städte: {', '.join(sorted(unknown_cities))}"
            )
        for item in row.get("cities", {}).values():
            status = item.get("status")
            if status not in VALID_COVERAGE_STATUSES:
                raise ValueError(f"Abdeckungsmatrix enthält ungültigen Status {status}")
            counted_statuses[status] += 1
    if dict(sorted(counted_statuses.items())) != coverage.get("statusCounts"):
        raise ValueError("Statuszusammenfassung der Abdeckungsmatrix stimmt nicht")
    counted_extraction_statuses = Counter(
        item.get("entityExtraction", {}).get("status")
        for row in matrix
        for item in row.get("cities", {}).values()
    )
    if dict(sorted(counted_extraction_statuses.items())) != coverage.get(
        "entityExtractionStatusCounts"
    ):
        raise ValueError(
            "Statuszusammenfassung des Entitätsaudits stimmt nicht"
        )
    return {work["id"]: work for work in works}, coverage_by_work


def main() -> int:
    registry_works, coverage_by_work = validate_source_registry()
    registry = read_json(REGISTRY_PATH)
    cities = registry.get("cities", [])
    if not cities:
        raise ValueError("data/cities.json enthält keine Städte")
    city_ids = [city.get("id") for city in cities]
    if len(city_ids) != len(set(city_ids)):
        raise ValueError("data/cities.json enthält doppelte Stadt-IDs")
    if sum(bool(city.get("default")) for city in cities) != 1:
        raise ValueError("Genau eine Stadt muss als Standard markiert sein")

    global_ids: set[str] = set()
    total_places = 0
    total_people = 0
    for city in cities:
        places, people = validate_city(
            city,
            global_ids,
            registry_works,
            coverage_by_work,
        )
        total_places += places
        total_people += people
        print(f"OK {city['name']} {city.get('year', '')}: {places} Orte, {people} Personen")

    search_index = read_json(ROOT / "data/search-index.json")
    if len(search_index.get("items", [])) != total_places + total_people:
        raise ValueError("Der globale Suchindex ist unvollständig")
    print(f"OK Gesamt: {len(cities)} Stadtpaket(e), {total_places} Orte, {total_people} Personen")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(f"FEHLER: {error}", file=sys.stderr)
        raise SystemExit(1)
