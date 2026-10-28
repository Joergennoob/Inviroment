#!/usr/bin/env python3
"""Add area aggregates, the 3,200-foot calculation, and the round-3 filings."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "data" / "cards"
NOTE = "Wayback-feltet fylles av scripts/archive_sources.py."
SOS = "https://campaignfinance.cdn.sos.ca.gov/dbwebexport.zip"
PLACES = "https://data.cdc.gov/resource/yjkw-uj5s.json?stateabbr=CA&$limit=1"
CES = (
    "https://services1.arcgis.com/PCHfdHz4GlDNAhBb/arcgis/rest/services/"
    "CalEnviroScreen_4_0_Results_/FeatureServer/0/query?where=1%3D1&returnCountOnly=true&f=json"
)
CAUS = (
    "Sammenligningen er korrelasjon. Den justerer ikke for inntekt, røyking eller alder. "
    "Terskelen for merkbart er 1,5 ganger resten av California, eller minst 10 prosentpoeng der målet er en andel."
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


def walk_claims(card: dict):
    for claim in card["summary"] + card["claims"]:
        yield claim
    for name in ("population", "demographics", "health_outcomes"):
        block = card.get(name)
        if block:
            for claim in block["claims"]:
                yield claim


def add_claim(card: dict, claim: dict, block: str | None = None) -> None:
    ids = {item["id"] for item in walk_claims(card)}
    if claim["id"] in ids:
        return
    if block:
        card[block]["claims"].append(claim)
    else:
        card["claims"].append(claim)


def replace_claim(card: dict, cid: str, text: str, status: str, note: str, sources: list) -> None:
    for claim in walk_claims(card):
        if claim["id"] == cid:
            claim["text"] = text
            claim["status"] = status
            claim["note"] = note
            claim["sources"] = sources
            return
    raise SystemExit(f"missing claim {cid} on {card['id']}")


def add_link(card: dict, rel: str, target: str, text: str) -> None:
    if any(link["target_id"] == target and link["rel"] == rel for link in card["links"]):
        return
    card["links"].append({"rel": rel, "target_id": target, "text": text})


PLACES_SRC = src(PLACES, "PLACES census tract data, GIS friendly format, 2025 release, California", "CDC")
CES_SRC = src(CES, "CalEnviroScreen 4.0 Results feature service", "OEHHA")
SETBACK_SRC = [
    src(
        "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/0/query?where=WellStatus%3D%27Active%27+OR+WellStatus%3D%27Idle%27&returnCountOnly=true&f=json",
        "WellSTAR active or idle well count",
        "CalGEM",
    ),
    src(
        "https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/California/ca2020.pl.zip",
        "2020 Census PL 94-171, California geographic header, summary level 750",
        "US Census Bureau",
    ),
    src(
        "https://nces.ed.gov/opengis/rest/services/K12_School_Locations/EDGE_GEOCODE_PUBLICSCH_2324/MapServer/0/query?where=STATE%3D%27CA%27&returnCountOnly=true&f=json",
        "NCES EDGE public school locations 2023-24, California",
        "National Center for Education Statistics",
    ),
]
VF = src(
    "https://www.cdph.ca.gov/Programs/CID/DCDC/CDPH%20Document%20Library/CocciEpiSummary2022.pdf",
    "Epidemiologic Summary of Valley Fever in California, 2022",
    "California Department of Public Health",
)
PISP = src(
    "https://www.cdpr.ca.gov/wp-content/uploads/2025/07/state_and_county_totals_2022.pdf",
    "Pesticide Illness Surveillance Program, state and county totals, 2022",
    "California Department of Pesticide Regulation",
)
CANCER = src(
    "https://statecancerprofiles.cancer.gov/incidencerates/index.php?age=001&areatype=county&cancer=001&race=00&sex=0&stateFIPS=06&type=incd",
    "Incidence rate report for California by county, all cancer sites, 2019-2023",
    "National Cancer Institute State Cancer Profiles",
)
SOS_SRC = src(SOS, "CAL-ACCESS raw data export, tables TEXT_MEMO_CD, CVR_LOBBY_DISCLOSURE_CD and LEMP_CD", "California Secretary of State")


def main() -> None:
    oil = load("ca-problem-oil-gas-proximity")
    oil["population"]["geography"] = "Blokker innenfor 3 200 fot fra en aktiv eller idle brønn, pluss CalGEM sin HPZ-telling."
    oil["population"]["vintage"] = "Census 2020 og WellSTAR lest 2026-10-28."
    oil["population"]["comparison"] = "CalGEM har ikke publisert et folketall. Tallet under er vår beregning."
    add_claim(
        oil,
        cl(
            "r3-oil-buffer",
            "Egen beregning: 2 977 829 personer og 1 104 614 boligenheter i Census 2020 ligger i blokker der blokkens indre punkt er innenfor 3 200 fot fra minst én brønn med status Active eller Idle. 694 av 10 400 offentlige skoler i NCES EDGE 2023–24 ligger innenfor samme avstand. CalGEM har ikke publisert et slikt tall.",
            "confirmed",
            SETBACK_SRC,
            "83 695 brønner etter API-nummer og 31 479 blokker inngår. Avstanden er ekvirektangulær med 69,172 miles per breddegrad. Internt punkt er ikke det samme som at blokkpolygonet skjærer sirkelen. Private skoler mangler, fordi CDE-filen pubschls.txt ga en omdirigeringsløkke. Pluggede brønner er utelatt. Skriptet er scripts/setback_3200.py.",
        ),
        "population",
    )
    replace_claim(
        oil,
        "r2-oil-demo",
        "Inntekt, fattigdom og utdanning er ikke regnet for folk som faktisk bor innenfor 3 200 fot. Blokkfilen har folketall og boligenheter, ikke ACS-kjennetegn. Et tract-snitt ville tatt med folk som bor lenger unna.",
        "not_found",
        "Det som er regnet, er folketall og boligenheter i blokkene, og PLACES for tractene som inneholder slike blokker.",
        SETBACK_SRC[:2],
    )
    oil["demographics"]["geography"] = "Selve bufferen på 3 200 fot."
    oil["demographics"]["vintage"] = "Census 2020 har ikke disse kjennetegnene på blokk."
    oil["demographics"]["comparison"] = "Ikke laget for bufferen."
    oil["health_outcomes"]["geography"] = "2020-tract som har minst én bebodd blokk innenfor 3 200 fot."
    oil["health_outcomes"]["vintage"] = "CDC PLACES, 2025-utgivelse, estimater for 2023."
    oil["health_outcomes"]["comparison"] = "Befolkningsvektet rå prevalens mot resten av California. Tracten er videre enn bufferen."
    replace_claim(
        oil,
        "r2-oil-health",
        "De 1 488 tractene har 6 422 573 innbyggere i PLACES. Rå prevalens mot resten av California: nåværende astma 9,35 mot 9,52 prosent, KOLS 4,83 mot 5,11, koronar hjertesykdom 5,27 mot 5,46, kreft unntatt hudkreft 6,09 mot 6,34, diagnostisert diabetes 11,70 mot 11,48. Ingen forhold når 1,5.",
        "confirmed",
        CAUS + " CalEnviroScreen er ikke koblet på, fordi den bruker 2010-tract.",
        [PLACES_SRC],
    )
    for item in oil["checked_empty"]:
        if item["field"] == "population_inside_zone":
            item["searched"] = "CalGEM har fortsatt ikke publisert folketall, boliger eller skoler. Vår blokkberegning ligger på kortet og er ikke etatens tall."
    oil["open_questions"] = [
        "CalGEMs egen metode for folk, boliger og skoler i health protection zone, hvis etaten senere publiserer den.",
        "Private skoler innenfor 3 200 fot. CDE-filen lot seg ikke laste ned.",
    ]
    save(oil)

    south = load("ca-problem-south-coast-air")
    add_claim(
        south,
        cl(
            "r3-sc-places",
            "For hele Los Angeles, Orange, Riverside og San Bernardino, som er videre enn luftbassenget, er PLACES-prevalensen ikke høyere enn resten av California. Astma 9,38 mot 9,58 prosent, KOLS 4,89 mot 5,21, koronar hjertesykdom 5,31 mot 5,53, kreft 5,84 mot 6,68, diabetes 12,03 mot 11,09. Folketallet i nevneren er 17 800 562.",
            "confirmed",
            [PLACES_SRC],
            CAUS + " Fylkene rekker utenfor South Coast Air Basin.",
        ),
        "health_outcomes",
    )
    add_claim(
        south,
        cl(
            "r3-sc-ces",
            "CalEnviroScreen 4.0, vektet med ACS 2015–2019-folketall i de samme fire fylkene: astmabesøk 50,2 mot 53,0 per 10 000, uten videregående 20,3 mot 15,5 prosent, språklig isolasjon 11,4 mot 8,3, fattigdomsindikatoren 33,3 mot 29,2. Ingen av disse når 1,5 ganger resten av delstaten.",
            "confirmed",
            [CES_SRC],
            "Fattigdomsindikatoren er OEHHA sin, ikke den offisielle fattigdomsandelen.",
        ),
        "demographics",
    )
    add_claim(
        south,
        cl(
            "r3-sc-cancer",
            "NCI State Cancer Profiles, alle kreftformer, aldersjustert per 100 000, 2019–2023: California 413,0. Los Angeles 388,7, Orange 420,2, Riverside 402,4, San Bernardino 405,6. Ingen av fylkene er i nærheten av 1,5 ganger delstaten.",
            "confirmed",
            [CANCER],
            "Tabellen er NCIs sammenstilling av registerdata, laget 28. oktober 2026. Den er ikke en fil eksportert fra CAL*Explorer.",
        ),
        "health_outcomes",
    )
    save(south)

    sjv = load("ca-problem-san-joaquin-air")
    add_claim(
        sjv,
        cl(
            "r3-sjv-places",
            "I de åtte fylkene San Joaquin, Stanislaus, Merced, Madera, Fresno, Tulare, Kings og Kern er PLACES-prevalensen astma 10,13 mot 9,41 prosent i resten av California, KOLS 6,25 mot 4,92, koronar hjertesykdom 6,17 mot 5,34, kreft 5,80 mot 6,36, diabetes 12,88 mot 11,34. Folketallet er 4 313 036. Ingen forhold når 1,5. Hele Kern er med, også øst for dalen.",
            "confirmed",
            [PLACES_SRC],
            CAUS,
        ),
        "health_outcomes",
    )
    add_claim(
        sjv,
        cl(
            "r3-sjv-ces",
            "CalEnviroScreen 4.0 for de samme åtte fylkene: andel uten videregående 25,6 mot 16,7 prosent, forhold 1,54. Drikkevannsindikatoren er 706 mot 451, forhold 1,57. Astmabesøk er 70,8 mot 49,4 per 10 000, forhold 1,43, og fattigdomsindikatoren 43,3 mot 29,6, forhold 1,46. De to siste når ikke terskelen på 1,5.",
            "confirmed",
            [CES_SRC],
            CAUS + " Drikkevannsindikatoren er ikke listen over failing systems.",
        ),
        "demographics",
    )
    add_claim(
        sjv,
        cl(
            "r3-sjv-vf",
            "CDPH sin årsrapport for 2022: California 7 451 tilfeller og 19,1 per 100 000. Kern 2 407 tilfeller og 264,9, Kings 168 og 111,0, Tulare 312 og 65,7, Fresno 448 og 44,3, Madera 51 og 32,4. Kern, Kings, Tulare, San Luis Obispo, Fresno, Madera og Ventura hadde til sammen 50,5 prosent av tilfellene.",
            "confirmed",
            [VF],
            "Ratene er CDPH sine. De er ikke en årsakskobling til partikler eller sprøytemidler.",
        ),
        "health_outcomes",
    )
    add_claim(
        sjv,
        cl(
            "r3-sjv-cancer",
            "NCI, alle kreftformer, 2019–2023, per 100 000: California 413,0. Fresno 415,4, Kern 410,9, Madera 410,5, San Joaquin 402,6, Stanislaus 432,8, Merced 396,8, Kings 384,3, Tulare 371,8. Fylkesratene ligger rundt eller under delstaten, ikke 1,5 ganger over.",
            "confirmed",
            [CANCER],
            "Aldersjustert til 2000 US standard population. Kilden er NCI, ikke en CSV fra CAL*Explorer.",
        ),
        "health_outcomes",
    )
    save(sjv)

    pest = load("ca-problem-pesticides")
    add_claim(
        pest,
        cl(
            "r3-pest-ces",
            "I Fresno, Kern, Tulare og Monterey, fylkene med flest pund virksomt stoff i 2022, er andelen uten videregående 27,5 mot 16,9 prosent i resten av California, forhold 1,63. Fattigdomsindikatoren er 45,0 mot 30,0, forhold 1,50. Astmabesøk er 66,6 mot 50,6 per 10 000, forhold 1,32.",
            "confirmed",
            [CES_SRC],
            CAUS + " Fylkene er valgt fra DPR sin pundstatistikk, ikke fra et sprøytefelt-polygon.",
        ),
        "demographics",
    )
    add_claim(
        pest,
        cl(
            "r3-pest-places",
            "PLACES i de samme fire fylkene, 2 830 007 innbyggere: astma 10,16 mot 9,44 prosent, KOLS 6,14 mot 4,98, koronar hjertesykdom 6,13 mot 5,37, kreft 5,73 mot 6,35, diabetes 12,99 mot 11,40. Ingen forhold når 1,5.",
            "confirmed",
            [PLACES_SRC],
            CAUS,
        ),
        "health_outcomes",
    )
    add_claim(
        pest,
        cl(
            "r3-pest-pisp",
            "DPR Pesticide Illness Surveillance Program 2022: 709 episoder og 1 041 tilfeller i California. Fresno 33 tilfeller i 24 episoder, der 21 hadde landbruksformål. Kern 50 i 42 episoder, 14 landbruk. Tulare 41 i 26, 12 landbruk. Monterey 14 i 14, 2 landbruk. Kings 20 i 7, 14 landbruk. Los Angeles 143 i 123, 6 landbruk. Santa Barbara 213 i 18 episoder, 199 landbruk.",
            "confirmed",
            [PISP],
            "Vår rate med folketall fra Census 2020 i PLACES-filen: California 2,63 per 100 000, Kings 13,12, Tulare 8,67, Kern 5,50, Fresno 3,27, Monterey 3,19, Los Angeles 1,43, Santa Barbara 47,53. Santa Barbara-raten kommer av få episoder med mange tilfeller. Teller og nevner er ikke samme år.",
        ),
        "health_outcomes",
    )
    save(pest)

    drink = load("ca-problem-drinking-water")
    add_claim(
        drink,
        cl(
            "r3-dw-tracts",
            "En tract-liste for de 390 failing-systemene er ikke lastet ned. Derfor er det ikke laget et befolkningsvektet snitt for tract med failing-system mot resten av California. CalEnviroScreen sin drikkevannsindikator er et annet mål og er ikke brukt som den listen.",
            "not_found",
            [
                src(
                    "https://www.waterboards.ca.gov/drinking_water/certlic/drinkingwater/documents/needs/2025needsassessment.pdf",
                    "2025 Drinking Water Needs Assessment",
                    "State Water Resources Control Board",
                )
            ],
            "Behovsvurderingen gir folketall på systemene. Den gir ikke tract-id.",
        ),
        "demographics",
    )
    save(drink)

    salt = load("ca-problem-salton-sea")
    add_claim(
        salt,
        cl(
            "r3-salt-ces",
            "For hele Imperial County, som er videre enn sjøen og playaen, og som utelater nordbredden i Riverside: uten videregående 30,1 mot 17,6 prosent, forhold 1,71. Språklig isolasjon 24,1 mot 9,6, forhold 2,50. Fattigdomsindikatoren 46,5 mot 31,0, forhold 1,50. Andel hispanic 84,2 mot 38,8. Astmabesøk 86,4 mot 51,6 per 10 000, forhold 1,68.",
            "confirmed",
            [CES_SRC],
            CAUS,
        ),
        "demographics",
    )
    add_claim(
        salt,
        cl(
            "r3-salt-places",
            "PLACES i Imperial County, 179 702 innbyggere: astma 9,41 mot 9,49 prosent, KOLS 5,97 mot 5,06, koronar hjertesykdom 6,80 mot 5,42, kreft 5,04 mot 6,31, diabetes 15,41 mot 11,49. Høyeste forhold er diabetes, 1,34, under terskelen på 1,5.",
            "confirmed",
            [PLACES_SRC],
            CAUS,
        ),
        "health_outcomes",
    )
    add_claim(
        salt,
        cl(
            "r3-salt-vf-cancer",
            "Valley fever 2022: Imperial 20 tilfeller og 11,2 per 100 000, mot 19,1 i California. NCI-kreftinsidens 2019–2023: Imperial 363,6 per 100 000, mot 413,0 i California. Begge ligger under delstaten. PISP 2022: Imperial 15 tilfeller i 11 episoder.",
            "confirmed",
            [VF, CANCER, PISP],
            "Valley fever-raten er CDPH sin. Kreft er NCI. PISP-tilfellene er DPR sine.",
        ),
        "health_outcomes",
    )
    save(salt)

    refin = load("ca-problem-refineries")
    refin["health_outcomes"]["geography"] = "Blokker innenfor 1 engelsk mil fra tre anleggspunkt, og tractene de ligger i."
    refin["health_outcomes"]["vintage"] = "Census 2020, NCES 2023–24 og CDC PLACES 2025-utgivelse."
    refin["health_outcomes"]["comparison"] = "PLACES for tractene mot resten av California. 1 mil er vår radius."
    replace_claim(
        refin,
        "r2-ref-health",
        "Egen beregning innenfor 1 engelsk mil: El Segundo 14 156 personer og 6 456 boligenheter, 4 offentlige skoler. Torrance 8 799 personer, 3 011 boligenheter, 4 skoler. Wilmington 6 731 personer, 1 731 boligenheter, 1 skole. De 19 tractene har PLACES-folketall 67 611. Rå prevalens mot resten av California: astma 8,95 mot 9,49, KOLS 4,15 mot 5,07, koronar hjertesykdom 4,59 mot 5,43, kreft 6,00 mot 6,30, diabetes 10,57 mot 11,51. Ingen forhold når 1,5.",
        "confirmed",
        CAUS + " Anleggstraktene med få beboere er ikke brukt som portrett. Radiusen er valgt her.",
        SETBACK_SRC + [PLACES_SRC],
    )
    save(refin)

    aliso = load("ca-problem-aliso-canyon")
    add_claim(
        aliso,
        cl(
            "r3-aliso-buffer",
            "Egen beregning innenfor 5 engelske mil fra FRS-punktet: 182 758 personer og 64 213 boligenheter i 2020, og 36 offentlige skoler. De 60 tractene har PLACES-folketall 242 127. Rå prevalens mot resten av California: astma 8,96 mot 9,50, KOLS 4,42 mot 5,07, koronar hjertesykdom 4,95 mot 5,43, kreft 6,86 mot 6,30, diabetes 10,69 mot 11,52. Kreftforholdet er 1,09. Ingen når 1,5.",
            "confirmed",
            SETBACK_SRC + [PLACES_SRC],
            CAUS + " 5 mil er vår radius rundt punktet, ikke et evakueringskart.",
        ),
        "health_outcomes",
    )
    add_claim(
        aliso,
        cl(
            "r3-aliso-scope",
            "Assigned Commissioner's Scoping Memo i A.26-01-009, datert 8. juli 2026, setter saken til om lageret skal bli på dagens kapasitet eller settes ned. Søknaden om å øke lageret er holdt utenfor saken. Et vedtak som endrer 68,6 milliarder kubikkfot i D.24-12-076, er ikke funnet.",
            "confirmed",
            [
                src(
                    "https://docs.cpuc.ca.gov/PublishedDocs/Efile/G000/M610/K355/610355447.PDF",
                    "Assigned Commissioner's Scoping Memo and Ruling, A.26-01-009, July 8, 2026",
                    "California Public Utilities Commission",
                )
            ],
            "Notatet siterer anbefalingen om 58,6 milliarder kubikkfot. Det vedtar ikke kuttet. Tidsplanen har statuskonferanse 28. oktober 2026.",
        ),
    )
    save(aliso)

    pfas = load("ca-problem-pfas")
    add_claim(
        pfas,
        cl(
            "r3-pfas-rows",
            "Arbeidsboken List of Sources and Monitoring Frequency, oppdatert 12. oktober 2026, for ordre DW-2025-0002-DDW har 10 701 unike PS-koder og 3 994 vannsystemnavn. 82 rader mangler PS-kode. Det er en annen liste enn anslaget på om lag 3 800 i QAPP.",
            "confirmed",
            [
                src(
                    "https://www.waterboards.ca.gov/drinking_water/certlic/drinkingwater/pfas_ddw_general_order/docs/order-dw-2025-0002-ddw-sources-20261012-update.xlsx",
                    "PFAS General Order DW-2025-0002-DDW sources, October 12, 2026 update",
                    "State Water Resources Control Board",
                )
            ],
            "Rader uten PS-kode er telt for seg. Systemnavn kan være stavet ulikt og er ikke slått sammen.",
        ),
    )
    save(pfas)

    gw = load("ca-problem-groundwater-overdraft")
    add_claim(
        gw,
        cl(
            "r3-gw-counties",
            "De åtte San Joaquin-fylkene, som er et grovt omriss av overtrekksbassengene og som tar med hele Kern, har samme CalEnviroScreen-snitt som på luftkortet: uten videregående 25,6 mot 16,7 prosent, forhold 1,54, og drikkevannsindikator 706 mot 451, forhold 1,57. PLACES-diabetessnittet er 12,88 mot 11,34 prosent.",
            "confirmed",
            [CES_SRC, PLACES_SRC],
            "Fylkesgrensen er ikke bassenggrensen. Tallet er det samme uttrekket som på San Joaquin-luftkortet.",
        ),
        "demographics",
    )
    save(gw)

    wspa = load("org-wspa")
    replace_claim(
        wspa,
        "c1",
        "Vedlegg A i filing 3070933, perioden 1. april til 30. juni 2025, lister blant annet AB 626, 751, 839, 881, 914, 1207, 1243 og 1448, og SB 34, 57, 222, 282, 237, 285, 318, 348, 542, 613, 614, 643, 684, 767 og 840. Teksten nevner CalGEM og setback rule, raffinerilager, cap and trade og CCUS. Den sier ikke om WSPA støttet eller motarbeidet noen sak. SB 1137 står ikke i dette vedlegget.",
        "confirmed",
        "Teksten er feltet TEXT4000 i tabellen TEXT_MEMO_CD for FILING_ID 3070933 og FORM_TYPE F635 i SOS-rådatafilen.",
        [SOS_SRC],
    )
    add_claim(
        wspa,
        cl(
            "r3-wspa-1137",
            "I vedlegg A for filing 3092136, perioden som slutter 30. september 2025, står SB 1137 sammen med blant annet SB 222, 237, 295, 318, 352, 542, 613, 614, 684, 755 og 840. Filing 3114837, som slutter 31. desember 2025, lister SB 237, 238 og 1137. Heller ikke her står det støtte eller motstand.",
            "confirmed",
            [SOS_SRC],
            "Samme tabell TEXT_MEMO_CD, FORM_TYPE F635.",
        ),
    )
    add_claim(
        wspa,
        cl(
            "r3-wspa-sgma",
            "Vedlegg A for 2014 lister SB 1319 i filing 1844606, 1872113, 1911643 og 1931993, for kvartalene som slutter 31. mars, 30. juni, 30. september og 31. desember 2014. SB 1168 og AB 1739 står ikke i de tekstene. Posisjon står ikke.",
            "confirmed",
            [SOS_SRC],
            "SB 1319 i sesjonen 2013–2014 er Pavleys grunnvannslov. Nummersjekken er gjort mot hele TEXT4000, ikke bare utdraget.",
        ),
    )
    wspa["open_questions"] = [
        "Hva som forklarer gapet mellom juli-arkivet av aktivitetssiden og oktobertotalen for sesjonen.",
    ]
    save(wspa)

    chev = load("org-chevron")
    add_claim(
        chev,
        cl(
            "r3-chev-sgma",
            "Vedlegg A i Chevron-filing 1872856, kvartalet som slutter 30. juni 2014, lister AB 1739 og SB 1319. SB 1168 står ikke i teksten. Teksten sier ikke om selskapet støttet eller motarbeidet lovene. Samme tekst tar også opp SB 4 og grunnvannsovervåking.",
            "confirmed",
            [SOS_SRC],
            "TEXT_MEMO_CD, FORM_TYPE F635. AB 1739 og SB 1319 i denne sesjonen er SGMA-lovene.",
        ),
    )
    save(chev)

    crc = load("org-crc")
    add_claim(
        crc,
        cl(
            "r3-aera-sgma",
            "Aera Energy LLC oppga i Form 635, filing 1869215 og 1909234, kvartalene som slutter 30. juni og 30. september 2014, lovene SB 1281, SB 1319 og SB 861. Juni-skjemaet har også SB 1132, SB 1017 og AB 2420. SB 1168 og AB 1739 står ikke i de to tekstene. Posisjon står ikke.",
            "confirmed",
            [SOS_SRC],
            "Teksten ligger i LBY_ACTVTY på CVR_LOBBY_DISCLOSURE_CD, filer-id C27739. Aera er senere fusjonert inn i CRC. Dette er 2014-skjemaet, ikke et CRC-skjema.",
        ),
    )
    save(crc)

    for cid, summary_id, clients in (
        (
            "firm-carpenter-garcia-sievers",
            "s3",
            "BD, Booking Holdings, C&C North America dba Cosentino, California Asphalt Pavement Association, Daikin U.S. Corporation, Hyundai Motor Company, Maximus, Medtronic og U.S. Tire Manufacturers Association",
        ),
        (
            "firm-greenberg-traurig",
            "s3",
            "Aspire Public Schools og Stockdale Capital Partners, LLC",
        ),
        (
            "firm-pillsbury",
            "s3",
            "Recycled Materials Association (REMA)",
        ),
    ):
        firm = load(cid)
        replace_claim(
            firm,
            summary_id,
            f"I SOS-rådata, tabellen LEMP_CD, der firmaet står som underfirma og ikrafttredelse er 2024–2026, er oppdragsgiverne: {clients}. Ingen av navnene er en miljø- eller klimaorganisasjon, så påstand om begge sider er ikke tatt med.",
            "confirmed",
            "Listen er oppdragsgivere som selv har ført firmaet. Den er ikke et bevis for at listen er uttømmende. WSPA-betalingen står på WSPAs skjema, ikke nødvendigvis her.",
            [SOS_SRC],
        )
        save(firm)

    leacox = load("firm-leacox")
    replace_claim(
        leacox,
        "s3",
        "I LEMP_CD er det ingen rad for 2024–2026 der Leacox & Associates eller Leacox California Governmental Advocacy står som underfirma. En klientliste ut over WSPA-betalingen er derfor ikke funnet i det uttrekket.",
        "not_found",
        "Søket er på firmanavn og filer-id 1385058 og 1438830. Fravær i tabellen er ikke det samme som at firmaet ikke har andre klienter.",
        [SOS_SRC],
    )
    save(leacox)

    carpenter = load("firm-carpenter-garcia-sievers")
    for item in carpenter["checked_empty"]:
        if item["field"] == "other_clients":
            item["field"] = "both_sides"
            item["searched"] = "LEMP_CD for 2024–2026 er lest. Oppdragsgiverne som er funnet, er ikke miljøorganisasjoner. Begge sider er ikke dokumentert."
            item["result"] = "not_found"
            item["urls"] = [SOS]
    save(carpenter)

    psx = load("org-phillips66")
    add_claim(
        psx,
        cl(
            "r3-psx-10k",
            "I Form 10-K for året som sluttet 31. desember 2025 skriver Phillips 66 at selskapet i fjerde kvartal 2025 begynte å legge Los Angeles-raffineriet i ro og stanset drivstoffproduksjonen. Full idling skulle etter teksten bli ferdig de neste månedene, og driftstillatelsene skulle beholdes. Et etatsdokument som sier at idlingen var ferdig per 28. oktober 2026, er ikke funnet.",
            "confirmed",
            [
                src(
                    "https://www.sec.gov/Archives/edgar/data/1534701/000153470126000006/psx-20251231.htm",
                    "Phillips 66 Form 10-K for the year ended December 31, 2025",
                    "US Securities and Exchange Commission",
                ),
                src(
                    "https://www.aqmd.gov/docs/default-source/fenceline_monitoring/updated_rule_1180_plans/p66-wilmington-famp_final-revised_2025_12_5.pdf",
                    "Phillips 66 Wilmington fenceline air monitoring plan, revised 2025-12-05",
                    "South Coast Air Quality Management District",
                ),
            ],
            "10-K-en er selskapets egen beskrivelse. SCAQMD-planen sier at anlegget var ventet å starte idling før utgangen av 2025, og at tillatelsene skulle beholdes under omreguleringen.",
        ),
    )
    save(psx)

    sb1319 = load("bill-sb-1319")
    add_claim(
        sb1319,
        cl(
            "r3-sb1319-lobby",
            "WSPA lister SB 1319 i vedlegg A for fire kvartaler i 2014, filing 1844606, 1872113, 1911643 og 1931993. Aera lister den i filing 1869215 og 1909234. Chevron lister den i filing 1872856. Ingen av tekstene sier støtte eller motstand.",
            "confirmed",
            [SOS_SRC],
            "Andre filere, blant dem Groundwater Resources Association of California i filing 1906459, lister også loven. Det er ikke tatt med som en full klientliste.",
        ),
    )
    add_link(sb1319, "organization", "org-wspa", "Oppga SB 1319 i 2014-vedlegg, uten posisjon.")
    add_link(sb1319, "organization", "org-chevron", "Oppga SB 1319 i juni 2014, uten posisjon.")
    add_link(sb1319, "organization", "org-crc", "Aera oppga SB 1319 i to kvartaler i 2014.")
    save(sb1319)

    ab1739 = load("bill-ab-1739")
    add_claim(
        ab1739,
        cl(
            "r3-ab1739-lobby",
            "Chevron lister AB 1739 i vedlegg A til filing 1872856, kvartalet som slutter 30. juni 2014, uten posisjon. WSPA og Aera sine 2014-tekster som er lest, lister ikke AB 1739. Groundwater Resources Association, filing 1906459, og Planning and Conservation League, filing 1909151, lister den sammen med de andre SGMA-lovene.",
            "confirmed",
            [SOS_SRC],
            "Flere byer og vannverk lister også loven. De er ikke tatt inn ett og ett.",
        ),
    )
    add_link(ab1739, "organization", "org-chevron", "Oppga AB 1739 i juni 2014, uten posisjon.")
    save(ab1739)

    sb1168 = load("bill-sb-1168")
    add_claim(
        sb1168,
        cl(
            "r3-sb1168-lobby",
            "SB 1168 står ikke i WSPA-, Chevron- eller Aera-tekstene fra 2014 som er lest. Den står hos andre filere, blant dem Groundwater Resources Association, filing 1906459, og Planning and Conservation League, filing 1909151, uten at teksten sier posisjon.",
            "confirmed",
            [SOS_SRC],
            "Fraværet gjelder de leste vedleggene og aktivitetslinjene, ikke alle mulige vedlegg i sesjonen.",
        ),
    )
    save(sb1168)

    bill = load("bill-sb-1137")
    add_claim(
        bill,
        cl(
            "r3-sb1137-wspa",
            "WSPA lister SB 1137 i vedlegg A for filing 3092136, kvartalet som slutter 30. september 2025, og filing 3114837, kvartalet som slutter 31. desember 2025. Filing 3070933 for andre kvartal 2025 lister den ikke. Ingen av tekstene sier støtte eller motstand.",
            "confirmed",
            [SOS_SRC],
        ),
    )
    for item in bill["checked_empty"]:
        if item["field"] == "lobby_position":
            item["searched"] = "Vedlegg A er lest. SB 1137 er listet i to kvartaler i 2025. Ordene støtte eller motstand står ikke."
            item["urls"] = [SOS]
    add_link(bill, "organization", "org-wspa", "Listet SB 1137 i to kvartaler i 2025, uten posisjon.")
    save(bill)


if __name__ == "__main__":
    main()
