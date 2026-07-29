#!/usr/bin/env python3
"""Close only fully decided incidental work/city entity relationships.

This is deliberately narrower than the old matrix finalizer:

* city-focused works are never closed here;
* relations without extracted candidates are never inferred to be empty;
* a single manual candidate keeps the relation open;
* every closed relation records exact merge and rejection counts.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from review_source_candidates import CITY_ALIASES, FOCUSED_WORKS, normalize_search


ROOT = Path(__file__).resolve().parents[1]
COVERAGE_PATH = ROOT / "data/source-coverage.json"
DECISIONS_PATH = ROOT / "source-data/candidate-decisions.jsonl"
PROPOSALS_PATH = ROOT / "source-data/proposed-dossiers.jsonl"
RUN_ID = "exhaustive-entity-audit-v2"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    coverage = read_json(COVERAGE_PATH)
    proposed_relations: set[tuple[str, str, str]] = set()
    if PROPOSALS_PATH.exists():
        for line in PROPOSALS_PATH.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            proposal = json.loads(line)
            for candidate_id in proposal.get("candidateIds", []):
                for source in proposal.get("sources", []):
                    proposed_relations.add(
                        (
                            candidate_id,
                            source["workId"],
                            proposal["cityId"],
                        )
                    )
    per_candidate_relation: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    decisions: dict[tuple[str, str], Counter] = defaultdict(Counter)
    target_ids: dict[tuple[str, str], set[str]] = defaultdict(set)

    for line in DECISIONS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        decision = json.loads(line)
        city_id = decision["cityId"]
        for occurrence in decision.get("occurrences", []):
            relation = (occurrence["workId"], city_id)
            occurrence_decision = decision["decision"]
            if (
                occurrence_decision == "manuell-prüfen"
                and occurrence.get("scope") == "proximity"
            ):
                description = " " + normalize_search(
                    occurrence.get(
                        "descriptionContext",
                        occurrence.get("context", ""),
                    )
                ) + " "
                if not any(
                    f" {alias} " in description
                    for alias in CITY_ALIASES[city_id]
                ):
                    occurrence_decision = "verworfen"
                elif (
                    decision["candidateId"],
                    relation[0],
                    relation[1],
                ) not in proposed_relations:
                    occurrence_decision = "verworfen"
            per_candidate_relation[
                (decision["candidateId"], relation[0], relation[1])
            ].add(occurrence_decision)
            target_ids[relation].update(decision.get("targetIds", []))
            if decision.get("targetId"):
                target_ids[relation].add(decision["targetId"])

    for (_, work_id, city_id), statuses in per_candidate_relation.items():
        relation = (work_id, city_id)
        if "manuell-prüfen" in statuses:
            status = "manuell-prüfen"
        elif "zusammengeführt" in statuses:
            status = "zusammengeführt"
        else:
            status = "verworfen"
        decisions[relation][status] += 1

    reopened = Counter()
    for row in coverage["matrix"]:
        work_id = row["workId"]
        for city_id, item in row["cities"].items():
            extraction = item.get("entityExtraction", {})
            if extraction.get("method") != "vollständig-entschiedene-nebenquelle":
                continue
            relation = (work_id, city_id)
            relation_decisions = decisions.get(relation, Counter())
            reason = None
            if work_id in FOCUSED_WORKS.get(city_id, set()):
                reason = "Beziehung gehört nach erweitertem Register zu den Kernwerken"
            elif relation_decisions["manuell-prüfen"]:
                reason = "Der erneute Kandidatenlauf enthält offene Entscheidungen"
            elif not relation_decisions:
                reason = "Der erneute Kandidatenlauf besitzt keine bestätigende Entscheidung"
            if reason:
                item["entityExtraction"] = {
                    "status": "offen",
                    "run": RUN_ID,
                    "reopenedBy": "relation-consistency-check",
                    "reason": reason,
                    "places": 0,
                    "people": 0,
                    "groups": 0,
                    "aliases": 0,
                    "rejected": 0,
                }
                reopened[reason] += 1

    closed = Counter()
    for row in coverage["matrix"]:
        work_id = row["workId"]
        for city_id, item in row["cities"].items():
            extraction = item.get("entityExtraction", {})
            if extraction.get("status") != "offen":
                continue
            if work_id in FOCUSED_WORKS.get(city_id, set()):
                continue
            relation = (work_id, city_id)
            relation_decisions = decisions.get(relation, Counter())
            if not relation_decisions or relation_decisions["manuell-prüfen"]:
                continue

            merged_ids = target_ids.get(relation, set())
            places = sum(":place:" in target_id for target_id in merged_ids)
            people = sum(
                ":person:" in target_id or ":source-person:" in target_id
                for target_id in merged_ids
            )
            status = (
                "vollständig-extrahiert"
                if relation_decisions["zusammengeführt"]
                else "keine-lokalen-dossiers"
            )
            item["entityExtraction"] = {
                "status": status,
                "run": RUN_ID,
                "method": "vollständig-entschiedene-nebenquelle",
                "candidateDecisions": sum(relation_decisions.values()),
                "merged": relation_decisions["zusammengeführt"],
                "places": places,
                "people": people,
                "groups": 0,
                "aliases": 0,
                "rejected": relation_decisions["verworfen"],
                "manualOpen": 0,
                "reason": (
                    "Alle aus dieser Nebenquelle für die Stadt extrahierten "
                    "Kandidaten sind einzeln mit einem vorhandenen Dossier "
                    "verknüpft oder als konkretes Struktur-/OCR-Rauschen "
                    "entschieden; kein Kandidat ist offen."
                ),
            }
            closed[status] += 1

    coverage["entityExtractionRun"] = RUN_ID
    coverage["entityExtractionComplete"] = False
    coverage["coverageComplete"] = False
    write_json(COVERAGE_PATH, coverage)
    print(
        f"Wieder geöffnet: {sum(reopened.values())}; "
        f"geschlossen: {sum(closed.values())} Beziehungen "
        f"({closed['vollständig-extrahiert']} mit Dossiers, "
        f"{closed['keine-lokalen-dossiers']} ohne lokale Dossiers)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
