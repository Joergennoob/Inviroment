#!/usr/bin/env python3
"""Write map layer files under public/data/layers.

Point files for wells and PFAS sources are compact JSON, not one GeoJSON
property bag per well, so the static map can cluster them without a huge
download. Polygons are simplified GeoJSON. Each feature carries the placement
source fields the map shows as «Kilde for plassering».
"""

from __future__ import annotations

import json
import math
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "data" / "layers"
CACHE = Path("/tmp/ca/src")
UA = "InviromentResearch/1.0 (public-data; educational)"
RETRIEVED = "2026-10-28"
MILES = 69.172
FEET = 5280.0

WELLS = "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/0/query"
EPA_PM = "https://geopub.epa.gov/ArcGIS/rest/services/icr/icrmap/MapServer/21/query"
EPA_OZ = "https://geopub.epa.gov/ArcGIS/rest/services/icr/icrmap/MapServer/16/query"
COD = "https://gis.water.ca.gov/arcgis/rest/services/Geoscientific/i08_CriticallyOverdraftedBasins/MapServer/0/query"
SABL = (
    "https://gispublic.waterboards.ca.gov/portalserver/rest/services/Drinking_Water/"
    "California_Drinking_Water_System_Area_Boundaries/FeatureServer/0/query"
)
TIGER_COUNTY = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query"
TIGER_SLDU_2024 = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Legislative/MapServer/5/query"
TIGER_SLDL_2024 = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Legislative/MapServer/6/query"
TIGER_SLDU_2018 = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Legislative/MapServer/13/query"
TIGER_SLDL_2018 = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Legislative/MapServer/14/query"
SALTON_URL = (
    "https://raw.githubusercontent.com/OpenTopography/Data_Catalog_Spatial_Boundaries/"
    "main/OpenTopography_Raster/Salton_Sea.geojson"
)
SAFER_PACKAGE = "https://data.ca.gov/api/3/action/package_show?id=safer-failing-and-at-risk-drinking-water-systems"
SOURCE_CSV = (
    "https://data.cnra.ca.gov/dataset/57b20340-2b03-4c22-bc52-b59047451496/resource/"
    "9688aeb1-6c77-44aa-9cf7-6b1c1306f399/download/source_name.csv"
)
PFAS_XLSX = (
    "https://www.waterboards.ca.gov/drinking_water/certlic/drinkingwater/"
    "pfas_ddw_general_order/docs/order-dw-2025-0002-ddw-sources-20261012-update.xlsx"
)
DPR_PDF = (
    "https://www.cdpr.ca.gov/wp-content/uploads/2024/12/"
    "2022_county_total_pounds_applied_agricultural_applications_and_acres_treated.pdf"
)
VF_PDF = "https://www.cdph.ca.gov/Programs/CID/DCDC/CDPH%20Document%20Library/CocciEpiSummary2022.pdf"
PUBLIC_SCHOOLS = (
    "https://nces.ed.gov/opengis/rest/services/K12_School_Locations/"
    "EDGE_GEOCODE_PUBLICSCH_2324/MapServer/0/query"
)
PRIVATE_SCHOOLS = (
    "https://nces.ed.gov/opengis/rest/services/K12_School_Locations/"
    "EDGE_GEOCODE_PRIVATESCH_2122/MapServer/0/query"
)

