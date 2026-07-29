#!/usr/bin/env python3
"""Close source coverage only after an explicit entity-extraction audit.

This command must never infer dossier completeness from exact source links.
Every official work/city relation requires a separately recorded extraction
decision before a city may be marked complete.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COVERAGE_PATH = ROOT / "data/source-coverage.json"
CITIES_PATH = ROOT / "data/cities.json"
RUN_ID = "exhaustive-entity-audit-v2"
RUN_DATE = "2026-07-29"
OPEN = {"offen", "nur-volltexttreffer", "noch-zu-prüfen"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    pretty = path.exists() and path.read_text(encoding="utf-8").startswith("{\n")
    path.write_text(
        (
            json.dumps(payload, ensure_ascii=False, indent=2)
            if pretty
            else json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        ) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    coverage = read_json(COVERAGE_PATH)
    registry = read_json(CITIES_PATH)
    package_ids = {city["id"] for city in registry["cities"]}
    matrix_ids = {city["id"] for city in coverage["cities"]}
    if package_ids != matrix_ids:
        missing_packages = sorted(matrix_ids - package_ids)
        missing_matrix = sorted(package_ids - matrix_ids)
        raise SystemExit(
            "Stadtpakete und Quellenmatrix weichen ab: "
            f"ohne Paket={missing_packages}, ohne Matrix={missing_matrix}"
        )

    review = {
        "run": RUN_ID,
        "date": RUN_DATE,
        "method": (
            "Werkweises Entitätsprotokoll für Orte, Personen und Gruppen; "
            "jede Übernahme, Dublette und Ablehnung ist einzeln entschieden."
        ),
    }
    incomplete = []
    for row in coverage["matrix"]:
        for city_id, item in row["cities"].items():
            if city_id not in package_ids:
                continue
            extraction = item.get("entityExtraction", {})
            if extraction.get("status") not in {
                "vollständig-extrahiert",
                "keine-lokalen-dossiers",
                "nichtoffiziell-ausgeschlossen",
            }:
                incomplete.append((row["workId"], city_id))

    if incomplete:
        sample = ", ".join(f"{work}/{city}" for work, city in incomplete[:12])
        raise SystemExit(
            f"{len(incomplete)} Werk-/Stadt-Entitätsprüfungen sind offen: {sample}"
        )

    legacy_counts = Counter(
        item["status"]
        for row in coverage["matrix"]
        for item in row["cities"].values()
    )
    extraction_counts = Counter(
        item["entityExtraction"]["status"]
        for row in coverage["matrix"]
        for item in row["cities"].values()
    )
    coverage["statusCounts"] = dict(sorted(legacy_counts.items()))
    coverage["entityExtractionStatusCounts"] = dict(
        sorted(extraction_counts.items())
    )
    coverage["coverageComplete"] = True
    coverage["entityExtractionComplete"] = True
    coverage["completionRun"] = review
    write_json(COVERAGE_PATH, coverage)

    for city in registry["cities"]:
        manifest_path = ROOT / city["manifest"]
        manifest = read_json(manifest_path)
        manifest["sourceCoverageComplete"] = True
        manifest["sourceEntityExtractionComplete"] = True
        manifest["sourceCoverageRun"] = RUN_ID
        write_json(manifest_path, manifest)

    print(
        "OK Quellenmatrix und werkweise Entitätsprüfung vollständig; "
        f"Status {coverage['statusCounts']}"
    )


if __name__ == "__main__":
    main()
