#!/usr/bin/env python3
"""Replace county stand-ins with published boundaries and record the new filings."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "data" / "cards"
NOTE = "Wayback-feltet fylles av scripts/archive_sources.py."
CAUS = (
    "Sammenligningen er korrelasjon. Den justerer ikke for inntekt, røyking eller alder. "
    "Terskelen for merkbart er 1,5 ganger sammenligningsgruppen."
)


def src(url: str, title: str, publisher: str) -> dict:
    return {
        "url": url,
        "title": title,
        "publisher": publisher,
        "retrieved": "2026-10-28",
        "archive_url": "",
        "archive_note": NOTE,
    }


def cl(cid: str, text: str, status: str, sources: list, note: str = "") -> dict:
    return {"id": cid, "text": text, "status": status, "note": note, "sources": sources}


def load(cid: str) -> dict:
    return json.loads((CARDS / f"{cid}.json").read_text(encoding="utf-8"))


def save(card: dict) -> None:
    (CARDS / f"{card['id']}.json").write_text(
        json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def walk(card: dict):
    for claim in card["summary"] + card["claims"]:
        yield claim
    for name in ("population", "demographics", "health_outcomes"):
        block = card.get(name)
        if block:
            yield from block["claims"]


def add_claim(card: dict, claim: dict, block: str | None = None) -> None:
    if any(item["id"] == claim["id"] for item in walk(card)):
        return
    if block:
        card[block]["claims"].append(claim)
    else:
        card["claims"].append(claim)


def replace_claim(card: dict, cid: str, text: str, status: str, note: str, sources: list) -> None:
    for claim in walk(card):
        if claim["id"] == cid:
            claim["text"] = text
            claim["status"] = status
            claim["note"] = note
            claim["sources"] = sources
            return
    raise SystemExit(f"missing {cid} on {card['id']}")


EPA_PM = src(
    "https://geopub.epa.gov/ArcGIS/rest/services/icr/icrmap/MapServer/21",
    "Green Book PM2.5 annual 2012 nonattainment polygons",
    "US EPA",
)
EPA_OZ = src(
    "https://geopub.epa.gov/ArcGIS/rest/services/icr/icrmap/MapServer/16",
    "Green Book 2015 8-hour ozone nonattainment polygons",
    "US EPA",
)
CENSUS = src(
    "https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/California/ca2020.pl.zip",
    "2020 Census PL 94-171 California geographic header",
    "US Census Bureau",
)
PLACES = src(
    "https://data.cdc.gov/resource/yjkw-uj5s.json?stateabbr=CA&$limit=1",
    "PLACES census tract estimates, 2025 release, California",
    "CDC",
)
CES = src(
    "https://services1.arcgis.com/PCHfdHz4GlDNAhBb/arcgis/rest/services/CalEnviroScreen_4_0_Results_/FeatureServer/0",
    "CalEnviroScreen 4.0 tract centroids",
    "OEHHA",
)
DWR = src(
    "https://gis.water.ca.gov/arcgis/rest/services/Geoscientific/i08_CriticallyOverdraftedBasins/MapServer/0",
    "Bulletin 118 critically overdrafted groundwater basins",
    "California Department of Water Resources",
)
SABL = src(
    "https://gispublic.waterboards.ca.gov/portalserver/rest/services/Drinking_Water/California_Drinking_Water_System_Area_Boundaries/FeatureServer/0",
    "California Drinking Water System Area Boundaries, water service areas",
    "State Water Resources Control Board",
)
SAFER = src(
    "https://data.ca.gov/dataset/safer-failing-and-at-risk-drinking-water-systems",
    "SAFER drinking water risk assessment public flat file",
    "State Water Resources Control Board",
)
BOUNDARY_NOTE = (
    "Folketallet er summen av Census 2020-blokker der det indre punktet ligger i polygonet. "
    "EPA sier at kartfilen er til kartbruk, og at den juridiske grensen står i 40 CFR part 81. "
    "Polygonet er generalisert med om lag 0,002 grader. "
    + CAUS
)


def main() -> None:
    south = load("ca-problem-south-coast-air")
    add_claim(
        south,
        cl(
            "r4-sc-boundary",
            "Innenfor EPA sitt PM2.5-polygon for 2012-standarden, Los Angeles-South Coast Air Basin, bor 16 361 181 personer i 2020. Ozonpolygonet for 2015-standarden gir 16 352 598. PLACES, vektet med blokkfolketallet inne i PM2.5-polygonet, mot resten av California: astma 9,30 mot 9,62 prosent, KOLS 4,75 mot 5,29, koronar hjertesykdom 5,19 mot 5,59, kreft 5,77 mot 6,68, diabetes 11,92 mot 11,23. Ingen forhold når 1,5.",
            "confirmed",
            [EPA_PM, EPA_OZ, CENSUS, PLACES],
            BOUNDARY_NOTE + " Fylkestallene på kortet er et videre omriss og er ikke denne grensen.",
        ),
        "health_outcomes",
    )
    add_claim(
        south,
        cl(
            "r4-sc-ces",
            "CalEnviroScreen 4.0, der 2010-tractets senterpunkt ligger i PM2.5-polygonet: uten videregående 20,3 mot 15,7 prosent, språklig isolasjon 11,5 mot 8,4, hispanic 46,5 mot 33,7, drikkevannsindikator 572 mot 411. Forholdene er 1,29 til 1,39. Astmabesøk er 48,4 mot 54,1 per 10 000.",
            "confirmed",
            [EPA_PM, CES],
            "Senterpunkt i polygonet er ikke det samme som at hele tractet ligger innenfor. " + CAUS,
        ),
        "demographics",
    )
    save(south)

    sjv = load("ca-problem-san-joaquin-air")
    add_claim(
        sjv,
        cl(
            "r4-sjv-boundary",
            "Innenfor EPA sitt PM2.5-polygon for San Joaquin Valley, 2012-standarden, bor 4 178 077 personer i 2020. Ozonpolygonet for 2015 gir 4 179 920. Andel uten videregående i CalEnviroScreen, senterpunkt i polygonet, er 26,0 mot 16,7 prosent, forhold 1,56. Drikkevannsindikatoren er 709 mot 451, forhold 1,57. Astmabesøk er 70,8 mot 49,5 per 10 000, forhold 1,43.",
            "confirmed",
            [EPA_PM, EPA_OZ, CENSUS, CES],
            BOUNDARY_NOTE + " Hele Kern fylke er ikke lenger med. Øst for dalen faller utenfor polygonet.",
        ),
        "demographics",
    )
    add_claim(
        sjv,
        cl(
            "r4-sjv-places",
            "PLACES for de samme blokkene, mot resten av California: astma 10,10 mot 9,42 prosent, KOLS 6,21 mot 4,93, koronar hjertesykdom 6,14 mot 5,34, kreft 5,73 mot 6,37, diabetes 12,88 mot 11,35. Høyeste forhold er KOLS, 1,26.",
            "confirmed",
            [EPA_PM, PLACES, CENSUS],
            CAUS,
        ),
        "health_outcomes",
    )
    save(sjv)

    gw = load("ca-problem-groundwater-overdraft")
    add_claim(
        gw,
        cl(
            "r4-gw-basins",
            "DWR sitt lag med 21 kritisk overtrukne Bulletin 118-basseng har 4 053 539 personer i blokker fra 2020 der punktet ligger i et basseng. CalEnviroScreen, senterpunkt i bassenget: uten videregående 26,4 mot 16,7 prosent, forhold 1,58. Drikkevannsindikatoren er 663 mot 458, forhold 1,45. PLACES-astma er 10,05 mot 9,43 prosent.",
            "confirmed",
            [DWR, CENSUS, CES, PLACES],
            "Navnene som tjenesten returnerer, gjentas for delbasseng: San Joaquin Valley, Salinas Valley, Cuyama Valley, Borrego Valley, Indian Wells Valley, Los Osos Valley, Santa Cruz Mid-County, Pleasant Valley, Corralitos og Santa Clara River Valley. Fylkesomrisset på kortet er et videre anslag.",
        ),
        "demographics",
    )
    save(gw)

    salt = load("ca-problem-salton-sea")
    add_claim(
        salt,
        cl(
            "r4-salt-mile",
            "Innenfor 1 engelsk mil fra strandlinjen i OpenTopography sitt Salton Sea-polygon bor 12 034 personer i 2020, i 12 tract. PLACES mot resten av California: diabetes 16,35 mot 11,51 prosent, forhold 1,42, KOLS 6,79 mot 5,06, forhold 1,34, koronar hjertesykdom 6,73 mot 5,43, astma 10,02 mot 9,49, kreft 3,49 mot 6,30. Ingen forhold når 1,5.",
            "confirmed",
            [
                src(
                    "https://raw.githubusercontent.com/OpenTopography/Data_Catalog_Spatial_Boundaries/main/OpenTopography_Raster/Salton_Sea.geojson",
                    "Salton Sea outline published with an OpenTopography raster boundary",
                    "OpenTopography",
                ),
                CENSUS,
                PLACES,
            ],
            "Dette er ikke IID sitt blotlagte playa-polygon. Et NHD-geometriuttak for Salton Sea tidsavbrøt. Imperial fylke på kortet er et videre område. Ett CalEnviroScreen-senterpunkt treffer ringen, så den indikatoren er ikke brukt som snitt for ringen.",
        ),
        "health_outcomes",
    )
    save(salt)

    drink = load("ca-problem-drinking-water")
    replace_claim(
        drink,
        "r3-dw-tracts",
        "SAFER-filen med opprettelsesdato 28. oktober 2026 har 416 systemer merket Failing. Summen av filens eget befolkningsfelt er 426 484. 415 av systemene har et vannservicepolygon i SABL. Ett system med 80 personer i filen har ikke polygon. I 2020-blokker som faller i et failing-polygon, bor 357 102 personer. I blokker som bare faller i et system merket Not Failing, bor 37 215 322. 23 628 personer ligger i begge og er telt med failing.",
        "confirmed",
        "Behovsvurderingens 811 964 personer er tallet per 31. desember 2024. Filen her er den daglige listen 28. oktober 2026. Systemets eget folketall og blokkfolketallet er to ulike mål. Skriptet er scripts/area_boundaries.py.",
        [SAFER, SABL, CENSUS],
    )
    add_claim(
        drink,
        cl(
            "r4-dw-health",
            "PLACES, vektet med blokkfolketallet i failing-polygon mot Not Failing-polygon: astma 9,94 mot 9,45 prosent, KOLS 6,47 mot 4,97, koronar hjertesykdom 6,52 mot 5,34, kreft 5,43 mot 6,21, diabetes 13,99 mot 11,45. Høyeste forhold er KOLS, 1,30. CalEnviroScreen der senterpunktet ligger i polygonet: uten videregående 29,4 mot 17,7 prosent, forhold 1,66, og språklig isolasjon 17,1 mot 10,0, forhold 1,71.",
            "confirmed",
            [SAFER, SABL, PLACES, CES],
            CAUS
            + " Senterpunktmetoden veier 192 693 personer, mindre enn blokktellingen, fordi store tract kan ha senter utenfor polygonet.",
        ),
        "health_outcomes",
    )
    for item in drink["checked_empty"]:
        if item["field"] == "named_failing_system_geometry":
            item["searched"] = "SABL-polygoner er koblet til SAFER-listen. Et punkt for hvert navngitte eksempelverk, som Halcyon, er fortsatt ikke lagt på kartet."
    drink["open_questions"] = [
        item
        for item in drink["open_questions"]
        if "Failing-liste" not in item
    ]
    save(drink)

    oil = load("ca-problem-oil-gas-proximity")
    replace_claim(
        oil,
        "r3-oil-buffer",
        "Egen beregning: 2 977 829 personer og 1 104 614 boligenheter i Census 2020 ligger i blokker der blokkens indre punkt er innenfor 3 200 fot fra minst én brønn med status Active eller Idle. 694 av 10 400 offentlige skoler i NCES 2023–24 og 193 av 2 452 private skoler i NCES Private School Survey 2021–22 ligger innenfor samme avstand. CalGEM har ikke publisert et slikt tall.",
        "confirmed",
        "83 695 brønner og 31 479 blokker inngår. Avstanden er ekvirektangulær. Internt punkt er ikke polygonkryss. Pluggede brønner er utelatt. De to skolefilene er ikke samme årgang. Skriptet er scripts/setback_3200.py.",
        [
            src(
                "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/0/query?where=WellStatus%3D%27Active%27+OR+WellStatus%3D%27Idle%27&returnCountOnly=true&f=json",
                "WellSTAR active or idle wells",
                "CalGEM",
            ),
            CENSUS,
            src(
                "https://nces.ed.gov/opengis/rest/services/K12_School_Locations/EDGE_GEOCODE_PUBLICSCH_2324/MapServer/0/query?where=STATE%3D%27CA%27&returnCountOnly=true&f=json",
                "NCES EDGE public schools 2023-24, California",
                "National Center for Education Statistics",
            ),
            src(
                "https://nces.ed.gov/opengis/rest/services/K12_School_Locations/EDGE_GEOCODE_PRIVATESCH_2122/MapServer/0/query?where=STATE%3D%27CA%27&returnCountOnly=true&f=json",
                "NCES EDGE private schools, PSS 2021-22, California",
                "National Center for Education Statistics",
            ),
        ],
    )
    oil["open_questions"] = [
        "CalGEMs egen metode for folk, boliger og skoler i health protection zone, hvis etaten senere publiserer den."
    ]
    save(oil)

    pfas = load("ca-problem-pfas")
    add_claim(
        pfas,
        cl(
            "r4-pfas-geo",
            "Arbeidsboken fra 12. oktober 2026 har ikke koordinater eller gateadresse. 5 547 av 10 701 PS-koder treffer en rad i DWR/CNRA-filen source_name.csv, som er SDWIS-anlegg med breddegrad og lengdegrad, når systemnummer og anleggsnummer kobles. 5 154 koder er ikke i den filen. Koblingen er anleggets punkt, ikke en ny adressematching.",
            "confirmed",
            [
                src(
                    "https://www.waterboards.ca.gov/drinking_water/certlic/drinkingwater/pfas_ddw_general_order/docs/order-dw-2025-0002-ddw-sources-20261012-update.xlsx",
                    "PFAS source list updated October 12, 2026",
                    "State Water Resources Control Board",
                ),
                src(
                    "https://data.cnra.ca.gov/dataset/57b20340-2b03-4c22-bc52-b59047451496/resource/9688aeb1-6c77-44aa-9cf7-6b1c1306f399/download/source_name.csv",
                    "Urban water source facilities with latitude and longitude",
                    "California Natural Resources Agency / Department of Water Resources",
                ),
            ],
            "Treffregelen er at PS-koden er systemnummer, anleggsnummer og samme anleggsnummer om igjen. Et helseutfall for naboene til disse punktene er ikke regnet, fordi under halvparten av kildene mangler punkt.",
        ),
    )
    save(pfas)

    psx = load("org-phillips66")
    add_claim(
        psx,
        cl(
            "r4-psx-idle",
            "Form 10-Q for kvartalet som sluttet 31. mars 2026 kaller Los Angeles-raffineriet idled, sier at drivstoffproduksjonen stanset da idlingen begynte i fjerde kvartal 2025, og flytter anleggets anleggsmidler fra raffineringssegmentet til Corporate and Other i første kvartal 2026. SCAQMD sitt styrenotat 7. august 2026 sier at driften har vært lagt i ro siden slutten av 2025, og at lagertanker ved anlegget fortsatt brukes til å lagre produkt. Gjerdemålingen er avtalt videre til 15. oktober 2027.",
            "confirmed",
            [
                src(
                    "https://www.sec.gov/Archives/edgar/data/1534701/000153470126000022/psx-20260331.htm",
                    "Phillips 66 Form 10-Q for the quarter ended March 31, 2026",
                    "US Securities and Exchange Commission",
                ),
                src(
                    "https://www.aqmd.gov/docs/default-source/agendas/governing-board/2026/2026-aug7-009.pdf",
                    "South Coast AQMD governing board item, August 7, 2026, Phillips 66 Wilmington optical tent",
                    "South Coast Air Quality Management District",
                ),
            ],
            "10-Q-en gjentar ikke 10-K-setningen om at full idling av alle enheter skulle bli ferdig de neste månedene. Tanker med produkt er ikke det samme som et tomt anlegg.",
        ),
    )
    save(psx)


if __name__ == "__main__":
    main()
