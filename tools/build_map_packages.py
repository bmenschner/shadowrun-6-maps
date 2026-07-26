#!/usr/bin/env python3
"""Build map-only city packages from the source files in maps/."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
MAPS_DIR = ROOT / "maps"
DATA_DIR = ROOT / "data"
ASSET_DIR = ROOT / "assets" / "cities"
Image.MAX_IMAGE_PIXELS = None
LANCZOS = getattr(getattr(Image, "Resampling", Image), "LANCZOS")


BERLIN_MAPS = [
    {
        "key": "berlin-v04-uebersicht",
        "title": "Berlin 2080 - Übersicht v04",
        "kind": "Historische Referenzkarte",
        "source": "SR6_berlin_karte_v04_uebersicht_web.pdf",
        "page": 1,
        "summary": (
            "Frühere Gesamtübersicht von Berlin und dem Lore-Umland. Sie dient als "
            "zusätzliche Referenz für Gebietsfarben, Bezirke und nummerierte Kartenorte."
        ),
    },
    {
        "key": "berlin-v04-details",
        "title": "Berlin 2080 - Detailkarten v04",
        "kind": "Historische Referenzkarte",
        "source": "SR6_berlin_karte_v04_details_web.pdf",
        "page": 1,
        "summary": (
            "Frühere Detailansichten der Berliner Innenstadt und ausgewählter Bezirke "
            "zur Gegenprüfung der aktuellen v06-Karten."
        ),
    },
]


PACKAGES = [
    {
        "id": "hamburg-2080",
        "name": "Hamburg",
        "year": 2080,
        "center": [53.5511, 9.9937],
        "zoom": 9,
        "bounds": [[53.10, 8.20], [54.40, 11.40]],
        "scopeLabel": "Hamburg + Deutsche Bucht",
        "atlasIntro": (
            "Das Kartenpaket enthält zunächst ausschließlich Übersichts-, Bezirks-, "
            "Verkehrs- und Innenstadtpläne. Orte und Personen folgen später."
        ),
        "books": [{"id": "hamburg-paket", "title": "Hamburg-Kartenpaket", "edition": "SR6"}],
        "maps": [
            {
                "key": "hamburg-gesamt",
                "title": "Hamburg - Gesamtübersicht",
                "kind": "Metroplexkarte",
                "source": "Hamburgpaket - Karte.pdf",
                "page": 1,
                "summary": "Großräumige Übersicht des Hamburger Metroplexes mit Bezirken, Grenzräumen und Legende.",
            },
            {
                "key": "hamburg-wildost-neue-mitte",
                "title": "Hamburg - Wildost und Neue Mitte",
                "kind": "Stadtteilkarte",
                "source": "Hamburgpaket - Karte wildost neue mitte.pdf",
                "page": 1,
                "summary": "Kombinierte Detailkarte der Gebiete Wildost und Neue Mitte mit Straßennetz und Kartenlegenden.",
            },
            {
                "key": "hamburg-bezirke",
                "title": "Hamburg - Bezirke und Sonderzonen",
                "kind": "Bezirkskarte",
                "source": "Hamburgpaket - Karten Karteikarten.pdf",
                "page": 1,
                "summary": "Schematische Bezirksübersicht mit farblich getrennten Gebieten und nummerierten Kartenorten.",
            },
            {
                "key": "hamburg-hochbahn",
                "title": "Hamburg - Hochbahnnetz",
                "kind": "Verkehrsnetz",
                "source": "Hamburgpaket - Karten Karteikarten.pdf",
                "page": 3,
                "summary": "Liniennetzplan der Hamburger Hochbahn und ihrer Verbindungen in die angrenzenden Gebiete.",
            },
            {
                "key": "hamburg-innenstadt",
                "title": "Hamburg - Zentrale Innenstadt",
                "kind": "Innenstadtplan",
                "source": "Hamburgpaket - Karten Karteikarten.pdf",
                "page": 4,
                "summary": "Straßen- und Blockplan der zentralen Innenstadt mit nummerierten Besonderheiten.",
            },
            {
                "key": "deutsche-bucht",
                "title": "Deutsche Bucht",
                "kind": "Regionalkarte",
                "source": "Hamburgpaket - Karten Karteikarten.pdf",
                "page": 5,
                "summary": "Regionalkarte der Deutschen Bucht mit Inseln, Küstenorten und Verkehrsverbindungen.",
            },
            {
                "key": "hamburg-innere-bezirke",
                "title": "Hamburg - Innere Bezirke",
                "kind": "Bezirkskarte",
                "source": "Hamburgpaket - Karten Karteikarten.pdf",
                "page": 6,
                "summary": "Übersicht der inneren Bezirke, Verkehrsachsen und besonders markierten Orte.",
            },
        ],
    },
    {
        "id": "seattle",
        "name": "Seattle",
        "year": 2082,
        "center": [47.47, -122.24],
        "zoom": 8,
        "bounds": [[46.82, -122.84], [48.12, -121.66]],
        "scopeLabel": "Seattle Metroplex 2082",
        "atlasIntro": (
            "SR5- und SR6-Karten des Seattle Metroplexes. Bezirke, Barrens und "
            "Sondergebiete sind als erste Inhaltsstufe georeferenziert; Orte und "
            "Personen folgen später."
        ),
        "books": [
            {"id": "seattle-sr5", "title": "Seattle-Kartenpaket", "edition": "SR5"},
            {"id": "seattle-sr6", "title": "Seattle Poster Map", "edition": "SR6"},
        ],
        "maps": [
            {
                "key": "seattle-sr5-detail",
                "title": "Seattle - Detailkarte",
                "kind": "Straßenkarte",
                "source": "SR5 Seattle - Detailkarte.pdf",
                "page": 1,
                "summary": "Detaillierte Straßenkarte des zentralen Seattle Metroplexes im SR5-Kartenstil.",
            },
            {
                "key": "seattle-sr5-metroplex",
                "title": "Seattle - Metroplex",
                "kind": "Metroplexkarte",
                "source": "SR5 Seattle - Karte Metroplex.pdf",
                "page": 1,
                "summary": "Gesamtübersicht des Metroplexes mit Bezirken, Sonderzonen und umfangreicher Ortslegende.",
            },
            {
                "key": "seattle-sr5-nordwest-downtown",
                "title": "Seattle - Nordwesten und Downtown",
                "kind": "Regionale Detailkarte",
                "source": "SR5 Seattle - Karte Nordwesten und Downtown.pdf",
                "page": 1,
                "summary": "Doppelseitige Übersicht des pazifischen Nordwestens und der Downtown-Bezirke.",
            },
            {
                "key": "seattle-sr6-poster",
                "title": "Seattle - Poster Map",
                "kind": "Metroplexkarte",
                "source": "Shadowrun 6E - Seattle - Poster Map.pdf",
                "page": 1,
                "summary": "SR6-Gesamtkarte des Metroplexes mit Innenstadtplan, Regionalausschnitten und Legende.",
            },
            {
                "key": "seattle-sr6-schauplatzplaene",
                "title": "Seattle - Schauplatzpläne",
                "kind": "Gebäudepläne",
                "source": "Shadowrun 6E - Seattle - Poster Map.pdf",
                "page": 2,
                "summary": "Zwei taktische Gebäudepläne aus dem SR6-Posterkartenpaket.",
            },
        ],
    },
    {
        "id": "rhein-ruhr-2082",
        "name": "Rhein-Ruhr-Megaplex",
        "year": 2082,
        "center": [51.45, 7.15],
        "zoom": 8,
        "bounds": [[50.75, 6.20], [52.15, 8.30]],
        "scopeLabel": "Rhein-Ruhr-Megaplex",
        "atlasIntro": "Karten aus dem Revierbericht 2082; Orts- und Personendaten folgen später.",
        "books": [{"id": "revierbericht-2082", "title": "Revierbericht 2082", "edition": "SR6"}],
        "maps": [
            {
                "key": "rrm-recklinghausen-bochum",
                "title": "Recklinghausen/Herten und Bochum",
                "kind": "Straßenkarte",
                "source": "Shadowrun 6D - Rhein Rhur Megaplex - Revierbericht 2082 - Karte.pdf",
                "page": 1,
                "summary": "Großformatige Straßenkarte zwischen Recklinghausen/Herten und der Bochumer Innenstadt.",
            },
            {
                "key": "rrm-revieruebersichten",
                "title": "Rhein-Ruhr-Megaplex - Revierübersichten",
                "kind": "Regional- und Detailkarten",
                "source": "Shadowrun 6D - Rhein Rhur Megaplex - Revierbericht 2082 - Karte.pdf",
                "page": 2,
                "summary": "Mehrteilige Regional- und Detailübersicht des Rhein-Ruhr-Megaplexes.",
            },
        ],
    },
    {
        "id": "toronto-2080",
        "name": "Toronto",
        "year": 2080,
        "center": [43.6532, -79.3832],
        "zoom": 10,
        "bounds": [[43.30, -80.20], [44.20, -78.80]],
        "scopeLabel": "Toronto Metroplex",
        "atlasIntro": "Zwei SR6-Gesamtkarten von Toronto; Orts- und Personendaten folgen später.",
        "books": [
            {"id": "toronto-poster", "title": "Toronto Poster", "edition": "SR6"},
            {"id": "30-nights", "title": "30 Nights", "edition": "SR6"},
        ],
        "maps": [
            {
                "key": "toronto-poster",
                "title": "Toronto - Posterkarte",
                "kind": "Stadtkarte",
                "source": "Shadowrun 6D - Toronto Poster_deutsch_420x295mm [v02][2020-01-31].pdf",
                "page": 1,
                "summary": "Deutsche Posterkarte Torontos mit Bezirksflächen, Ortsmarken und Legende.",
            },
            {
                "key": "toronto-30-nights",
                "title": "Toronto - 30 Nights",
                "kind": "Stadtkarte",
                "source": "Shadowrun 6E - Tornto - 30 Nights - Maps.pdf",
                "page": 1,
                "summary": "Stadtübersicht aus 30 Nights mit nummerierten Schauplätzen und Bezirksbezeichnungen.",
            },
        ],
    },
    {
        "id": "denver",
        "name": "Denver",
        "year": None,
        "center": [39.7392, -104.9903],
        "zoom": 9,
        "bounds": [[39.25, -105.65], [40.25, -104.25]],
        "scopeLabel": "Denver Metroplex",
        "atlasIntro": "SR6-Posterkarte aus The Third Parallel; Orts- und Personendaten folgen später.",
        "books": [{"id": "third-parallel", "title": "The Third Parallel", "edition": "SR6"}],
        "maps": [
            {
                "key": "denver-third-parallel",
                "title": "Denver - The Third Parallel",
                "kind": "Stadtkarte",
                "source": "Shadowrun 6E - Denver Map - The Third Parallel - .pdf",
                "page": 1,
                "summary": "Stadtübersicht von Denver mit nummerierten Schauplätzen und Straßenraster.",
            }
        ],
    },
    {
        "id": "manhattan",
        "name": "Manhattan",
        "year": None,
        "center": [40.7831, -73.9712],
        "zoom": 11,
        "bounds": [[40.45, -74.35], [41.05, -73.55]],
        "scopeLabel": "Manhattan und Umgebung",
        "atlasIntro": "Manhattan-Karten aus Flüsternetze; Orts- und Personendaten folgen später.",
        "books": [{"id": "fluesternetze", "title": "Flüsternetze", "edition": "SR6"}],
        "maps": [
            {
                "key": "manhattan-legende",
                "title": "Manhattan - Karte mit Legende",
                "kind": "Stadtkarte",
                "source": "Shadowrun 6E - Fluesternetze_Manhattenkarte_mit_Legende.pdf",
                "page": 1,
                "summary": "Nummerierte Manhattan-Karte mit vollständiger Schauplatzlegende.",
            },
            {
                "key": "manhattan-spielerkarte",
                "title": "Manhattan - Karte ohne Legende",
                "kind": "Spielerkarte",
                "source": "Shadowrun 6E - Manhattan_Karte_Flsternetze.png",
                "summary": "Saubere Manhattan-Straßenkarte ohne Nummern und Legende für die Verwendung am Spieltisch.",
            },
        ],
    },
    {
        "id": "adl-2082",
        "name": "ADL",
        "year": 2082,
        "center": [51.1657, 10.4515],
        "zoom": 6,
        "bounds": [[47.00, 5.50], [55.40, 15.50]],
        "scopeLabel": "Allianz Deutscher Länder",
        "atlasIntro": "Regionale ADL-Karten; einzelne Städte, Orte und Personen folgen später.",
        "books": [{"id": "adl-regionalkarten", "title": "ADL-Regionalkarten 2082", "edition": "SR6"}],
        "maps": [
            {
                "key": "adl-autobahnen",
                "title": "ADL - Europouten und Autobahnen",
                "kind": "Verkehrskarte",
                "source": "Shadowrun 6D - adl_autobahnen.png",
                "summary": "Übersicht der Europouten und Autobahnverbindungen in der Allianz Deutscher Länder.",
            },
            {
                "key": "hessen-nassau-2082",
                "title": "Hessen-Nassau 2082",
                "kind": "Regionalkarte",
                "source": "Shadowrun 6D - hessen-nassau_2082.png",
                "summary": "Regionalkarte Hessen-Nassaus mit Grenzen, Städten, Arkologien und markierten Schauplätzen.",
            },
            {
                "key": "norddeutscher-bund-2082",
                "title": "Norddeutscher Bund 2082",
                "kind": "Regionalkarte",
                "source": "Shadowrun 6D - norddeutscher_bund_2082.png",
                "summary": "Übersicht des Norddeutschen Bundes mit Verkehrsachsen und nummerierten Besonderheiten.",
            },
        ],
    },
]


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def render_pdf_page(source: Path, page: int, max_dimension: int, temp_dir: Path) -> Image.Image:
    prefix = temp_dir / "page"
    subprocess.run(
        [
            "pdftoppm",
            "-f",
            str(page),
            "-l",
            str(page),
            "-singlefile",
            "-jpeg",
            "-jpegopt",
            "quality=95",
            "-scale-to",
            str(max_dimension),
            str(source),
            str(prefix),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    rendered = prefix.with_suffix(".jpg")
    if not rendered.exists():
        raise RuntimeError(f"PDF-Seite konnte nicht gerendert werden: {source.name}, Seite {page}")
    with Image.open(rendered) as image:
        return image.convert("RGB")


def render_map(source: Path, target: Path, page: int | None, max_dimension: int, force: bool) -> tuple[int, int]:
    if target.exists() and not force:
        with Image.open(target) as image:
            return image.size
    if not source.exists():
        raise FileNotFoundError(f"Kartenquelle fehlt: {source}")
    if source.suffix.lower() == ".pdf":
        with tempfile.TemporaryDirectory(prefix="sr-map-") as directory:
            image = render_pdf_page(source, page or 1, max_dimension, Path(directory))
    else:
        with Image.open(source) as original:
            image = ImageOps.exif_transpose(original).convert("RGB")
    image.thumbnail((max_dimension, max_dimension), LANCZOS)
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, "WEBP", quality=84, method=6)
    return image.size


def atlas_entry(city_id: str, item: dict, max_dimension: int, force: bool) -> dict:
    source = MAPS_DIR / item["source"]
    target = ASSET_DIR / city_id / "detail-maps" / f"{item['key']}.webp"
    width, height = render_map(source, target, item.get("page"), max_dimension, force)
    return {
        "key": item["key"],
        "title": item["title"],
        "kind": item["kind"],
        "source": item["source"],
        "summary": item["summary"],
        "markerIds": [],
        "width": width,
        "height": height,
        "image": f"../../assets/cities/{city_id}/detail-maps/{target.name}",
    }


def empty_collection(name: str, topology: bool = False) -> dict:
    payload = {"type": "FeatureCollection", "name": name, "features": []}
    if topology:
        payload["topology"] = {
            "model": "exclusive-partition",
            "priority": [],
            "unresolved_overlap_area_degrees_squared": 0,
        }
    return payload


def build_city_package(package: dict, max_dimension: int, force: bool) -> None:
    city_id = package["id"]
    city_dir = DATA_DIR / city_id
    atlas = [atlas_entry(city_id, item, max_dimension, force) for item in package["maps"]]
    manifest_path = city_dir / "manifest.json"
    places_path = city_dir / "places.geojson"
    people_path = city_dir / "people.json"
    existing_places = (
        json.loads(places_path.read_text(encoding="utf-8")).get("features", [])
        if places_path.exists()
        else []
    )
    existing_people = (
        json.loads(people_path.read_text(encoding="utf-8"))
        if people_path.exists()
        else []
    )
    if manifest_path.exists() and (existing_places or existing_people):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.update({
            "name": package["name"],
            "year": package["year"],
            "center": package["center"],
            "zoom": package["zoom"],
            "overlayBounds": package["bounds"],
            "cityBounds": package["bounds"],
            "regionBounds": package["bounds"],
            "scopeLabel": package["scopeLabel"],
            "atlasIntro": package["atlasIntro"],
        })
        write_json(manifest_path, manifest)
        write_json(city_dir / "atlas.json", atlas)
        sources_path = city_dir / "sources.json"
        sources = json.loads(sources_path.read_text(encoding="utf-8"))
        known_books = {book["id"] for book in sources.get("books", [])}
        sources.setdefault("books", []).extend(
            book for book in package["books"] if book["id"] not in known_books
        )
        write_json(sources_path, sources)
        return
    files = {
        "places": "places.geojson",
        "people": "people.json",
        "atlas": "atlas.json",
        "zones": "zones.geojson",
        "exterritorial": "exterritorial.geojson",
        "districts": "districts.geojson",
        "neighborhoods": "neighborhoods.geojson",
        "outskirts": "outskirts.geojson",
        "boundary": "city-boundary.geojson",
        "labels": "labels.json",
        "sources": "sources.json",
    }
    manifest = {
        "schemaVersion": 1,
        "id": city_id,
        "name": package["name"],
        "year": package["year"],
        "dataVersion": 3,
        "availableEditions": [],
        "center": package["center"],
        "zoom": package["zoom"],
        "overlayBounds": package["bounds"],
        "cityBounds": package["bounds"],
        "regionBounds": package["bounds"],
        "scopeLabel": package["scopeLabel"],
        "atlasIntro": package["atlasIntro"],
        "summary": {
            "entities": 0,
            "marker_instances": 0,
            "overview_marker_instances": 0,
            "detail_marker_instances": 0,
            "gangs": 0,
            "corporations": 0,
        },
        "files": files,
    }
    write_json(city_dir / "manifest.json", manifest)
    write_json(city_dir / "places.geojson", empty_collection(f"{package['name']} Orte"))
    write_json(city_dir / "people.json", [])
    write_json(city_dir / "atlas.json", atlas)
    write_json(city_dir / "zones.geojson", empty_collection(f"{package['name']} Gebietsstatus", topology=True))
    for key, label in (
        ("exterritorial.geojson", "EXTER"),
        ("districts.geojson", "Bezirke"),
        ("neighborhoods.geojson", "Stadtteile"),
        ("outskirts.geojson", "Umland"),
        ("city-boundary.geojson", "Stadtgrenze"),
    ):
        write_json(city_dir / key, empty_collection(f"{package['name']} {label}"))
    write_json(city_dir / "labels.json", [])
    write_json(
        city_dir / "sources.json",
        {"schemaVersion": 1, "books": package["books"], "citations": []},
    )


def extend_berlin(max_dimension: int, force: bool) -> None:
    city_id = "berlin-2080"
    atlas_path = DATA_DIR / city_id / "atlas.json"
    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    additions = {
        item["key"]: atlas_entry(city_id, item, max_dimension, force)
        for item in BERLIN_MAPS
    }
    merged = [item for item in atlas if item["key"] not in additions]
    merged.extend(additions[item["key"]] for item in BERLIN_MAPS)
    write_json(atlas_path, merged)


def update_registry(selected: set[str]) -> None:
    path = DATA_DIR / "cities.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    catalog_ids = {package["id"] for package in PACKAGES}
    existing_by_id = {city["id"]: city for city in registry["cities"]}
    existing = [
        city
        for city in registry["cities"]
        if city["id"] not in catalog_ids
    ]
    for package in PACKAGES:
        if package["id"] not in selected and package["id"] not in existing_by_id:
            continue
        city = {
            "id": package["id"],
            "name": package["name"],
            "manifest": f"data/{package['id']}/manifest.json",
        }
        if package["year"]:
            city["year"] = package["year"]
        existing.append(city)
    default = next((city for city in existing if city.get("default")), None)
    if default is None:
        existing[0]["default"] = True
    write_json(path, {"schemaVersion": 1, "cities": existing})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", action="append", choices=["berlin", *[p["id"] for p in PACKAGES]])
    parser.add_argument("--max-dimension", type=int, default=4200)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    selected = set(args.package or ["berlin", *[p["id"] for p in PACKAGES]])
    if "berlin" in selected:
        extend_berlin(args.max_dimension, args.force)
        print(f"Berlin: {len(BERLIN_MAPS)} zusätzliche Karten")
    package_ids = selected - {"berlin"}
    for package in PACKAGES:
        if package["id"] not in package_ids:
            continue
        build_city_package(package, args.max_dimension, args.force)
        print(f"{package['name']}: {len(package['maps'])} Karten")
    if package_ids:
        update_registry(package_ids)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
