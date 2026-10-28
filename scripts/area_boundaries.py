#!/usr/bin/env python3
"""Population inside published area boundaries, not county stand-ins.

Writes data/derived/area_boundaries.json.

Geographies
- EPA Green Book PM2.5 (2012) and ozone (2015) nonattainment polygons for
  Los Angeles-South Coast Air Basin and San Joaquin Valley.
- DWR Bulletin 118 critically overdrafted basin polygons (21 basins).
- Blocks within 1 mile of the Salton Sea shoreline polygon published with the
  OpenTopography catalog. That outline is not the IID exposed-playa polygon.
- State Water Board SABL water-service areas joined to the SAFER flat file by
  water system number. Failing is CURRENT_FAILING = Failing. The comparison
  group is CURRENT_FAILING = Not Failing. Systems absent from the SAFER file
  are not called compliant.

People are 2020 census block populations whose internal point falls in the
polygon. PLACES prevalence is the tract value, weighted by the block population
inside the area. CalEnviroScreen uses 2010 tract centroids that fall in the
polygon, weighted by ACS2019TotalPop. A centroid test is not a polygon
intersection of the tract.
"""

from __future__ import annotations

import csv
import json
import math
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "area_boundaries.json"
CACHE = Path("/tmp/ca/src")
UA = "InviromentResearch/1.0 (public-data; educational)"
MILES_PER_DEG = 69.172
FEET_PER_MILE = 5280.0
PL_ZIP = (
    "https://www2.census.gov/programs-surveys/decennial/2020/data/"
    "01-Redistricting_File--PL_94-171/California/ca2020.pl.zip"
)
PLACES_URL = "https://data.cdc.gov/resource/yjkw-uj5s.csv"
CES_URL = (
    "https://services1.arcgis.com/PCHfdHz4GlDNAhBb/arcgis/rest/services/"
    "CalEnviroScreen_4_0_Results_/FeatureServer/0/query"
)
SABL_URL = (
    "https://gispublic.waterboards.ca.gov/portalserver/rest/services/"
    "Drinking_Water/California_Drinking_Water_System_Area_Boundaries/FeatureServer/0/query"
)
EPA_PM = "https://geopub.epa.gov/ArcGIS/rest/services/icr/icrmap/MapServer/21/query"
EPA_OZONE = "https://geopub.epa.gov/ArcGIS/rest/services/icr/icrmap/MapServer/16/query"
COD_URL = (
    "https://gis.water.ca.gov/arcgis/rest/services/Geoscientific/"
    "i08_CriticallyOverdraftedBasins/MapServer/0/query"
)
SAFER_PACKAGE = "https://data.ca.gov/api/3/action/package_show?id=safer-failing-and-at-risk-drinking-water-systems"
SALTON_URL = (
    "https://raw.githubusercontent.com/OpenTopography/Data_Catalog_Spatial_Boundaries/"
    "main/OpenTopography_Raster/Salton_Sea.geojson"
)
PLACE_KEYS = [
    "casthma_crudeprev",
    "copd_crudeprev",
    "chd_crudeprev",
    "cancer_crudeprev",
    "diabetes_crudeprev",
]
CES_KEYS = ["asthma", "cvd", "lbw", "edu", "ling", "pov", "Hispanic_pct", "drink"]


