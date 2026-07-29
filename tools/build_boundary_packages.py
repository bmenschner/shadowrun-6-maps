#!/usr/bin/env python3
"""Build geographic boundary layers for the non-Berlin map packages.

The checked-in GeoJSON files combine official Shadowrun map assignments with
public administrative geometries. Click That Hood, deutschlandGeoJSON and the
other geometry sources only supply precise linework; they are not lore sources.
Source files are cached in tmp/boundaries.
"""

from __future__ import annotations

import json
import subprocess
import urllib.request
from collections import defaultdict
from pathlib import Path

from shapely.geometry import MultiPoint, Point, Polygon, box, mapping, shape
from shapely.ops import unary_union, voronoi_diagram


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "tmp" / "boundaries"
DATA = ROOT / "data"
SOURCE_NAME = "Code for Germany / Click That Hood"
SOURCE_URL = "https://github.com/codeforgermany/click_that_hood"
TIGERWEB_SOURCE_NAME = "U.S. Census Bureau TIGERweb"
TIGERWEB_SOURCE_URL = (
    "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/"
    "Places_CouSub_ConCity_SubMCD/MapServer/4/query"
)
TIGERWEB_COLORADO_QUERY = (
    TIGERWEB_SOURCE_URL
    + "?where=STATE%3D%2708%27&outFields=NAME%2CSTATE%2CBASENAME"
    "&returnGeometry=true&outSR=4326&f=geojson"
)
SIMPLIFY_TOLERANCE = 0.00012
SOURCE_ENDPOINTS = {
    "hamburg": "repos/codeforgermany/click_that_hood/contents/public/data/hamburg.geojson",
    "seattle": "repos/codeforgermany/click_that_hood/contents/public/data/seattle.geojson",
    "toronto": "repos/codeforgermany/click_that_hood/contents/public/data/toronto.geojson",
    "chicago": "repos/codeforgermany/click_that_hood/contents/public/data/chicago.geojson",
    "denver": "repos/codeforgermany/click_that_hood/contents/public/data/denver.geojson",
    "manhattan": "repos/codeforgermany/click_that_hood/contents/public/data/manhattan.geojson",
    "germany": "repos/codeforgermany/click_that_hood/contents/public/data/germany.geojson",
    "nordrhein-westfalen": "repos/codeforgermany/click_that_hood/contents/public/data/nordrhein-westfalen.geojson",
    "essen-districts": "repos/gitter-badger/plasmap/contents/dal/src/test/resources/districts.essen.geojson",
    "germany-counties": "repos/isellsoap/deutschlandGeoJSON/contents/4_kreise/2_hoch.geo.json",
}


HAMBURG_BOROUGHS = {
    "Hamburg-Mitte": {
        "Billbrook", "Billstedt", "Borgfelde", "Finkenwerder", "HafenCity",
        "Hamburg-Altstadt", "Hamm", "Hammerbrook", "Horn", "Kleiner Grasbrook",
        "Neustadt", "Rothenburgsort", "St. Georg", "St. Pauli",
        "Steinwerder", "Veddel", "Waltershof", "Wilhelmsburg",
    },
    "Altona": {
        "Altona-Altstadt", "Altona-Nord", "Bahrenfeld", "Blankenese",
        "Groß Flottbek", "Iserbrook", "Lurup", "Nienstedten", "Osdorf",
        "Othmarschen", "Ottensen", "Rissen", "Sternschanze", "Sülldorf",
    },
    "Eimsbüttel": {
        "Eidelstedt", "Eimsbüttel", "Harvestehude", "Hoheluft-West",
        "Lokstedt", "Niendorf", "Rotherbaum", "Schnelsen", "Stellingen",
    },
    "Hamburg-Nord": {
        "Alsterdorf", "Barmbek-Nord", "Barmbek-Süd", "Dulsberg", "Eppendorf",
        "Fuhlsbüttel", "Groß Borstel", "Hoheluft-Ost", "Hohenfelde",
        "Langenhorn", "Ohlsdorf", "Uhlenhorst", "Winterhude",
    },
    "Wandsbek": {
        "Bergstedt", "Bramfeld", "Duvenstedt", "Eilbek", "Farmsen-Berne",
        "Hummelsbüttel", "Jenfeld", "Lehmsahl-Mellingstedt", "Marienthal",
        "Poppenbüttel", "Rahlstedt", "Sasel", "Steilshoop", "Tonndorf",
        "Volksdorf", "Wandsbek", "Wellingsbüttel", "Wohlsdorf-Ohlstedt",
    },
    "Bergedorf": {
        "Allermöhe", "Altengamme", "Bergedorf", "Billwerder", "Curslack",
        "Kirchwerder", "Lohbrügge", "Moorfleet", "Neuallermöhe", "Neuengamme",
        "Ochsenwerder", "Reitbrook", "Spadenland", "Tatenberg",
    },
    "Harburg": {
        "Altenwerder", "Cranz", "Eißendorf", "Francop", "Gut Moor", "Harburg",
        "Hausbruch", "Heimfeld", "Langenbek", "Marmstorf", "Moorburg",
        "Neuenfelde", "Neugraben-Fischbek", "Neuland", "Rönneburg", "Sinstorf",
        "Wilstorf",
    },
}

