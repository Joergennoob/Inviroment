#!/usr/bin/env python3
"""Estimate people, housing units, and public schools within 3,200 feet of a well.

This is our calculation. CalGEM has not published these counts. The script downloads
public inputs, writes data/derived/setback_3200.json, and prints a short summary.

Inputs
- CalGEM WellSTAR Wells layer 0. Wells with WellStatus Active or Idle and a
  coordinate inside California. One record per API number.
- Census 2020 PL 94-171 geographic header for California, summary level 750
  (census block). Population and housing units are on the same record as the
  block internal point.
- NCES EDGE public school locations, 2023-24, and private schools from the
  2021-22 Private School Survey, STATE = CA.

Rule
- A block counts when its internal point is within 3,200 feet of at least one
  selected well. Distance is equirectangular, 69.172 miles per degree of latitude.
- A 2020 census tract is flagged when at least one of its blocks with population
  greater than zero meets that test. The tract flag is for a later comparison.
  It is wider than the buffer.
- A school counts when the school point is within 3,200 feet of at least one
  selected well. Public and private schools are counted separately. The
  private-school file is the 2021-22 PSS, two years older than the public file.

The block internal point is not a polygon intersection. A large block can have
people who live farther from the well than the internal point, or closer.
"""

from __future__ import annotations

import json
import math
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "setback_3200.json"
CACHE = Path("/tmp/ca/src")
UA = "InviromentResearch/1.0 (public-data; educational)"
FEET = 3200.0
MILES_PER_DEG_LAT = 69.172
FEET_PER_MILE = 5280.0
CELL = 0.01
WELLS = "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/0/query"
PL_ZIP = (
    "https://www2.census.gov/programs-surveys/decennial/2020/data/"
    "01-Redistricting_File--PL_94-171/California/ca2020.pl.zip"
)
SCHOOLS = (
    "https://nces.ed.gov/opengis/rest/services/K12_School_Locations/"
    "EDGE_GEOCODE_PUBLICSCH_2324/MapServer/0/query"
)
PRIVATE_SCHOOLS = (
    "https://nces.ed.gov/opengis/rest/services/K12_School_Locations/"
    "EDGE_GEOCODE_PRIVATESCH_2122/MapServer/0/query"
)
FACILITIES = {
    "el_segundo": (33.916216, -118.41873, 5280.0),
    "torrance": (33.854967, -118.336907, 5280.0),
    "wilmington": (33.76336, -118.27645, 5280.0),
    "aliso_canyon": (34.307569, -118.551235, 26400.0),
}


