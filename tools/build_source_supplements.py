#!/usr/bin/env python3
"""Build optional, reviewed source-dossier packages for city maps.

Inputs live in ``tools/source-supplements/<city>.json``.  They contain only
editorially accepted names, paraphrased descriptions and source locators; no
copyrighted source context is published.  Generated packages are loaded in
addition to the regular city builder output and therefore survive rebuilds of
the older hard-coded city catalogues.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "tools/source-supplements"
AUDIT_INPUT_DIR = INPUT_DIR / "audit"
REGISTRY_PATH = ROOT / "data/source-registry.json"
CITIES_PATH = ROOT / "data/cities.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    pretty = (
        path.parent.name == "berlin-2080"
        and path.name in {"manifest.json", "sources.json"}
    )
    path.write_text(
        (
            json.dumps(payload, ensure_ascii=False, indent=2)
            if pretty
            else json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        )
        + "\n",
        encoding="utf-8",
    )


def fold(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    return value.encode("ascii", "ignore").decode("ascii").casefold()


def key(value: str) -> str:
    value = re.sub(r"\([^)]*\)", " ", value)
    value = re.sub(r"^(?:the|der|die|das)\s+", "", fold(value))
    return re.sub(r"[^a-z0-9]+", "", value)


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", fold(value)).strip("-")


def source_for(appearance: dict, works: dict[str, dict]) -> dict:
    work = works[appearance["bookId"]]
    return {
        "bookId": work["id"],
        "title": work["title"],
        "edition": work["edition"],
        "citation": appearance["citation"],
        "purpose": "description",
    }


def edition_descriptions(
    appearances: list[dict],
    works: dict[str, dict],
    kind: str,
) -> tuple[list[str], list[dict], dict]:
    by_edition: dict[str, list[tuple[dict, dict]]] = {}
    all_sources = []
    for appearance in appearances:
        source = source_for(appearance, works)
        all_sources.append(source)
        by_edition.setdefault(source["edition"], []).append((appearance, source))
    descriptions = {}
    for edition, values in sorted(by_edition.items()):
        description = values[0][0]["summary"]
        sources = [value[1] for value in values]
        descriptions[edition] = {
            "kind": kind,
            "preview": description,
            "full": (
                f"{description} Das Dossier fasst den belegten Quellenstand "
                "redaktionell zusammen; eine nicht belegte Kartenposition "
                "wird nicht ergänzt."
            ),
            "hasMore": True,
            "hasExcerpt": True,
            "sources": sources,
        }
    return sorted(by_edition), all_sources, descriptions


def existing_places(city_dir: Path, manifest: dict) -> tuple[list[dict], set[str], int]:
    features = []
    for field in ("places", "virtualPlaces", "historicalPlaces"):
        filename = manifest.get("files", {}).get(field)
        if not filename:
            continue
        features.extend(read_json(city_dir / filename).get("features", []))
    names = {
        key(name)
        for feature in features
        for name in (
            [feature.get("properties", {}).get("name", "")]
            + feature.get("properties", {}).get("aliases", [])
        )
        if name
    }
    numeric_ids = [
        feature.get("properties", {}).get("id")
        for feature in features
        if isinstance(feature.get("properties", {}).get("id"), int)
    ]
    return features, names, max(numeric_ids, default=0)


def existing_people(city_dir: Path, manifest: dict) -> tuple[list[dict], set[str]]:
    people = []
    for field in ("people", "historicalPeople"):
        filename = manifest.get("files", {}).get(field)
        if filename:
            people.extend(read_json(city_dir / filename))
    names = {
        key(name)
        for person in people
        for name in [person.get("name", "")] + person.get("aliases", [])
        if name
    }
    return people, names


def augmented_editions(
    city_dir: Path,
    manifest: dict,
    entries: list[dict],
    fields: tuple[str, ...],
    *,
    properties: bool = False,
) -> set[str]:
    editions = {
        edition
        for entry in entries
        for edition in (
            entry.get("properties", {}).get("editions", [])
            if properties
            else entry.get("editions", [])
        )
    }
    for field in fields:
        filename = manifest.get("files", {}).get(field)
        if not filename:
            continue
        for augmentation in read_json(city_dir / filename):
            editions.update(augmentation.get("editions", []))
    return editions


def build_city(city: dict, works: dict[str, dict]) -> tuple[int, int]:
    city_id = city["id"]
    input_path = INPUT_DIR / f"{city_id}.json"
    audit_input_path = AUDIT_INPUT_DIR / f"{city_id}.json"
    manifest_path = ROOT / city["manifest"]
    city_dir = manifest_path.parent
    manifest = read_json(manifest_path)
    if not input_path.exists() and not audit_input_path.exists():
        core_place_features, _, _ = existing_places(city_dir, manifest)
        core_people, _ = existing_people(city_dir, manifest)
        for field in ("sourcePlaces", "sourcePeople"):
            filename = manifest.get("files", {}).pop(field, None)
            if filename:
                generated_path = city_dir / filename
                if generated_path.exists():
                    generated_path.unlink()
        manifest["availableEditions"] = sorted(
            augmented_editions(
                city_dir,
                manifest,
                core_place_features,
                ("placeAugmentations", "archivePlaceAugmentations"),
                properties=True,
            )
            | augmented_editions(
                city_dir,
                manifest,
                core_people,
                ("personAugmentations", "archivePersonAugmentations"),
            )
        )
        summary = manifest.setdefault("summary", {})
        summary["entities"] = len(core_place_features)
        summary["people"] = len(core_people)
        summary["gangs"] = sum(
            person.get("entity_type") == "group"
            for person in core_people
        )
        write_json(manifest_path, manifest)
        return 0, 0
    configs = [
        read_json(path)
        for path in (input_path, audit_input_path)
        if path.exists()
    ]
    config = {
        "dataVersion": max(
            [int(manifest.get("dataVersion", 1))]
            + [int(item.get("dataVersion", 1)) for item in configs]
        ),
        "places": [
            entity
            for item in configs
            for entity in item.get("places", [])
        ],
        "people": [
            entity
            for item in configs
            for entity in item.get("people", [])
        ],
    }
    core_place_features, place_names, max_place_id = existing_places(
        city_dir, manifest
    )
    core_people, person_names = existing_people(city_dir, manifest)

    place_features = []
    accepted_place_names = set(place_names)
    for item in sorted(config.get("places", []), key=lambda value: fold(value["name"])):
        candidate_keys = {key(item["name"])} | {key(alias) for alias in item.get("aliases", [])}
        if candidate_keys & accepted_place_names:
            continue
        max_place_id += 1
        editions, sources, descriptions = edition_descriptions(
            item["appearances"], works, "Ortsdossier"
        )
        first = item["appearances"][0]
        summary = first["summary"]
        properties = {
            "id": max_place_id,
            "global_id": f"{city_id}:source-place:{slug(item['name'])}",
            "name": item["name"],
            "aliases": item.get("aliases", []),
            "category": item.get("category", "Sonstige Spots"),
            "detail_map": item.get("scope", manifest["name"]),
            "source_pages": first["citation"],
            "map_source": works[first["bookId"]]["title"],
            "placement_note": "Keine belastbare Einzelposition; Eintrag bleibt im Katalog",
            "accuracy": "Nur Stadt oder Lore-Teilraum belegt",
            "source_map": "source-supplement",
            "source_panel": item.get("scope", manifest["name"]),
            "description_preview": summary,
            "description_full": (
                f"{summary} Das Dossier fasst den belegten Quellenstand "
                "redaktionell zusammen; eine nicht belegte Kartenposition "
                "wird nicht ergänzt."
            ),
            "description_source": first["citation"],
            "description_kind": "Ortsdossier",
            "description_has_more": True,
            "detail_plans": [],
            "alternate_locations": [],
            "sources": sources,
            "map_sources": [],
            "editions": editions,
            "edition_descriptions": descriptions,
        }
        place_features.append({"type": "Feature", "geometry": None, "properties": properties})
        accepted_place_names.update(candidate_keys)

    source_people = []
    accepted_person_names = set(person_names)
    for item in sorted(config.get("people", []), key=lambda value: fold(value["name"])):
        candidate_keys = {key(item["name"])} | {key(alias) for alias in item.get("aliases", [])}
        if candidate_keys & accepted_person_names:
            continue
        kind = "Gruppendossier" if item.get("entity_type") == "group" else "Personendossier"
        editions, sources, descriptions = edition_descriptions(
            item["appearances"], works, kind
        )
        summary = item["appearances"][0]["summary"]
        source_people.append({
            "id": f"source-{slug(item['name'])}",
            "global_id": f"{city_id}:source-person:{slug(item['name'])}",
            "name": item["name"],
            "aliases": item.get("aliases", []),
            "category": item.get(
                "category",
                "Gruppen und Organisationen"
                if item.get("entity_type") == "group"
                else "Personen von Interesse",
            ),
            "entity_type": item.get("entity_type", "person"),
            "role": item.get("role", "Lokale Akteurin oder lokaler Akteur"),
            "affiliation": item.get("affiliation", manifest["name"]),
            "status": "Quellenstand beachten",
            "summary": summary,
            "description": (
                f"{summary} Das Dossier fasst den belegten Quellenstand "
                "redaktionell zusammen."
            ),
            "source": item["appearances"][0]["citation"],
            "locations": [],
            "scope": item.get("scope", manifest["name"]),
            "sources": sources,
            "editions": editions,
            "edition_descriptions": descriptions,
        })
        accepted_person_names.update(candidate_keys)

    source_places_path = city_dir / "source-places.geojson"
    source_people_path = city_dir / "source-people.json"
    write_json(
        source_places_path,
        {
            "type": "FeatureCollection",
            "name": f"{manifest['name']} – geprüfte zusätzliche Quellenorte",
            "features": place_features,
        },
    )
    write_json(source_people_path, source_people)
    manifest["files"]["sourcePlaces"] = source_places_path.name
    manifest["files"]["sourcePeople"] = source_people_path.name
    manifest["dataVersion"] = max(
        int(manifest.get("dataVersion", 1)),
        int(config.get("dataVersion", manifest.get("dataVersion", 1))),
    )
    manifest["availableEditions"] = sorted(
        augmented_editions(
            city_dir,
            manifest,
            core_place_features,
            ("placeAugmentations", "archivePlaceAugmentations"),
            properties=True,
        )
        | augmented_editions(
            city_dir,
            manifest,
            core_people,
            ("personAugmentations", "archivePersonAugmentations"),
        )
        | {edition for item in place_features for edition in item["properties"]["editions"]}
        | {edition for item in source_people for edition in item["editions"]}
    )
    summary = manifest.setdefault("summary", {})
    summary["entities"] = len(core_place_features) + len(place_features)
    summary["people"] = len(core_people) + len(source_people)
    summary["gangs"] = sum(
        person.get("entity_type") == "group"
        for person in [*core_people, *source_people]
    )
    write_json(manifest_path, manifest)

    sources_path = city_dir / manifest["files"]["sources"]
    source_catalogue = read_json(sources_path)
    known_books = {book["id"] for book in source_catalogue["books"]}
    used_sources = [
        source
        for feature in place_features
        for source in feature["properties"]["sources"]
    ] + [source for person in source_people for source in person["sources"]]
    for source in used_sources:
        if source["bookId"] not in known_books:
            source_catalogue["books"].append({
                "id": source["bookId"],
                "title": source["title"],
                "edition": source["edition"],
                "registryWorkId": source["bookId"],
            })
            known_books.add(source["bookId"])
        citation = {
            "bookId": source["bookId"],
            "title": source["title"],
            "edition": source["edition"],
            "citation": source["citation"],
            "purpose": source["purpose"],
        }
        if citation not in source_catalogue["citations"]:
            source_catalogue["citations"].append(citation)
    source_catalogue["books"].sort(key=lambda item: (item["edition"], fold(item["title"])))
    write_json(sources_path, source_catalogue)
    return len(place_features), len(source_people)


def main() -> int:
    works = {
        work["id"]: work
        for work in read_json(REGISTRY_PATH)["works"]
    }
    cities = read_json(CITIES_PATH)["cities"]
    selected = set(sys.argv[1:])
    total_places = total_people = 0
    for city in cities:
        if selected and city["id"] not in selected:
            continue
        places, people = build_city(city, works)
        if places or people:
            print(f"OK {city['id']}: {places} zusätzliche Orte, {people} Personen/Gruppen")
        total_places += places
        total_people += people
    print(f"Gesamt: {total_places} Orte, {total_people} Personen/Gruppen")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