RRM_MUNICIPALITIES = {
    "Bochum", "Bönen", "Bonn", "Bottrop", "Castrop-Rauxel", "Datteln",
    "Bergisch Gladbach", "Brühl", "Dinslaken", "Dormagen", "Dortmund",
    "Dorsten", "Duisburg", "Düsseldorf", "Erkrath",
    "Ennepetal", "Essen", "Fröndenberg/Ruhr", "Gevelsberg", "Gelsenkirchen",
    "Frechen", "Gladbeck", "Grevenbroich", "Hagen", "Haltern am See", "Hamm",
    "Hamminkeln", "Hattingen", "Herne", "Herten", "Hilden", "Holzwickede",
    "Hünxe", "Hürth", "Iserlohn", "Kamen", "Kamp-Lintfort",
    "Köln", "Korschenbroich", "Krefeld", "Langenfeld (Rhld.)", "Leverkusen",
    "Lünen", "Marl", "Meerbusch",
    "Menden (Sauerland)", "Mönchengladbach", "Moers", "Mülheim an der Ruhr",
    "Monheim am Rhein", "Neukirchen-Vluyn", "Neuss", "Niederkassel",
    "Oberhausen", "Oer-Erkenschwick", "Pulheim",
    "Ratingen", "Recklinghausen", "Remscheid", "Rheinberg", "Schermbeck",
    "Sankt Augustin", "Schwelm", "Schwerte", "Selm", "Soest", "Solingen",
    "Sprockhövel", "Troisdorf", "Unna", "Velbert", "Viersen",
    "Voerde (Niederrhein)", "Waltrop", "Welver", "Werl", "Werne", "Wesel",
    "Wesseling", "Willich", "Witten", "Wuppertal",
}