# Pounds of pesticide active ingredient applied, DPR county table 2022.
PESTICIDE_POUNDS = {
    "Alameda": 257269, "Alpine": 305, "Amador": 119239, "Butte": 2892919, "Calaveras": 82487,
    "Colusa": 1344045, "Contra Costa": 472548, "Del Norte": 134850, "El Dorado": 253400,
    "Fresno": 26468541, "Glenn": 1510915, "Humboldt": 36690, "Imperial": 4433052, "Inyo": 15324,
    "Kern": 25835076, "Kings": 6665233, "Lake": 579575, "Lassen": 170231, "Los Angeles": 2362207,
    "Madera": 8313969, "Marin": 86016, "Mariposa": 5278, "Mendocino": 1995053, "Merced": 8005882,
    "Modoc": 136420, "Mono": 3431, "Monterey": 9187117, "Napa": 1144942, "Nevada": 72113,
    "Orange": 800590, "Placer": 478049, "Plumas": 97004, "Riverside": 2818998, "Sacramento": 4499558,
    "San Benito": 775704, "San Bernardino": 433381, "San Diego": 1557503, "San Francisco": 28729,
    "San Joaquin": 11969511, "San Luis Obispo": 2687678, "San Mateo": 193135, "Santa Barbara": 6025426,
    "Santa Clara": 676151, "Santa Cruz": 1342869, "Shasta": 258887, "Sierra": 2965, "Siskiyou": 1475294,
    "Solano": 1192385, "Sonoma": 2313992, "Stanislaus": 6386408, "Sutter": 2460627, "Tehama": 1065913,
    "Trinity": 33053, "Tulare": 17537932, "Tuolumne": 44333, "Ventura": 6238569, "Yolo": 3735238,
    "Yuba": 1079614,
}
# CDPH Table 1, 2022 column. Second value is True when CDPH marked the rate unreliable.
VALLEY_FEVER = {
    "Alameda": (4.8, False), "Alpine": (None, False), "Amador": (12.5, True), "Butte": (1.0, True),
    "Calaveras": (4.5, True), "Colusa": (4.6, True), "Contra Costa": (7.6, False),
    "Del Norte": (None, False), "El Dorado": (3.2, True), "Fresno": (44.3, False),
    "Glenn": (7.0, True), "Humboldt": (2.2, True), "Imperial": (11.2, False), "Inyo": (5.3, True),
    "Kern": (264.9, False), "Kings": (111.0, False), "Lake": (None, False), "Lassen": (3.4, True),
    "Los Angeles": (15.7, False), "Madera": (32.4, False), "Marin": (0.8, True),
    "Mariposa": (5.9, True), "Mendocino": (3.4, True), "Merced": (24.2, False),
    "Modoc": (None, False), "Mono": (None, False), "Monterey": (26.0, False), "Napa": (0.7, True),
    "Nevada": (1.0, True), "Orange": (9.4, False), "Placer": (2.2, True), "Plumas": (None, False),
    "Riverside": (14.3, False), "Sacramento": (3.4, False), "San Benito": (3.0, True),
    "San Bernardino": (10.5, False), "San Diego": (12.7, False), "San Francisco": (2.2, True),
    "San Joaquin": (13.3, False), "San Luis Obispo": (51.5, False), "San Mateo": (3.0, False),
    "Santa Barbara": (9.3, False), "Santa Clara": (4.5, False), "Santa Cruz": (6.0, True),
    "Shasta": (None, False), "Sierra": (None, False), "Siskiyou": (2.3, True), "Solano": (6.1, False),
    "Sonoma": (2.1, True), "Stanislaus": (11.5, False), "Sutter": (None, False),
    "Tehama": (1.5, True), "Trinity": (None, False), "Tulare": (65.7, False),
    "Tuolumne": (3.7, True), "Ventura": (28.3, False), "Yolo": (1.9, True), "Yuba": (3.8, True),
}
DISTRICTS = [
    ("lawmaker-lena-gonzalez", "SD 33", TIGER_SLDU_2024, "033", "2024 SLDU", "Senatdistrikt 33, Census 2024, Citizens Redistricting Commission-kartet som gjelder nå."),
    ("lawmaker-al-muratsuchi", "AD 66", TIGER_SLDL_2024, "066", "2024 SLDL", "Forsamlingsdistrikt 66, Census 2024."),
    ("lawmaker-fran-pavley", "SD 27 (2012-2021)", TIGER_SLDU_2018, "027", "2018 SLDU", "Senatdistrikt 27 i kartet som gjaldt da hun satt, Census 2018."),
    ("lawmaker-bill-monning", "SD 17 (2012-2020)", TIGER_SLDU_2018, "017", "2018 SLDU", "Senatdistrikt 17 i kartet som gjaldt da han satt, Census 2018."),
    ("lawmaker-roger-dickinson", "AD 7 (2012-2016)", TIGER_SLDL_2018, "007", "2018 SLDL", "Forsamlingsdistrikt 7 i 2013-14-kartet, Census 2018-laget."),
    ("lawmaker-cristina-garcia", "AD 58 (2012-2022)", TIGER_SLDL_2018, "058", "2018 SLDL", "Forsamlingsdistrikt 58 i kartet som gjaldt da hun satt, Census 2018."),
    ("lawmaker-shannon-grove", "SD 12", TIGER_SLDU_2024, "012", "2024 SLDU", "Senatdistrikt 12, Census 2024. Valgkrets, ikke forurensningsområde."),
    ("lawmaker-melissa-hurtado", "SD 16", TIGER_SLDU_2024, "016", "2024 SLDU", "Senatdistrikt 16, Census 2024."),
    ("lawmaker-monique-limon", "SD 21", TIGER_SLDU_2024, "021", "2024 SLDU", "Senatdistrikt 21, Census 2024."),
    ("lawmaker-henry-stern", "SD 27", TIGER_SLDU_2024, "027", "2024 SLDU", "Senatdistrikt 27 slik det er nå, Census 2024."),
    ("lawmaker-benjamin-allen", "SD 24", TIGER_SLDU_2024, "024", "2024 SLDU", "Senatdistrikt 24, Census 2024."),
    ("lawmaker-anna-caballero", "SD 14", TIGER_SLDU_2024, "014", "2024 SLDU", "Senatdistrikt 14, Census 2024."),
    ("lawmaker-steve-padilla", "SD 18", TIGER_SLDU_2024, "018", "2024 SLDU", "Senatdistrikt 18, Census 2024."),
    ("lawmaker-john-laird", "SD 17", TIGER_SLDU_2024, "017", "2024 SLDU", "Senatdistrikt 17 slik det er nå, Census 2024."),
    ("lawmaker-suzette-valladares", "SD 23", TIGER_SLDU_2024, "023", "2024 SLDU", "Senatdistrikt 23, Census 2024."),
    ("lawmaker-rosilicie-ochoa-bogh", "SD 19", TIGER_SLDU_2024, "019", "2024 SLDU", "Senatdistrikt 19, Census 2024."),
    ("lawmaker-tim-grayson", "SD 9", TIGER_SLDU_2024, "009", "2024 SLDU", "Senatdistrikt 9, Census 2024. Stemmene i 2022 var fra forsamlingen."),
    ("lawmaker-marie-alvarado-gil", "SD 4", TIGER_SLDU_2024, "004", "2024 SLDU", "Senatdistrikt 4, Census 2024."),
    ("lawmaker-heath-flora", "AD 9", TIGER_SLDL_2024, "009", "2024 SLDL", "Forsamlingsdistrikt 9, Census 2024."),
    ("lawmaker-jasmeet-bains", "AD 35", TIGER_SLDL_2024, "035", "2024 SLDL", "Forsamlingsdistrikt 35, Census 2024."),
    ("lawmaker-jeff-gonzalez", "AD 36", TIGER_SLDL_2024, "036", "2024 SLDL", "Forsamlingsdistrikt 36, Census 2024."),
    ("lawmaker-pilar-schiavo", "AD 40", TIGER_SLDL_2024, "040", "2024 SLDL", "Forsamlingsdistrikt 40, Census 2024."),
    ("lawmaker-lori-wilson", "AD 11", TIGER_SLDL_2024, "011", "2024 SLDL", "Forsamlingsdistrikt 11, Census 2024."),
    ("lawmaker-esmeralda-soria", "AD 27", TIGER_SLDL_2024, "027", "2024 SLDL", "Forsamlingsdistrikt 27, Census 2024."),
    ("lawmaker-damon-connolly", "AD 12", TIGER_SLDL_2024, "012", "2024 SLDL", "Forsamlingsdistrikt 12, Census 2024."),
    ("lawmaker-joaquin-arambula", "AD 31", TIGER_SLDL_2024, "031", "2024 SLDL", "Forsamlingsdistrikt 31, Census 2024."),
]


