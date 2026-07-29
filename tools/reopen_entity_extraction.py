#!/usr/bin/env python3
"""Reopen every official work/city relation for exhaustive entity review."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "exhaustive-entity-audit-v2"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    pretty = path.exists() and path.read_text(encoding="utf-8").startswith("{\n")
    path.write_text(
        (
            json.dumps(payload, ensure_ascii=False, indent=2)
            if pretty
            else json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    coverage_path = ROOT / "data/source-coverage.json"
    cities_path = ROOT / "data/cities.json"
    coverage = read_json(coverage_path)
    cities = read_json(cities_path)["cities"]
    counts = Counter()

    for row in coverage["matrix"]:
        for item in row["cities"].values():
            if item.get("status") == "nichtoffiziell-ausgeschlossen":
                status = "nichtoffiziell-ausgeschlossen"
            else:
                status = "offen"
            item["entityExtraction"] = {
                "status": status,
                "run": RUN_ID,
                "places": 0,
                "people": 0,
                "groups": 0,
                "aliases": 0,
                "rejected": 0,
            }
            counts[status] += 1

    coverage["coverageComplete"] = False
    coverage["entityExtractionComplete"] = False
    coverage["entityExtractionRun"] = RUN_ID
    coverage.pop("completionRun", None)
    write_json(coverage_path, coverage)

    for city in cities:
        manifest_path = ROOT / city["manifest"]
        manifest = read_json(manifest_path)
        manifest["sourceCoverageComplete"] = False
        manifest["sourceEntityExtractionComplete"] = False
        manifest["sourceCoverageRun"] = RUN_ID
        write_json(manifest_path, manifest)

    print(
        f"Entitätsprüfung neu geöffnet: {counts['offen']} offen, "
        f"{counts['nichtoffiziell-ausgeschlossen']} nichtoffiziell ausgeschlossen"
    )


if __name__ == "__main__":
    main()