def read_payload(name: str) -> dict:
    path = CACHE / f"{name}.geojson"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        response = None
        last_error = None
        commands = [
            ["gh"],
            ["wsl.exe", "gh"],
        ]
        for prefix in commands:
            try:
                response = subprocess.run(
                    [
                        *prefix, "api", "-H",
                        "Accept: application/vnd.github.raw+json",
                        SOURCE_ENDPOINTS[name],
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                break
            except (FileNotFoundError, subprocess.CalledProcessError) as error:
                last_error = error
        if response is None:
            raise SystemExit(
                f"Quelldatei fehlt: {path.relative_to(ROOT)} und konnte nicht über gh abgerufen werden."
            ) from last_error
        path.write_text(response.stdout, encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))


def read_source(name: str) -> dict:
    payload = read_payload(name)
    if payload.get("type") != "FeatureCollection":
        raise SystemExit(
            f"Verwaltungsquelle {name} besitzt nicht das erwartete GeoJSON-Format."
        )
    return payload


def read_colorado_places() -> dict:
    path = CACHE / "colorado-places.geojson"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with urllib.request.urlopen(TIGERWEB_COLORADO_QUERY, timeout=90) as response:
                path.write_bytes(response.read())
        except OSError as error:
            raise SystemExit(
                f"Quelldatei fehlt: {path.relative_to(ROOT)} und konnte nicht "
                "über Census TIGERweb abgerufen werden."
            ) from error
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("type") != "FeatureCollection":
        raise SystemExit("Census-TIGERweb-Daten besitzen nicht das erwartete GeoJSON-Format.")
    return payload


def clean_geometry(geometry):
    cleaned = geometry.buffer(0) if not geometry.is_valid else geometry
    return cleaned.simplify(SIMPLIFY_TOLERANCE, preserve_topology=True)


def source_properties(**extra) -> dict:
    return {
        **extra,
        "source": SOURCE_NAME,
        "source_url": SOURCE_URL,
    }


def geo_feature(name: str, geometry, *, basis: str, role: str) -> dict:
    return {
        "type": "Feature",
        "geometry": mapping(clean_geometry(geometry)),
        "properties": source_properties(
            name=name,
            basis=basis,
            boundary_role=role,
        ),
    }


def collection(name: str, features: list[dict], **extra) -> dict:
    return {
        "type": "FeatureCollection",
        "name": name,
        **extra,
        "features": features,
    }


def named_geometries(payload: dict) -> dict[str, object]:
    return {
        feature["properties"]["name"]: clean_geometry(shape(feature["geometry"]))
        for feature in payload["features"]
    }


def county_geometries() -> dict[tuple[str, str], object]:
    payload = read_source("germany-counties")
    return {
        (feature["properties"]["NAME_1"], feature["properties"]["NAME_3"]): clean_geometry(
            shape(feature["geometry"])
        )
        for feature in payload["features"]
    }


def write_geojson(city_id: str, filename: str, payload: dict) -> None:
    path = DATA / city_id / filename
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def zone_collection(display_name: str, geometry, *, label: str, basis: str) -> dict:
    feature = {
        "type": "Feature",
        "geometry": mapping(clean_geometry(geometry)),
        "properties": source_properties(
            status="normal",
            zone_type="magenta",
            label=label,
            basis=basis,
            topology="disjoint",
        ),
    }
    return collection(
        f"{display_name} Gebietsstatus",
        [feature],
        topology={
            "model": "exclusive-partition",
            "priority": ["corporate", "normal"],
            "unresolved_overlap_area_degrees_squared": 0,
            "basis": basis,
        },
    )


def empty_exterritorial(display_name: str) -> dict:
    return collection(
        f"{display_name} exterritoriale Konzerngebiete",
        [],
        topology={
            "model": "exclusive-corporate-over-normal",
            "unresolved_overlap_area_degrees_squared": 0,
        },
    )


def entity_ids(city_id: str) -> dict[str, object]:
    payload = json.loads((DATA / city_id / "places.geojson").read_text(encoding="utf-8"))
    return {
        feature["properties"]["name"]: feature["properties"]["id"]
        for feature in payload["features"]
    }


def label_payload(
    city_id: str,
    geometries: dict[str, object],
    *,
    type_name: str = "district",
) -> list[dict]:
    ids = entity_ids(city_id)
    labels = []
    for name, geometry in geometries.items():
        point = geometry.representative_point()
        label = {
            "name": name,
            "lat": round(point.y, 6),
            "lon": round(point.x, 6),
            "type": type_name,
        }
        if name in ids:
            label["entity_id"] = ids[name]
        labels.append(label)
    return labels


def source_feature(
    name: str,
    geometry,
    *,
    basis: str,
    role: str,
    lore_source: str,
    source: str,
    source_url: str,
    review_status: str,
    review_label: str,
    preserve_partition: bool = False,
) -> dict:
    output_geometry = geometry
    if (
        not output_geometry.is_valid
        or output_geometry.geom_type not in {"Polygon", "MultiPolygon"}
    ):
        output_geometry = output_geometry.buffer(0)
    if not preserve_partition:
        output_geometry = clean_geometry(output_geometry)
    return {
        "type": "Feature",
        "geometry": mapping(output_geometry),
        "properties": {
            "name": name,
            "basis": basis,
            "boundary_role": role,
            "lore_source": lore_source,
            "source": source,
            "source_url": source_url,
            "boundary_review_status": review_status,
            "boundary_review_label": review_label,
        },
    }


def named_partition(boundary, anchors: dict[str, tuple[float, float]]) -> dict[str, object]:
    points = [Point(lon, lat) for lat, lon in anchors.values()]
    diagram = voronoi_diagram(MultiPoint(points), envelope=boundary.envelope)
    cells = list(diagram.geoms)
    result = {}
    for name, (lat, lon) in anchors.items():
        point = Point(lon, lat)
        cell = min(cells, key=lambda candidate: candidate.distance(point))
        result[name] = clean_geometry(cell.intersection(boundary))
    return result


def build_chicago() -> None:
    reference = named_geometries(read_source("chicago"))
    chicago_city = clean_geometry(unary_union(list(reference.values())))

    # Mission Chicago gives four unambiguous hard limits for the former
    # Containment Zone: Belmont Avenue, 115th Street, Harlem Avenue and Lake
    # Michigan. Intersecting that street rectangle with the current municipal
    # shoreline preserves the lake edge instead of drawing a synthetic line.
    containment_clip = box(-87.8065, 41.6844, -87.50, 41.9401)
    containment_zone = clean_geometry(chicago_city.intersection(containment_clip))
    outside_zone = clean_geometry(chicago_city.difference(containment_zone))

    district = source_feature(
        "The Zone",
        containment_zone,
        basis=(
            "Ehemalige Containment Zone zwischen Harlem Avenue, Belmont "
            "Avenue, 115th Street und dem Ufer des Lake Michigan"
        ),
        role="lore-district",
        lore_source=(
            "Mission Chicago, Chicago-Kapitel (SR5); "
            "Bug City, The Wall (SR2)"
        ),
        source=SOURCE_NAME,
        source_url=SOURCE_URL,
        review_status="source-aligned",
        review_label="Vier publizierte Straßen- und Ufergrenzen vollständig umgesetzt",
    )
    references = [
        geo_feature(
            name,
            geometry,
            basis="Heutiges Chicago Community Area als geografische Referenz",
            role="reference-neighborhood",
        )
        for name, geometry in sorted(reference.items())
    ]
    boundary = source_feature(
        "Chicago · heutiger Stadtumriss",
        chicago_city,
        basis=(
            "Heutiger kommunaler Stadtumriss als harte geografische Referenz; "
            "der größere Chicagoland-Sprawl ist textlich belegt, aber nicht "
            "als exakte äußere Linie publiziert"
        ),
        role="reference-city",
        lore_source="Feral Cities, Kapitel Chicago (SR4)",
        source=SOURCE_NAME,
        source_url=SOURCE_URL,
        review_status="contextual",
        review_label=(
            "Containment Zone quellenabgeglichen; äußerer Chicagoland-Rand "
            "mangels publizierter Grenzlinie nicht erfunden"
        ),
    )
    zone_features = [
        {
            "type": "Feature",
            "geometry": mapping(containment_zone),
            "properties": source_properties(
                status="barrens",
                zone_type="barrens",
                label="Containment Zone · Chicago",
                basis=(
                    "Ehemalige Sperrzone innerhalb der publizierten "
                    "Belmont–Harlem–115th–Lake-Michigan-Grenzen"
                ),
                topology="disjoint",
                source="Mission Chicago (SR5) und Bug City (SR2)",
                boundary_review_status="source-aligned",
            ),
        },
        {
            "type": "Feature",
            "geometry": mapping(outside_zone),
            "properties": source_properties(
                status="normal",
                zone_type="magenta",
                label="Normal / Stadt · Chicago außerhalb der Zone",
                basis=(
                    "Heutiger Stadtumriss abzüglich der quellenabgeglichenen "
                    "Containment Zone; keine Behauptung über den gesamten Chicagoland-Sprawl"
                ),
                topology="disjoint",
                boundary_review_status="contextual",
            ),
        },
    ]
    write_geojson(
        "chicago",
        "districts.geojson",
        collection("Chicago Lore-Distrikte", [district]),
    )
    write_geojson(
        "chicago",
        "neighborhoods.geojson",
        collection("Chicago Community Areas", references),
    )
    write_geojson(
        "chicago",
        "city-boundary.geojson",
        collection("Chicago geografischer Stadtbezug", [boundary]),
    )
    write_geojson(
        "chicago",
        "zones.geojson",
        collection(
            "Chicago Gebietsstatus",
            zone_features,
            topology={
                "model": "exclusive-partition",
                "priority": ["barrens", "normal"],
                "unresolved_overlap_area_degrees_squared": 0,
                "basis": "Mission Chicago, Bug City und heutige Community-Area-Uferkante",
            },
        ),
    )
    write_geojson("chicago", "exterritorial.geojson", empty_exterritorial("Chicago"))
    write_json(
        DATA / "chicago" / "labels.json",
        label_payload("chicago", {"The Zone": containment_zone}),
    )


def build_denver() -> None:
    reference = named_geometries(read_source("denver"))
    colorado_payload = read_colorado_places()
    municipalities = {
        feature["properties"]["BASENAME"]: clean_geometry(shape(feature["geometry"]))
        for feature in colorado_payload["features"]
    }
    district_anchors = {
        "Arvada": (39.8028, -105.0875),
        "Aurora Warrens": (39.7294, -104.8319),
        "Boulder": (40.0150, -105.2705),
        "Brighton": (39.9853, -104.8205),
        "Broomfield": (39.9205, -105.0867),
        "Castle Rock": (39.3722, -104.8561),
        "Centennial": (39.5807, -104.8772),
        "Colorado Springs": (38.8339, -104.8214),
        "Commerce City": (39.8083, -104.9339),
        "Elbert": (39.2194, -104.5372),
        "Englewood": (39.6478, -104.9878),
        "Front Range": (39.7080, -105.2300),
        "Lakewood": (39.7047, -105.0814),
        "Lowry": (39.7167, -104.9008),
        "Stapleton": (39.7794, -104.8814),
        "The Gap": (39.4400, -104.9400),
        "The Hub": (39.7392, -104.9903),
        "Thornton": (39.8680, -104.9719),
        "Westminster": (39.8367, -105.0372),
    }
    # The Third Parallel defines the FRFZ as a 12,754 km² corridor from Boulder
    # to Colorado Springs. No surveyed line coordinates are supplied, so the
    # zone follows a conservative Front Range envelope while the published
    # roughly one-kilometre DMZ is represented as its own ring.
    frfz = clean_geometry(
        shape(
            {
                "type": "Polygon",
                "coordinates": [[
                    [-105.43, 39.92],
                    [-105.34, 40.10],
                    [-105.05, 40.14],
                    [-104.68, 40.08],
                    [-104.42, 39.90],
                    [-104.40, 39.38],
                    [-104.46, 38.74],
                    [-104.78, 38.65],
                    [-105.20, 38.72],
                    [-105.37, 39.02],
                    [-105.43, 39.92],
                ]],
            }
        )
    )
    dmz_outer = clean_geometry(frfz.buffer(0.0105, join_style=2))
    dmz_ring = clean_geometry(dmz_outer.difference(frfz))
    districts = named_partition(frfz, district_anchors)

    modern_names = {
        "Arvada": "Arvada",
        "Aurora Warrens": "Aurora",
        "Boulder": "Boulder",
        "Brighton": "Brighton",
        "Broomfield": "Broomfield",
        "Castle Rock": "Castle Rock",
        "Centennial": "Centennial",
        "Colorado Springs": "Colorado Springs",
        "Commerce City": "Commerce City",
        "Englewood": "Englewood",
        "Lakewood": "Lakewood",
        "Thornton": "Thornton",
        "Westminster": "Westminster",
    }
    exact_claims = {
        lore_name: municipalities[current_name].intersection(frfz)
        for lore_name, current_name in modern_names.items()
        if current_name in municipalities
    }
    forced = clean_geometry(unary_union(list(exact_claims.values())))
    for name in districts:
        districts[name] = districts[name].difference(forced)
    for name, geometry in exact_claims.items():
        districts[name] = clean_geometry(unary_union([districts[name], geometry]))

    # Within modern Denver the source distinguishes the Hub, Lowry and
    # Stapleton. Statistical neighborhood lines provide defensible hard edges.
    local_claims = {
        "The Hub": {
            "Auraria", "CBD", "Capitol Hill", "Civic Center", "Five Points",
            "Lincoln Park", "North Capitol Hill", "Union Station",
        },
        "Lowry": {
            "Belcaro", "Cherry Creek", "Hilltop", "Indian Creek", "Lowry Field",
            "Washington Virginia Vale",
        },
        "Stapleton": {
            "DIA", "Elyria Swansea", "Gateway / Green Valley Ranch", "Montbello",
            "North Park Hill", "Northeast Park Hill", "Stapleton",
        },
    }
    local_geometries = {
        name: clean_geometry(unary_union([reference[item] for item in members]))
        for name, members in local_claims.items()
    }
    local_forced = clean_geometry(unary_union(list(local_geometries.values())))
    for name in districts:
        districts[name] = districts[name].difference(local_forced)
    for name, geometry in local_geometries.items():
        districts[name] = clean_geometry(unary_union([districts[name], geometry]))

    # Remove numerical slivers introduced by administrative islands and enforce
    # a deterministic, overlap-free priority order.
    occupied = None
    clean_districts = {}
    for name in district_anchors:
        geometry = districts[name].intersection(frfz)
        if occupied is not None:
            geometry = geometry.difference(occupied)
        geometry = geometry.buffer(0)
        clean_districts[name] = geometry
        occupied = geometry if occupied is None else unary_union([occupied, geometry])
    remainder = frfz.difference(occupied)
    clean_districts["Front Range"] = unary_union(
        [clean_districts["Front Range"], remainder]
    )
    districts = clean_districts

    district_features = [
        source_feature(
            name,
            geometry,
            basis=(
                "Shadowrun-Distrikt der Front Range Free Zone; aktuelle "
                "Gemeinde- bzw. Denver-Stadtteilgrenzen liefern die harte "
                "Linienbasis, Zwischenräume folgen der relativen SR6-Kartenlage"
            ),
            role="lore-district",
            lore_source="The Third Parallel, S. 12-50 und Denver-Karte (SR6)",
            source=TIGERWEB_SOURCE_NAME,
            source_url=TIGERWEB_SOURCE_URL,
            review_status="source-aligned",
            review_label="Mit SR6-Distriktliste und geografischen Außenkanten abgeglichen",
            preserve_partition=True,
        )
        for name, geometry in districts.items()
        if not geometry.is_empty
    ]
    reference_features = [
        geo_feature(
            name,
            geometry,
            basis="Heutiger Denver-Stadtteil als getrennte geografische Referenz",
            role="reference-neighborhood",
        )
        for name, geometry in sorted(reference.items())
    ]
    boundary = source_feature(
        "Front Range Free Zone · äußere DMZ-Kante",
        dmz_outer,
        basis=(
            "SR6-Ausdehnung von Boulder bis Colorado Springs; äußere Kante "
            "aus dem Front-Range-Korridor und der beschriebenen etwa einen "
            "Kilometer breiten umlaufenden DMZ"
        ),
        role="lore-city",
        lore_source="The Third Parallel, S. 12-13 (SR6)",
        source=TIGERWEB_SOURCE_NAME,
        source_url=TIGERWEB_SOURCE_URL,
        review_status="source-aligned",
        review_label=(
            "Mit Boulder–Colorado-Springs-Korridor, publizierter Flächengröße "
            "und ungefähr ein Kilometer breiter äußerer DMZ abgeglichen"
        ),
    )
    write_geojson("denver", "districts.geojson", collection("Denver FRFZ-Distrikte", district_features))
    write_geojson("denver", "neighborhoods.geojson", collection("Denver heutige Stadtteile", reference_features))
    write_geojson("denver", "city-boundary.geojson", collection("Front Range Free Zone", [boundary]))
    write_geojson(
        "denver",
        "outskirts.geojson",
        collection(
            "Denver äußere DMZ",
            [
                source_feature(
                    "Äußere DMZ der Front Range Free Zone",
                    dmz_ring,
                    basis=(
                        "Etwa ein Kilometer breiter, vollständig umlaufender "
                        "Grenzstreifen außerhalb der FRFZ"
                    ),
                    role="lore-dmz",
                    lore_source="The Third Parallel, S. 12–13 (SR6)",
                    source=TIGERWEB_SOURCE_NAME,
                    source_url=TIGERWEB_SOURCE_URL,
                    review_status="source-aligned",
                    review_label=(
                        "Quellenabgeglichene Breite; mangels publizierter "
                        "Vermessung bleibt der exakte Verlauf modelliert"
                    ),
                )
            ],
        ),
    )
    write_geojson(
        "denver",
        "zones.geojson",
        zone_collection(
            "Denver",
            frfz,
            label="Normal / Stadt · Front Range Free Zone",
            basis="Gebiet innerhalb der umlaufenden SR6-DMZ; Distrikte überschneiden sich nicht",
        ),
    )
    write_geojson("denver", "exterritorial.geojson", empty_exterritorial("Denver"))
    write_json(DATA / "denver" / "labels.json", label_payload("denver", districts))


def build_manhattan() -> None:
    reference = named_geometries(read_source("manhattan"))
    district_groups = {
        "Inwood": {"Inwood", "Marble Hill"},
        "Washington Heights": {"Washington Heights"},
        "Newtown": {"Harlem", "East Harlem", "Morningside Heights"},
        "Westside": {"Upper West Side"},
        "Upper Eastside": {"Upper East Side"},
        "Central Park": {"Central Park"},
        "Midtown": {"Midtown", "Flatiron District", "Murray Hill"},
        "Times Square": {"Theater District"},
        "Lower Westside": {"Chelsea"},
        "Terminal": {"Hell's Kitchen"},
        "Stuyvesant": {"Gramercy", "Kips Bay", "Stuyvesant Town"},
        "The Village": {"Greenwich Village", "West Village"},
        "The Pit": {"East Village", "Lower East Side"},
        "SoHo": {"SoHo", "NoHo", "Nolita"},
        "Southside": {"Tribeca"},
        "City Center": {"Civic Center"},
        "Chinatown": {"Chinatown", "Little Italy", "Two Bridges"},
        "The Towers": {"Financial District"},
        "Battery City": {"Battery Park City"},
        "New York Harbor Islands": {
            "Ellis Island", "Governors Island", "Liberty Island",
        },
        "Roosevelt Island": {"Roosevelt Island"},
        "Randall’s and Ward’s Islands": {"Randall's Island"},
    }
    assigned = set().union(*district_groups.values())
    missing = sorted(set(reference) - assigned)
    unknown = sorted(assigned - set(reference))
    if missing or unknown:
        raise SystemExit(f"Manhattan-Lorezuordnung unvollständig: neu={missing}, unbekannt={unknown}")
    districts = {
        name: clean_geometry(unary_union([reference[item] for item in members]))
        for name, members in district_groups.items()
    }
    city_geometry = clean_geometry(unary_union(list(reference.values())))
    partition_priority = [
        "Times Square", "Terminal", "Central Park", "Battery City",
        "The Towers", "City Center", "Chinatown", "The Pit", "SoHo",
        "The Village", "Southside", "Stuyvesant", "Lower Westside",
        "Midtown", "Upper Eastside", "Westside", "Newtown",
        "Washington Heights", "Inwood", "New York Harbor Islands",
        "Roosevelt Island", "Randall’s and Ward’s Islands",
    ]
    occupied = None
    partitioned = {}
    for name in partition_priority:
        geometry = districts[name].intersection(city_geometry)
        if occupied is not None:
            geometry = geometry.difference(occupied)
        geometry = geometry.buffer(0)
        partitioned[name] = geometry
        occupied = geometry if occupied is None else unary_union([occupied, geometry])
    partitioned["Midtown"] = unary_union(
        [partitioned["Midtown"], city_geometry.difference(occupied)]
    )
    districts = {name: partitioned[name] for name in district_groups}
    district_features = [
        source_feature(
            name,
            geometry,
            basis=(
                "Manhattan-Loreviertel aus The Rotten Apple; heutige Straßen- "
                "und Statistikgrenzen dienen ausschließlich als harte Linienbasis"
            ),
            role="lore-district",
            lore_source="The Rotten Apple: Manhattan, S. 13-23 (SR4)",
            source=SOURCE_NAME,
            source_url=SOURCE_URL,
            review_status="source-aligned",
            review_label="Mit SR4-Viertelbeschreibungen und SR6-Karte abgeglichen",
            preserve_partition=True,
        )
        for name, geometry in districts.items()
    ]
    reference_features = [
        geo_feature(
            name,
            geometry,
            basis="Heutiges Manhattan-Viertel als getrennte geografische Referenz",
            role="reference-neighborhood",
        )
        for name, geometry in sorted(reference.items())
    ]
    boundary = source_feature(
        "Manhattan Development Consortium",
        city_geometry,
        basis="Gesamter kartierter Manhattan-Komplex als MDC-Jurisdiktion",
        role="lore-city",
        lore_source="The Rotten Apple: Manhattan, S. 8-12 und 20-23 (SR4)",
        source=SOURCE_NAME,
        source_url=SOURCE_URL,
        review_status="confirmed",
        review_label="MDC-Gesamtjurisdiktion laut Quellenband bestätigt",
    )
    governors = reference["Governors Island"]
    mdc = clean_geometry(city_geometry.difference(governors))
    corporate_features = [
        {
            "type": "Feature",
            "geometry": mapping(mdc),
            "properties": {
                "status": "corporate",
                "zone_type": "orange",
                "label": "Exterritoriales Konzerngebiet · MDC Manhattan",
                "basis": "Die gesamte Manhattan-Insel ist MDC-extraterritorial; Governors Island ist separat Ares zugeordnet",
                "topology": "disjoint",
                "source": "The Rotten Apple: Manhattan, S. 8-12 (SR4)",
                "boundary_review_status": "confirmed",
            },
        },
        {
            "type": "Feature",
            "geometry": mapping(governors),
            "properties": {
                "status": "corporate",
                "zone_type": "orange",
                "label": "Exterritoriales Konzerngebiet · Ares Governors Island",
                "basis": "Ares besitzt laut Quellenband die extraterritorialen Rechte an der gesamten Insel",
                "topology": "disjoint",
                "source": "The Rotten Apple: Manhattan, S. 20 (SR4)",
                "boundary_review_status": "confirmed",
            },
        },
    ]
    topology = {
        "model": "exclusive-partition",
        "priority": ["corporate"],
        "unresolved_overlap_area_degrees_squared": 0,
        "basis": "MDC Manhattan und Ares Governors Island",
    }
    write_geojson("manhattan", "districts.geojson", collection("Manhattan Lore-Viertel", district_features))
    write_geojson("manhattan", "neighborhoods.geojson", collection("Manhattan heutige Viertel", reference_features))
    write_geojson("manhattan", "city-boundary.geojson", collection("MDC Manhattan", [boundary]))
    write_geojson(
        "manhattan",
        "zones.geojson",
        collection("Manhattan Gebietsstatus", corporate_features, topology=topology),
    )
    write_geojson(
        "manhattan",
        "exterritorial.geojson",
        collection("Manhattan exterritoriale Konzerngebiete", corporate_features, topology=topology),
    )
    write_json(DATA / "manhattan" / "labels.json", label_payload("manhattan", districts))


def build_rrm_status(region_geometry) -> tuple[dict, dict]:
    payload = read_payload("essen-districts")
    essen = {
        boundary["name"]: clean_geometry(
            shape({"type": boundary["type"], "coordinates": boundary["coordinates"]})
        )
        for boundary in payload["boundaries"]
    }
    corporate_names = {
        "Rüttenscheid", "Margarethenhöhe", "Fulerum", "Haarzopf",
        "Stadtwald", "Heisingen", "Rellinghausen", "Schuir", "Kettwig",
        "Bredeney", "Werden", "Fischlaken", "Heidhausen",
    }
    missing = sorted(corporate_names - set(essen))
    if missing:
        raise SystemExit(f"Essener Stadtteile für S-K-Enklave fehlen: {missing}")
    # RRM (SR4) names the portions of Holsterhausen and Bergerhausen south of
    # the A40 explicitly. The gently eastward-rising line below follows the
    # motorway centreline through Essen; clipping the municipal polygons keeps
    # their remaining street-level outer edges intact.
    south_of_a40 = Polygon([
        (6.88, 51.20),
        (7.12, 51.20),
        (7.12, 51.462),
        (7.04, 51.458),
        (6.96, 51.454),
        (6.88, 51.450),
    ])
    a40_additions = [
        essen[name].intersection(south_of_a40)
        for name in ("Holsterhausen", "Bergerhausen")
        if name in essen
    ]
    if len(a40_additions) != 2:
        raise SystemExit("Holsterhausen oder Bergerhausen fehlen für den A40-Abgleich")

    # The current airfield footprint is the only surviving hard geographic
    # edge for the fully extraterritorial Essen-Mülheim airport. The source
    # describes later expansion, so the polygon includes its immediately
    # adjoining security verge without extending into surrounding settlements.
    essen_muelheim_airport = Polygon([
        (6.9135, 51.4105),
        (6.9250, 51.4170),
        (6.9575, 51.4138),
        (6.9680, 51.4040),
        (6.9580, 51.3940),
        (6.9255, 51.3930),
        (6.9135, 51.4015),
        (6.9135, 51.4105),
    ])
    corporate_geometry = clean_geometry(
        unary_union(
            [
                *[essen[name] for name in corporate_names],
                *a40_additions,
                essen_muelheim_airport,
            ]
        )
    )
    corporate_geometry = corporate_geometry.intersection(region_geometry)
    normal_geometry = region_geometry.difference(corporate_geometry)
    if not normal_geometry.is_valid:
        normal_geometry = normal_geometry.buffer(0)
    review_label = (
        "Mit benannten Stadtteilen, den südlich der A40 liegenden Teilflächen "
        "und dem vollständig exterritorialen Flughafen Essen-Mülheim abgeglichen"
    )
    corporate = {
        "type": "Feature",
        "geometry": mapping(corporate_geometry),
        "properties": {
            "status": "corporate",
            "zone_type": "orange",
            "label": "Exterritoriales Konzerngebiet · S-K Essen",
            "basis": (
                "Benannte Essener Stadtteile, Teilflächen südlich der A40 und "
                "Flughafen Essen-Mülheim"
            ),
            "topology": "disjoint",
            "source": (
                "Rhein-Ruhr-Megaplex, S. 10–11 und 76–84 (SR4); "
                "Revierbericht 2082, S. 67–71 (SR6)"
            ),
            "geometry_source": "OpenStreetMap-Stadtteilgeometrien über gitter-badger/plasmap",
            "boundary_review_status": "source-aligned",
            "boundary_review_label": review_label,
        },
    }
    normal = {
        "type": "Feature",
        "geometry": mapping(normal_geometry),
        "properties": source_properties(
            status="normal",
            zone_type="magenta",
            label="Normal / Stadt · Rhein-Ruhr-Megaplex",
            basis="Kommunaler Arbeitsumriss abzüglich der bereits erfassten S-K-Enklave",
            topology="disjoint",
        ),
    }
    zones = collection(
        "Rhein-Ruhr-Megaplex Gebietsstatus",
        [corporate, normal],
        topology={
            "model": "exclusive-partition",
            "priority": ["corporate", "normal"],
            "unresolved_overlap_area_degrees_squared": 0,
            "basis": "Rhein-Ruhr-Megaplex (SR4) und geografische Verwaltungsgrundlagen",
        },
    )
    exterritorial = collection(
        "Rhein-Ruhr-Megaplex exterritoriale Konzerngebiete",
        [corporate],
        topology={
            "model": "exclusive-corporate-over-normal",
            "unresolved_overlap_area_degrees_squared": 0,
        },
    )
    return zones, exterritorial


def build_city_from_neighborhoods(city_id: str, display_name: str, source_key: str) -> None:
    geometries = named_geometries(read_source(source_key))
    city_geometry = clean_geometry(unary_union(list(geometries.values())))
    neighborhoods = [
        geo_feature(
            name,
            geometry,
            basis=(
                "Heutige Verwaltungs- bzw. Statistikgrenze; nur geografische "
                "Referenz, keine bestätigte Shadowrun-Grenze"
            ),
            role="reference-neighborhood",
        )
        for name, geometry in sorted(geometries.items())
    ]
    boundary = geo_feature(
        display_name,
        city_geometry,
        basis=(
            "Vereinigung heutiger Stadtteilgeometrien; geografischer "
            "Arbeitsumriss, keine bestätigte Shadowrun-Außengrenze"
        ),
        role="reference-city",
    )
    write_geojson(city_id, "neighborhoods.geojson", collection(f"{display_name} Stadtteile", neighborhoods))
    write_geojson(city_id, "districts.geojson", collection(f"{display_name} Bezirke", []))
    write_geojson(city_id, "city-boundary.geojson", collection(f"{display_name} Stadtgrenze", [boundary]))
    write_geojson(
        city_id,
        "zones.geojson",
        zone_collection(
            display_name,
            city_geometry,
            label=f"Normal / Stadt · {display_name}",
            basis=(
                "Heutiger geografischer Arbeitsumriss. Der Gebietsstatus ist "
                "noch nicht als vollständige Shadowrun-Grenze bestätigt."
            ),
        ),
    )
    write_geojson(city_id, "exterritorial.geojson", empty_exterritorial(display_name))


def build_hamburg() -> None:
    geometries = named_geometries(read_source("hamburg"))
    counties = county_geometries()
    expected = set().union(*HAMBURG_BOROUGHS.values())
    if set(geometries) != expected:
        missing = sorted(set(geometries) - expected)
        unknown = sorted(expected - set(geometries))
        raise SystemExit(f"Hamburger Bezirkszuordnung unvollständig: neu={missing}, unbekannt={unknown}")

    current_boroughs = {
        borough: clean_geometry(unary_union([geometries[name] for name in names]))
        for borough, names in HAMBURG_BOROUGHS.items()
    }
    wilhelmsburg = geometries["Wilhelmsburg"]
    lore_district_geometries = {
        "Altona": current_boroughs["Altona"],
        "Eimsbüttel": current_boroughs["Eimsbüttel"],
        "Nord": current_boroughs["Hamburg-Nord"],
        "Neue Mitte": current_boroughs["Hamburg-Mitte"].difference(wilhelmsburg),
        "Big Willi": wilhelmsburg,
        "Wandsbek": current_boroughs["Wandsbek"],
        "Bergedorf": current_boroughs["Bergedorf"],
        "Harburg": unary_union(
            [
                current_boroughs["Harburg"],
                counties[("Niedersachsen", "Harburg")],
            ]
        ),
        "Pinneberg": counties[("Schleswig-Holstein", "Pinneberg")],
        "Stade": counties[("Niedersachsen", "Stade")],
        "Stormarn": counties[("Schleswig-Holstein", "Stormarn")],
        "Lauenburg": counties[("Schleswig-Holstein", "Lauenburg")],
        # Der Quellenband nennt "weite Teile des Kreises Kaltenkirchen".
        # Der heutige Kreis Segeberg wird deshalb bewusst auf das aus der
        # offiziellen Übersichtskarte ablesbare südwestliche Umfeld begrenzt.
        "Kaltenkirchen": counties[("Schleswig-Holstein", "Segeberg")].intersection(
            box(9.72, 53.62, 10.28, 54.03)
        ),
    }
    districts = []
    inner_districts = {"Altona", "Eimsbüttel", "Nord", "Neue Mitte", "Big Willi"}
    for district_name, geometry in lore_district_geometries.items():
        districts.append(
            {
                "type": "Feature",
                "geometry": mapping(clean_geometry(geometry)),
                "properties": source_properties(
                    name=district_name,
                    basis=(
                        "Shadowrun-Bezirk laut Hamburg-Kartenpaket; auf heutige "
                        "Stadtteil- bzw. Kreisgeometrien übertragen"
                    ),
                    boundary_role=(
                        "lore-inner-district"
                        if district_name in inner_districts
                        else "lore-outer-district"
                    ),
                    lore_source="Datapuls Hamburg und Hamburg-Kartenpaket (SR5)",
                    boundary_review_status=(
                        "source-aligned" if district_name == "Kaltenkirchen" else "confirmed"
                    ),
                    boundary_review_label=(
                        "Mit der offiziellen Hamburg-2080-Übersicht auf den "
                        "südwestlichen Kreis-Segeberg-Ausschnitt abgeglichen"
                        if district_name == "Kaltenkirchen"
                        else "Mit der offiziellen Hamburg-2080-Karte abgeglichen"
                    ),
                ),
            }
        )
    neighborhoods = [
        geo_feature(
            name,
            geometry,
            basis="Heutiger Hamburger Stadtteil als geografische Referenz",
            role="reference-neighborhood",
        )
        for name, geometry in sorted(geometries.items())
    ]
    city_geometry = clean_geometry(unary_union(list(lore_district_geometries.values())))
    boundary = geo_feature(
        "Hamburg",
        city_geometry,
        basis=(
            "Vereinigung der Shadowrun-Bezirke einschließlich der 2045 "
            "eingemeindeten Umlandgebiete"
        ),
        role="lore-city",
    )
    write_geojson("hamburg-2080", "districts.geojson", collection("Hamburg Bezirke", districts))
    write_geojson("hamburg-2080", "neighborhoods.geojson", collection("Hamburg Stadtteile", neighborhoods))
    write_geojson("hamburg-2080", "city-boundary.geojson", collection("Hamburg Stadtgrenze", [boundary]))
    write_geojson(
        "hamburg-2080",
        "zones.geojson",
        zone_collection(
            "Hamburg",
            city_geometry,
            label="Normal / Stadt · Hamburg",
            basis=(
                "Hamburger Shadowrun-Stadtgrenze aus inneren und äußeren Bezirken; "
                "noch nicht einzeln erfasste Konzernflächen bleiben unklassifiziert"
            ),
        ),
    )
    write_geojson("hamburg-2080", "exterritorial.geojson", empty_exterritorial("Hamburg"))


def build_rrm() -> None:
    source = named_geometries(read_source("nordrhein-westfalen"))
    missing = sorted(RRM_MUNICIPALITIES - set(source))
    if missing:
        raise SystemExit(f"RRM-Kommunen fehlen im Quelldatensatz: {missing}")
    geometries = {name: source[name] for name in sorted(RRM_MUNICIPALITIES)}
    region_geometry = clean_geometry(unary_union(list(geometries.values())))
    districts = [
        geo_feature(
            name,
            geometry,
            basis=(
                "Auf der offiziellen Revierübersicht benannte oder innerhalb des "
                "kartierten Megaplexumrisses liegende Kommune; heutige "
                "Gemeindegrenze als geografische Liniengrundlage"
            ),
            role="lore-municipality",
        )
        for name, geometry in geometries.items()
    ]
    boundary = geo_feature(
        "Rhein-Ruhr-Megaplex",
        region_geometry,
        basis=(
            "Vereinigung der auf der offiziellen Revierübersicht benannten und "
            f"innerhalb ihres Umrisses liegenden {len(geometries)} Kommunen"
        ),
        role="lore-region",
    )
    write_geojson("rhein-ruhr-2082", "districts.geojson", collection("Rhein-Ruhr Kommunen", districts))
    write_geojson("rhein-ruhr-2082", "neighborhoods.geojson", collection("Rhein-Ruhr Stadtteile", []))
    write_geojson("rhein-ruhr-2082", "city-boundary.geojson", collection("Rhein-Ruhr-Megaplex Grenze", [boundary]))
    zones, exterritorial = build_rrm_status(region_geometry)
    write_geojson("rhein-ruhr-2082", "zones.geojson", zones)
    write_geojson("rhein-ruhr-2082", "exterritorial.geojson", exterritorial)


def build_adl() -> None:
    states = named_geometries(read_source("germany"))
    country_geometry = clean_geometry(unary_union(list(states.values())))
    boundary = geo_feature(
        "Allianz Deutscher Länder",
        country_geometry,
        basis=(
            "Heutiger deutscher Staatsumriss als geografische Referenz. Die "
            "abweichenden Grenzen der Allianzländer sind noch nicht flächengenau "
            "georeferenziert."
        ),
        role="reference-country",
    )
    # Heutige Bundesländer dürfen nicht als Shadowrun-Allianzländer erscheinen.
    # Bis zur belastbaren Georeferenzierung der Lore-Karte bleibt diese Ebene leer.
    write_geojson("adl-2082", "districts.geojson", collection("ADL Allianzländer", []))
    write_geojson("adl-2082", "neighborhoods.geojson", collection("ADL Stadtteile", []))
    write_geojson("adl-2082", "city-boundary.geojson", collection("ADL Außengrenze", [boundary]))
    write_geojson(
        "adl-2082",
        "zones.geojson",
        zone_collection(
            "Allianz Deutscher Länder",
            country_geometry,
            label="ADL-Gebiet",
            basis=(
                "Geografischer Referenzumriss; keine Darstellung heutiger "
                "Bundesländer als Shadowrun-Allianzländer"
            ),
        ),
    )
    write_geojson("adl-2082", "exterritorial.geojson", empty_exterritorial("Allianz Deutscher Länder"))


def main() -> None:
    from build_seattle_package import build_package as build_seattle_package

    build_hamburg()
    build_seattle_package()
    build_rrm()
    build_city_from_neighborhoods("toronto-2080", "Toronto", "toronto")
    build_denver()
    build_chicago()
    build_manhattan()
    build_adl()
    print(
        "Boundary packages generated for Chicago, Hamburg, Seattle, RRM, "
        "Toronto, Denver, Manhattan, and ADL."
    )


if __name__ == "__main__":
    main()
