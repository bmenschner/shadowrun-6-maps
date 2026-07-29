#!/usr/bin/env python3
"""Link verified city entities to every matching official archive source.

This importer deliberately does not create entities from isolated mentions.
It adds structured edition/source evidence to already verified places,
persons and groups.  New-entity candidates remain in the ignored review queue
created by ``extract_source_candidates.py``.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path

from validate_city_data import apply_augmentations, merge_unique


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = Path("/mnt/c/Users/Privat/Documents/Shadowrun/txtexports")
REGISTRY_PATH = ROOT / "data/source-registry.json"
COVERAGE_PATH = ROOT / "data/source-coverage.json"
PAGE_PATTERN = re.compile(r"^===== PDF-Seite (\d+) =====$")
VALID_EDITIONS = {f"SR{number}" for number in range(1, 7)}
GENERIC_NAMES = {
    "downtown", "central", "zentrum", "city", "metroplex", "sprawl",
    "north", "south", "east", "west", "nord", "süd", "ost", "west",
    "airport", "flughafen", "university", "universität", "police", "polizei",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    pretty = False
    if path.exists():
        prefix = path.read_text(encoding="utf-8")[:2]
        pretty = prefix in {"{\n", "[\n"}
    path.write_text(
        (
            json.dumps(payload, ensure_ascii=False, indent=2)
            if pretty
            else json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        ) + "\n",
        encoding="utf-8",
    )


def title_key(value: str) -> str:
    value = value.casefold()
    value = re.sub(r"\b(?:shadowrun|sr|searchable|scan|ocr|original|pdf)\b", " ", value)
    return re.sub(r"[^a-z0-9äöüß]+", "", value)


class AhoMatcher:
    def __init__(self) -> None:
        self.next: list[dict[str, int]] = [{}]
        self.fail = [0]
        self.output: list[list[str]] = [[]]

    def add(self, pattern: str) -> None:
        state = 0
        for character in pattern:
            target = self.next[state].get(character)
            if target is None:
                target = self._new_state()
                self.next[state][character] = target
            state = target
        if pattern not in self.output[state]:
            self.output[state].append(pattern)

    def _new_state(self) -> int:
        index = len(self.next)
        self.next.append({})
        self.fail.append(0)
        self.output.append([])
        return index

    def build(self) -> None:
        queue = deque()
        for state in self.next[0].values():
            queue.append(state)
        while queue:
            state = queue.popleft()
            for character, target in self.next[state].items():
                queue.append(target)
                fallback = self.fail[state]
                while fallback and character not in self.next[fallback]:
                    fallback = self.fail[fallback]
                self.fail[target] = self.next[fallback].get(character, 0)
                self.output[target].extend(self.output[self.fail[target]])

    def find(self, text: str):
        state = 0
        for index, character in enumerate(text):
            while state and character not in self.next[state]:
                state = self.fail[state]
            state = self.next[state].get(character, 0)
            for pattern in self.output[state]:
                start = index - len(pattern) + 1
                before = text[start - 1] if start else " "
                after = text[index + 1] if index + 1 < len(text) else " "
                if not before.isalnum() and not after.isalnum():
                    yield pattern


def load_city_entities(city: dict):
    manifest_path = ROOT / city["manifest"]
    manifest = read_json(manifest_path)
    city_dir = manifest_path.parent
    places_payload = read_json(city_dir / manifest["files"]["places"])
    places = places_payload["features"]
    for key in ("virtualPlaces", "historicalPlaces", "sourcePlaces"):
        path = manifest.get("files", {}).get(key)
        if path:
            places.extend(read_json(city_dir / path)["features"])
    place_aug_path = manifest.get("files", {}).get("placeAugmentations")
    place_augmentations = read_json(city_dir / place_aug_path) if place_aug_path else []
    if place_augmentations:
        apply_augmentations(places, place_augmentations, properties=True)
    archive_place_aug_path = manifest.get("files", {}).get("archivePlaceAugmentations")
    archive_place_augmentations = (
        read_json(city_dir / archive_place_aug_path) if archive_place_aug_path else []
    )
    if archive_place_augmentations:
        apply_augmentations(places, archive_place_augmentations, properties=True)

    people = read_json(city_dir / manifest["files"]["people"])
    historical_people_path = manifest.get("files", {}).get("historicalPeople")
    if historical_people_path:
        people.extend(read_json(city_dir / historical_people_path))
    source_people_path = manifest.get("files", {}).get("sourcePeople")
    if source_people_path:
        people.extend(read_json(city_dir / source_people_path))
    person_aug_path = manifest.get("files", {}).get("personAugmentations")
    person_augmentations = read_json(city_dir / person_aug_path) if person_aug_path else []
    if person_augmentations:
        apply_augmentations(people, person_augmentations)
    archive_person_aug_path = manifest.get("files", {}).get("archivePersonAugmentations")
    archive_person_augmentations = (
        read_json(city_dir / archive_person_aug_path) if archive_person_aug_path else []
    )
    if archive_person_augmentations:
        apply_augmentations(people, archive_person_augmentations)
    return (
        manifest_path,
        manifest,
        places,
        people,
        archive_place_aug_path,
        archive_place_augmentations,
        archive_person_aug_path,
        archive_person_augmentations,
    )


def entity_patterns(city_id: str, places: list, people: list):
    result: dict[str, list[tuple[str, object, dict]]] = defaultdict(list)
    for feature in places:
        entity = feature["properties"]
        if entity.get("category") == "Bezirke":
            continue
        names = [entity.get("name"), *entity.get("aliases", [])]
        for name in names:
            pattern = str(name or "").casefold().strip()
            if (
                len(pattern) >= 6
                and pattern not in GENERIC_NAMES
                and sum(character.isalpha() for character in pattern) >= 5
            ):
                result[pattern].append((city_id, "place", entity))
    for entity in people:
        names = [entity.get("name"), *entity.get("aliases", [])]
        for name in names:
            pattern = str(name or "").casefold().strip()
            if (
                len(pattern) >= 6
                and pattern not in GENERIC_NAMES
                and sum(character.isalpha() for character in pattern) >= 5
            ):
                result[pattern].append((city_id, "person", entity))
    return result


def add_reference(entity: dict, work: dict, citation: str) -> bool:
    edition = work["edition"]
    if edition not in VALID_EDITIONS:
        return False
    source = {
        "bookId": work["id"],
        "title": work["title"],
        "edition": edition,
        "citation": citation,
        "purpose": "reference",
    }
    if any(
        item.get("bookId") == source["bookId"] and item.get("citation") == citation
        for item in entity.get("sources", [])
    ):
        return False
    entity["sources"] = merge_unique(
        entity.get("sources"),
        [source],
        key=lambda item: json.dumps(item, sort_keys=True, ensure_ascii=False),
    )
    entity["editions"] = merge_unique(entity.get("editions"), [edition], key=str)
    descriptions = dict(entity.get("edition_descriptions", {}))
    if edition in descriptions:
        description = dict(descriptions[edition])
        description["sources"] = merge_unique(
            description.get("sources"),
            [source],
            key=lambda item: json.dumps(item, sort_keys=True, ensure_ascii=False),
        )
    else:
        preview = (
            entity.get("description_preview")
            or entity.get("summary")
            or f"{entity.get('name')} ist in {work['title']} belegt."
        )
        full = (
            entity.get("description_full")
            or entity.get("description")
            or preview
        )
        description = {
            "kind": "Quellennachweis",
            "preview": preview,
            "full": full,
            "hasMore": full != preview,
            "hasExcerpt": False,
            "sources": [source],
        }
    descriptions[edition] = description
    entity["edition_descriptions"] = descriptions
    return True


def augmentation_record(entity: dict, existing: dict | None) -> dict:
    result = dict(existing or {})
    result["id"] = entity["id"]
    result["editions"] = entity["editions"]
    result["sources"] = entity["sources"]
    result["edition_descriptions"] = entity["edition_descriptions"]
    return result


def relevant_city_works(coverage: dict, registry: dict, selected: set[str]):
    works = {work["id"]: work for work in registry["works"]}
    result: dict[str, dict[str, dict]] = defaultdict(dict)
    for row in coverage["matrix"]:
        work = works[row["workId"]]
        if not work["official"] or work["edition"] not in VALID_EDITIONS:
            continue
        for city_id, item in row["cities"].items():
            if city_id not in selected:
                continue
            if item["status"] in {"nur-volltexttreffer", "noch-zu-prüfen"} and (
                item["mentions"] >= 4
                or any(
                    alias.casefold() in work["title"].casefold()
                    for city in coverage["cities"]
                    if city["id"] == city_id
                    for alias in city["aliases"]
                )
            ):
                result[work["id"]][city_id] = item
    return result


def source_blocks(text: str) -> list[tuple[int | None, list[str]]]:
    """Split exports into PDF pages or bounded synthetic blocks."""
    lines = text.splitlines()
    if any(PAGE_PATTERN.match(line.strip()) for line in lines):
        result = []
        page = None
        block = []
        for line in lines:
            match = PAGE_PATTERN.match(line.strip())
            if match:
                if block:
                    result.append((page, block))
                page = int(match.group(1))
                block = []
            else:
                block.append(line)
        if block:
            result.append((page, block))
        return result
    return [(None, lines[index:index + 80]) for index in range(0, len(lines), 80)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--cities", nargs="+", required=True)
    arguments = parser.parse_args()

    registry = read_json(REGISTRY_PATH)
    coverage = read_json(COVERAGE_PATH)
    city_registry = read_json(ROOT / "data/cities.json")
    selected = set(arguments.cities)
    city_configs = {
        city["id"]: city for city in city_registry["cities"] if city["id"] in selected
    }
    missing = selected - set(city_configs)
    if missing:
        raise SystemExit(f"Unbekannte Stadtpakete: {', '.join(sorted(missing))}")

    city_state = {}
    pattern_targets: dict[str, list[tuple[str, str, dict]]] = defaultdict(list)
    matcher = AhoMatcher()
    for city_id, city in city_configs.items():
        state = load_city_entities(city)
        city_state[city_id] = state
        patterns = entity_patterns(city_id, state[2], state[3])
        for pattern, targets in patterns.items():
            if pattern not in pattern_targets:
                matcher.add(pattern)
            pattern_targets[pattern].extend(targets)
    matcher.build()

    relevant = relevant_city_works(coverage, registry, selected)
    works = {work["id"]: work for work in registry["works"]}
    city_aliases = {
        city["id"]: [alias.casefold() for alias in city["aliases"]]
        for city in coverage["cities"]
        if city["id"] in selected
    }
    known_titles = {}
    for city_id, state in city_state.items():
        manifest_path, manifest = state[0], state[1]
        sources = read_json(manifest_path.parent / manifest["files"]["sources"])
        known_titles[city_id] = {
            title_key(book["title"])
            for book in sources["books"]
            if not book.get("registryWorkId")
        }

    matches: dict[tuple[str, str, object, str], str] = {}
    work_city_links: Counter[tuple[str, str]] = Counter()
    for work_id, relevant_cities in relevant.items():
        work = works[work_id]
        eligible_cities = {
            city_id
            for city_id in relevant_cities
            if title_key(work["title"]) not in known_titles[city_id]
        }
        if not eligible_cities:
            continue
        path = arguments.corpus / work["primaryFile"]
        text = path.read_text(encoding="utf-8", errors="ignore")
        title = work["title"].casefold()
        focused_cities = {
            city_id
            for city_id in eligible_cities
            if any(alias in title for alias in city_aliases[city_id])
        }
        for page, block in source_blocks(text):
            block_text = "\n".join(block).casefold()
            block_cities = focused_cities | {
                city_id
                for city_id in eligible_cities
                if any(alias in block_text for alias in city_aliases[city_id])
            }
            if not block_cities:
                continue
            for raw_line in block:
                line = raw_line.casefold()
                for pattern in matcher.find(line):
                    for city_id, entity_type, entity in pattern_targets[pattern]:
                        if city_id not in block_cities:
                            continue
                        key = (city_id, entity_type, entity["id"], work_id)
                        if key in matches:
                            continue
                        citation = (
                            f"{work['title']}, PDF-Seite {page}"
                            if page
                            else f"{work['title']}, Textblock bei „{entity['name']}“"
                        )
                        matches[key] = citation
                        work_city_links[(work_id, city_id)] += 1

    for city_id, state in city_state.items():
        (
            manifest_path,
            manifest,
            places,
            people,
            archive_place_aug_path,
            archive_place_augmentations,
            archive_person_aug_path,
            archive_person_augmentations,
        ) = state
        city_dir = manifest_path.parent
        place_by_id = {feature["properties"]["id"]: feature["properties"] for feature in places}
        person_by_id = {person["id"]: person for person in people}
        place_aug_by_id = {item["id"]: item for item in archive_place_augmentations}
        person_aug_by_id = {item["id"]: item for item in archive_person_augmentations}
        linked_works = set()
        place_links = person_links = 0
        for (match_city, entity_type, entity_id, work_id), citation in matches.items():
            if match_city != city_id:
                continue
            work = works[work_id]
            entity = place_by_id[entity_id] if entity_type == "place" else person_by_id[entity_id]
            if not add_reference(entity, work, citation):
                continue
            linked_works.add(work_id)
            if entity_type == "place":
                place_aug_by_id[entity_id] = augmentation_record(
                    entity, place_aug_by_id.get(entity_id)
                )
                place_links += 1
            else:
                person_aug_by_id[entity_id] = augmentation_record(
                    entity, person_aug_by_id.get(entity_id)
                )
                person_links += 1

        if not linked_works:
            print(f"OK {city_id}: keine neuen exakten Archivverknüpfungen")
            continue

        archive_place_aug_path = (
            archive_place_aug_path or "archive-place-augmentations.json"
        )
        archive_person_aug_path = (
            archive_person_aug_path or "archive-person-augmentations.json"
        )
        manifest["files"]["archivePlaceAugmentations"] = archive_place_aug_path
        manifest["files"]["archivePersonAugmentations"] = archive_person_aug_path
        write_json(
            city_dir / archive_place_aug_path,
            sorted(place_aug_by_id.values(), key=lambda item: str(item["id"])),
        )
        write_json(
            city_dir / archive_person_aug_path,
            sorted(person_aug_by_id.values(), key=lambda item: str(item["id"])),
        )

        sources_path = city_dir / manifest["files"]["sources"]
        sources = read_json(sources_path)
        existing_ids = {book["id"] for book in sources["books"]}
        for work_id in sorted(linked_works):
            work = works[work_id]
            if work_id not in existing_ids:
                sources["books"].append(
                    {
                        "id": work_id,
                        "title": work["title"],
                        "edition": work["edition"],
                        "registryWorkId": work_id,
                    }
                )
        sources["books"].sort(key=lambda book: (book["edition"], book["title"].casefold()))
        write_json(sources_path, sources)
        manifest["availableEditions"] = sorted(
            {
                edition
                for entity in [*place_by_id.values(), *person_by_id.values()]
                for edition in entity["editions"]
            }
        )
        manifest["dataVersion"] = int(manifest.get("dataVersion", 0)) + 1
        write_json(manifest_path, manifest)
        write_json(
            city_dir / "archive-import-audit.json",
            {
                "schemaVersion": 1,
                "registry": "../source-registry.json",
                "linkedWorks": len(linked_works),
                "placeSourceLinks": place_links,
                "personSourceLinks": person_links,
                "workIds": sorted(linked_works),
            },
        )
        print(
            f"OK {city_id}: {len(linked_works)} Werke, "
            f"{place_links} Orts- und {person_links} Personenbelege"
        )

    for row in coverage["matrix"]:
        for city_id, item in row["cities"].items():
            links = work_city_links[(row["workId"], city_id)]
            if city_id in selected and links:
                item["reason"] = (
                    f"Teilimport: {links} exakte Verknüpfung(en) mit bereits "
                    "geprüften Orten, Personen oder Gruppen; Prüfung neuer "
                    "Kandidaten bleibt offen."
                )
                item["partialImport"] = {
                    "run": "archive-exact-reference-v1",
                    "entitySourceLinks": links,
                }
    status_counts = Counter(
        item["status"]
        for row in coverage["matrix"]
        for item in row["cities"].values()
    )
    coverage["statusCounts"] = dict(sorted(status_counts.items()))
    write_json(COVERAGE_PATH, coverage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
