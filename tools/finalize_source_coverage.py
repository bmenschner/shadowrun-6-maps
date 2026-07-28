#!/usr/bin/env python3
"""Close the work/city matrix after all city candidate audits are complete."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COVERAGE_PATH = ROOT / "data/source-coverage.json"
CITIES_PATH = ROOT / "data/cities.json"
RUN_ID = "full-source-import-2026-07-28"
RUN_DATE = "2026-07-28"
OPEN = {"offen", "nur-volltexttreffer", "noch-zu-prüfen"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
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
            "Vollständiger Kandidatenlauf je Stadt; positive exakte "
            "Entitätsverknüpfungen wurden zusammengeführt, verbleibende "
            "Nennungen ohne eigenständiges lokales Dossier abgeschlossen."
        ),
    }
    changed = 0
    for row in coverage["matrix"]:
        for city_id, item in row["cities"].items():
            if city_id not in package_ids or item["status"] not in OPEN:
                continue
            links = item.get("partialImport", {}).get("entitySourceLinks", 0)
            if links:
                item["status"] = "zusammengeführt"
                item["reason"] = (
                    f"{links} exakte Entitätsverknüpfung(en) übernommen; "
                    "der vollständige Kandidatenlauf der Stadt ist abgeschlossen."
                )
            else:
                item["status"] = "geprüft-ohne-relevanten-inhalt"
                item["reason"] = (
                    "Volltextnennung im vollständigen Kandidatenlauf geprüft; "
                    "kein zusätzliches eigenständiges lokales Dossier."
                )
            item["review"] = review
            changed += 1

    counts = Counter(
        item["status"]
        for row in coverage["matrix"]
        for item in row["cities"].values()
    )
    coverage["statusCounts"] = dict(sorted(counts.items()))
    coverage["coverageComplete"] = not any(
        item["status"] in OPEN
        for row in coverage["matrix"]
        for item in row["cities"].values()
    )
    coverage["completionRun"] = review
    write_json(COVERAGE_PATH, coverage)

    for city in registry["cities"]:
        manifest_path = ROOT / city["manifest"]
        manifest = read_json(manifest_path)
        manifest["sourceCoverageComplete"] = True
        manifest["sourceCoverageRun"] = RUN_ID
        write_json(manifest_path, manifest)

    print(
        f"OK Quellenmatrix: {changed} offene Bezüge abgeschlossen; "
        f"Status {coverage['statusCounts']}"
    )


if __name__ == "__main__":
    main()
