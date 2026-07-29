#!/usr/bin/env python3
"""Extract local-only mention snippets for open relations without candidates."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = Path("/mnt/c/Users/Privat/Documents/Shadowrun/txtexports")
OUTPUT = ROOT / "source-data/open-relation-mentions.jsonl"
SUMMARY = ROOT / "source-data/open-relation-mentions-summary.json"


def fold(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    return value.encode("ascii", "ignore").decode("ascii").casefold()


def normalize_search(value: str) -> str:
    """Fold accents without deleting punctuation before word separation."""
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def main() -> int:
    coverage = json.loads(
        (ROOT / "data/source-coverage.json").read_text(encoding="utf-8")
    )
    registry = json.loads(
        (ROOT / "data/source-registry.json").read_text(encoding="utf-8")
    )
    works = {work["id"]: work for work in registry["works"]}
    aliases = {
        city["id"]: [
            normalize_search(alias)
            for alias in city["aliases"]
        ]
        for city in coverage["cities"]
    }
    relations_with_candidates = set()
    decisions_path = ROOT / "source-data/candidate-decisions.jsonl"
    for line in decisions_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        decision = json.loads(line)
        for occurrence in decision.get("occurrences", []):
            relations_with_candidates.add(
                (occurrence["workId"], decision["cityId"])
            )

    open_relations: dict[str, list[str]] = defaultdict(list)
    for row in coverage["matrix"]:
        for city_id, item in row["cities"].items():
            relation = (row["workId"], city_id)
            if (
                item.get("entityExtraction", {}).get("status") == "offen"
                and relation not in relations_with_candidates
            ):
                open_relations[row["workId"]].append(city_id)

    rows = []
    for work_id, city_ids in sorted(open_relations.items()):
        work = works[work_id]
        unique_files = []
        seen_hashes = set()
        for source_file in work.get("files", []):
            content_hash = source_file.get("sha256")
            if content_hash and content_hash in seen_hashes:
                continue
            if content_hash:
                seen_hashes.add(content_hash)
            unique_files.append(source_file["path"])
        if not unique_files:
            unique_files = [work["primaryFile"]]

        variants = []
        for relative_path in unique_files:
            path = CORPUS / relative_path
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            variants.append({
                "file": relative_path,
                "lines": lines,
                "foldedLines": [
                    " "
                    + normalize_search(line)
                    + " "
                    for line in lines
                ],
            })
        for city_id in sorted(city_ids):
            hits = []
            for variant in variants:
                for index, line in enumerate(variant["foldedLines"]):
                    if any(f" {alias} " in line for alias in aliases[city_id]):
                        hits.append((variant, index))
            snippets = []
            for variant, index in hits[:20]:
                lines = variant["lines"]
                start = max(0, index - 3)
                end = min(len(lines), index + 4)
                snippets.append({
                    "file": variant["file"],
                    "line": index + 1,
                    "text": " ".join(
                        re.sub(r"\s+", " ", line).strip()
                        for line in lines[start:end]
                        if line.strip()
                    )[:1200],
                })
            rows.append({
                "workId": work_id,
                "workTitle": work["title"],
                "edition": work["edition"],
                "cityId": city_id,
                "mentions": len(hits),
                "filesChecked": unique_files,
                "snippets": snippets,
                "status": "offen",
            })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )
    summary = {
        "schemaVersion": 2,
        "relations": len(rows),
        "works": len(open_relations),
        "mentions": sum(row["mentions"] for row in rows),
        "uniqueSourceVariantsChecked": sum(
            len({
                source_file.get("sha256") or source_file["path"]
                for source_file in works[work_id].get("files", [])
            })
            for work_id in open_relations
        ),
        "published": False,
    }
    SUMMARY.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
