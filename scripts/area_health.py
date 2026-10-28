#!/usr/bin/env python3
"""Population-weighted health and demographic comparisons for the ten problems.

Writes data/derived/area_health.json. County groups are stand-ins where the
agency boundary is not a county. Tract groups for the 3,200-foot zone, the
refinery circles, and Aliso Canyon come from scripts/setback_3200.py.

CDC PLACES crude prevalence is weighted by the PLACES totalpopulation field.
CalEnviroScreen 4.0 indicators are weighted by ACS2019TotalPop. The two files
use different tract vintages, so a 2020 tract list is not applied to
CalEnviroScreen.
"""

from __future__ import annotations

import csv
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "derived" / "area_health.json"
SETBACK = ROOT / "data" / "derived" / "setback_3200.json"
CACHE = Path("/tmp/ca/src")
UA = "InviromentResearch/1.0 (public-data; educational)"
PLACES_URL = "https://data.cdc.gov/resource/yjkw-uj5s.csv"
CES_URL = (
    "https://services1.arcgis.com/PCHfdHz4GlDNAhBb/arcgis/rest/services/"
    "CalEnviroScreen_4_0_Results_/FeatureServer/0/query"
)
PLACES_FIELDS = (
    "tractfips,countyfips,totalpopulation,casthma_crudeprev,copd_crudeprev,"
    "chd_crudeprev,cancer_crudeprev,diabetes_crudeprev"
)
CES_FIELDS = (
    "tract,ACS2019TotalPop,asthma,cvd,lbw,edu,ling,pov,housingB,"
    "Hispanic_pct,White_pct,African_American_pct,Asian_American_pct,"
    "Children_under10_pct,Elderly_65over_pct,drink"
)

SOUTH_COAST = {"06037", "06059", "06065", "06071"}
SJV = {"06077", "06099", "06047", "06039", "06019", "06107", "06031", "06029"}
PESTICIDE = {"06019", "06029", "06107", "06053"}
IMPERIAL = {"06025"}


def get(url: str, timeout: int = 120) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def load_places() -> list[dict]:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "places_ca.csv"
    if not path.exists() or path.stat().st_size < 1000:
        query = urllib.parse.urlencode(
            {
                "stateabbr": "CA",
                "$select": PLACES_FIELDS,
                "$limit": 20000,
            }
        )
        path.write_bytes(get(f"{PLACES_URL}?{query}"))
    rows = []
    with path.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            tract = row["tractfips"].zfill(11)
            pop = float(row["totalpopulation"] or 0)
            item = {"tract": tract, "county": tract[:5], "pop": pop}
            for key in (
                "casthma_crudeprev",
                "copd_crudeprev",
                "chd_crudeprev",
                "cancer_crudeprev",
                "diabetes_crudeprev",
            ):
                item[key] = float(row[key]) if row[key] not in ("", None) else None
            rows.append(item)
    return rows


def load_ces() -> list[dict]:
    rows = []
    offset = 0
    while True:
        query = urllib.parse.urlencode(
            {
                "where": "1=1",
                "outFields": CES_FIELDS,
                "returnGeometry": "false",
                "f": "json",
                "resultOffset": offset,
                "resultRecordCount": 2000,
            }
        )
        payload = json.loads(get(f"{CES_URL}?{query}"))
        features = payload.get("features") or []
        for feature in features:
            attr = feature["attributes"]
            tract = f"{int(attr['tract']):011d}"
            pop = attr.get("ACS2019TotalPop") or 0
            item = {"tract": tract, "county": tract[:5], "pop": float(pop)}
            for key in CES_FIELDS.split(","):
                if key in ("tract", "ACS2019TotalPop"):
                    continue
                value = attr.get(key)
                item[key] = float(value) if value is not None else None
            rows.append(item)
        offset += len(features)
        if not payload.get("exceededTransferLimit") or not features:
            break
    return rows


def weighted(rows: list[dict], key: str) -> dict:
    numerator = 0.0
    denominator = 0.0
    count = 0
    for row in rows:
        value = row.get(key)
        pop = row.get("pop") or 0
        if value is None or pop <= 0:
            continue
        numerator += value * pop
        denominator += pop
        count += 1
    mean = numerator / denominator if denominator else None
    return {"mean": None if mean is None else round(mean, 2), "population": int(denominator), "tracts": count}