def get(url: str, timeout: int = 120) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def arcgis(url: str, where: str, fields: str, simplify: float, page: int = 100) -> list[dict]:
    features = []
    offset = 0
    while True:
        query = urllib.parse.urlencode(
            {
                "where": where,
                "outFields": fields,
                "returnGeometry": "true",
                "outSR": "4326",
                "maxAllowableOffset": str(simplify),
                "geometryPrecision": "5",
                "resultOffset": offset,
                "resultRecordCount": page,
                "f": "json",
            }
        )
        payload = json.loads(get(f"{url}?{query}", timeout=180))
        if payload.get("error"):
            raise SystemExit(payload["error"])
        batch = payload.get("features") or []
        features.extend(batch)
        if not batch or len(batch) < page:
            break
        offset += len(batch)
        time.sleep(0.05)
    return features


def props(card_id: str, name: str, layer: str, source_name: str, record_id: str, url: str, note: str, **extra) -> dict:
    item = {
        "card_id": card_id,
        "name": name,
        "layer": layer,
        "source_name": source_name,
        "source_record_id": record_id,
        "source_url": url,
        "source_retrieved": RETRIEVED,
        "source_note": note,
    }
    item.update(extra)
    return item


def feature(geometry: dict, properties: dict) -> dict:
    return {"type": "Feature", "geometry": geometry, "properties": properties}


def write_fc(name: str, features: list[dict]) -> None:
    path = OUT / name
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(name, len(features), path.stat().st_size, flush=True)


