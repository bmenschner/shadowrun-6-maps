#!/usr/bin/env python3
"""Extract review candidates from every city-relevant source work.

The generated JSONL file is intentionally stored below ``source-data`` and is
ignored by Git.  It contains short local contexts from copyrighted source
texts and therefore must never be published with the application.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = Path("/mnt/c/Users/Privat/Documents/Shadowrun/txtexports")
REGISTRY_PATH = ROOT / "data/source-registry.json"
COVERAGE_PATH = ROOT / "data/source-coverage.json"
OUTPUT_PATH = ROOT / "source-data/import-candidates.jsonl"

PAGE_PATTERN = re.compile(r"^===== PDF-Seite (\d+) =====$")
HEADING_PATTERN = re.compile(
    r"^[A-ZÄÖÜ0-9][A-Za-zÀ-ÖØ-öø-ÿÄÖÜäöüß0-9&'’.,:/+() -]{1,78}$"
)
PERSON_PATTERN = re.compile(
    r"^(?:Dr\.?|Prof\.?|Captain|Major|Colonel|General|Detective|Kommissar(?:in)?|"
    r"Doktor|Herr|Frau|Mr\.?|Mrs\.?|Ms\.?)?\s*"
    r"[A-ZÄÖÜ][A-Za-zÀ-ÖØ-öø-ÿÄÖÜäöüß'’.-]+"
    r"(?:\s+[„“\"']?[A-ZÄÖÜ][A-Za-zÀ-ÖØ-öø-ÿÄÖÜäöüß'’.-]+[”\"']?){1,4}$"
)

PLACE_WORDS = re.compile(
    r"\b(club|bar|pub|hotel|restaurant|cafe|café|shop|store|mall|markt|market|"
    r"tower|turm|building|gebäude|arcology|arkologie|hospital|klinik|airport|"
    r"flughafen|station|bahnhof|park|street|straße|strasse|avenue|road|weg|platz|"
    r"dock|hafen|district|bezirk|neighborhood|viertel|kiez|zone|barrens|sprawl|"
    r"headquarter|hauptquartier|labor|lab|factory|werk|schule|school|university|"
    r"universität|museum|theater|casino|bunker|base|basis|temple|tempel)\b",
    re.I,
)
GROUP_WORDS = re.compile(
    r"\b(gang|syndikat|syndicate|mafia|yakuza|triad|triade|vory|crew|team|"
    r"organisation|organization|gruppe|group|kult|cult|fraktion|faction|"
    r"aktivisten|activists|security force|sicherheitskräfte|polizei|police|"
    r"familie|family|clan|go-gang|motocycle club|mc)\b",
    re.I,
)
PERSON_WORDS = re.compile(
    r"\b(contact|kontakt|person|npc|nsc|fixer|schieber|runner|shadowrunner|"
    r"bürgermeister|mayor|präsident|president|captain|kommissar|detective|"
    r"magier|mage|decker|rigger|samurai|owner|besitzer|leiter|director|chef|"
    r"ceo|chief|chairman|chairwoman|vorsitzende|führer|leader|boss|wirt|wirtin|"
    r"manager|sprecher|sprecherin|kommandant|commander|doktor|doctor)\b",
    re.I,
)
REJECT_PATTERN = re.compile(
    r"^(contents?|credits?|index|introduction|einleitung|inhalt|kapitel|chapter|"
    r"shadowrun|spielwerte|game information|für die spielleitung|adventure summary|"
    r"pdf-seite|seite|table|tabelle|abbildung|figure|abenteuer\w*|adventure\w*|"
    r"hintergrund|background|security|sicherheit|history|geschichte|government|"
    r"regierung|economy|wirtschaft|magic|magie|crime|kriminalität|contacts?|"
    r"kontakte?|locations?|orte|people|personen|places?|districts?|bezirke|"
    r"neighborhoods?|stadtteile|game|spiel|runner|mission|scene|szene|legwork|"
    r"nachforschungen|matrix|astral|conclusion|zusammenfassung|beschreibung|"
    r"overview|übersicht|news|nachrichten|timeline|chronik)\b",
    re.I,
)
PERSON_NAME_STOPWORDS = {
    "der", "die", "das", "den", "dem", "des", "ein", "eine", "einer",
    "the", "a", "an", "of", "and", "und", "im", "in", "am", "auf",
    "chapter", "kapitel", "mission", "scene", "szene", "table", "tabelle",
}


def fold(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    return value.encode("ascii", "ignore").decode("ascii").casefold()


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", fold(value))


def normalized_city_aliases(coverage: dict) -> dict[str, list[str]]:
    result = {}
    for city in coverage["cities"]:
        result[city["id"]] = [
            re.sub(r"[^a-z0-9]+", " ", fold(alias)).strip()
            for alias in city["aliases"]
        ]
    return result


def pages(text: str) -> list[tuple[int | None, list[str]]]:
    result: list[tuple[int | None, list[str]]] = []
    page_number: int | None = None
    lines: list[str] = []
    for raw in text.splitlines():
        match = PAGE_PATTERN.match(raw.strip())
        if match:
            if lines:
                result.append((page_number, lines))
            page_number = int(match.group(1))
            lines = []
        else:
            lines.append(raw.rstrip())
    if lines:
        result.append((page_number, lines))
    return result


def is_heading(line: str) -> bool:
    line = re.sub(r"\s+", " ", line).strip(" •·\t")
    if not 3 <= len(line) <= 80 or REJECT_PATTERN.search(line):
        return False
    if not line[0].isalpha() or any(character.isdigit() for character in line):
        return False
    if ":" in line or re.search(r"\.\s+[A-ZÄÖÜ]", line):
        return False
    if fold(line.split()[-1].strip(".,()")) in {"der", "die", "das", "the", "a", "an"}:
        return False
    if line.endswith((".", "!", "?", ";", ",")) or line.count(" ") > 5:
        return False
    if not HEADING_PATTERN.match(line):
        return False
    letters = [character for character in line if character.isalpha()]
    if not letters or len(letters) / len(line) < 0.62:
        return False
    upper_ratio = sum(character.isupper() for character in letters) / len(letters)
    title_words = sum(
        bool(re.match(r"^[A-ZÄÖÜ0-9]", word))
        for word in line.split()
        if word.casefold() not in {"der", "die", "das", "des", "den", "von", "und", "of", "the", "in", "im", "am"}
    )
    return upper_ratio >= 0.45 or title_words >= max(1, len(line.split()) - 2)


def looks_like_person(name: str) -> bool:
    cleaned = re.sub(
        r"^(?:Dr\.?|Prof\.?|Captain|Major|Colonel|General|Detective|Kommissar(?:in)?|"
        r"Doktor|Herr|Frau|Mr\.?|Mrs\.?|Ms\.?)\s+",
        "",
        name,
        flags=re.I,
    )
    words = [word.strip("„“\"'’.,()") for word in cleaned.split()]
    if not 2 <= len(words) <= 5:
        return False
    if any(fold(word) in PERSON_NAME_STOPWORDS for word in words):
        return False
    return all(word and word[0].isupper() for word in words)


def classify(name: str, context: str) -> tuple[str, float]:
    direct = context[:420]
    relation = re.compile(
        r"\b(ist|sind|war|waren|liegt|befindet|führt|leitet|betreibt|gehört|"
        r"is|are|was|were|located|runs|leads|owns|serves|works)\b",
        re.I,
    )
    scores = {
        "group": (
            0.9 if GROUP_WORDS.search(name)
            else 0.82 if GROUP_WORDS.search(direct) and relation.search(direct)
            else 0.0
        ),
        "place": (
            0.9 if PLACE_WORDS.search(name)
            else 0.82 if PLACE_WORDS.search(direct) and relation.search(direct)
            else 0.0
        ),
        "person": (
            0.86 if looks_like_person(name)
            and PERSON_WORDS.search(direct)
            else 0.0
        ),
    }
    entity_type = max(scores, key=scores.get)
    score = scores[entity_type]
    return (entity_type if score else "unknown", score or 0.45)


def extract_for_work(
    work: dict,
    text: str,
    relevant_cities: set[str],
    city_aliases: dict[str, list[str]],
) -> list[dict]:
    candidates: dict[tuple[str, str, str], dict] = {}
    folded_title = " " + re.sub(r"[^a-z0-9]+", " ", fold(work["title"])) + " "
    focused_cities = {
        city_id
        for city_id in relevant_cities
        if any(f" {alias} " in folded_title for alias in city_aliases[city_id])
    }
    for page_number, page_lines in pages(text):
        folded_lines = [
            " " + re.sub(r"[^a-z0-9]+", " ", fold(line)) + " "
            for line in page_lines
        ]
        mention_lines = {
            city_id: [
                index
                for index, line in enumerate(folded_lines)
                if any(f" {alias} " in line for alias in city_aliases[city_id])
            ]
            for city_id in relevant_cities
        }
        page_cities = focused_cities | {
            city_id for city_id, indices in mention_lines.items() if indices
        }
        if not page_cities:
            continue
        for index, raw in enumerate(page_lines):
            name = re.sub(r"\s+", " ", raw).strip(" •·\t")
            if not is_heading(name):
                continue
            previous_blank = index == 0 or not page_lines[index - 1].strip()
            letters = [character for character in name if character.isalpha()]
            mostly_upper = bool(letters) and (
                sum(character.isupper() for character in letters) / len(letters) >= 0.72
            )
            if not previous_blank and not mostly_upper:
                continue
            candidate_cities = {
                city_id
                for city_id in page_cities
                if city_id in focused_cities
                or any(abs(index - mention_index) <= 10 for mention_index in mention_lines[city_id])
            }
            if not candidate_cities:
                continue
            context_lines = [
                re.sub(r"\s+", " ", line).strip()
                for line in page_lines[index: min(len(page_lines), index + 6)]
                if line.strip()
            ]
            context = " ".join(context_lines)
            if len(context) > 700:
                context = context[:697].rstrip() + "…"
            entity_type, confidence = classify(name, context)
            if entity_type == "unknown" or confidence < 0.78:
                continue
            normalized = normalize_name(name)
            if not normalized:
                continue
            for city_id in candidate_cities:
                key = (city_id, normalized, entity_type)
                if key in candidates:
                    continue
                candidates[key] = {
                    "candidateId": f"{work['id']}:{city_id}:{normalized}:{entity_type}",
                    "workId": work["id"],
                    "edition": work["edition"],
                    "cityId": city_id,
                    "rawName": name,
                    "entityType": entity_type,
                    "confidence": confidence,
                    "locator": f"PDF-Seite {page_number}" if page_number else "Seitenstruktur fehlt",
                    "context": context,
                    "status": "offen",
                }
    return list(candidates.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument(
        "--cities",
        nargs="*",
        help="Optional list of city IDs; without this option every city is processed.",
    )
    arguments = parser.parse_args()
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    coverage = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    city_aliases = normalized_city_aliases(coverage)
    works = {work["id"]: work for work in registry["works"]}
    rows = {row["workId"]: row for row in coverage["matrix"]}
    selected_cities = set(arguments.cities or ())
    output_by_entity: dict[tuple[str, str, str], dict] = {}
    for work_id, work in works.items():
        if not work["official"]:
            continue
        relevant = {
            city_id
            for city_id, item in rows[work_id]["cities"].items()
            if item["status"] in {"nur-volltexttreffer", "noch-zu-prüfen"}
            and (not selected_cities or city_id in selected_cities)
        }
        if not relevant:
            continue
        path = arguments.corpus / work["primaryFile"]
        text = path.read_text(encoding="utf-8", errors="ignore")
        candidates = extract_for_work(
            work,
            text,
            relevant,
            city_aliases,
        )
        for candidate in candidates:
            key = (
                candidate["cityId"],
                normalize_name(candidate["rawName"]),
                candidate["entityType"],
            )
            occurrence = {
                "workId": candidate.pop("workId"),
                "edition": candidate.pop("edition"),
                "locator": candidate.pop("locator"),
                "context": candidate.pop("context"),
                "confidence": candidate["confidence"],
            }
            current = output_by_entity.get(key)
            if current is None:
                candidate["candidateId"] = (
                    f"{candidate['cityId']}:{key[1]}:{candidate['entityType']}"
                )
                candidate["occurrences"] = [occurrence]
                output_by_entity[key] = candidate
            elif len(current["occurrences"]) < 25 and not any(
                item["workId"] == occurrence["workId"]
                and item["locator"] == occurrence["locator"]
                for item in current["occurrences"]
            ):
                current["occurrences"].append(occurrence)
                current["confidence"] = max(current["confidence"], occurrence["confidence"])
    output = sorted(
        output_by_entity.values(),
        key=lambda item: (item["cityId"], fold(item["rawName"]), item["entityType"]),
    )
    per_city = defaultdict(int)
    for candidate in output:
        per_city[candidate["cityId"]] += 1
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        for candidate in output:
            handle.write(json.dumps(candidate, ensure_ascii=False, separators=(",", ":")) + "\n")
    summary_path = OUTPUT_PATH.with_name("import-candidates-summary.json")
    summary_path.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "candidates": len(output),
                "perCity": dict(sorted(per_city.items())),
                "published": False,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"OK Kandidaten: {len(output)} in {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