def split(rows: list[dict], pred) -> tuple[list[dict], list[dict]]:
    inside = [row for row in rows if pred(row)]
    outside = [row for row in rows if not pred(row)]
    return inside, outside


def compare(rows: list[dict], pred, keys: list[str]) -> dict:
    inside, outside = split(rows, pred)
    result = {}
    for key in keys:
        a = weighted(inside, key)
        b = weighted(outside, key)
        ratio = None
        if a["mean"] is not None and b["mean"] not in (None, 0):
            ratio = round(a["mean"] / b["mean"], 2)
        result[key] = {"area": a, "rest_of_california": b, "ratio": ratio}
    return result


def main() -> None:
    places = load_places()
    ces = load_ces()
    setback = json.loads(SETBACK.read_text(encoding="utf-8"))
    oil_tracts = set(setback["tracts_2020_with_populated_block"])
    refinery = set()
    for name in ("el_segundo", "torrance", "wilmington"):
        refinery.update(setback["facilities"][name]["tracts_2020"])
    aliso = set(setback["facilities"]["aliso_canyon"]["tracts_2020"])
    place_keys = [
        "casthma_crudeprev",
        "copd_crudeprev",
        "chd_crudeprev",
        "cancer_crudeprev",
        "diabetes_crudeprev",
    ]
    ces_keys = [
        "asthma",
        "cvd",
        "lbw",
        "edu",
        "ling",
        "pov",
        "housingB",
        "Hispanic_pct",
        "White_pct",
        "African_American_pct",
        "Asian_American_pct",
        "Children_under10_pct",
        "Elderly_65over_pct",
        "drink",
    ]
    groups = {
        "south_coast_counties": ("PLACES and CES use county FIPS 037, 059, 065, 071. The South Coast air basin is smaller than these four counties.", lambda row: row["county"] in SOUTH_COAST),
        "san_joaquin_counties": ("County FIPS 077, 099, 047, 039, 019, 107, 031, 029. Eastern Kern is outside the valley air basin and outside some groundwater basins.", lambda row: row["county"] in SJV),
        "pesticide_top_counties": ("Fresno, Kern, Tulare, and Monterey, the four counties with the most pesticide pounds in DPR 2022.", lambda row: row["county"] in PESTICIDE),
        "imperial_county": ("Imperial County only. The Salton Sea's northern shore is in Riverside County and is not in this cut.", lambda row: row["county"] in IMPERIAL),
        "oil_gas_3200ft_tracts_2020": ("2020 tracts with at least one populated block whose internal point is within 3,200 feet of an active or idle well. The whole tract is wider than the buffer. CES is not joined, because CES uses 2010 tracts.", lambda row: row["tract"] in oil_tracts),
        "refinery_1_mile_tracts_2020": ("2020 tracts with a populated block within 1 mile of the El Segundo, Torrance, or Wilmington facility point.", lambda row: row["tract"] in refinery),
        "aliso_5_mile_tracts_2020": ("2020 tracts with a populated block within 5 miles of the Aliso Canyon FRS point. The radius is our choice.", lambda row: row["tract"] in aliso),
    }
    output = {
        "retrieved": "2026-10-28",
        "places": {
            "url": "https://data.cdc.gov/resource/yjkw-uj5s",
            "rows": len(places),
            "weight": "totalpopulation",
            "measure": "crude prevalence, percent of adults",
        },
        "ces": {
            "url": CES_URL,
            "rows": len(ces),
            "weight": "ACS2019TotalPop",
            "vintage": "CalEnviroScreen 4.0, 2010 tracts, ACS 2015-2019 population",
        },
        "groups": {},
    }
    for name, (note, pred) in groups.items():
        places_cmp = compare(places, pred, place_keys)
        # 2020 tract groups are not applied to 2010 CES tracts.
        ces_cmp = None if "2020" in name else compare(ces, pred, ces_keys)
        output["groups"][name] = {"note": note, "places": places_cmp, "ces": ces_cmp}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    brief = {}
    for name, group in output["groups"].items():
        brief[name] = {
            key: group["places"][key]
            for key in ("casthma_crudeprev", "copd_crudeprev", "diabetes_crudeprev")
        }
        if group["ces"]:
            brief[name]["ces_asthma"] = group["ces"]["asthma"]
            brief[name]["ces_pov"] = group["ces"]["pov"]
            brief[name]["ces_edu"] = group["ces"]["edu"]
    print(json.dumps(brief, indent=2))


if __name__ == "__main__":
    main()