def circle(lon: float, lat: float, radius_feet: float, steps: int = 48) -> list:
    ring = []
    for index in range(steps + 1):
        angle = 2 * math.pi * index / steps
        dlat = (radius_feet / (MILES * FEET)) * math.cos(angle)
        dlon = (radius_feet / (MILES * FEET * math.cos(math.radians(lat)))) * math.sin(angle)
        ring.append([round(lon + dlon, 5), round(lat + dlat, 5)])
    return ring


def company_for(operator: str) -> str:
    name = operator.upper()
    if "CHEVRON" in name:
        return "org-chevron"
    if "AERA" in name or "CALIFORNIA RESOURCES" in name:
        return "org-crc"
    if "TORRANCE REFIN" in name or name.startswith("PBF"):
        return "org-pbf"
    if "PHILLIPS" in name:
        return "org-phillips66"
    if "VALERO" in name:
        return "org-valero"
    if "MARATHON" in name:
        return "org-marathon"
    return "ca-problem-oil-gas-proximity"


def download_wells() -> list[dict]:
    points = []
    offset = 0
    while True:
        query = urllib.parse.urlencode(
            {
                "where": "(WellStatus='Active' OR WellStatus='Idle') AND Latitude IS NOT NULL",
                "outFields": "API,Latitude,Longitude,WellStatus,OperatorName",
                "returnGeometry": "false",
                "f": "json",
                "resultOffset": offset,
                "resultRecordCount": 2000,
            }
        )
        payload = json.loads(get(f"{WELLS}?{query}"))
        batch = payload.get("features") or []
        for feature_row in batch:
            attr = feature_row["attributes"]
            lat = attr.get("Latitude")
            lon = attr.get("Longitude")
            if lat is None or lon is None:
                continue
            lat_f = float(lat)
            lon_f = float(lon)
            if not (32 <= lat_f <= 42.5 and -125 <= lon_f <= -114):
                continue
            operator = str(attr.get("OperatorName") or "")
            points.append(
                {
                    "lon": round(lon_f, 5),
                    "lat": round(lat_f, 5),
                    "id": str(attr.get("API") or ""),
                    "status": attr.get("WellStatus") or "",
                    "card_id": company_for(operator),
                    "operator": operator[:80],
                }
            )
        offset += len(batch)
        print("wells", offset, flush=True)
        if not batch or not payload.get("exceededTransferLimit"):
            break
    # Dedupe API
    seen = set()
    unique = []
    for point in points:
        if point["id"] in seen:
            continue
        seen.add(point["id"])
        unique.append(point)
    return unique