def get(url: str, timeout: int = 120) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def feet_between(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    mid = math.radians((lat1 + lat2) / 2.0)
    dy = (lat1 - lat2) * MILES_PER_DEG * FEET_PER_MILE
    dx = (lon1 - lon2) * MILES_PER_DEG * math.cos(mid) * FEET_PER_MILE
    return math.hypot(dx, dy)


def point_in_rings(lon: float, lat: float, rings: list) -> bool:
    inside = False
    for ring in rings:
        count = len(ring)
        if count < 3:
            continue
        previous = count - 1
        hit = False
        for index in range(count):
            lon_i, lat_i = ring[index][0], ring[index][1]
            lon_j, lat_j = ring[previous][0], ring[previous][1]
            if (lat_i > lat) != (lat_j > lat):
                cross = (lon_j - lon_i) * (lat - lat_i) / (lat_j - lat_i) + lon_i
                if lon < cross:
                    hit = not hit
            previous = index
        if hit:
            inside = not inside
    return inside


class PolygonIndex:
    def __init__(self, cell: float = 0.05) -> None:
        self.cell = cell
        self.grid: dict[tuple[int, int], list[int]] = {}
        self.items: list[dict] = []

    def add(self, key: str, rings: list) -> None:
        lons = [point[0] for ring in rings for point in ring]
        lats = [point[1] for ring in rings for point in ring]
        if not lons:
            return
        item = {
            "key": key,
            "rings": rings,
            "minx": min(lons),
            "maxx": max(lons),
            "miny": min(lats),
            "maxy": max(lats),
        }
        index = len(self.items)
        self.items.append(item)
        x0 = math.floor(item["minx"] / self.cell)
        x1 = math.floor(item["maxx"] / self.cell)
        y0 = math.floor(item["miny"] / self.cell)
        y1 = math.floor(item["maxy"] / self.cell)
        for ix in range(x0, x1 + 1):
            for iy in range(y0, y1 + 1):
                self.grid.setdefault((ix, iy), []).append(index)

    def keys_at(self, lon: float, lat: float) -> set[str]:
        found: set[str] = set()
        cell = (math.floor(lon / self.cell), math.floor(lat / self.cell))
        for index in self.grid.get(cell, ()):
            item = self.items[index]
            if not (item["minx"] <= lon <= item["maxx"] and item["miny"] <= lat <= item["maxy"]):
                continue
            if point_in_rings(lon, lat, item["rings"]):
                found.add(item["key"])
        return found


def query_geojson(url: str, where: str, out_fields: str, offset_step: float) -> list[dict]:
    features = []
    offset = 0
    while True:
        query = urllib.parse.urlencode(
            {
                "where": where,
                "outFields": out_fields,
                "returnGeometry": "true",
                "outSR": "4326",
                "maxAllowableOffset": str(offset_step),
                "geometryPrecision": "5",
                "resultOffset": offset,
                "resultRecordCount": 100,
                "f": "json",
            }
        )
        payload = json.loads(get(f"{url}?{query}", timeout=180))
        if payload.get("error"):
            raise SystemExit(payload["error"])
        batch = payload.get("features") or []
        features.extend(batch)
        print(f"geo {len(features)}", flush=True)
        if not batch or len(batch) < 100:
            break
        offset += len(batch)
        time.sleep(0.1)
    return features


def load_blocks() -> list[tuple[str, int, float, float]]:
    path = CACHE / "ca2020.pl.zip"
    if not path.exists() or path.stat().st_size < 1_000_000:
        print("downloading census blocks", flush=True)
        path.write_bytes(get(PL_ZIP, timeout=300))
    blocks = []
    with zipfile.ZipFile(path) as archive:
        with archive.open("cageo2020.pl") as handle:
            for raw in handle:
                parts = raw.decode("latin1").rstrip("\r\n").split("|")
                if len(parts) < 20 or parts[2] != "750":
                    continue
                try:
                    pop = int(parts[-7])
                    lat = float(parts[-5])
                    lon = float(parts[-4])
                except ValueError:
                    continue
                if pop <= 0:
                    continue
                blocks.append((parts[9][:11], pop, lat, lon))
    print(f"populated blocks {len(blocks)}", flush=True)
    return blocks


def load_places() -> dict[str, dict]:
    path = CACHE / "places_ca.csv"
    if not path.exists() or path.stat().st_size < 1000:
        query = urllib.parse.urlencode(
            {
                "stateabbr": "CA",
                "$select": "tractfips,totalpopulation," + ",".join(PLACE_KEYS),
                "$limit": 20000,
            }
        )
        path.write_bytes(get(f"{PLACES_URL}?{query}"))
    rows = {}
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            item = {}
            for key in PLACE_KEYS:
                item[key] = float(row[key]) if row[key] not in ("", None) else None
            rows[row["tractfips"].zfill(11)] = item
    return rows


def load_ces() -> list[dict]:
    rows = []
    offset = 0
    fields = "tract,ACS2019TotalPop," + ",".join(CES_KEYS)
    while True:
        query = urllib.parse.urlencode(
            {
                "where": "1=1",
                "outFields": fields,
                "returnGeometry": "false",
                "returnCentroid": "true",
                "outSR": "4326",
                "f": "json",
                "resultOffset": offset,
                "resultRecordCount": 2000,
            }
        )
        payload = json.loads(get(f"{CES_URL}?{query}"))
        features = payload.get("features") or []
        for feature in features:
            centroid = feature.get("centroid") or {}
            attr = feature["attributes"]
            if centroid.get("x") is None:
                continue
            item = {
                "tract": f"{int(attr['tract']):011d}",
                "pop": float(attr.get("ACS2019TotalPop") or 0),
                "lon": float(centroid["x"]),
                "lat": float(centroid["y"]),
            }
            for key in CES_KEYS:
                value = attr.get(key)
                item[key] = float(value) if value is not None else None
            rows.append(item)
        offset += len(features)
        if not features or not payload.get("exceededTransferLimit"):
            break
    print(f"ces centroids {len(rows)}", flush=True)
    return rows


def safer_rows() -> list[dict]:
    path = CACHE / "SAFER_RA.csv"
    if not path.exists() or path.stat().st_size < 1000:
        package = json.loads(get(SAFER_PACKAGE))
        url = ""
        for resource in package["result"]["resources"]:
            if "flat file" in resource.get("name", "").lower() and resource.get("format", "").upper() == "CSV":
                url = resource["url"]
        if not url:
            raise SystemExit("SAFER CSV url missing")
        path.write_bytes(get(url, timeout=180))
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def weighted(pairs: list[tuple[float, float]]) -> dict:
    numerator = 0.0
    denominator = 0.0
    for value, weight in pairs:
        if weight <= 0:
            continue
        numerator += value * weight
        denominator += weight
    mean = numerator / denominator if denominator else None
    return {"mean": None if mean is None else round(mean, 2), "population": int(round(denominator))}


def places_summary(pop_by_tract: dict[str, int], places: dict[str, dict], outside: dict[str, int]) -> dict:
    result = {}
    for key in PLACE_KEYS:
        inside_pairs = []
        outside_pairs = []
        for tract, pop in pop_by_tract.items():
            value = places.get(tract, {}).get(key)
            if value is not None:
                inside_pairs.append((value, pop))
        for tract, pop in outside.items():
            value = places.get(tract, {}).get(key)
            if value is not None:
                outside_pairs.append((value, pop))
        area = weighted(inside_pairs)
        rest = weighted(outside_pairs)
        ratio = None
        if area["mean"] is not None and rest["mean"] not in (None, 0):
            ratio = round(area["mean"] / rest["mean"], 2)
        result[key] = {"area": area, "comparison": rest, "ratio": ratio}
    return result


def ces_summary(inside_rows: list[dict], outside_rows: list[dict]) -> dict:
    result = {}
    for key in CES_KEYS:
        area = weighted([(row[key], row["pop"]) for row in inside_rows if row[key] is not None and row["pop"] > 0])
        rest = weighted([(row[key], row["pop"]) for row in outside_rows if row[key] is not None and row["pop"] > 0])
        ratio = None
        if area["mean"] is not None and rest["mean"] not in (None, 0):
            ratio = round(area["mean"] / rest["mean"], 2)
        result[key] = {"area": area, "comparison": rest, "ratio": ratio}
    return result


def block_pop(blocks, pred) -> tuple[int, int, dict[str, int]]:
    population = 0
    count = 0
    by_tract: dict[str, int] = {}
    for tract, pop, lat, lon in blocks:
        if pred(lat, lon):
            population += pop
            count += 1
            by_tract[tract] = by_tract.get(tract, 0) + pop
    return population, count, by_tract


def outside_tracts(total: dict[str, int], inside: dict[str, int]) -> dict[str, int]:
    result = {}
    for tract, pop in total.items():
        rest = pop - inside.get(tract, 0)
        if rest > 0:
            result[tract] = rest
    return result


def load_salton_rings() -> list:
    path = CACHE / "salton.geojson"
    if not path.exists():
        path.write_bytes(get(SALTON_URL))
    payload = json.loads(path.read_text(encoding="utf-8"))
    geometry = payload["geometry"] if "geometry" in payload else payload["features"][0]["geometry"]
    return geometry["coordinates"]


def near_salton(lat: float, lon: float, ring: list, limit_feet: float = 5280.0) -> bool:
    best = 1e12
    previous = ring[-1]
    for point in ring:
        # Closest point on the segment in local equirectangular feet.
        lat1, lon1 = previous[1], previous[0]
        lat2, lon2 = point[1], point[0]
        mid = math.radians((lat + lat1) / 2.0)
        scale_x = MILES_PER_DEG * math.cos(mid) * FEET_PER_MILE
        scale_y = MILES_PER_DEG * FEET_PER_MILE
        ax = (lon1 - lon) * scale_x
        ay = (lat1 - lat) * scale_y
        bx = (lon2 - lon) * scale_x
        by = (lat2 - lat) * scale_y
        dx = bx - ax
        dy = by - ay
        denom = dx * dx + dy * dy
        if denom == 0:
            distance = math.hypot(ax, ay)
        else:
            tee = max(0.0, min(1.0, -((ax * dx) + (ay * dy)) / denom))
            distance = math.hypot(ax + tee * dx, ay + tee * dy)
        if distance < best:
            best = distance
            if best <= limit_feet:
                return True
        previous = point
    return best <= limit_feet


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    rows = safer_rows()
    failing = {}
    compliant = {}
    for row in rows:
        number = row["WATER_SYSTEM_NUMBER"].strip().upper()
        try:
            population = int(float(row["POPULATION"] or 0))
        except ValueError:
            population = 0
        if row["CURRENT_FAILING"] == "Failing":
            failing[number] = population
        elif row["CURRENT_FAILING"] == "Not Failing":
            compliant[number] = population
    print(f"safer failing {len(failing)} compliant {len(compliant)}", flush=True)

    print("downloading SABL", flush=True)
    sabl = query_geojson(
        SABL_URL,
        "BOUNDARY_TYPE='Water Service Area'",
        "SABL_PWSID",
        0.0003,
    )
    water_index = PolygonIndex(0.08)
    matched_failing = set()
    matched_compliant = set()
    for feature in sabl:
        number = str(feature["attributes"].get("SABL_PWSID") or "").strip().upper()
        rings = feature.get("geometry", {}).get("rings") or []
        if number in failing:
            water_index.add("fail:" + number, rings)
            matched_failing.add(number)
        elif number in compliant:
            water_index.add("ok:" + number, rings)
            matched_compliant.add(number)
    print(f"sabl features {len(sabl)} matched failing {len(matched_failing)} compliant {len(matched_compliant)}", flush=True)

    areas = {}
    for url, ids in (
        (EPA_PM, ["PM-2.5.2012.LA-South_Coast", "PM-2.5.2012.San_Joaquin_Valley"]),
        (EPA_OZONE, ["Ozone_8-hr.2015.LA-South_Coast", "Ozone_8-hr.2015.San_Joaquin_Valley"]),
    ):
        for composite in ids:
            print("epa", composite, flush=True)
            features = query_geojson(url, f"composite_id='{composite}'", "area_name,composite_id", 0.002)
            index = PolygonIndex(0.1)
            for feature in features:
                index.add(composite, feature["geometry"]["rings"])
            areas[composite] = index
    print("basins", flush=True)
    basin_features = query_geojson(COD_URL, "1=1", "Basin_Subbasin_Number,Basin_Name", 0.001)
    basin_index = PolygonIndex(0.1)
    basin_names = []
    for feature in basin_features:
        name = feature["attributes"].get("Basin_Name")
        basin_names.append(name)
        basin_index.add("cod", feature["geometry"]["rings"])
    salton_ring = load_salton_rings()[0]

    blocks = load_blocks()
    total_by_tract: dict[str, int] = {}
    for tract, pop, _lat, _lon in blocks:
        total_by_tract[tract] = total_by_tract.get(tract, 0) + pop
    places = load_places()
    ces = load_ces()

    def polygon_report(index: PolygonIndex, key: str) -> dict:
        population, count, by_tract = block_pop(blocks, lambda lat, lon: key in index.keys_at(lon, lat))
        health = places_summary(by_tract, places, outside_tracts(total_by_tract, by_tract))
        inside_ces = [row for row in ces if key in index.keys_at(row["lon"], row["lat"])]
        outside_ces = [row for row in ces if key not in index.keys_at(row["lon"], row["lat"])]
        return {
            "block_population_2020": population,
            "populated_blocks": count,
            "places": health,
            "ces_centroid": ces_summary(inside_ces, outside_ces),
            "ces_tracts": len(inside_ces),
        }

    reports = {}
    for composite, index in areas.items():
        print("score", composite, flush=True)
        reports[composite] = polygon_report(index, composite)
    print("score basins", flush=True)
    reports["critically_overdrafted_basins"] = polygon_report(basin_index, "cod")
    reports["critically_overdrafted_basins"]["basin_count"] = len(basin_features)
    reports["critically_overdrafted_basins"]["basin_names"] = basin_names

    print("score salton", flush=True)
    salton_pop, salton_blocks, salton_tracts = block_pop(
        blocks,
        lambda lat, lon: 32.6 <= lat <= 33.8 and -116.4 <= lon <= -115.2 and near_salton(lat, lon, salton_ring),
    )
    reports["salton_1_mile"] = {
        "block_population_2020": salton_pop,
        "populated_blocks": salton_blocks,
        "tracts_with_populated_block": len(salton_tracts),
        "places": places_summary(salton_tracts, places, outside_tracts(total_by_tract, salton_tracts)),
        "note": "1 mile from the OpenTopography Salton Sea outline. Not the IID exposed-playa polygon.",
    }

    print("score water", flush=True)
    fail_pop = 0
    ok_pop = 0
    both = 0
    fail_tracts: dict[str, int] = {}
    ok_tracts: dict[str, int] = {}
    for tract, pop, lat, lon in blocks:
        hits = water_index.keys_at(lon, lat)
        kinds = {item.split(":", 1)[0] for item in hits}
        if "fail" in kinds and "ok" in kinds:
            both += pop
        if "fail" in kinds:
            fail_pop += pop
            fail_tracts[tract] = fail_tracts.get(tract, 0) + pop
        elif "ok" in kinds:
            ok_pop += pop
            ok_tracts[tract] = ok_tracts.get(tract, 0) + pop
    unmatched_failing_population = sum(pop for number, pop in failing.items() if number not in matched_failing)
    reports["drinking_water"] = {
        "safer_retrieved_created_date": rows[0]["CREATED_DATE"][:10] if rows else "",
        "safer_failing_systems": len(failing),
        "safer_failing_population_field": sum(failing.values()),
        "safer_not_failing_systems": len(compliant),
        "failing_with_water_service_polygon": len(matched_failing),
        "failing_without_water_service_polygon": len(failing) - len(matched_failing),
        "safer_population_of_failing_systems_without_polygon": unmatched_failing_population,
        "not_failing_with_water_service_polygon": len(matched_compliant),
        "block_population_in_failing_service_area": fail_pop,
        "block_population_in_not_failing_service_area_only": ok_pop,
        "block_population_in_both": both,
        "places_failing_vs_not_failing": places_summary(fail_tracts, places, ok_tracts),
        "rule": (
            "A block is failing if its internal point is inside at least one failing "
            "water-service polygon. It is not-failing only if it is inside a not-failing "
            "polygon and no failing polygon. Overlap is counted in failing."
        ),
    }
    # CES centroids for water, same rule.
    fail_ces = []
    ok_ces = []
    for row in ces:
        hits = water_index.keys_at(row["lon"], row["lat"])
        kinds = {item.split(":", 1)[0] for item in hits}
        if "fail" in kinds:
            fail_ces.append(row)
        elif "ok" in kinds:
            ok_ces.append(row)
    reports["drinking_water"]["ces_centroid_failing_vs_not_failing"] = ces_summary(fail_ces, ok_ces)
    reports["drinking_water"]["ces_failing_tracts"] = len(fail_ces)
    reports["drinking_water"]["ces_not_failing_tracts"] = len(ok_ces)

    output = {
        "retrieved": "2026-10-28",
        "method": (
            "2020 block internal point in a published polygon. "
            "EPA polygons were generalized by about 0.002 degrees, SABL by about 0.0003, basins by about 0.001. "
            "EPA says the shapefile is for mapping and 40 CFR part 81 is the legal boundary."
        ),
        "sources": {
            "epa_pm25_2012": EPA_PM,
            "epa_ozone_2015": EPA_OZONE,
            "dwr_cod": COD_URL,
            "sabl": SABL_URL,
            "safer_package": SAFER_PACKAGE,
            "salton_outline": SALTON_URL,
            "places": PLACES_URL,
            "ces": CES_URL,
            "blocks": PL_ZIP,
        },
        "areas": reports,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    brief = {
        key: {
            "pop": item.get("block_population_2020") or item.get("block_population_in_failing_service_area"),
            "asthma": (item.get("places") or item.get("places_failing_vs_not_failing") or {}).get("casthma_crudeprev"),
        }
        for key, item in reports.items()
    }
    print(json.dumps(brief, indent=2))


if __name__ == "__main__":
    main()
