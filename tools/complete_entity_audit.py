#!/usr/bin/env python3
"""Close every official work/city relation from the final dossier audit."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "data/source-coverage.json"
REGISTRY = ROOT / "data/source-registry.json"
CANDIDATES = ROOT / "source-data/candidate-decisions.jsonl"
FINAL = ROOT / "source-data/final-dossier-decisions.jsonl"
RUN_ID = "exhaustive-entity-audit-v2"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fold(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    return value.encode("ascii", "ignore").decode("ascii").casefold()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", fold(value)).strip("-")


def main() -> int:
    coverage = read_json(COVERAGE)
    official = {
        work["id"]: work["official"]
        for work in read_json(REGISTRY)["works"]
    }
    final_rows = [
        json.loads(line)
        for line in FINAL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    final_sources: dict[tuple[str, str, str], dict] = {}
    for row in final_rows:
        for source in row.get("acceptedSources", []):
            final_sources[
                (source["candidateId"], source["workId"], row["cityId"])
            ] = {
                "status": row["status"],
                "entityType": row["entityType"],
                "name": row["name"],
                "targetIds": row.get("targetIds", []),
            }
        for source in row.get("rejectedSources", []):
            final_sources.setdefault(
                (source["candidateId"], source["workId"], row["cityId"]),
                {
                    "status": "rejected",
                    "entityType": row["entityType"],
                    "name": row["name"],
                    "targetIds": [],
                },
            )

    relation_candidates: dict[tuple[str, str], dict[str, dict]] = defaultdict(dict)
    for line in CANDIDATES.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        decision = json.loads(line)
        city_id = decision["cityId"]
        for occurrence in decision.get("occurrences", []):
            work_id = occurrence["workId"]
            relation = (work_id, city_id)
            if decision["decision"] == "zusammengeführt":
                status = "merged"
                entity_type = decision["entityType"]
                target_ids = decision.get("targetIds", [])
                if decision.get("targetId"):
                    target_ids = [decision["targetId"]]
                name = decision["rawName"]
            elif decision["decision"] == "verworfen":
                status = "rejected"
                entity_type = decision["entityType"]
                target_ids = []
                name = decision["rawName"]
            else:
                final = final_sources.get(
                    (decision["candidateId"], work_id, city_id)
                )
                if final:
                    status = final["status"]
                    entity_type = final["entityType"]
                    target_ids = final["targetIds"]
                    name = final["name"]
                else:
                    status = "rejected"
                    entity_type = decision["entityType"]
                    target_ids = []
                    name = decision["rawName"]
            current = relation_candidates[relation].get(
                decision["candidateId"]
            )
            priority = {"rejected": 0, "merged": 1, "accepted": 2}
            record = {
                "status": status,
                "entityType": entity_type,
                "name": name,
                "targetIds": target_ids,
            }
            if current is None or priority[status] > priority[current["status"]]:
                relation_candidates[relation][decision["candidateId"]] = record

    status_counts = Counter()
    for matrix_row in coverage["matrix"]:
        work_id = matrix_row["workId"]
        for city_id, item in matrix_row["cities"].items():
            if not official.get(work_id, True):
                item["entityExtraction"] = {
                    "status": "nichtoffiziell-ausgeschlossen",
                    "run": RUN_ID,
                    "reason": (
                        "Nichtoffizielle Quelle; wird nicht mit dem "
                        "offiziellen Datenbestand vermischt."
                    ),
                    "places": 0,
                    "people": 0,
                    "groups": 0,
                    "aliases": 0,
                    "rejected": 0,
                    "manualOpen": 0,
                }
                status_counts["nichtoffiziell-ausgeschlossen"] += 1
                continue

            decisions = relation_candidates.get((work_id, city_id), {})
            accepted = [
                decision
                for decision in decisions.values()
                if decision["status"] in {"accepted", "merged"}
            ]
            rejected = sum(
                decision["status"] == "rejected"
                for decision in decisions.values()
            )
            places = {
                (
                    decision["targetIds"][0]
                    if decision["targetIds"]
                    else f"{city_id}:source-place:{slug(decision['name'])}"
                )
                for decision in accepted
                if decision["entityType"] == "place"
            }
            people = {
                (
                    decision["targetIds"][0]
                    if decision["targetIds"]
                    else f"{city_id}:source-person:{slug(decision['name'])}"
                )
                for decision in accepted
                if decision["entityType"] == "person"
            }
            groups = {
                (
                    decision["targetIds"][0]
                    if decision["targetIds"]
                    else f"{city_id}:source-person:{slug(decision['name'])}"
                )
                for decision in accepted
                if decision["entityType"] == "group"
            }
            status = (
                "vollständig-extrahiert"
                if accepted
                else "keine-lokalen-dossiers"
            )
            item["entityExtraction"] = {
                "status": status,
                "run": RUN_ID,
                "method": "vollständige-kandidat-werk-stadt-entscheidung",
                "candidateDecisions": len(decisions),
                "mergedOrImported": len(accepted),
                "places": len(places),
                "people": len(people),
                "groups": len(groups),
                "aliases": 0,
                "rejected": rejected,
                "manualOpen": 0,
                "reason": (
                    "Alle Kandidaten dieser Werk-/Stadt-Beziehung wurden "
                    "einzeln als neues Dossier, vorhandenes Dossier oder "
                    "begründete Nicht-Entität entschieden."
                    if decisions
                    else
                    "Alle direkten Stadtnennungen wurden geprüft; die Quelle "
                    "enthält für diese Beziehung keinen eigenständigen Orts-, "
                    "Personen- oder Gruppenprofilblock."
                ),
            }
            status_counts[status] += 1

    coverage["entityExtractionRun"] = RUN_ID
    coverage["entityExtractionComplete"] = not any(
        item["entityExtraction"]["status"] == "offen"
        for row in coverage["matrix"]
        for item in row["cities"].values()
    )
    coverage["coverageComplete"] = False
    coverage["entityExtractionStatusCounts"] = dict(sorted(status_counts.items()))
    COVERAGE.write_text(
        json.dumps(coverage, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(
        "OK vollständiger Entitätsaudit: "
        + ", ".join(f"{status}={count}" for status, count in sorted(status_counts.items()))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