def zone_rectangles(wells: list[dict]) -> list[dict]:
    cell = 0.012
    marked = set()
    span = 1
    for well in wells:
        ix = math.floor(well["lon"] / cell)
        iy = math.floor(well["lat"] / cell)
        for dx in range(-span, span + 1):
            for dy in range(-span, span + 1):
                marked.add((ix + dx, iy + dy))
    by_row: dict[int, list[int]] = {}
    for ix, iy in marked:
        by_row.setdefault(iy, []).append(ix)
    features = []
    for iy, columns in by_row.items():
        columns = sorted(set(columns))
        start = previous = columns[0]
        def emit(x0: int, x1: int) -> None:
            lon0 = round(x0 * cell, 5)
            lon1 = round((x1 + 1) * cell, 5)
            lat0 = round(iy * cell, 5)
            lat1 = round((iy + 1) * cell, 5)
            features.append(
                feature(
                    {"type": "Polygon", "coordinates": [[[lon0, lat0], [lon1, lat0], [lon1, lat1], [lon0, lat1], [lon0, lat0]]]},
                    props(
                        "ca-problem-oil-gas-proximity",
                        "Område innenfor om lag 3 200 fot fra en aktiv eller idle brønn",
                        "oil-zone",
                        "CalGEM WellSTAR og egen rutenettberegning",
                        f"cell-{x0}-{iy}",
                        WELLS,
                        "Ruter på 0,012 grader rundt brønnpunkt. Det er en forenkling av 3 200 fot, ikke et bufferpolygon per brønn.",
                    ),
                )
            )
        for column in columns[1:]:
            if column == previous + 1:
                previous = column
                continue
            emit(start, previous)
            start = previous = column
        emit(start, previous)
    return features


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("air", flush=True)
    air_specs = [
        (EPA_PM, "PM-2.5.2012.LA-South_Coast", "ca-problem-south-coast-air", "South Coast PM2.5 2012"),
        (EPA_PM, "PM-2.5.2012.San_Joaquin_Valley", "ca-problem-san-joaquin-air", "San Joaquin Valley PM2.5 2012"),
        (EPA_PM, "PM-2.5.2012.Imperial_Co", "ca-problem-salton-sea", "Imperial County PM2.5 2012"),
        (EPA_OZ, "Ozone_8-hr.2015.LA-South_Coast", "ca-problem-south-coast-air", "South Coast ozon 2015"),
        (EPA_OZ, "Ozone_8-hr.2015.San_Joaquin_Valley", "ca-problem-san-joaquin-air", "San Joaquin Valley ozon 2015"),
        (EPA_OZ, "Ozone_8-hr.2015.Imperial_Co", "ca-problem-salton-sea", "Imperial County ozon 2015"),
    ]
    air = []
    for url, composite, card_id, title in air_specs:
        rows = arcgis(url, f"composite_id='{composite}'", "area_name,composite_id", 0.002, 10)
        for row in rows:
            air.append(
                feature(
                    {"type": "Polygon", "coordinates": row["geometry"]["rings"]},
                    props(
                        card_id,
                        title,
                        "pm25" if "PM-2.5" in composite else "ozone",
                        "US EPA Green Book",
                        composite,
                        url.split("?")[0],
                        "Nonattainment-polygon. EPA: kartfilen er til kartbruk. Den juridiske grensen står i 40 CFR part 81. Generalisert med om lag 0,002 grader.",
                    ),
                )
            )
    write_fc("air.geojson", air)

    print("basins", flush=True)
    basins = []
    for row in arcgis(COD, "1=1", "Basin_Subbasin_Number,Basin_Subbasin_Name", 0.001, 30):
        attr = row["attributes"]
        basins.append(
            feature(
                {"type": "Polygon", "coordinates": row["geometry"]["rings"]},
                props(
                    "ca-problem-groundwater-overdraft",
                    attr.get("Basin_Subbasin_Name") or "Basseng",
                    "basins",
                    "DWR Bulletin 118",
                    str(attr.get("Basin_Subbasin_Number") or ""),
                    COD.split("?")[0],
                    "Kritisk overtrukket grunnvannsbasseng. Polygonet er generalisert med om lag 0,001 grader.",
                ),
            )
        )
    write_fc("basins.geojson", basins)

    print("failing water", flush=True)
    import csv
    safer_path = CACHE / "SAFER_RA.csv"
    if not safer_path.exists():
        package = json.loads(get(SAFER_PACKAGE))
        csv_url = next(item["url"] for item in package["result"]["resources"] if "flat file" in item["name"].lower())
        safer_path.write_bytes(get(csv_url, timeout=180))
    failing_ids = []
    with safer_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["CURRENT_FAILING"] == "Failing":
                failing_ids.append(row["WATER_SYSTEM_NUMBER"].strip().upper())
    water = []
    for start in range(0, len(failing_ids), 40):
        chunk = failing_ids[start : start + 40]
        quoted = ",".join(f"'{item}'" for item in chunk)
        rows = arcgis(SABL, f"BOUNDARY_TYPE='Water Service Area' AND SABL_PWSID IN ({quoted})", "SABL_PWSID,WATER_SYSTEM_NAME", 0.0005, 50)
        for row in rows:
            attr = row["attributes"]
            water.append(
                feature(
                    {"type": "Polygon", "coordinates": row["geometry"]["rings"]},
                    props(
                        "ca-problem-drinking-water",
                        attr.get("WATER_SYSTEM_NAME") or attr.get("SABL_PWSID"),
                        "failing-water",
                        "State Water Board SABL",
                        str(attr.get("SABL_PWSID") or ""),
                        SABL.split("?")[0],
                        "Vannserviceområde for et system merket Failing i SAFER-filen 2026-10-28. Generalisert med om lag 0,0005 grader.",
                    ),
                )
            )
        print("water", len(water), flush=True)
    write_fc("failing-water.geojson", water)

    print("counties", flush=True)
    counties = arcgis(TIGER_COUNTY, "STATE='06'", "NAME,GEOID", 0.02, 80)
    pest_features = []
    fever_features = []
    for row in counties:
        name = row["attributes"]["NAME"]
        geoid = str(row["attributes"]["GEOID"])
        pounds = PESTICIDE_POUNDS.get(name)
        pest_features.append(
            feature(
                {"type": "Polygon", "coordinates": row["geometry"]["rings"]},
                props(
                    "ca-problem-pesticides",
                    name,
                    "pesticide",
                    "US Census Bureau TIGERweb county og DPR",
                    geoid,
                    TIGER_COUNTY.split("?")[0],
                    "Fylkespolygon fra Census. Pund er DPR sin tabell for 2022, avrundet i kilden.",
                    value=pounds if pounds is not None else "",
                    value_label="pund virksomt stoff 2022" if pounds is not None else "mangler",
                ),
            )
        )
        rate = VALLEY_FEVER.get(name)
        fever_features.append(
            feature(
                {"type": "Polygon", "coordinates": row["geometry"]["rings"]},
                props(
                    "ca-problem-san-joaquin-air",
                    name,
                    "valley-fever",
                    "US Census Bureau TIGERweb county og CDPH",
                    geoid,
                    TIGER_COUNTY.split("?")[0],
                    "Fylkespolygon fra Census. Raten er CDPH Table 1 for 2022, tilfeller per 100 000. Stjerne i kilden er merket upålitelig.",
                    value="" if rate is None or rate[0] is None else rate[0],
                    unreliable=bool(rate[1]) if rate else False,
                    value_label="per 100 000 i 2022" if rate and rate[0] is not None else "ikke oppgitt",
                ),
            )
        )
    write_fc("pesticide-counties.geojson", pest_features)
    write_fc("valley-fever-counties.geojson", fever_features)

    print("salton and circles", flush=True)
    salton = json.loads(get(SALTON_URL))
    ring = salton["geometry"]["coordinates"][0]
    places = [
        ("ca-problem-refineries", "Chevron El Segundo, 1 engelsk mil", -118.41873, 33.916216, 5280, "110002899908"),
        ("ca-problem-refineries", "Torrance Refining, 1 engelsk mil", -118.336907, 33.854967, 5280, "110070241046"),
        ("ca-problem-refineries", "Phillips 66 Wilmington, 1 engelsk mil", -118.27645, 33.76336, 5280, "110000476235"),
        ("ca-problem-aliso-canyon", "Aliso Canyon, 5 engelske mil", -118.551235, 34.307569, 26400, "110001158238"),
    ]
    circles = []
    for card_id, title, lon, lat, radius, record in places:
        circles.append(
            feature(
                {"type": "Polygon", "coordinates": [circle(lon, lat, radius)]},
                props(card_id, title, "circles", "Egen sirkel rundt FRS-punkt", record, "https://frs-public.epa.gov/", "Radiusen er valgt i dette prosjektet rundt et FRS-koordinat som står på kortet. Det er ikke et etatspolygon."),
            )
        )
    circles.append(
        feature(
            {"type": "LineString", "coordinates": ring},
            props(
                "ca-problem-salton-sea",
                "Salton Sea, strandlinje",
                "salton-line",
                "OpenTopography Salton Sea outline",
                "Salton_Sea.geojson",
                SALTON_URL,
                "Publisert omriss av sjøen. Ikke IID sitt blotlagte playa-polygon. NHD-geometrien tidsavbrøt.",
            ),
        )
    )
    # 1-mile cells around the shoreline
    cell = 0.01
    marked = set()
    for lon, lat in ring:
        ix = math.floor(lon / cell)
        iy = math.floor(lat / cell)
        marked.add((ix, iy))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                marked.add((ix + dx, iy + dy))
    for ix, iy in marked:
        lon0, lon1 = round(ix * cell, 5), round((ix + 1) * cell, 5)
        lat0, lat1 = round(iy * cell, 5), round((iy + 1) * cell, 5)
        circles.append(
            feature(
                {"type": "Polygon", "coordinates": [[[lon0, lat0], [lon1, lat0], [lon1, lat1], [lon0, lat1], [lon0, lat0]]]},
                props("ca-problem-salton-sea", "Om lag 1 engelsk mil fra strandlinjen", "salton-ring", "OpenTopography og egen rutenettberegning", f"{ix}:{iy}", SALTON_URL, "Ruter på 0,01 grader som treffer strandlinjen eller naboruten. Det tilsvarer om lag 1 engelsk mil, ikke et eksakt buffer."),
            )
        )
    write_fc("circles.geojson", circles)

    print("districts", flush=True)
    districts = []
    for card_id, title, url, code, vintage, note in DISTRICTS:
        field = "SLDU" if "SLDU" in vintage else "SLDL"
        where = f"STATE='06' AND {field}='{code}'"
        rows = arcgis(url, where, f"NAME,{field},GEOID", 0.01, 5)
        if not rows:
            where = f"GEOID LIKE '06{code}'"
            rows = arcgis(url, where, "*", 0.01, 5)
        for row in rows:
            districts.append(
                feature(
                    {"type": "Polygon", "coordinates": row["geometry"]["rings"]},
                    props(card_id, title, "districts", f"US Census TIGERweb {vintage}", str(row["attributes"].get("GEOID") or code), url.split("?")[0], note),
                )
            )
    write_fc("districts.geojson", districts)

    print("facilities from cards", flush=True)
    facilities = []
    for path in (ROOT / "data" / "cards").glob("*.json"):
        card = json.loads(path.read_text(encoding="utf-8"))
        if card.get("geometry") and card["geometry"]["type"] == "Point":
            geo = card["geometry"]
            facilities.append(
                feature(
                    {"type": "Point", "coordinates": geo["coordinates"]},
                    props(card["id"], card["name"], "facilities", geo["source_name"], geo["source_record_id"], geo["source_url"], geo["note"]),
                )
            )
    write_fc("facilities.geojson", facilities)

    wells = download_wells()
    (OUT / "wells.json").write_text(
        json.dumps(
            {
                "source_name": "CalGEM WellSTAR",
                "source_url": WELLS,
                "source_retrieved": RETRIEVED,
                "source_note": "Brønn med status Active eller Idle, ett punkt per API-nummer. Koordinat fra WellSTAR lag 0.",
                "points": [[item["lon"], item["lat"], item["id"], item["card_id"], item["status"]] for item in wells],
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    print("wells.json", len(wells), (OUT / "wells.json").stat().st_size, flush=True)
    write_fc("oil-zone.geojson", zone_rectangles(wells))

    print("schools", flush=True)
    well_grid: dict[tuple[int, int], list[tuple[float, float]]] = {}
    for well in wells:
        key = (math.floor(well["lat"] / 0.01), math.floor(well["lon"] / 0.01))
        well_grid.setdefault(key, []).append((well["lat"], well["lon"]))

    def near_well(lat: float, lon: float) -> bool:
        ix, iy = math.floor(lat / 0.01), math.floor(lon / 0.01)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                for wlat, wlon in well_grid.get((ix + dx, iy + dy), ()):
                    mid = math.radians((lat + wlat) / 2)
                    dy_ft = (lat - wlat) * MILES * FEET
                    dx_ft = (lon - wlon) * MILES * math.cos(mid) * FEET
                    if dx_ft * dx_ft + dy_ft * dy_ft <= 3200 * 3200:
                        return True
        return False

    schools = []
    for url, id_field, vintage, layer in (
        (PUBLIC_SCHOOLS, "NCESSCH", "NCES offentlige skoler 2023-24", "schools-public"),
        (PRIVATE_SCHOOLS, "PPIN", "NCES private skoler, PSS 2021-22", "schools-private"),
    ):
        offset = 0
        while True:
            query = urllib.parse.urlencode(
                {"where": "STATE='CA'", "outFields": f"{id_field},NAME,LAT,LON", "returnGeometry": "false", "f": "json", "resultOffset": offset, "resultRecordCount": 2000}
            )
            payload = json.loads(get(f"{url}?{query}"))
            batch = payload.get("features") or []
            for row in batch:
                attr = row["attributes"]
                lat, lon = attr.get("LAT"), attr.get("LON")
                if lat is None or lon is None or not near_well(float(lat), float(lon)):
                    continue
                schools.append(
                    feature(
                        {"type": "Point", "coordinates": [round(float(lon), 5), round(float(lat), 5)]},
                        props("ca-problem-oil-gas-proximity", str(attr.get("NAME") or ""), layer, vintage, str(attr.get(id_field) or ""), url.split("?")[0], "Skolepunkt innenfor 3 200 fot fra en aktiv eller idle brønn, egen avstandsberegning."),
                    )
                )
            offset += len(batch)
            if not batch or not payload.get("exceededTransferLimit"):
                break
    write_fc("schools.geojson", schools)

    print("pfas", flush=True)
    # Reuse cached workbook and source csv when present.
    import csv as csvmod
    import zipfile
    from xml.etree import ElementTree as ET
    xlsx = CACHE / "pfas_sources_20261012.xlsx"
    if not xlsx.exists():
        xlsx.write_bytes(get(PFAS_XLSX, timeout=180))
    source_path = CACHE / "source_name.csv"
    if not source_path.exists():
        source_path.write_bytes(get(SOURCE_CSV, timeout=120))
    by_facility = {}
    with source_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csvmod.DictReader(handle):
            key = f"{row['pwsid'].strip().upper()}_{row['source_facility_id'].strip().zfill(3)}"
            try:
                by_facility[key] = (float(row["latitude"]), float(row["longitude"]), row["source_facility_name"])
            except ValueError:
                continue
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    book = zipfile.ZipFile(xlsx)
    shared = []
    root = ET.fromstring(book.read("xl/sharedStrings.xml"))
    for item in root.findall("m:si", ns):
        shared.append("".join(node.text or "" for node in item.findall(".//m:t", ns)))
    sheet = ET.fromstring(book.read("xl/worksheets/sheet1.xml"))
    pfas = []
    seen_codes = set()
    for index, row in enumerate(sheet.findall("m:sheetData/m:row", ns)):
        values = []
        for cell in row.findall("m:c", ns):
            kind = cell.get("t")
            node = cell.find("m:v", ns)
            if node is None or node.text is None:
                values.append("")
            else:
                values.append(shared[int(node.text)] if kind == "s" else node.text)
        if index == 0 or len(values) < 5 or not values[4]:
            continue
        code = values[4].strip().upper()
        if code in seen_codes:
            continue
        parts = code.split("_")
        if len(parts) < 2:
            continue
        hit = by_facility.get(f"{parts[0]}_{parts[1]}")
        if not hit:
            continue
        seen_codes.add(code)
        lat, lon, facility_name = hit
        if not (32 <= lat <= 42.5 and -125 <= lon <= -114):
            continue
        pfas.append(
            feature(
                {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]},
                props(
                    "ca-problem-pfas",
                    f"{values[2]} · {values[3]}",
                    "pfas",
                    "SDWIS-anlegg i DWR/CNRA source_name.csv, koblet til PFAS-kildelisten",
                    code,
                    SOURCE_CSV,
                    "Koordinatet er anleggets punkt, ikke en prøveverdi. Arbeidsboken har ikke selv koordinater. Et PFAS-måleresultat for dette punktet er ikke koblet på.",
                ),
            )
        )
    write_fc("pfas.geojson", pfas)

    index = {
        "retrieved": RETRIEVED,
        "layers": [
            {"id": "pm25", "file": "air.geojson", "filter": "pm25", "title": "PM2.5 2012", "problem": "luft", "kind": "fill", "color": "#c45c26", "default": True},
            {"id": "ozone", "file": "air.geojson", "filter": "ozone", "title": "Ozon 2015", "problem": "luft", "kind": "fill", "color": "#d4a017", "default": False},
            {"id": "basins", "file": "basins.geojson", "filter": "basins", "title": "Kritisk overtrekk", "problem": "grunnvann", "kind": "fill", "color": "#3d6b8a", "default": True},
            {"id": "failing-water", "file": "failing-water.geojson", "filter": "failing-water", "title": "Failing-vannområder", "problem": "drikkevann", "kind": "fill", "color": "#1d4e89", "default": True},
            {"id": "pesticide", "file": "pesticide-counties.geojson", "filter": "pesticide", "title": "Sprøytemiddel, pund 2022", "problem": "sprøytemiddel", "kind": "choropleth", "color": "#6b3f69", "default": False},
            {"id": "valley-fever", "file": "valley-fever-counties.geojson", "filter": "valley-fever", "title": "Valley fever 2022", "problem": "dal-luft", "kind": "choropleth", "color": "#8a5a00", "default": False},
            {"id": "salton-line", "file": "circles.geojson", "filter": "salton-line", "title": "Salton Sea", "problem": "salton", "kind": "line", "color": "#1a6b7a", "default": True},
            {"id": "salton-ring", "file": "circles.geojson", "filter": "salton-ring", "title": "Salton, 1 mil", "problem": "salton", "kind": "fill", "color": "#7eb8c4", "default": True},
            {"id": "circles", "file": "circles.geojson", "filter": "circles", "title": "Raffineri 1 mil og Aliso 5 mil", "problem": "raffineri", "kind": "fill", "color": "#9a4318", "default": True},
            {"id": "oil-zone", "file": "oil-zone.geojson", "filter": "oil-zone", "title": "Om lag 3 200 fot", "problem": "olje", "kind": "fill", "color": "#1f4d3a", "default": False},
            {"id": "wells", "file": "wells.json", "filter": "wells", "title": "Aktive og idle brønner", "problem": "olje", "kind": "cluster", "color": "#1f4d3a", "default": False},
            {"id": "schools", "file": "schools.geojson", "filter": "schools", "title": "Skoler innenfor 3 200 fot", "problem": "olje", "kind": "circle", "color": "#7a1f4d", "default": False},
            {"id": "pfas", "file": "pfas.geojson", "filter": "pfas", "title": "PFAS-kilder med koordinat", "problem": "pfas", "kind": "circle", "color": "#5c3d8a", "default": False},
            {"id": "facilities", "file": "facilities.geojson", "filter": "facilities", "title": "Anlegg fra kortene", "problem": "anlegg", "kind": "circle", "color": "#111111", "default": True},
            {"id": "districts", "file": "districts.geojson", "filter": "districts", "title": "Distrikter for folkevalgte", "problem": "lov", "kind": "fill", "color": "#4d5a4e", "default": False},
        ],
    }
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("done", flush=True)


if __name__ == "__main__":
    main()
