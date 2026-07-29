#!/usr/bin/env python3
"""Rebuild the global static search index from all city packages."""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

from validate_city_data import apply_augmentations


ROOT = Path(__file__).resolve().parents[1]


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def search_text(*values) -> str:
    parts: list[str] = []

    def add(value) -> None:
        if value is None:
            return
        if isinstance(value, dict):
            for key, item in value.items():
                add(key)
                add(item)
        elif isinstance(value, list):
            for item in value:
                add(item)
        else:
            parts.append(str(value))

    for value in values:
        add(value)
    text = unicodedata.normalize("NFKD", " ".join(parts))
    return text.encode("ascii", "ignore").decode("ascii").casefold()


def main() -> int:
    registry = read(ROOT / "data" / "cities.json")
    items = []
    for city in registry["cities"]:
        manifest_path = ROOT / city["manifest"]
        manifest = read(manifest_path)
        city_dir = manifest_path.parent
        places = read(city_dir / manifest["files"]["places"])
        for key in ("virtualPlaces", "historicalPlaces", "sourcePlaces"):
            path = manifest.get("files", {}).get(key)
            if path:
                places["features"].extend(read(city_dir / path).get("features", []))
        path = manifest.get("files", {}).get("placeAugmentations")
        if path:
            apply_augmentations(places["features"], read(city_dir / path), properties=True)
        path = manifest.get("files", {}).get("archivePlaceAugmentations")
        if path:
            apply_augmentations(places["features"], read(city_dir / path), properties=True)
        people = read(city_dir / manifest["files"]["people"])
        path = manifest.get("files", {}).get("historicalPeople")
        if path:
            people.extend(read(city_dir / path))
        path = manifest.get("files", {}).get("sourcePeople")
        if path:
            people.extend(read(city_dir / path))
        path = manifest.get("files", {}).get("personAugmentations")
        if path:
            apply_augmentations(people, read(city_dir / path))
        path = manifest.get("files", {}).get("archivePersonAugmentations")
        if path:
            apply_augmentations(people, read(city_dir / path))

        city_label = f"{city['name']} {city.get('year', '')}".strip()
        for feature in places["features"]:
            properties = feature["properties"]
            items.append({
                "cityId": city["id"],
                "cityName": city["name"],
                "cityLabel": city_label,
                "type": "place",
                "id": properties["id"],
                "globalId": properties.get("global_id"),
                "name": properties["name"],
                "category": properties.get("category", "Ort"),
                "editions": properties.get("editions", []),
                "search": search_text(
                    properties.get("name"),
                    properties.get("category"),
                    properties.get("description_full"),
                    properties.get("description_source"),
                    properties.get("source_pages"),
                    properties.get("aliases"),
                    properties.get("editions"),
                    properties.get("edition_descriptions"),
                ),
            })
        for person in people:
            items.append({
                "cityId": city["id"],
                "cityName": city["name"],
                "cityLabel": city_label,
                "type": "person",
                "id": person["id"],
                "globalId": person.get("global_id"),
                "name": person["name"],
                "category": person.get("category", "Person"),
                "entityType": person.get("entity_type", "person"),
                "editions": person.get("editions", []),
                "search": search_text(
                    person.get("name"),
                    person.get("aliases"),
                    person.get("category"),
                    person.get("role"),
                    person.get("affiliation"),
                    person.get("summary"),
                    person.get("description"),
                    person.get("source"),
                    person.get("members"),
                    person.get("danger"),
                    person.get("editions"),
                    person.get("edition_descriptions"),
                ),
            })
    output = ROOT / "data" / "search-index.json"
    output.write_text(
        json.dumps({"schemaVersion": 1, "items": items}, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"OK {output.relative_to(ROOT)}: {len(items)} Einträge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
