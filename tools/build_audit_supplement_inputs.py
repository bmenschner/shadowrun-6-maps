#!/usr/bin/env python3
"""Convert accepted final audit decisions into publishable supplement inputs."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "source-data/final-dossier-decisions.jsonl"
REGISTRY = ROOT / "data/source-registry.json"
CITIES = ROOT / "data/cities.json"
OUTPUT_DIR = ROOT / "tools/source-supplements/audit"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fold(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    return value.encode("ascii", "ignore").decode("ascii").casefold()


def key(value: str) -> str:
    value = fold(value)
    value = re.sub(r"\([^)]*\)", " ", value)
    value = re.sub(
        r"\b(?:der|die|das|the|president|prasident|präsident)\b",
        " ",
        value,
    )
    replacements = {
        "brillant": "brilliant",
        "amerika": "america",
        "kunst museum": "art museum",
        "kunst museum": "art museum",
        "ave": "avenue",
        "rd": "road",
        "st": "street",
    }
    for old, new in replacements.items():
        value = re.sub(rf"\b{re.escape(old)}\b", new, value)
    value = re.sub(r"\b(?:and|und)\b|[&/]", " ", value)
    return re.sub(r"[^a-z0-9]+", "", value)


def name_score(value: str) -> tuple[int, int, int]:
    penalty = 0
    penalty += 4 * bool(re.search(r"\b(?:ath|gth|ist|olst)\b", value, re.I))
    penalty += 3 * bool(re.search(r"(?:-|,|/)\s*$", value))
    penalty += 2 * value.count("/")
    penalty += bool(re.search(r"\([^)]*\)", value))
    expanded = len(re.findall(r"\b(?:avenue|boulevard|road|street)\b", value, re.I))
    return (-penalty, expanded, -len(value))


def clean_name(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip(" \t,;:-")
    value = re.sub(r"\s+and$", "", value, flags=re.I)
    return value


def place_category(name: str) -> str:
    if re.search(r"\b(?:bar|cafe|café|club|pub|restaurant)\b", name, re.I):
        return "Bars, Clubs und Gastronomie"
    if re.search(r"\b(?:hospital|clinic|klinik|krankenhaus)\b", name, re.I):
        return "Medizin und Versorgung"
    if re.search(r"\b(?:airport|flughafen|station|bahnhof|bridge|brücke)\b", name, re.I):
        return "Verkehr und Infrastruktur"
    if re.search(r"\b(?:arcology|arkologie|tower|turm|headquarters)\b", name, re.I):
        return "Konzerne und markante Bauwerke"
    if re.search(r"\b(?:district|bezirk|viertel|zone|barrens)\b", name, re.I):
        return "Bezirke und Lore-Gebiete"
    return "Sonstige Spots"


def summary(name: str, entity_type: str, work_title: str, city_name: str) -> str:
    if entity_type == "place":
        return (
            f"{name} ist in {work_title} als benannter Schauplatz mit "
            f"Bezug zu {city_name} belegt."
        )
    if entity_type == "group":
        return (
            f"{name} ist in {work_title} als benannte Gruppe oder "
            f"Organisation mit Bezug zu {city_name} belegt."
        )
    return (
        f"{name} ist in {work_title} als Person von Interesse mit "
        f"Bezug zu {city_name} belegt."
    )


def main() -> int:
    works = {work["id"]: work for work in read_json(REGISTRY)["works"]}
    cities = read_json(CITIES)["cities"]
    city_names = {city["id"]: city["name"] for city in cities}
    manifest_versions = {
        city["id"]: int(
            read_json(ROOT / city["manifest"]).get("dataVersion", 1)
        )
        for city in cities
    }
    decisions = [
        json.loads(line)
        for line in DECISIONS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    grouped: dict[tuple[str, str], dict] = {}
    for decision in decisions:
        if decision["status"] != "accepted":
            continue
        name = clean_name(decision["name"])
        entity_type = decision["entityType"]
        group_key = (decision["cityId"], key(name))
        current = grouped.get(group_key)
        if current is None:
            current = {
                "cityId": decision["cityId"],
                "name": name,
                "entityType": entity_type,
                "aliases": set(),
                "sources": [],
            }
            grouped[group_key] = current
        else:
            if name != current["name"]:
                if name_score(name) > name_score(current["name"]):
                    current["aliases"].add(current["name"])
                    current["name"] = name
                else:
                    current["aliases"].add(name)
            if current["entityType"] != entity_type:
                priority = {"group": 3, "place": 2, "person": 1}
                if priority[entity_type] > priority[current["entityType"]]:
                    current["entityType"] = entity_type
        for source in decision["acceptedSources"]:
            source_key = (source["workId"], source["locator"])
            if source_key not in {
                (item["workId"], item["locator"])
                for item in current["sources"]
            }:
                current["sources"].append(source)

    payloads: dict[str, dict] = defaultdict(
        lambda: {"places": [], "people": []}
    )
    for item in sorted(
        grouped.values(),
        key=lambda row: (row["cityId"], fold(row["name"])),
    ):
        appearances = []
        for source in item["sources"]:
            work = works[source["workId"]]
            appearances.append({
                "bookId": source["workId"],
                "citation": source["locator"],
                "summary": summary(
                    item["name"],
                    item["entityType"],
                    work["title"],
                    city_names[item["cityId"]],
                ),
            })
        if not appearances:
            continue
        if item["entityType"] == "place":
            payloads[item["cityId"]]["places"].append({
                "name": item["name"],
                "aliases": sorted(item["aliases"], key=fold),
                "category": place_category(item["name"]),
                "scope": city_names[item["cityId"]],
                "appearances": appearances,
            })
        else:
            payloads[item["cityId"]]["people"].append({
                "name": item["name"],
                "aliases": sorted(item["aliases"], key=fold),
                "entity_type": item["entityType"],
                "category": (
                    "Gruppen und Organisationen"
                    if item["entityType"] == "group"
                    else "Personen von Interesse"
                ),
                "role": (
                    "Lokale Gruppe oder Organisation"
                    if item["entityType"] == "group"
                    else "Person von Interesse"
                ),
                "affiliation": city_names[item["cityId"]],
                "scope": city_names[item["cityId"]],
                "appearances": appearances,
            })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    expected = set()
    total_places = total_people = 0
    for city_id, payload in sorted(payloads.items()):
        output_path = OUTPUT_DIR / f"{city_id}.json"
        expected.add(output_path)
        data = {
            "schemaVersion": 1,
            "dataVersion": manifest_versions[city_id] + 1,
            "places": payload["places"],
            "people": payload["people"],
        }
        output_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        total_places += len(payload["places"])
        total_people += len(payload["people"])

    for path in OUTPUT_DIR.glob("*.json"):
        if path not in expected:
            path.unlink()
    print(
        f"OK Audit-Supplemente: {len(payloads)} Städte, "
        f"{total_places} Orte, {total_people} Personen/Gruppen"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