def get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def feet_between(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    mid = math.radians((lat1 + lat2) / 2.0)
    dy = (lat1 - lat2) * MILES_PER_DEG_LAT * FEET_PER_MILE
    dx = (lon1 - lon2) * MILES_PER_DEG_LAT * math.cos(mid) * FEET_PER_MILE
    return math.hypot(dx, dy)


def cell_of(lat: float, lon: float) -> tuple[int, int]:
    return int(math.floor(lat / CELL)), int(math.floor(lon / CELL))


def download_wells() -> list[tuple[float, float]]:
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / "wells_active_idle.json"
    if cached.exists() and cached.stat().st_size > 1000:
        loaded = json.loads(cached.read_text(encoding="utf-8"))
        print(f"wells cached {len(loaded)}", flush=True)
        return [(item[0], item[1]) for item in loaded]
    where = "(WellStatus='Active' OR WellStatus='Idle') AND Latitude IS NOT NULL"
    seen: set[str] = set()
    points: list[tuple[float, float]] = []
    offset = 0
    while True:
        query = urllib.parse.urlencode(
            {
                "where": where,
                "outFields": "API,Latitude,Longitude,WellStatus",
                "returnGeometry": "false",
                "f": "json",
                "resultOffset": offset,
                "resultRecordCount": 2000,
            }
        )
        payload = json.loads(get(f"{WELLS}?{query}"))
        if "error" in payload:
            raise SystemExit(payload["error"])
        features = payload.get("features") or []
        for feature in features:
            attr = feature["attributes"]
            lat = attr.get("Latitude")
            lon = attr.get("Longitude")
            if lat is None or lon is None:
                continue
            lat_f = float(lat)
            lon_f = float(lon)
            if not (32.0 <= lat_f <= 42.5 and -125.0 <= lon_f <= -114.0):
                continue
            api = str(attr.get("API") or f"{lat_f:.5f},{lon_f:.5f}")
            if api in seen:
                continue
            seen.add(api)
            points.append((lat_f, lon_f))
        offset += len(features)
        print(f"wells {offset}", flush=True)
        if not payload.get("exceededTransferLimit") or not features:
            break
        time.sleep(0.2)
    cached.write_text(json.dumps(points), encoding="utf-8")
    return points


def grid_points(points: list[tuple[float, float]]) -> dict[tuple[int, int], list[tuple[float, float]]]:
    grid: dict[tuple[int, int], list[tuple[float, float]]] = {}
    for lat, lon in points:
        grid.setdefault(cell_of(lat, lon), []).append((lat, lon))
    return grid


def near(grid: dict[tuple[int, int], list[tuple[float, float]]], lat: float, lon: float, limit: float) -> bool:
    ix, iy = cell_of(lat, lon)
    # 0.01 degree is about 0.69 miles. 3,200 feet is 0.61 miles, so two cells
    # of padding covers the diagonal.
    span = 2 if limit <= 5280 else 8
    for dx in range(-span, span + 1):
        for dy in range(-span, span + 1):
            for wlat, wlon in grid.get((ix + dx, iy + dy), ()):
                if feet_between(lat, lon, wlat, wlon) <= limit:
                    return True
    return False


def ensure_pl() -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "ca2020.pl.zip"
    if not path.exists() or path.stat().st_size < 1_000_000:
        print("downloading PL 94-171", flush=True)
        path.write_bytes(get(PL_ZIP, timeout=300))
    return path


def scan_blocks(grid: dict[tuple[int, int], list[tuple[float, float]]]) -> dict:
    path = ensure_pl()
    population = 0
    housing = 0
    blocks_hit = 0
    blocks_read = 0
    populated_tracts: set[str] = set()
    facility_pop = {name: 0 for name in FACILITIES}
    facility_housing = {name: 0 for name in FACILITIES}
    facility_tracts: dict[str, set[str]] = {name: set() for name in FACILITIES}
    with zipfile.ZipFile(path) as archive:
        with archive.open("cageo2020.pl") as handle:
            for raw in handle:
                parts = raw.decode("latin1").rstrip("\r\n").split("|")
                if len(parts) < 20 or parts[2] != "750":
                    continue
                blocks_read += 1
                try:
                    pop = int(parts[-7])
                    homes = int(parts[-6])
                    lat = float(parts[-5])
                    lon = float(parts[-4])
                except ValueError:
                    continue
                geoid = parts[9]
                tract = geoid[:11]
                if near(grid, lat, lon, FEET):
                    blocks_hit += 1
                    population += pop
                    housing += homes
                    if pop > 0:
                        populated_tracts.add(tract)
                for name, (flat, flon, limit) in FACILITIES.items():
                    if feet_between(lat, lon, flat, flon) <= limit:
                        facility_pop[name] += pop
                        facility_housing[name] += homes
                        if pop > 0:
                            facility_tracts[name].add(tract)
                if blocks_read % 100000 == 0:
                    print(f"blocks {blocks_read}", flush=True)
    return {
        "blocks_read": blocks_read,
        "blocks_within_3200_ft": blocks_hit,
        "population_2020": population,
        "housing_units_2020": housing,
        "tracts_2020_with_populated_block": sorted(populated_tracts),
        "facilities": {
            name: {
                "population_2020": facility_pop[name],
                "housing_units_2020": facility_housing[name],
                "radius_feet": FACILITIES[name][2],
                "latitude": FACILITIES[name][0],
                "longitude": FACILITIES[name][1],
                "tracts_2020": sorted(facility_tracts[name]),
            }
            for name in FACILITIES
        },
    }


def download_schools(url: str, id_field: str, label: str) -> list[tuple[str, str, float, float]]:
    schools: list[tuple[str, str, float, float]] = []
    offset = 0
    while True:
        query = urllib.parse.urlencode(
            {
                "where": "STATE='CA'",
                "outFields": f"{id_field},NAME,LAT,LON",
                "returnGeometry": "false",
                "f": "json",
                "resultOffset": offset,
                "resultRecordCount": 2000,
            }
        )
        payload = json.loads(get(f"{url}?{query}"))
        features = payload.get("features") or []
        for feature in features:
            attr = feature["attributes"]
            lat = attr.get("LAT")
            lon = attr.get("LON")
            if lat is None or lon is None:
                continue
            schools.append((str(attr.get(id_field) or ""), str(attr.get("NAME") or ""), float(lat), float(lon)))
        offset += len(features)
        print(f"{label} {offset}", flush=True)
        if not payload.get("exceededTransferLimit") or not features:
            break
    return schools


def main() -> None:
    wells = download_wells()
    grid = grid_points(wells)
    block_result = scan_blocks(grid)
    schools = download_schools(SCHOOLS, "NCESSCH", "public schools")
    private = download_schools(PRIVATE_SCHOOLS, "PPIN", "private schools")
    school_hits = [
        {"ncessch": nces, "name": name}
        for nces, name, lat, lon in schools
        if near(grid, lat, lon, FEET)
    ]
    private_hits = [
        {"ppin": ppin, "name": name}
        for ppin, name, lat, lon in private
        if near(grid, lat, lon, FEET)
    ]
    facility_schools = {}
    for name, (flat, flon, limit) in FACILITIES.items():
        facility_schools[name] = sum(
            1 for _nces, _name, lat, lon in schools if feet_between(lat, lon, flat, flon) <= limit
        )
    for name in block_result["facilities"]:
        block_result["facilities"][name]["public_schools_2023_24"] = facility_schools[name]
    result = {
        "label": "Egen beregning. CalGEM har ikke publisert dette tallet.",
        "retrieved": "2026-10-28",
        "distance_feet": 3200,
        "wells": {
            "count": len(wells),
            "definition": "WellStatus Active or Idle, one row per API, coordinate inside California",
            "url": WELLS,
        },
        "census": {
            "url": PL_ZIP,
            "file": "cageo2020.pl",
            "summary_level": "750",
            "population_field": "2020 census population on the geographic header",
            "housing_field": "2020 census housing units on the geographic header",
        },
        "schools": {
            "url": SCHOOLS,
            "vintage": "NCES EDGE public schools 2023-24",
            "california_public_schools": len(schools),
            "within_3200_ft": len(school_hits),
            "private_url": PRIVATE_SCHOOLS,
            "private_vintage": "NCES EDGE private schools, PSS 2021-22",
            "california_private_schools": len(private),
            "private_within_3200_ft": len(private_hits),
        },
        "method": (
            "Block internal point or school point within 3,200 feet of an active or idle well. "
            "Equirectangular distance, 69.172 miles per degree of latitude."
        ),
        **block_result,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # School names can be long. Keep the count in the main file and the ids beside it.
    ids_path = OUT.with_name("setback_3200_schools.json")
    ids_path.write_text(
        json.dumps({"public": school_hits, "private": private_hits}, ensure_ascii=False),
        encoding="utf-8",
    )
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "wells": len(wells),
                "blocks_hit": block_result["blocks_within_3200_ft"],
                "population_2020": block_result["population_2020"],
                "housing_units_2020": block_result["housing_units_2020"],
                "tracts": len(block_result["tracts_2020_with_populated_block"]),
                "public_schools": len(school_hits),
                "private_schools": len(private_hits),
                "facilities": {
                    name: {
                        "population_2020": item["population_2020"],
                        "housing_units_2020": item["housing_units_2020"],
                        "schools": item["public_schools_2023_24"],
                        "tracts": len(item["tracts_2020"]),
                    }
                    for name, item in block_result["facilities"].items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
