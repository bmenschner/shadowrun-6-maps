#!/usr/bin/env python3
"""Build the central Shadowrun source registry and city coverage matrix.

The source texts remain outside the repository.  This script records stable
work identities, file variants, exact duplicates, editions, source types and
city relevance without copying copyrighted source text into the project.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = Path("/mnt/c/Users/Privat/Documents/Shadowrun/txtexports")
REGISTRY_PATH = ROOT / "data/source-registry.json"
COVERAGE_PATH = ROOT / "data/source-coverage.json"


CITY_DEFINITIONS = [
    ("berlin-2080", "Berlin", ["Berlin"]),
    ("hamburg-2080", "Hamburg", ["Hamburg"]),
    ("seattle", "Seattle", ["Seattle"]),
    ("rhein-ruhr-2082", "Rhein-Ruhr-Megaplex", ["Rhein-Ruhr", "Ruhrplex", "Ruhrgebiet", "Neu-Essen", "Duisport"]),
    ("toronto-2080", "Toronto", ["Toronto"]),
    ("denver", "Denver", ["Denver"]),
    ("manhattan", "Manhattan", ["Manhattan"]),
    ("adl-2082", "ADL", ["Allianz Deutscher Länder", "ADL"]),
    ("chicago", "Chicago", ["Chicago"]),
    ("boston", "Boston", ["Boston"]),
    ("hong-kong", "Hongkong", ["Hongkong", "Hong Kong"]),
    ("london", "London", ["London"]),
    ("muenchen", "München", ["München", "Munich"]),
    ("frankfurt", "Frankfurt", ["Frankfurt"]),
    ("san-francisco", "San Francisco", ["San Francisco"]),
    ("cheyenne", "Cheyenne", ["Cheyenne"]),
    ("karlsruhe", "Karlsruhe", ["Karlsruhe"]),
    ("new-orleans", "New Orleans", ["New Orleans"]),
    ("paris", "Paris", ["Paris"]),
    ("montreal", "Montreal", ["Montréal", "Montreal"]),
    ("neo-tokio", "Neo-Tokio", ["Neo-Tokio", "Neo-Tokyo", "Neo Tokyo", "Tokyo", "Tokio"]),
    ("washington-fdc", "Washington FDC", ["Washington FDC", "Washington, FDC", "Washington D.C.", "Washington DC"]),
    ("los-angeles", "Los Angeles", ["Los Angeles"]),
    ("bogota", "Bogotá", ["Bogotá", "Bogota"]),
    ("lagos", "Lagos", ["Lagos"]),
    ("detroit", "Detroit", ["Detroit"]),
    ("atlanta", "Atlanta", ["Atlanta"]),
    ("portland", "Portland", ["Portland"]),
    ("wien", "Wien", ["Wien", "Vienna"]),
    ("kairo", "Kairo", ["Kairo", "Cairo"]),
    ("metropole", "Metrópole", ["Metrópole", "Metropole"]),
    ("butte", "Butte", ["Butte"]),
    ("casablanca-rabat", "Casablanca-Rabat", ["Casablanca", "Rabat"]),
    ("vladivostok", "Vladivostok", ["Vladivostok", "Wladiwostok"]),
    ("zuerich", "Zürich", ["Zürich", "Zurich"]),
    ("leipzig-halle", "Leipzig-Halle", ["Leipzig", "Halle"]),
    ("quebec", "Québec", ["Québec", "Quebec"]),
    ("bremen", "Bremen", ["Bremen"]),
    ("hannover", "Hannover", ["Hannover", "Hanover"]),
    ("istanbul", "Istanbul", ["Istanbul"]),
    ("tenochtitlan", "Mexiko-Stadt/Tenochtitlán", ["Tenochtitlán", "Tenochtitlan", "Mexico City", "Mexiko-Stadt"]),
    ("stuttgart", "Stuttgart", ["Stuttgart"]),
    ("caracas", "Caracas", ["Caracas"]),
    ("st-louis", "St. Louis", ["St. Louis", "Saint Louis"]),
    ("santiago", "Santiago", ["Santiago"]),
    ("sydney", "Sydney", ["Sydney"]),
    ("austin", "Austin", ["Austin"]),
    ("dublin", "Dublin", ["Dublin"]),
    ("dubai", "Dubai", ["Dubai"]),
    ("las-vegas", "Las Vegas", ["Las Vegas"]),
    ("singapur", "Singapur", ["Singapur", "Singapore"]),
    ("kapstadt", "Kapstadt", ["Kapstadt", "Cape Town"]),
    ("nuernberg", "Nürnberg", ["Nürnberg", "Nuremberg"]),
    ("baltimore", "Baltimore", ["Baltimore"]),
    ("nairobi", "Nairobi", ["Nairobi"]),
    ("manaus", "Manaus", ["Manaus"]),
    ("bruessel", "Brüssel", ["Brüssel", "Brussels", "Bruxelles"]),
    ("perth", "Perth", ["Perth"]),
    ("sarajevo", "Sarajevo", ["Sarajevo"]),
    ("vancouver", "Vancouver", ["Vancouver"]),
    ("san-diego", "San Diego", ["San Diego"]),
    ("lima", "Lima", ["Lima"]),
    ("buenos-aires", "Buenos Aires", ["Buenos Aires"]),
    ("havanna", "Havanna", ["Havanna", "Havana"]),
    ("dallas-fort-worth", "Dallas/Fort Worth", ["Dallas", "Fort Worth"]),
    ("prag", "Prag", ["Prag", "Prague"]),
    ("miami", "Miami", ["Miami"]),
    ("teheran", "Teheran", ["Teheran", "Tehran"]),
    ("melbourne", "Melbourne", ["Melbourne"]),
    ("salt-lake-city", "Salt Lake City", ["Salt Lake City"]),
    ("manila", "Manila", ["Manila"]),
    ("johannesburg", "Johannesburg", ["Johannesburg"]),
    ("phoenix", "Phoenix", ["Phoenix"]),
    ("brisbane", "Brisbane", ["Brisbane"]),
    ("bangkok", "Bangkok", ["Bangkok"]),
]


TYPE_RULES = [
    ("Karte", re.compile(r"\b(map|karte|stadtplan|netzspinne)\b", re.I)),
    ("Nachrichtenmaterial", re.compile(r"(nova|extra|mega)puls|schattenload|extraload", re.I)),
    ("Handout", re.compile(r"\b(handout|karteikarte|character card|archetype)\b", re.I)),
    ("Regelwerk", re.compile(r"grundregelwerk|core rulebook|rulebook|kompendium|companion|arsenal|grimoire|rigger|matrix|cybertechnology|street grimoire", re.I)),
    ("Abenteuer", re.compile(r"abenteuer|mission|srm\d|kampagne|adventure|run faster|schnell und dreckig", re.I)),
    ("Roman", re.compile(r"\broman\b|novel", re.I)),
    ("Quellenband", re.compile(r"sourcebook|quellenbuch|datapuls|reiseführer|almanach|shadows of|in den schatten|state of the art|brennpunkt", re.I)),
]


TITLE_NOISE = [
    r"^\d+\s+",
    r"^(?:E-)?FAS\d+\s+",
    r"^Shadowrun\s+[1-6](?:D|E|e|d|D6)?\s*-\s*",
    r"^Shadowrun\s+[1-6]\s*[-–]\s*",
    r"\s*\((?:searchable|scan|ocr|original pdf|compressed|foto|highres)[^)]*\)\s*$",
    r"\s*\[(?:19|20)\d{2}[^\]]*]\s*$",
    r"\s*\[(?:v?[\d.]+|OEF|DTRPG|OCR)[^\]]*]\s*$",
]


@dataclass
class FileRecord:
    relative_path: str
    edition: str
    language: str
    title: str
    title_key: str
    source_type: str
    official: bool
    sha256: str
    bytes: int
    city_mentions: dict[str, int]


class UnionFind:
    def __init__(self, count: int) -> None:
        self.parent = list(range(count))

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, first: int, second: int) -> None:
        first_root = self.find(first)
        second_root = self.find(second)
        if first_root != second_root:
            self.parent[second_root] = first_root


def fold(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    return value.casefold()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", fold(value)).strip("-")


def clean_title(path: Path) -> str:
    title = path.stem.strip()
    for pattern in TITLE_NOISE:
        title = re.sub(pattern, "", title, flags=re.I)
    title = re.sub(r"\s+", " ", title).strip(" -–")
    return title or path.stem


def title_key(title: str) -> str:
    value = fold(title)
    value = re.sub(r"\b(?:shadowrun|sr)\b", " ", value)
    value = re.sub(r"\b(?:searchable|scan|ocr|original|pdf|compressed|highres|lowres|auflage)\b", " ", value)
    value = re.sub(r"\b(?:v|version)\s*\d+(?:\.\d+)*\b", " ", value)
    return re.sub(r"[^a-z0-9]+", "", value)


def infer_edition(relative: Path) -> str:
    match = re.search(r"Shadowrun\s+([1-6])", relative.as_posix(), re.I)
    return f"SR{match.group(1)}" if match else "unbekannt"


def infer_language(path: Path, title: str) -> str:
    name = path.name
    if re.search(r"Shadowrun\s+[1-6]D\b", name, re.I):
        return "de"
    if re.search(r"Shadowrun\s+[1-6](?:E|e)\b", name):
        return "en"
    german_markers = (" der ", " die ", " das ", " und ", "schatten", "quellen", "abenteuer", "regelwerk")
    return "de" if any(marker in f" {fold(title)} " for marker in german_markers) else "unbekannt"


def infer_type(relative: Path, title: str) -> str:
    context = f"{relative.as_posix()} {title}"
    for source_type, pattern in TYPE_RULES:
        if pattern.search(context):
            return source_type
    return "Sonstiges"


def is_official(relative: Path, title: str) -> bool:
    context = fold(f"{relative.as_posix()} {title}")
    return not any(marker in context for marker in ("fanstuff", "inoffiziell", "fan made", "fanmade"))


def compile_city_pattern() -> tuple[re.Pattern[str], dict[str, set[str]]]:
    aliases_to_cities: dict[str, set[str]] = defaultdict(set)
    alias_display: dict[str, str] = {}
    for city_id, _, city_aliases in CITY_DEFINITIONS:
        for alias in city_aliases:
            key = fold(alias)
            aliases_to_cities[key].add(city_id)
            alias_display.setdefault(key, alias)
    alternatives = sorted((re.escape(alias) for alias in alias_display.values()), key=len, reverse=True)
    pattern = re.compile(r"(?<!\w)(?:" + "|".join(alternatives) + r")(?!\w)", re.I)
    return pattern, aliases_to_cities


def load_existing_source_titles() -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    cities = json.loads((ROOT / "data/cities.json").read_text(encoding="utf-8"))
    for city in cities["cities"]:
        manifest_path = ROOT / city["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        source_path = manifest_path.parent / manifest["files"]["sources"]
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        result[city["id"]] = {
            title_key(book["title"])
            for book in payload.get("books", [])
            if not book.get("registryWorkId")
        }
    return result


def scan_files(corpus: Path) -> list[FileRecord]:
    city_pattern, aliases_to_cities = compile_city_pattern()
    records = []
    for path in sorted(corpus.rglob("*.txt"), key=lambda item: fold(item.as_posix())):
        payload = path.read_bytes()
        text = payload.decode("utf-8", errors="ignore")
        relative = path.relative_to(corpus)
        title = clean_title(relative)
        mentions: Counter[str] = Counter()
        for match in city_pattern.finditer(text):
            for city_id in aliases_to_cities[fold(match.group(0))]:
                mentions[city_id] += 1
        records.append(
            FileRecord(
                relative_path=relative.as_posix(),
                edition=infer_edition(relative),
                language=infer_language(relative, title),
                title=title,
                title_key=title_key(title),
                source_type=infer_type(relative, title),
                official=is_official(relative, title),
                sha256=hashlib.sha256(payload).hexdigest(),
                bytes=len(payload),
                city_mentions=dict(mentions),
            )
        )
    return records


def group_works(records: list[FileRecord]) -> list[list[int]]:
    union = UnionFind(len(records))
    by_hash: dict[str, int] = {}
    by_title: dict[tuple[str, str], int] = {}
    for index, record in enumerate(records):
        if record.sha256 in by_hash:
            union.union(index, by_hash[record.sha256])
        else:
            by_hash[record.sha256] = index
        key = (record.edition, record.title_key)
        if record.title_key and key in by_title:
            union.union(index, by_title[key])
        elif record.title_key:
            by_title[key] = index
    groups: dict[int, list[int]] = defaultdict(list)
    for index in range(len(records)):
        groups[union.find(index)].append(index)
    return sorted(groups.values(), key=lambda group: fold(records[group[0]].title))


def primary_index(group: list[int], records: list[FileRecord]) -> int:
    return max(
        group,
        key=lambda index: (
            records[index].official,
            records[index].language == "de",
            records[index].bytes,
            -len(records[index].relative_path),
        ),
    )


def build_payloads(records: list[FileRecord], groups: list[list[int]]) -> tuple[dict, dict]:
    existing_titles = load_existing_source_titles()
    city_names = {city_id: name for city_id, name, _ in CITY_DEFINITIONS}
    city_package_ids = set(existing_titles)
    used_ids: Counter[str] = Counter()
    works = []
    coverage_rows = []
    status_counts: Counter[str] = Counter()

    for group in groups:
        primary = records[primary_index(group, records)]
        base_id = f"{primary.edition.casefold()}-{slug(primary.title) or primary.sha256[:12]}"
        used_ids[base_id] += 1
        work_id = base_id if used_ids[base_id] == 1 else f"{base_id}-{primary.sha256[:8]}"
        hashes = Counter(records[index].sha256 for index in group)
        city_mentions: Counter[str] = Counter()
        for index in group:
            city_mentions.update(records[index].city_mentions)

        official = all(records[index].official for index in group)
        files = []
        first_for_hash: dict[str, str] = {}
        for index in sorted(group, key=lambda value: records[value].relative_path):
            record = records[index]
            duplicate_of = first_for_hash.get(record.sha256)
            if not duplicate_of:
                first_for_hash[record.sha256] = record.relative_path
            files.append(
                {
                    "path": record.relative_path,
                    "sha256": record.sha256,
                    "bytes": record.bytes,
                    "language": record.language,
                    "exactDuplicateOf": duplicate_of,
                }
            )

        relevant_cities = []
        city_status = {}
        for city_id, count in sorted(city_mentions.items(), key=lambda item: (-item[1], item[0])):
            if not official:
                status = "nichtoffiziell-ausgeschlossen"
                reason = "Nichtoffizielle Quelle; wird nicht mit offizieller Lore vermischt."
            elif primary.title_key in existing_titles.get(city_id, set()):
                status = "zusammengeführt"
                reason = "Titel ist bereits im Quellenkatalog des Stadtpakets enthalten."
            elif count >= 2:
                status = "nur-volltexttreffer"
                reason = "Stadtbezug erkannt; redaktioneller Werk-/Stadt-Abgleich steht noch aus."
            else:
                status = "noch-zu-prüfen"
                reason = "Einzelne Stadtnennung; lokaler oder beiläufiger Bezug muss geprüft werden."
            status_counts[status] += 1
            city_status[city_id] = {
                "status": status,
                "mentions": count,
                "reason": reason,
                "cityPackageExists": city_id in city_package_ids,
            }
            relevant_cities.append(
                {
                    "id": city_id,
                    "name": city_names[city_id],
                    "mentions": count,
                }
            )

        work = {
            "id": work_id,
            "title": primary.title,
            "edition": primary.edition,
            "language": primary.language,
            "type": primary.source_type,
            "official": official,
            "primaryFile": primary.relative_path,
            "variants": sorted({records[index].title for index in group}),
            "contentHashes": sorted(hashes),
            "files": files,
            "relevantCities": relevant_cities,
        }
        works.append(work)
        coverage_rows.append(
            {
                "workId": work_id,
                "defaultStatus": (
                    "nichtoffiziell-ausgeschlossen"
                    if not official
                    else "geprüft-ohne-relevanten-inhalt"
                ),
                "cities": city_status,
            }
        )

    registry = {
        "schemaVersion": 1,
        "generated": date.today().isoformat(),
        "sourceRoot": "C:/Users/Privat/Documents/Shadowrun/txtexports",
        "summary": {
            "files": len(records),
            "works": len(works),
            "exactDuplicateFiles": sum(
                1 for work in works for file in work["files"] if file["exactDuplicateOf"]
            ),
            "officialWorks": sum(work["official"] for work in works),
            "nonOfficialWorks": sum(not work["official"] for work in works),
        },
        "works": works,
    }
    coverage = {
        "schemaVersion": 1,
        "generated": date.today().isoformat(),
        "registry": "source-registry.json",
        "cities": [
            {
                "id": city_id,
                "name": name,
                "packageExists": city_id in city_package_ids,
                "aliases": aliases,
            }
            for city_id, name, aliases in CITY_DEFINITIONS
        ],
        "statusCounts": dict(sorted(status_counts.items())),
        "matrix": coverage_rows,
    }
    return registry, coverage


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    arguments = parser.parse_args()
    if not arguments.corpus.exists():
        raise SystemExit(f"Quellenordner fehlt: {arguments.corpus}")
    records = scan_files(arguments.corpus)
    groups = group_works(records)
    registry, coverage = build_payloads(records, groups)
    write_json(REGISTRY_PATH, registry)
    write_json(COVERAGE_PATH, coverage)
    print(
        "OK Quellenregister: "
        f"{registry['summary']['files']} Dateien, "
        f"{registry['summary']['works']} Werke, "
        f"{registry['summary']['exactDuplicateFiles']} exakte Dubletten"
    )
    print(
        "OK Abdeckungsmatrix: "
        f"{len(coverage['cities'])} Städte/Regionen, "
        f"{sum(coverage['statusCounts'].values())} relevante Werk-/Stadt-Bezüge"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
