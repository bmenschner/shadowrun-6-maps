#!/usr/bin/env python3
"""Close incidental relations whose direct mentions contain no dossier block."""

from __future__ import annotations

import json
from pathlib import Path

from review_source_candidates import FOCUSED_WORKS


ROOT = Path(__file__).resolve().parents[1]
COVERAGE_PATH = ROOT / "data/source-coverage.json"
MENTIONS_PATH = ROOT / "source-data/open-relation-mentions.jsonl"
RUN_ID = "exhaustive-entity-audit-v2"


def main() -> int:
    coverage = json.loads(COVERAGE_PATH.read_text(encoding="utf-8"))
    mention_rows = {}
    for line in MENTIONS_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            mention_rows[(row["workId"], row["cityId"])] = row

    closed = 0
    skipped_zero = 0
    skipped_focus = 0
    for matrix_row in coverage["matrix"]:
        work_id = matrix_row["workId"]
        for city_id, item in matrix_row["cities"].items():
            if item.get("entityExtraction", {}).get("status") != "offen":
                continue
            mention = mention_rows.get((work_id, city_id))
            if not mention:
                continue
            if work_id in FOCUSED_WORKS.get(city_id, set()):
                skipped_focus += 1
                continue
            if mention["mentions"] <= 0:
                skipped_zero += 1
                continue
            item["entityExtraction"] = {
                "status": "keine-lokalen-dossiers",
                "run": RUN_ID,
                "method": "direktnennungen-ohne-dossierblock",
                "mentions": mention["mentions"],
                "mentionContextsRetainedLocally": len(mention["snippets"]),
                "places": 0,
                "people": 0,
                "groups": 0,
                "aliases": 0,
                "rejected": 0,
                "manualOpen": 0,
                "reason": (
                    f"{mention['mentions']} direkte Stadtnennung(en) im "
                    "Volltext geprüft. Der werkweite Extraktionslauf enthält "
                    "für diese Beziehung keinen eigenständigen Orts-, "
                    "Personen- oder Gruppenprofilblock; die Nennungen bleiben "
                    "Stadt-, Reise-, Historien-, Vergleichs- oder "
                    "Biografiekontext und erzeugen kein Dossier."
                ),
            }
            closed += 1

    coverage["coverageComplete"] = False
    coverage["entityExtractionComplete"] = False
    COVERAGE_PATH.write_text(
        json.dumps(coverage, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(
        f"Geschlossen: {closed}; Kernwerke offen: {skipped_focus}; "
        f"nicht reproduzierbare Nulltreffer offen: {skipped_zero}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
