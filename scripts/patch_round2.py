#!/usr/bin/env python3
"""Add round-2 findings and area profiles. Idempotent on claim ids starting with r2-."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "data" / "cards"
NOTE = "Wayback-feltet fylles av scripts/archive_sources.py."


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


def add_claim(card: dict, claim: dict) -> None:
    ids = {c["id"] for c in card["summary"] + card["claims"]}
    if claim["id"] not in ids:
        card["claims"].append(claim)


def add_summary(card: dict, claim: dict) -> None:
    ids = {c["id"] for c in card["summary"] + card["claims"]}
    if claim["id"] in ids or len(card["summary"]) >= 5:
        return
    card["summary"].append(claim)


def add_link(card: dict, rel: str, target: str, text: str) -> None:
    if any(link["target_id"] == target and link["text"] == text for link in card["links"]):
        return
    card["links"].append({"rel": rel, "target_id": target, "text": text})


def block(geography: str, vintage: str, comparison: str, claims: list) -> dict:
    return {
        "geography": geography,
        "vintage": vintage,
        "comparison": comparison,
        "claims": claims,
    }


CENSUS = "https://data.census.gov/api/access/data/table"
CES = "https://services1.arcgis.com/PCHfdHz4GlDNAhBb/arcgis/rest/services/CalEnviroScreen_4_0_Results_/FeatureServer/0"
CES_REPORT = "https://oehha.ca.gov/sites/default/files/media/downloads/calenviroscreen/report/calenviroscreen40reportf2021.pdf"
WELLS = "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/0/query?where=inHPZ%3D%27Verified+HPZ%27&returnCountOnly=true&f=json"
CAUS = "Sammenligningen er korrelasjon. Den justerer ikke for inntekt eller røyking. CalEnviroScreen-persentilen er mot alle tract i California."


def acs(table: str, geo: str) -> dict:
    return src(
        f"{CENSUS}?id={table}&g={geo}",
        f"{table} for {geo}",
        "US Census Bureau ACS 2019-2023",
    )


def ces_src(tract: str) -> dict:
    return src(
        f"{CES}/query?where=tract%3D{tract}&outFields=asthma,asthmaP,lbw,lbwP,cvd,cvdP,edu,ling,pov,housingB,ACS2019TotalPop&f=json",
        f"CalEnviroScreen 4.0 tract {tract}",
        "OEHHA",
    )


def profile_acs(prefix: str, geo: str, tract_label: str, ces_tract: str, numbers: dict, ces: dict) -> tuple:
    """numbers keys: pop, income, pov, less, bach, u5, old, ling, hisp, white, black, asian, unins."""
    ca = {
        "pop": "39 242 785",
        "income": "96 334",
        "pov": "12,0",
        "less": "15,4",
        "bach": "36,5",
        "u5": "5,6",
        "old": "15,3",
        "ling": "8,3",
        "hisp": "39,8",
        "white": "34,6",
        "black": "5,3",
        "asian": "15,1",
        "unins": "6,9",
    }
    sources = [
        acs("ACSDT5Y2023.B01003", geo),
        acs("ACSDT5Y2023.B19013", geo),
        acs("ACSDT5Y2023.B17001", geo),
        acs("ACSDT5Y2023.B15003", geo),
        acs("ACSDT5Y2023.B01001", geo),
        acs("ACSDT5Y2023.C16002", geo),
        acs("ACSDT5Y2023.B03002", geo),
        acs("ACSST5Y2023.S2701", geo),
        acs("ACSDT5Y2023.B01003", "0400000US06"),
    ]
    text = (
        f"I {tract_label} (ACS 2019–2023) er folketallet {numbers['pop']}, medianinntekten {numbers['income']} dollar "
        f"mot {ca['income']} i California, fattigdom {numbers['pov']} prosent mot {ca['pov']}, uten videregående {numbers['less']} prosent "
        f"mot {ca['less']}, bachelor eller høyere {numbers['bach']} prosent mot {ca['bach']}, under 5 år {numbers['u5']} prosent mot {ca['u5']}, "
        f"65 år og eldre {numbers['old']} prosent mot {ca['old']}, språklig isolerte husholdninger {numbers['ling']} prosent mot {ca['ling']}, "
        f"hispanic {numbers['hisp']} prosent mot {ca['hisp']}, ikke-hispanic hvit {numbers['white']} prosent mot {ca['white']}, "
        f"svart {numbers['black']} prosent mot {ca['black']}, asiatisk {numbers['asian']} prosent mot {ca['asian']}, "
        f"uten helseforsikring {numbers['unins']} prosent mot {ca['unins']}."
    )
    demo = cl(f"{prefix}-demo", text, "confirmed", sources, "Andeler er regnet fra tabellene som beskrevet i data/ca/metoder.md.")
    health_claims = []
    for key, label, unit in (
        ("asthma", "Astma, aldersjusterte akuttmottak per 10 000", "besøk"),
        ("lbw", "Lav fødselsvekt", "prosent"),
        ("cvd", "Hjerteinfarkt, aldersjusterte akuttmottak", "besøk"),
    ):
        value = ces[key]
        pct = ces[key + "P"]
        notable = pct >= 90
        status_word = "merkbart høyt" if notable else "ikke over terskelen på persentil 90"
        health_claims.append(
            cl(
                f"{prefix}-{key}",
                f"{label} i tract {ces_tract} er {value} ({unit} i CalEnviroScreen 4.0). Persentilen mot alle California-tract er {pct}. Det er {status_word}.",
                "confirmed",
                [ces_src(ces_tract), src(CES_REPORT, "CalEnviroScreen 4.0 report", "OEHHA")],
                CAUS,
            )
        )
    return demo, health_claims


def main() -> None:
    ces = {
        "6037204920": {"asthma": "76,1", "asthmaP": 82.8, "lbw": "7,11", "lbwP": 90.9, "cvd": "20,9", "cvdP": 90.2},
        "6019001100": {"asthma": "129,5", "asthmaP": 97.2, "lbw": "7,80", "lbwP": 95.6, "cvd": "21,5", "cvdP": 92.2},
        "6019001000": {"asthma": "139,3", "asthmaP": 98.2, "lbw": "8,76", "lbwP": 98.4, "cvd": "22,7", "cvdP": 94.6},
        "6019001500": {"asthma": "101,7", "asthmaP": 93.1, "lbw": "4,33", "lbwP": 34.4, "cvd": "15,9", "cvdP": 71.2},
        "6025012100": {"asthma": "60,3", "asthmaP": 69.3, "lbw": "4,13", "lbwP": 29.7, "cvd": "21,1", "cvdP": 91.0},
        "6029006201": {"asthma": "77,5", "asthmaP": 83.6, "lbw": "7,77", "lbwP": 95.4, "cvd": "21,7", "cvdP": 92.9},
        "6037920303": {"asthma": "31,7", "asthmaP": 28.3, "lbw": "3,36", "lbwP": 13.9, "cvd": "9,9", "cvdP": 29.3},
    }

    profiles = {
        "ca-problem-south-coast-air": (
            "1400000US06037204920",
            "census tract 2049.20 i Los Angeles County",
            "6037204920",
            {"pop": "2 459", "income": "70 500", "pov": "15,1", "less": "49,2", "bach": "7,1", "u5": "5,4", "old": "16,5", "ling": "17,1", "hisp": "94,8", "white": "2,8", "black": "2,0", "asian": "0,0", "unins": "10,5"},
            "EPA knytter 15 716 242 mennesker (folketelling 2010) til Los Angeles-South Coast Air Basin. Tract-tallet er ett boligområde, ikke bassenget.",
        ),
        "ca-problem-san-joaquin-air": (
            "1400000US06019001100",
            "census tract 11 i Fresno County",
            "6019001100",
            {"pop": "3 200", "income": "32 647", "pov": "41,5", "less": "50,7", "bach": "4,2", "u5": "8,1", "old": "9,3", "ling": "19,1", "hisp": "80,7", "white": "2,1", "black": "13,7", "asian": "0,1", "unins": "9,3"},
            "EPA knytter 3 842 165 mennesker (folketelling 2010) til San Joaquin Valley-området for PM2.5. Tract-tallet er ett boligområde i Fresno.",
        ),
        "ca-problem-drinking-water": (
            "1400000US06019001500",
            "census tract 15 i Fresno County",
            "6019001500",
            {"pop": "1 956", "income": "59 375", "pov": "20,3", "less": "32,5", "bach": "15,9", "u5": "3,8", "old": "10,6", "ling": "6,2", "hisp": "70,6", "white": "15,3", "black": "0,5", "asian": "13,3", "unins": "6,8"},
            "State Water Board knytter 811 964 mennesker til failing-systemene per 31. desember 2024. Tract 15 er et eksempel med høy drikkevannsindikator, ikke tjenesteområdet til de 390 systemene.",
        ),
        "ca-problem-pesticides": (
            "1400000US06019001000",
            "census tract 10 i Fresno County",
            "6019001000",
            {"pop": "4 714", "income": "29 581", "pov": "44,5", "less": "49,0", "bach": "6,4", "u5": "8,3", "old": "10,3", "ling": "12,4", "hisp": "64,0", "white": "2,9", "black": "16,1", "asian": "12,9", "unins": "5,0"},
            "DPR publiserer pund per fylke, ikke et folketall for eksponerte. Tract 10 er et eksempel med høy pesticidindikator i Fresno.",
        ),
        "ca-problem-groundwater-overdraft": (
            "1400000US06029006201",
            "census tract 62.01 i Kern County",
            "6029006201",
            {"pop": "2 447", "income": "51 723", "pov": "30,2", "less": "42,3", "bach": "4,8", "u5": "7,5", "old": "9,9", "ling": "9,0", "hisp": "82,9", "white": "14,1", "black": "0,0", "asian": "1,4", "unins": "13,2"},
            "DWR oppgir ikke et folketall for de kritisk overtrukne bassengene i dokumentene som er lest. Tract 62.01 ligger i Kern County, som har delbasseng 5-022.14, men trakten er ikke vist å ligge inni bassenget.",
        ),
    }

    for cid, (geo, label, tract, numbers, agency) in profiles.items():
        card = load(cid)
        demo, health = profile_acs(cid.split("-")[-1], geo, label, tract, numbers, ces[tract])
        card["population"] = block(
            agency.split(".")[0] + ".",
            "Folketelling 2010 der EPA er kilden, ellers ACS 2019–2023 eller etatens egen dato.",
            "California ACS 2019–2023 der et tract-tall er sammenlignet. Etatstallet er ikke en rate.",
            [cl(f"r2-{cid}-pop", agency, "confirmed", [acs("ACSDT5Y2023.B01003", geo), ces_src(tract)], "Se også de eldre etatstallene i sammendraget.")],
        )
        card["demographics"] = block(label, "ACS 2019–2023", "Hele California, samme tabeller", [demo])
        card["health_outcomes"] = block(
            f"CalEnviroScreen 4.0 tract {tract}",
            "OEHHA 4.0, helseindikatorer fra årene i rapporten",
            "Alle census tracts i California i CalEnviroScreen 4.0. Merkbart betyr persentil 90 eller høyere.",
            health,
        )
        notable = [h for h in health if "merkbart høyt" in h["text"]]
        if notable:
            add_summary(card, cl(f"r2-{cid}-sum", notable[0]["text"], "confirmed", notable[0]["sources"], CAUS))
        save(card)

    # Salton: CES health + no matching ACS 2023 for the 2010 tract id
    salton = load("ca-problem-salton-sea")
    salton["population"] = block(
        "Imperial County i EPA Green Book, pluss census tract 012100 i CalEnviroScreen.",
        "Folketelling 2010 for fylket. ACS 2015–2019 i CalEnviroScreen for trakten.",
        "California-tract i CalEnviroScreen. ACS 2019–2023 for geoid 06025012100 svarte tomt.",
        [cl(
            "r2-salton-pop",
            "EPA fører 154 061 mennesker (2010) i Imperial County for PM2.5. CalEnviroScreen-tract 6025012100 har 6 779 innbyggere i ACS 2015–2019. data.census.gov returnerte tomt svar for ACS 2019–2023 på geoid 1400000US06025012100. Et punkt i området treffer 2020-tract 121.02, som er en annen geografi.",
            "confirmed",
            [
                src("https://www3.epa.gov/airquality/greenbook/rncl2.html", "PM-2.5 Green Book", "US EPA"),
                ces_src("6025012100"),
                src("https://data.census.gov/api/access/data/table?id=ACSDT5Y2023.B01003&g=1400000US06025012100", "Tomt svar for 2010-tract i ACS 2023", "US Census Bureau"),
                src("https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x=-115.50&y=32.68&benchmark=4&vintage=4&format=json", "Census geocoder, punkt i Imperial", "US Census Bureau"),
            ],
        )],
    )
    salton["demographics"] = block(
        "Tract 6025012100, CalEnviroScreen 4.0",
        "ACS 2015–2019 via OEHHA",
        "Persentil mot alle California-tract. ACS 2019–2023-andelene er ikke regnet for denne 2010-geoid-en.",
        [cl(
            "r2-salton-demo",
            "I tract 6025012100 er andelen med lav utdanning 43,5 prosent (persentil 92,5), språklig isolasjon 52,8 prosent (persentil 99,6), fattigdom 56,6 prosent (persentil 88,7), boligbyrde 31,8 prosent (persentil 92,9) og hispanic 98,6 prosent. Barn under 10 år er 12,6 prosent og 65 år og eldre 17,8 prosent i CalEnviroScreen-feltene.",
            "confirmed",
            [ces_src("6025012100"), src(CES_REPORT, "CalEnviroScreen 4.0 report", "OEHHA")],
            "Dette er OEHHA-indikatorer, ikke de samme ACS 2019–2023-andelene som på de andre kortene.",
        )],
    )
    salton_health = []
    for key, label, unit in (
        ("asthma", "Astma, aldersjusterte akuttmottak per 10 000", "besøk"),
        ("lbw", "Lav fødselsvekt", "prosent"),
        ("cvd", "Hjerteinfarkt, aldersjusterte akuttmottak", "besøk"),
    ):
        value = ces["6025012100"][key]
        pct = ces["6025012100"][key + "P"]
        word = "merkbart høyt" if pct >= 90 else "ikke over terskelen på persentil 90"
        salton_health.append(cl(
            f"salton-{key}",
            f"{label} i tract 6025012100 er {value} ({unit}). Persentilen er {pct}. Det er {word}.",
            "confirmed",
            [ces_src("6025012100"), src(CES_REPORT, "CalEnviroScreen 4.0 report", "OEHHA")],
            CAUS,
        ))
    salton["health_outcomes"] = block(
        "Tract 6025012100",
        "CalEnviroScreen 4.0",
        "Alle California-tract. Persentil 90 er terskelen.",
        salton_health,
    )
    add_claim(salton, cl(
        "r2-salton-playa",
        "SSMP-årsrapporten for 2025 sier at faktisk blotlagt areal i 2024 var om lag 20 000 acre mindre enn anslaget fra 2018, fordi tilsiget var høyere enn modellene. Den gir ikke ett tall for samlet blotlagt playa. En egen IID-rapport om utslipp sier at eksponert playa økte fra 33 311 acre ved utgangen av 2023 til 37 804 acre ved utgangen av 2024, målt med satellitt og USGS-vannstand.",
        "confirmed",
        [
            src("https://saltonsea.ca.gov/wp-content/uploads/2025/03/SSMP-2025-Annual-Report_Mar-28.pdf", "2025 SSMP annual report", "California Natural Resources Agency"),
            src("https://saltonseaprogram.com/documents/2024_2025_Annual_Report_and_Emissions_Estimates.pdf", "Salton Sea Emissions Monitoring Program 2024/2025", "Imperial Irrigation District"),
        ],
        "De to tallene er ikke samme mål. 20 000 acre er et avvik fra en prognose. 37 804 acre er IIDs areal mellom strandlinjen i 2002 og strandlinjen i 2024.",
    ))
    save(salton)

    aliso = load("ca-problem-aliso-canyon")
    demo, health = profile_acs(
        "aliso",
        "1400000US06037920303",
        "census tract 9203.03 i Los Angeles County, som Census geocoder knytter til FRS-punktet",
        "6037920303",
        {"pop": "1 564", "income": "138 750", "pov": "6,5", "less": "4,7", "bach": "64,6", "u5": "5,3", "old": "14,6", "ling": "7,5", "hisp": "5,8", "white": "52,2", "black": "0", "asian": "0", "unins": "1,1"},
        ces["6037920303"],
    )
    # fix black/asian if I passed 0 incorrectly - I didn't compute asian. Let me not invent. I only computed hisp and white. I put asian 0 and black 0 wrongly.
    # Recalculate from the statement: I only printed hisp and white. I should not include black and asian as 0.
    # I'll overwrite the demo claim text to omit black and asian if I didn't compute them.
    # I computed only hisp and white. Remove black/asian from the generated sentence by replacing the claim.
    demo["text"] = (
        "Census tract 9203.03, som geocoderen knytter til Aliso Canyon-punktet, hadde 1 564 innbyggere i ACS 2019–2023. "
        "Medianinntekten var 138 750 dollar mot 96 334 i California. Fattigdom var 6,5 prosent mot 12,0. "
        "Uten videregående var 4,7 prosent mot 15,4, og bachelor eller høyere 64,6 prosent mot 36,5. "
        "Under 5 år var 5,3 prosent mot 5,6, og 65 år og eldre 14,6 prosent mot 15,3. "
        "Språklig isolasjon var 7,5 prosent mot 8,3. Hispanic var 5,8 prosent mot 39,8, og ikke-hispanic hvit 52,2 prosent mot 34,6. "
        "Uten helseforsikring var 1,1 prosent mot 6,9."
    )
    aliso["population"] = block(
        "Census tract 9203.03 rundt FRS-punktet for Aliso Canyon.",
        "ACS 2019–2023. Geocoder vintage 4.",
        "California ACS 2019–2023.",
        [cl("r2-aliso-pop", "Tract 9203.03 har 1 564 innbyggere. Det er trakten punktet faller i, ikke et opptellingsområde for evakuerte.", "confirmed", [acs("ACSDT5Y2023.B01003", "1400000US06037920303"), src("https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x=-118.55124&y=34.30757&benchmark=4&vintage=4&format=json", "Census geocoder for Aliso Canyon FRS point", "US Census Bureau")])],
    )
    aliso["demographics"] = block("Tract 9203.03", "ACS 2019–2023", "California", [demo])
    aliso["health_outcomes"] = block("Tract 6037920303 i CalEnviroScreen 4.0", "OEHHA 4.0", "Alle California-tract", health)
    add_claim(aliso, cl(
        "r2-aliso-cpuc",
        "CPUC-vedtak D.24-12-076 setter største arbeidsvolum for gass i Aliso Canyon til 68,6 milliarder kubikkfot og lar anlegget fortsette, med vurdering annethvert år. Et vedtak som avslår gjenopptakelse, gjentar dette nivået. Energidivisjonens vurdering i 2025 anbefaler et kutt på 10 milliarder kubikkfot til 58,6. Den anbefalingen er ikke et nytt vedtak. SoCalGas har bedt kommisjonen avslå kuttet i sak A.26-01-009.",
        "confirmed",
        [
            src("https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M569/K577/569577353.PDF", "Order denying rehearing of D.24-12-076", "CPUC"),
            src("https://www.cpuc.ca.gov/-/media/cpuc-website/divisions/energy-division/documents/natural-gas/aliso-canyon/2025_aliso_canyon_biennial_assessment.pdf", "2025 Aliso Canyon biennial assessment", "CPUC Energy Division"),
            src("https://docs.cpuc.ca.gov/PublishedDocs/Efile/G000/M595/K083/595083702.PDF", "SoCalGas application on the 2025 assessment", "CPUC docket"),
        ],
    ))
    save(aliso)

    oil = load("ca-problem-oil-gas-proximity")
    oil["population"] = block(
        "Health protection zones i CalGEM WellSTAR.",
        "Karttjeneste lest 2026-10-28.",
        "Ingen folketelling innenfor 3 200 fot er publisert i dokumentene som er lest.",
        [cl(
            "r2-oil-pop",
            "CalGEM WellSTAR hadde 74 506 brønner merket Verified HPZ, av dem 12 317 active og 8 987 idle. Tjenesten har ikke antall mennesker, boliger eller skoler. Notatet av 11. april 2025 og lovvarselet fra oktober 2026 sier at operatørene skal levere inventar, og at CalGEM har gitt brønner en HPZ-status. Ingen av dem oppgir et folketall.",
            "not_found",
            [
                src(WELLS, "WellSTAR count, inHPZ = Verified HPZ", "CalGEM"),
                src("https://www.conservation.ca.gov/calgem/Documents/NTO_2025-03_PRC%203285.pdf", "Notice to Operators 2025-03", "CalGEM"),
                src("https://www.conservation.ca.gov/calgem/Documents/SB%201137%20Legislative%20Notification%20-%20October%202026.pdf", "SB 1137 legislative notification, October 2026", "CalGEM"),
            ],
            "Brønntallet er bekreftet. Folketallet er ikke funnet. Status not_found gjelder menneskene.",
        )],
    )
    oil["demographics"] = block(
        "Hele helsesonen.",
        "Ikke hentet.",
        "Ikke laget, fordi sonen ikke har et folketall eller en tract-liste fra CalGEM.",
        [cl("r2-oil-demo", "Demografi for alle som bor innenfor 3 200 fot er ikke regnet. Det krever en kobling mellom brønnlag og census blocks som ikke er gjort.", "not_found", [src(WELLS, "WellSTAR wells", "CalGEM")])],
    )
    oil["health_outcomes"] = block(
        "Helsesonen som helhet.",
        "Ikke hentet fra et samlet uttrekk.",
        "Ikke sammenlignet med områder utenfor sonen i denne runden.",
        [cl("r2-oil-health", "Et samlet helseutfall for sonen, sammenlignet med tract utenfor sonen, er ikke hentet. Lovteksten viser til studier om nærhet. Den er ikke en rate for sonen.", "not_found", [src("https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202120220SB1137", "SB 1137", "Legislative Counsel")])],
    )
    add_claim(oil, cl(
        "r2-oil-wells",
        "Av brønnene merket Verified HPZ var 50 491 plugged, 2 546 canceled og 138 new, i tillegg til active og idle. Aera Energy LLC sto fortsatt som operatorName på 57 805 brønner i samme tjeneste, hvorav 1 410 active eller idle i Verified HPZ.",
        "confirmed",
        [src(WELLS.replace("Verified+HPZ", "Verified+HPZ") , "WellSTAR inHPZ query", "CalGEM")],
    ))
    save(oil)

    refin = load("ca-problem-refineries")
    refin["population"] = block(
        "Census tracts som anleggspunktene faller i.",
        "ACS 2019–2023 og Census geocoder vintage 4.",
        "Ikke et nabolag. 9800-trakter er ofte anleggsareal.",
        [cl(
            "r2-ref-pop",
            "Geocoderen legger Chevron El Segundo i tract 9800.30 med 0 innbyggere, Torrance i tract 9800.05 med 0 innbyggere, og Phillips 66 Wilmington i tract 9800.31 med 970 innbyggere. Medianinntekt er ikke publisert for disse tractene (verdi -666666666 i B19013). De er ikke brukt som portrett av nabolagene ved gjerdet.",
            "confirmed",
            [
                src("https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x=-118.41873&y=33.916216&benchmark=4&vintage=4&format=json", "Geocoder El Segundo", "US Census Bureau"),
                acs("ACSDT5Y2023.B01003", "1400000US06037980030"),
                acs("ACSDT5Y2023.B01003", "1400000US06037980005"),
                acs("ACSDT5Y2023.B01003", "1400000US06037980031"),
            ],
        )],
    )
    refin["demographics"] = block("Nabolag ved gjerdet.", "Ikke avgrenset.", "Ikke regnet.", [cl("r2-ref-demo", "Demografi for boliger innenfor en satt avstand fra raffinerigjerdet er ikke regnet. Anleggstractene har ikke et brukbart befolkningsgrunnlag.", "not_found", [acs("ACSDT5Y2023.B01003", "1400000US06037980030")])])
    refin["health_outcomes"] = block("Nabolag ved gjerdet.", "Ikke hentet.", "Ikke sammenlignet.", [cl("r2-ref-health", "Helseutfall for et avgrenset nabolag ved hvert raffineri er ikke hentet i denne runden.", "not_found", [src("https://www.epa.gov/system/files/documents/2025-01/torrance-order_1-7-25.pdf", "EPA title V order, Torrance, 7. januar 2025", "US EPA")])])
    add_claim(refin, cl(
        "r2-ref-ops",
        "EPA skriver i et vedtak 7. januar 2025 at Torrance-raffineriet drives av Torrance Refining Company, LLC, at PBF Energy kjøpte det i 2016, og at South Coast AQMD utstedte fornyet title V-tillatelse 30. mai 2024. Phillips 66 kunngjorde 16. oktober 2024 at Los Angeles-raffineriet, med anlegg i Wilmington og Carson, skulle stanse driften i fjerde kvartal 2025.",
        "confirmed",
        [
            src("https://www.epa.gov/system/files/documents/2025-01/torrance-order_1-7-25.pdf", "EPA order on Torrance title V permit", "US EPA"),
            src("https://investor.phillips66.com/financial-information/news-releases/news-release-details/2024/Phillips-66-provides-notice-of-its-plan-to-cease-operations-at-Los-Angeles-area-refinery/default.aspx", "Phillips 66 notice, 16. oktober 2024", "Phillips 66"),
        ],
        "Phillips 66-teksten er selskapets kunngjøring om en plan. Et senere etatsdokument som bekrefter at driften faktisk stoppet, er ikke åpnet.",
    ))
    save(refin)

    pfas = load("ca-problem-pfas")
    pfas["population"] = block(
        "Brønner i disadvantaged communities i General Order DW-2024-0002-DDW.",
        "2024–2025 etatsdokumenter.",
        "Ikke ett tjenesteområde.",
        [cl(
            "r2-pfas-pop",
            "Dokumentene bruker avrundede planleggingsanslag, ikke én ferdig telling. Pressemeldingen 1. april 2024 sier nearly 4 000 brønner og at 1 190 vannsystemer fikk varsel. Kvalitetsplanen fra september 2024 og juni 2025 sier approximately 3 800 brønner. Programsiden sier about 3 600. Junidokumentet skriver at tallet kan endres etter at pålegget er sendt, fordi systemer kan legges til eller tas ut. Derfor er 3 600 og 3 800 ikke to konkurrerende fasit-tall.",
            "confirmed",
            [
                src("https://www.waterboards.ca.gov/press_room/press_releases/2024/pr20240401-final-pfas-testing.html", "PFAS testing press release, 1. april 2024", "State Water Board"),
                src("https://www.waterboards.ca.gov/pfas/drinking_water.html", "PFAS drinking water page", "State Water Board"),
                src("https://pfas.owp.csus.edu/pdfs/QAPP_06.30.2025.pdf", "PFAS QAPP, juni 2025", "State Water Board"),
            ],
        )],
    )
    pfas["demographics"] = block("De om lag 3 600–3 800 brønnene.", "Ikke ett tract.", "Ikke regnet.", [cl("r2-pfas-demo", "Det er ikke laget et befolkningsvektet demografisk snitt for brønnene på pålegget. Exhibit A med kildelisten er ikke telt rad for rad.", "not_found", [src("https://www.waterboards.ca.gov/drinking_water/certlic/drinkingwater/pfas_ddw_general_order/", "PFAS general order page", "State Water Board")])])
    pfas["health_outcomes"] = block("Området som dekkes av pålegget.", "Ikke hentet.", "Ikke sammenlignet.", [cl("r2-pfas-health", "Et helseutfall for folk som får vann fra brønnene med PFAS-funn, sammenlignet med systemer uten funn, er ikke hentet.", "not_found", [src("https://www.waterboards.ca.gov/pfas/drinking_water.html", "PFAS drinking water", "State Water Board")])])
    save(pfas)

    # organizations and bills
    crc = load("org-crc")
    add_claim(crc, cl(
        "r2-crc-merger",
        "CRC skrev i skjema 8-K, med tidligste hendelse 28. juni 2024 og innlevert 1. juli 2024, at sammenslåingen med Aera Energy, LLC var fullført 1. juli 2024, og at Aera og Aera Energy Services Company da var heleide datterselskaper. CRC utstedte 21 315 707 aksjer til selgerne.",
        "confirmed",
        [src("https://www.sec.gov/Archives/edgar/data/1609253/000119312524173343/d845209d8k.htm", "CRC Form 8-K, 1. juli 2024", "SEC")],
    ))
    add_claim(crc, cl(
        "r2-crc-recip",
        "For navnestrenger uten personnavn i parentes, der detaljsiden summerte til samme total som sammendraget, var de største mottakerne i perioden 1. januar 2025–28. oktober 2026 Coalition to Restore California's Middle Class ID 1365275 med 1 500 000 dollar, Yes on 45 ID 1484853 med 500 000 dollar, og Californians for Central Valley Public Safety med 330 000 dollar. Strengen for Los Angeles på 125 000 dollar er utelatt fordi detaljlisten ikke summerte til sammendraget.",
        "confirmed",
        [src("https://dbsearch.sos.ca.gov/ContributorSearch.aspx", "Cal-Access contributor search, California Resources Corporation", "California Secretary of State")],
        "Mottakerbeløpene er summert bare innenfor navnestrenger der linjene traff sammendragstotalen. Se data/ca/metoder.md er ikke brukt her. Metoden er beskrevet i kortets note.",
    ))
    save(crc)

    chev = load("org-chevron")
    add_claim(chev, cl(
        "r2-chev-recip",
        "For selskapsstrenger i San Ramon der detaljsiden traff sammendragstotalen, unntatt en streng på 400 000 dollar som ikke traff, er summen 6 777 900 dollar. Største mottaker er Coalition to Restore California's Middle Class ID 1365275 med 3 784 000 dollar. Deretter Becerra for Governor 2026 ID 1490885 med 500 000 dollar, to varianter av Keeping Californians Working med 350 000 og 300 000 dollar, Legislative Action PAC ID 1481714 med 325 000 dollar og Committee for Industrial Safety ID 990741 med 325 000 dollar. Dublin Chevron, La Cienega Chevron, Yuba City Chevron og Murrieta er holdt utenfor.",
        "confirmed",
        [src("https://dbsearch.sos.ca.gov/ContributorSearch.aspx", "Cal-Access contributor detail for Chevron name strings", "California Secretary of State")],
    ))
    add_claim(chev, cl(
        "r2-chev-fec",
        "FEC schedule A for toårsperioden 2026, søk på bidragsyternavn CHEVRON, ga 326 treff. De største på første side sortert etter beløp var 2 000 000 dollar fra Chevron Corporation til SLF PAC 26. februar 2026, og to innbetalinger på 750 000 dollar til samme komité 23. juni og 20. august 2025. Samme søk med navnet CALIFORNIA RESOURCES ga 0 treff.",
        "confirmed",
        [src("https://api.open.fec.gov/v1/schedules/schedule_a/?contributor_name=CHEVRON&two_year_transaction_period=2026&per_page=20&sort=-contribution_receipt_amount", "FEC schedule A, contributor_name CHEVRON, cycle 2026", "FEC")],
        "URL-en krever en gratis FEC-nøkkel. DEMO_KEY virket 2026-10-28. Tallet 326 er pagineringens count, ikke en sum av dollar.",
    ))
    save(chev)

    pbf = load("org-pbf")
    add_claim(pbf, cl(
        "r2-pbf-own",
        "EPA skriver 7. januar 2025 at Torrance-raffineriet ble kjøpt av PBF Energy i 2016 og drives av Torrance Refining Company, LLC.",
        "confirmed",
        [src("https://www.epa.gov/system/files/documents/2025-01/torrance-order_1-7-25.pdf", "EPA title V order, Torrance", "US EPA")],
    ))
    save(pbf)

    torr = load("org-torrance-refining")
    add_claim(torr, cl(
        "r2-torr-op",
        "Samme EPA-vedtak sier at selskapet er operatør, og at South Coast AQMD utstedte fornyet title V-tillatelse 30. mai 2024 for facility ID 181667.",
        "confirmed",
        [src("https://www.epa.gov/system/files/documents/2025-01/torrance-order_1-7-25.pdf", "EPA title V order, Torrance", "US EPA")],
    ))
    save(torr)

    ph = load("org-phillips66")
    add_claim(ph, cl(
        "r2-psx-close",
        "Phillips 66 kunngjorde 16. oktober 2024 at Los Angeles-raffineriet, med tomter i Wilmington og Carson, skulle stanse driften i fjerde kvartal 2025. Om stansen var gjennomført per 28. oktober 2026, er ikke bekreftet i et etatsdokument i denne runden.",
        "confirmed",
        [src("https://investor.phillips66.com/financial-information/news-releases/news-release-details/2024/Phillips-66-provides-notice-of-its-plan-to-cease-operations-at-Los-Angeles-area-refinery/default.aspx", "Phillips 66 notice of plan to cease operations", "Phillips 66")],
        "Bekreftet er kunngjøringen. Faktisk stans er åpen.",
    ))
    save(ph)

    gw = load("ca-problem-groundwater-overdraft")
    add_link(gw, "bill", "bill-sb-1168", "SB 1168, en av de tre SGMA-lovene.")
    add_link(gw, "bill", "bill-ab-1739", "AB 1739.")
    add_link(gw, "bill", "bill-sb-1319", "SB 1319.")
    add_link(gw, "lawmaker", "lawmaker-fran-pavley", "Pavley er forfatter på to av lovene.")
    save(gw)

    # new cards
    def write_new(card: dict) -> None:
        path = CARDS / f"{card['id']}.json"
        if path.exists():
            return
        card.setdefault("state", "CA")
        card.setdefault("updated", "2026-10-28")
        card.setdefault("rank", None)
        card.setdefault("org_kind", None)
        card.setdefault("geometry", None)
        card.setdefault("map_features", [])
        card.setdefault("checked_empty", [])
        card.setdefault("open_questions", [])
        card["schema_version"] = "1.0.0"
        save(card)

    hist1168 = src("https://leginfo.legislature.ca.gov/faces/billHistoryClient.xhtml?bill_id=201320140SB1168", "SB 1168 history", "Legislative Counsel")
    st1168 = src("https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=201320140SB1168", "SB 1168 status", "Legislative Counsel")
    hist1319 = src("https://leginfo.legislature.ca.gov/faces/billHistoryClient.xhtml?bill_id=201320140SB1319", "SB 1319 history", "Legislative Counsel")
    st1319 = src("https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=201320140SB1319", "SB 1319 status", "Legislative Counsel")
    hist1739 = src("https://leginfo.legislature.ca.gov/faces/billHistoryClient.xhtml?bill_id=201320140AB1739", "AB 1739 history", "Legislative Counsel")
    st1739 = src("https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=201320140AB1739", "AB 1739 status", "Legislative Counsel")
    votes1168 = src("https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201320140SB1168", "SB 1168 votes", "Legislative Counsel")

    write_new({
        "id": "bill-sb-1168",
        "type": "bill",
        "name": "SB 1168 (2013-2014), grunnvann",
        "summary": [
            cl("s1", "SB 1168, kapittel 346, godkjent 16. september 2014. Forfatter på statussiden er Pavley. Loven legger til del 2.74 i Water Code.", "confirmed", [st1168]),
            cl("s2", "Senatet samtykket i forsamlingens endringer 29. august 2014 med 25 mot 10. Forsamlingen vedtok lovforslaget samme dag med 47 mot 27.", "confirmed", [hist1168]),
            cl("s3", "Pavley står på ja-listen i senatets samtykkevotering.", "confirmed", [votes1168]),
            cl("s4", "Ingen Cal-Access-filing som er lest, sier at en navngitt lobbyvirksomhet oppga SB 1168. Loven er fra 2014. Skjemaene som er åpnet, er fra 2025.", "not_found", [src("https://dbsearch.sos.ca.gov/LobbyIntSearch.aspx", "Cal-Access lobbying search", "California Secretary of State")]),
        ],
        "claims": [cl("c1", "Første senatsvotering 27. mai 2014 var 24 mot 12.", "confirmed", [hist1168])],
        "links": [
            {"rel": "problem", "target_id": "ca-problem-groundwater-overdraft", "text": "SGMA-rammen."},
            {"rel": "lawmaker", "target_id": "lawmaker-fran-pavley", "text": "Forfatter."},
            {"rel": "bill", "target_id": "bill-ab-1739", "text": "Vedtatt samme dag."},
            {"rel": "bill", "target_id": "bill-sb-1319", "text": "Vedtatt samme dag."},
        ],
        "open_questions": ["Hvem som lobbet på SB 1168 i 2014. Det krever sesjonen 2013–2014 i Cal-Access, som ikke er åpnet."],
    })
    write_new({
        "id": "bill-sb-1319",
        "type": "bill",
        "name": "SB 1319 (2013-2014), grunnvann",
        "summary": [
            cl("s1", "SB 1319, kapittel 348, godkjent 16. september 2014. Forfatter er Pavley. Loven endrer Water Code avsnitt 10735.2 og 10735.8.", "confirmed", [st1319]),
            cl("s2", "Senatet samtykket 29. august 2014 med 24 mot 10. Forsamlingen vedtok samme dag med 48 mot 26.", "confirmed", [hist1319]),
            cl("s3", "Ingen åpnet lobbyfiling oppgir SB 1319.", "not_found", [src("https://dbsearch.sos.ca.gov/LobbyIntSearch.aspx", "Cal-Access lobbying search", "California Secretary of State")]),
        ],
        "claims": [cl("c1", "Senatets tredje lesning 28. mai 2014 var 23 mot 12.", "confirmed", [hist1319])],
        "links": [
            {"rel": "problem", "target_id": "ca-problem-groundwater-overdraft", "text": "Del av SGMA."},
            {"rel": "lawmaker", "target_id": "lawmaker-fran-pavley", "text": "Forfatter."},
        ],
        "open_questions": ["Enkeltstemmen til Pavley på den endelige voteringen er ikke åpnet på votes-siden. Historikken gir tellingene."],
    })
    write_new({
        "id": "bill-ab-1739",
        "type": "bill",
        "name": "AB 1739 (2013-2014), grunnvann",
        "summary": [
            cl("s1", "AB 1739, kapittel 347, godkjent 16. september 2014. Forfatter er Dickinson. Pavley står som principal coauthor.", "confirmed", [st1739]),
            cl("s2", "Forsamlingen samtykket i senatets endringer 29. august 2014 med 47 mot 28. Senatet vedtok 27. august 2014 med 26 mot 11.", "confirmed", [hist1739]),
            cl("s3", "Ingen åpnet lobbyfiling oppgir AB 1739.", "not_found", [src("https://dbsearch.sos.ca.gov/LobbyIntSearch.aspx", "Cal-Access lobbying search", "California Secretary of State")]),
        ],
        "claims": [cl("c1", "Forsamlingens tredje lesning 28. mai 2014 var 48 mot 24.", "confirmed", [hist1739])],
        "links": [
            {"rel": "problem", "target_id": "ca-problem-groundwater-overdraft", "text": "Del av SGMA."},
            {"rel": "lawmaker", "target_id": "lawmaker-roger-dickinson", "text": "Forfatter."},
            {"rel": "lawmaker", "target_id": "lawmaker-fran-pavley", "text": "Principal coauthor."},
        ],
        "open_questions": ["Lobbyfiler fra 2014 er ikke åpnet."],
    })
    write_new({
        "id": "lawmaker-fran-pavley",
        "type": "lawmaker",
        "name": "Fran Pavley",
        "summary": [
            cl("s1", "Statussiden for SB 1168 og SB 1319 oppgir Pavley som lead author.", "confirmed", [st1168, st1319]),
            cl("s2", "På AB 1739 står hun som principal coauthor.", "confirmed", [st1739]),
            cl("s3", "På votes-siden for SB 1168 står hun på ja-listen i samtykkevotoeringen 29. august 2014.", "confirmed", [votes1168]),
            cl("s4", "Distrikt er ikke slått opp. Hun er med som forfatter i 2014, ikke som sittende senator i 2026.", "not_verified", [st1168]),
        ],
        "claims": [cl("c1", "Ingen biografi er hentet.", "not_found", [st1168])],
        "links": [
            {"rel": "bill", "target_id": "bill-sb-1168", "text": "Forfatter."},
            {"rel": "bill", "target_id": "bill-sb-1319", "text": "Forfatter."},
            {"rel": "bill", "target_id": "bill-ab-1739", "text": "Principal coauthor."},
        ],
        "checked_empty": [{
            "field": "district",
            "searched": "Senatets nåværende medlemsliste er ikke brukt til å gjette et distrikt fra 2014.",
            "result": "not_found",
            "urls": ["https://www.senate.ca.gov/senators"],
            "retrieved": "2026-10-28",
        }],
        "open_questions": ["Offisielt distrikt i 2014."],
    })
    write_new({
        "id": "lawmaker-roger-dickinson",
        "type": "lawmaker",
        "name": "Roger Dickinson",
        "summary": [
            cl("s1", "Statussiden for AB 1739 oppgir Dickinson som lead author.", "confirmed", [st1739]),
            cl("s2", "Forsamlingen vedtok loven 29. august 2014 med 47 mot 28. Hans egen stemme er ikke lest av fra en votes-side.", "not_verified", [hist1739], "billVotesClient for AB 1739 er ikke åpnet."),
            cl("s3", "Distrikt i 2014 er ikke slått opp.", "not_verified", [st1739]),
        ],
        "claims": [cl("c1", "Historikklinjen for SB 1168 sier at tredje lesning i forsamlingen ble lagt frem av Dickinson. Det er en prosedyrelinje.", "confirmed", [hist1168])],
        "links": [{"rel": "bill", "target_id": "bill-ab-1739", "text": "Forfatter."}],
        "checked_empty": [{
            "field": "district",
            "searched": "assembly.ca.gov er ikke åpnet for 2014-distriktet.",
            "result": "not_found",
            "urls": ["https://www.assembly.ca.gov/"],
            "retrieved": "2026-10-28",
        }],
        "open_questions": ["Hans stemme på den endelige voteringen."],
    })

    firm = load("firm-carpenter-garcia-sievers")
    add_claim(firm, cl(
        "r2-firm-clients",
        "LobbyFirmsDetail for sesjonen 2025–2026 viser firmaets kvartalsvise innbetalinger, ikke navn på oppdragsgivere. Andre klienter enn WSPA, og om noen av dem er miljø- eller klimaorganisasjoner, er derfor ikke dokumentert fra denne siden.",
        "not_found",
        [src("https://dbsearch.sos.ca.gov/LobbyFirmsSearch.aspx", "Cal-Access lobbying firm search, session 2025-2026", "California Secretary of State")],
    ))
    save(firm)
    print("patched")


if __name__ == "__main__":
    main()
