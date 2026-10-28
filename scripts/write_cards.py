#!/usr/bin/env python3
"""Author the first California card set. Re-run only to regenerate data/cards."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "cards"
TRACTS = Path("/tmp/ca/tracts.json")
NOTE = "Wayback-feltet fylles av scripts/archive_sources.py etter at kortet er skrevet."


def src(url: str, title: str, publisher: str, archive_url: str = "", archive_note: str = NOTE) -> dict:
    return {
        "url": url,
        "title": title,
        "publisher": publisher,
        "retrieved": "2026-10-28",
        "archive_url": archive_url,
        "archive_note": archive_note,
    }


def cl(cid: str, text: str, status: str, sources: list, note: str = "") -> dict:
    return {"id": cid, "text": text, "status": status, "note": note, "sources": sources}


def geom(gtype, coords, name, record, url, note) -> dict:
    return {
        "type": gtype,
        "coordinates": coords,
        "source_name": name,
        "source_record_id": record,
        "source_url": url,
        "retrieved": "2026-10-28",
        "note": note,
    }


def link(rel: str, target: str, text: str) -> dict:
    return {"rel": rel, "target_id": target, "text": text}


def empty(field: str, searched: str, urls: list[str] | None = None, result: str = "not_found") -> dict:
    return {
        "field": field,
        "searched": searched,
        "result": result,
        "urls": urls or [],
        "retrieved": "2026-10-28",
    }


def card(**kwargs) -> dict:
    kwargs.setdefault("state", "CA")
    kwargs.setdefault("updated", "2026-10-28")
    kwargs.setdefault("rank", None)
    kwargs.setdefault("org_kind", None)
    kwargs.setdefault("geometry", None)
    kwargs.setdefault("map_features", [])
    kwargs.setdefault("links", [])
    kwargs.setdefault("checked_empty", [])
    kwargs.setdefault("open_questions", [])
    kwargs["schema_version"] = "1.0.0"
    return kwargs


def tract_geom(tracts: dict, tid: str, note: str) -> dict:
    item = tracts[tid]
    return geom(
        item["geometry"]["type"],
        item["geometry"]["coordinates"],
        "OEHHA CalEnviroScreen 4.0",
        tid,
        "https://services1.arcgis.com/PCHfdHz4GlDNAhBb/arcgis/rest/services/CalEnviroScreen_4_0_Results_/FeatureServer/0",
        note,
    )


def main() -> None:
    if "--force" not in sys.argv:
        print("Kortene er allerede skrevet. Kjør med --force bare hvis JSON skal bygges på nytt. Det sletter arkiv-URL-er.")
        return
    tracts = json.loads(TRACTS.read_text())
    ces_url = "https://services1.arcgis.com/PCHfdHz4GlDNAhBb/arcgis/rest/services/CalEnviroScreen_4_0_Results_/FeatureServer/0/query?where=tract%3D6019001100&outFields=tract,CIscore,CIscoreP,ACS2019TotalPop,pm,drink,pest&returnGeometry=true&outSR=4326&f=geojson"
    oehha = src(
        "https://oehha.ca.gov/calenviroscreen/report/calenviroscreen-40",
        "CalEnviroScreen 4.0",
        "OEHHA",
    )
    ces_src = src(ces_url, "CalEnviroScreen 4.0 FeatureServer, utvalgte trakter", "OEHHA")
    green = src(
        "https://www3.epa.gov/airquality/greenbook/rncl2.html",
        "PM-2.5 nonattainment areas, Green Book, data current as of September 30, 2026",
        "US EPA",
    )
    ozone_fail = src(
        "https://www.federalregister.gov/documents/2025/09/25/2025-18636/finding-of-failure-to-attain-the-1997-8-hour-ozone-standards-california-san-joaquin-valley",
        "Finding of Failure To Attain the 1997 8-Hour Ozone Standards; San Joaquin Valley",
        "US EPA",
    )
    pm_ext = src(
        "https://www.federalregister.gov/documents/2026/06/11/2026-11735/attainment-date-extension-for-the-san-joaquin-valley-california-2012-annual-pm25-fine-particulate",
        "Attainment Date Extension for the San Joaquin Valley 2012 Annual PM2.5 Area",
        "US EPA",
    )
    aqmd = src(
        "https://www.aqmd.gov/docs/default-source/default-document-library/sc-contingency-measures-finalcb7e02f0c2b66f27bf6fff02004a91a9.pdf",
        "South Coast Air Basin Contingency Measure SIP Revision for the 2015 8-Hour Ozone NAAQS",
        "South Coast AQMD",
    )
    needs = src(
        "https://www.waterboards.ca.gov/drinking_water/certlic/drinkingwater/documents/needs/2025needsassessment.pdf",
        "2025 Drinking Water Needs Assessment",
        "State Water Resources Control Board",
    )
    harter = src(
        "https://groundwaternitrate.ucdavis.edu/files/138958.pdf",
        "Addressing Nitrate in California's Drinking Water (2012)",
        "UC Davis for the State Water Board",
    )
    calgem = src(
        "https://www.conservation.ca.gov/calgem/Documents/State%20Oil%20and%20Gas%20Supervisor%20Annual%20Report%202023.pdf",
        "Annual Report of the State Oil and Gas Supervisor 2023",
        "CalGEM",
    )
    sb1137 = src(
        "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202120220SB1137",
        "SB 1137, Chapter 365, Statutes of 2022",
        "California Legislative Counsel",
    )
    sb1137_hist = src(
        "https://leginfo.legislature.ca.gov/faces/billHistoryClient.xhtml?bill_id=202120220SB1137",
        "SB 1137 bill history",
        "California Legislative Counsel",
    )
    sb1137_votes = src(
        "https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202120220SB1137",
        "SB 1137 bill votes",
        "California Legislative Counsel",
    )
    isor = src(
        "https://www.conservation.ca.gov/calgem/Documents/SB%201137%20Initial%20Statement%20of%20Reasons.pdf",
        "SB 1137 Initial Statement of Reasons",
        "CalGEM",
    )
    sb1137_page = src(
        "https://www.conservation.ca.gov/calgem/Pages/SB1137.aspx",
        "Understanding California's Oil and Gas Safety Zones: Senate Bill 1137",
        "CalGEM",
    )
    lobby_search = src(
        "https://dbsearch.sos.ca.gov/LobbyIntSearch.aspx",
        "Cal-Access Lobbyist Employer Category Search, sesjon 2025-2026, database oppdatert 28-OCT-2026 08:15:07",
        "California Secretary of State",
    )
    contrib_search = src(
        "https://dbsearch.sos.ca.gov/ContributorSearch.aspx",
        "Cal-Access Contributor Search, 01/01/2025-10/28/2026, California, database oppdatert 28-OCT-2026 08:15:07",
        "California Secretary of State",
    )
    wspa_page = src(
        "https://cal-access.sos.ca.gov/Lobbying/Employers/Detail.aspx?id=1147195&session=2025&view=activity",
        "Cal-Access employer 1147195, Western States Petroleum Association, activity",
        "California Secretary of State",
        archive_url="https://web.archive.org/web/20260703125215/https://cal-access.sos.ca.gov/Lobbying/Employers/Detail.aspx?view=activity&id=1147195&session=2025",
        archive_note="Wayback-øyeblikksbilde 2026-07-03 av aktivitetssiden.",
    )
    wspa_pdf = src(
        "https://cal-access.sos.ca.gov/PDFGen/pdfgen.prg?amendid=0&filingid=3070933",
        "Form 635 filing 3070933, Western States Petroleum Association, 2025-04-01 til 2025-06-30",
        "California Secretary of State",
    )
    crc_10k = src(
        "https://www.sec.gov/Archives/edgar/data/1609253/000160925324000043/crc-20231231.htm",
        "California Resources Corporation Form 10-K for the year ended December 31, 2023",
        "SEC",
    )
    sb200 = src(
        "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201920200SB200",
        "SB 200, Chapter 120, Statutes of 2019",
        "California Legislative Counsel",
    )
    sb200_hist = src(
        "https://leginfo.legislature.ca.gov/faces/billHistoryClient.xhtml?bill_id=201920200SB200",
        "SB 200 bill history",
        "California Legislative Counsel",
    )
    safer_hist = src(
        "https://www.waterboards.ca.gov/safer/docs/safer_program_legislative_history.pdf",
        "SAFER Program Legislative History",
        "State Water Resources Control Board",
    )
    ab617 = src(
        "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=201720180AB617",
        "AB 617, Chapter 136, Statutes of 2017",
        "California Legislative Counsel",
    )
    ab617_votes = src(
        "https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201720180AB617",
        "AB 617 bill votes",
        "California Legislative Counsel",
    )
    ab1647 = src(
        "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=201720180AB1647",
        "AB 1647, Chapter 589, Statutes of 2017",
        "California Legislative Counsel",
    )
    ab1647_hist = src(
        "https://leginfo.legislature.ca.gov/faces/billHistoryClient.xhtml?bill_id=201720180AB1647",
        "AB 1647 bill history",
        "California Legislative Counsel",
    )
    dpr = src(
        "https://www.cdpr.ca.gov/wp-content/uploads/2024/12/pur_2022_data_summary.pdf",
        "Pesticide Use Annual Report 2022 Data Summary",
        "California Department of Pesticide Regulation",
    )
    dpr_county = src(
        "https://www.cdpr.ca.gov/wp-content/uploads/2024/12/2022_county_total_pounds_applied_agricultural_applications_and_acres_treated.pdf",
        "Total Pounds, Applications, and Acres Treated by County, 2022",
        "California Department of Pesticide Regulation",
    )
    iid = src(
        "https://saltonseaprogram.com/documents/Salton_Sea_Air_Quality_Mitigation_Program.pdf",
        "Salton Sea Air Quality Mitigation Program",
        "Imperial Irrigation District",
    )
    ssmp = src(
        "https://saltonsea.ca.gov/wp-content/uploads/2025/03/SSMP-2025-Annual-Report_Mar-28.pdf",
        "2025 Annual Report on the Salton Sea Management Program",
        "California Natural Resources Agency",
    )
    aliso_pdf = src(
        "https://ww2.arb.ca.gov/sites/default/files/2020-07/aliso_canyon_methane_emissions-arb_final.pdf",
        "Determination of Total Methane Emissions from the Aliso Canyon Natural Gas Leak Incident, 21. oktober 2016",
        "California Air Resources Board",
    )
    aliso_news = src(
        "https://ww2.arb.ca.gov/news/aliso-canyon-leak-emitted-109000-metric-tons-methane",
        "Aliso Canyon leak emitted 109,000 metric tons of methane",
        "California Air Resources Board",
    )
    pfas_qapp = src(
        "https://www.waterboards.ca.gov/water_issues/programs/pfas/docs/CA_QAPP_PFAS_Final_09172024.pdf",
        "PFAS QAPP, General Order DW-2024-0002-DDW, September 2024",
        "State Water Resources Control Board",
    )
    pfas_page = src(
        "https://www.waterboards.ca.gov/pfas/drinking_water.html",
        "PFAS Drinking Water",
        "State Water Resources Control Board",
    )
    pfas_slides = src(
        "https://biomonitoring.ca.gov/sites/default/files/downloads/Linck_032525.pdf",
        "PFAS DAC Community Water System Sampling Project, March 2025",
        "California Water Boards / CDPH Biomonitoring",
    )
    dwr = src(
        "https://water.ca.gov/programs/groundwater-management/bulletin-118/critically-overdrafted-basins",
        "Critically Overdrafted Basins",
        "California Department of Water Resources",
    )
    dwr_pdf = src(
        "https://water.ca.gov/-/media/DWR-Website/Web-Pages/Programs/Groundwater-Management/Bulletin-118/Critically-Overdrafted-Basins/Files/COD-Basins.pdf",
        "California's Critically Overdrafted Groundwater Basins",
        "California Department of Water Resources",
    )
    echo = src(
        "https://echodata.epa.gov/echo/echo_rest_services.get_facility_info?p_frs=110002899908&output=JSON",
        "ECHO facility info, registry 110002899908",
        "US EPA",
    )
    frs_chevron = src(
        "https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?facility_name=CHEVRON%20EL%20SEGUNDO%20REFINERY&state_abbr=CA&output=JSON",
        "FRS facility CHEVRON EL SEGUNDO REFINERY",
        "US EPA",
    )
    frs_torrance = src(
        "https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?facility_name=TORRANCE%20REFINERY&state_abbr=CA&output=JSON",
        "FRS facility TORRANCE REFINING COMPANY LLC",
        "US EPA",
    )
    frs_phillips = src(
        "https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?facility_name=PHILLIPS%2066%20WILMINGTON&state_abbr=CA&output=JSON",
        "FRS facility PHILLIPS 66 COMPANY WILMINGTON PLANT",
        "US EPA",
    )
    frs_aliso = src(
        "https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?facility_name=SOUTHERN%20CALIFORNIA%20GAS%20ALISO&state_abbr=CA&output=JSON",
        "FRS facility SOUTHERN CALIFORNIA GAS COMPANY - ALISO CANYON",
        "US EPA",
    )
    frs_valero = src(
        "https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?facility_name=VALERO%20REFINING&state_abbr=CA&output=JSON",
        "FRS facility BENICIA VALERO REFINERY",
        "US EPA",
    )
    flux = src(
        "https://www.aqmd.gov/docs/default-source/fenceline_monitoring/project_1/fluxsense_scaqmd2015_project1_finalreport(040717).pdf",
        "Emission Measurements from the Refineries in the South Coast Air Basin, 2015 campaign",
        "South Coast AQMD",
    )
    gonzalez = src(
        "https://www.senate.ca.gov/senators/33",
        "District 33 Details, Lena A. Gonzalez",
        "California State Senate",
    )
    gonzalez_dist = src(
        "https://sd33.senate.ca.gov/district",
        "Senate District 33",
        "Office of Senator Lena A. Gonzalez",
    )
    tijuana = src(
        "https://www.epa.gov/sustainable-water-infrastructure/usmca-tijuana-river-watershed",
        "USMCA Tijuana River Watershed",
        "US EPA",
    )
    wildfire = src(
        "https://ww2.arb.ca.gov/wildfire-emissions",
        "California Wildfire Emissions Estimates",
        "California Air Resources Board",
    )
    wildfire_2020 = src(
        "https://ww2.arb.ca.gov/sites/default/files/2021-07/Wildfire%20Emission%20Estimates%20for%202020%20_Final.pdf",
        "Wildfire Emission Estimates for 2020",
        "California Air Resources Board",
    )

    fresno_high = tract_geom(
        tracts,
        "6019001100",
        "Polygonet er census tract 6019001100 slik det er levert av OEHHA sitt CalEnviroScreen 4.0-tjenestelag. Det er traketen med høyest samlet score i uttrekket, ikke grensen for hele San Joaquin Valley.",
    )
    la_tract = tract_geom(
        tracts,
        "6037204920",
        "Polygonet er census tract 6037204920 i Los Angeles County fra CalEnviroScreen 4.0. Det er ett høyt belastet område i South Coast, ikke grensen for luftbassenget.",
    )
    pest_tract = tract_geom(
        tracts,
        "6019001000",
        "Polygonet er census tract 6019001000 fra CalEnviroScreen 4.0. Trakten brukes som eksempel på høy pesticidindikator i Fresno County, ikke som kart over all bruk.",
    )
    drink_tract = tract_geom(
        tracts,
        "6019001500",
        "Polygonet er census tract 6019001500 fra CalEnviroScreen 4.0. Det viser indikatoren for drikkevannsforurensning, ikke et navngitt vannverk på Failing-listen.",
    )
    imperial = tract_geom(
        tracts,
        "6025012100",
        "Polygonet er census tract 6025012100 i Imperial County fra CalEnviroScreen 4.0. Det er ikke strandlinjen til Salton Sea.",
    )
    kern_tract = tract_geom(
        tracts,
        "6029006201",
        "Polygonet er census tract 6029006201 i Kern County fra CalEnviroScreen 4.0. Det ligger i et fylke med et kritisk overtrukket delbasseng, men kortet påstår ikke at trakten er identisk med basseng 5-022.14.",
    )
    chevron_pt = geom(
        "Point",
        [-118.41873, 33.916216],
        "US EPA FRS",
        "110002899908",
        frs_chevron["url"],
        "Punktet er Latitude83/Longitude83 for CHEVRON EL SEGUNDO REFINERY, registry id 110002899908, 324 W El Segundo Blvd.",
    )
    torrance_pt = geom(
        "Point",
        [-118.33691, 33.85497],
        "US EPA FRS",
        "110070241046",
        frs_torrance["url"],
        "Punktet er Latitude83/Longitude83 for TORRANCE REFINING COMPANY LLC, registry id 110070241046, 3700 W 190th St.",
    )
    phillips_pt = geom(
        "Point",
        [-118.27645, 33.76336],
        "US EPA FRS",
        "110000476235",
        frs_phillips["url"],
        "Punktet er Latitude83/Longitude83 for PHILLIPS 66 COMPANY WILMINGTON PLANT, registry id 110000476235, 1660 W Anaheim Street.",
    )
    aliso_pt = geom(
        "Point",
        [-118.55124, 34.30757],
        "US EPA FRS",
        "110001158238",
        frs_aliso["url"],
        "Punktet er Latitude83/Longitude83 for SOUTHERN CALIFORNIA GAS COMPANY - ALISO CANYON, registry id 110001158238, 12801 Tampa Ave, Porter Ranch.",
    )
    valero_pt = geom(
        "Point",
        [-122.14456, 38.07417],
        "US EPA FRS",
        "110071102220",
        frs_valero["url"],
        "Punktet er Latitude83/Longitude83 for BENICIA VALERO REFINERY, registry id 110071102220. Adressefeltet i samme treff er ikke en gateadresse.",
    )

    cards = []

    cards.append(card(
        id="ca-problem-south-coast-air",
        type="problem",
        name="Ozon og PM2.5 i South Coast Air Basin",
        rank=1,
        summary=[
            cl("s1", "EPA fører Los Angeles-South Coast Air Basin som Serious nonattainment for PM2.5-standarden fra 2012, med 2010-befolkning 15 716 242 i fire fylker og årsdesignverdi 13,2 for 2023-2025.", "confirmed", [green]),
            cl("s2", "South Coast AQMD skriver at bassenget er i extreme nonattainment for 8-timers ozonstandarden fra 2015, og at 2022-planen legger opp til å nå standarden i 2037.", "confirmed", [aqmd]),
            cl("s3", "I 2018-regnskapet som AQMD bruker i 2025-dokumentet, sto vegtrafikk for 44 prosent av NOx, tunge lastebiler for 27 prosent av all NOx, og stasjonære kilder for 15 prosent.", "confirmed", [aqmd]),
            cl("s4", "Census tract 6037204920 i Los Angeles County har CalEnviroScreen 4.0-score 82,39 og persentil 99,97, med ACS 2015-2019-befolkning 2 751. Det er ett høyt belastet område, ikke hele bassenget.", "confirmed", [ces_src, oehha]),
        ],
        claims=[
            cl("c1", "Samme Green Book-tabell fører området som Serious for døgnstandarden for PM2.5 fra 2006, med 24-timers designverdi 38.", "confirmed", [green]),
            cl("c2", "AQMD skriver at NOx i 2018 kom mest fra mobile kilder, og at de største stasjonære NOx-kildene var brensel i boliger og næringsbygg, deretter petroleumsraffinering.", "confirmed", [aqmd]),
            cl("c3", "Rangeringen setter dette først fordi det er den største befolkningen i utvalget som en føderal primærkilde knytter til et område som fortsatt ikke oppfyller en helsebasert luftstandard.", "confirmed", [green], "Redaksjonell bruk av EPAs befolkningstall. Designverdien er lavere enn i San Joaquin Valley."),
        ],
        geometry=la_tract,
        map_features=[{"layer": "problem", "name": "Census tract 6037204920", "geometry": la_tract}],
        links=[
            link("organization", "org-chevron", "Chevron El Segundo-raffineriet ligger i bassenget."),
            link("organization", "org-scaqmd", "South Coast AQMD lager luftplanen."),
            link("organization", "org-carb", "CARB regulerer mobile kilder."),
            link("bill", "bill-ab-617", "AB 617 om samfunnsovervåking og gjerdemåling."),
            link("bill", "bill-ab-1647", "AB 1647 om måling ved raffinerier."),
            link("problem", "ca-problem-refineries", "Raffinerier er skilt ut som eget punkt fordi eksponeringen ved gjerdet ikke er det samme som regional ozon."),
        ],
        checked_empty=[
            empty("campaign_contributions", "Bidrag er søkt på selskapsnavn, ikke på luftbassenget som giver. Se org-chevron.", ["https://dbsearch.sos.ca.gov/ContributorSearch.aspx"]),
        ],
        open_questions=[
            "Offisiell polygon for South Coast-nonattainmentområdet er ikke lastet ned. Trakten er et eksempel, ikke områdegrensen.",
            "Hvor stor del av 2018-NOx som kom fra hvert navngitt raffineri, står ikke i sammendraget som er lest.",
        ],
    ))

    cards.append(card(
        id="ca-problem-san-joaquin-air",
        type="problem",
        name="Ozon og PM2.5 i San Joaquin Valley",
        rank=2,
        summary=[
            cl("s1", "EPA fører San Joaquin Valley som Serious nonattainment for PM2.5-standarden fra 2012, med 2010-befolkning 3 842 165 i åtte fylker og årsdesignverdi 13,7 for 2023-2025. Det er høyere enn South Coast sin 13,2 i samme tabell.", "confirmed", [green]),
            cl("s2", "EPA skrev i 2026 at dalen har de høyeste årlige PM2.5-nivåene i landet, og at området er over 23 000 square miles i åtte fylker, med om lag fire millioner innbyggere og landets ledende jordbruksregion.", "confirmed", [pm_ext], "Fire millioner er EPAs ordlyd i kunngjøringen. Green Book bruker 3 842 165 fra 2010. Begge tallene står, de er ikke regnet om."),
            cl("s3", "EPA fastslo at San Joaquin Valley ikke nådde 1997-ozonstandarden innen fristen 15. juni 2024 for et Extreme-område. Vedtaket trådte i kraft 27. oktober 2025.", "confirmed", [ozone_fail]),
            cl("s4", "Census tract 6019001100 har den høyeste CalEnviroScreen 4.0-scoren i uttrekket, 93,18 og persentil 100, med 2 780 innbyggere i ACS 2015-2019 og PM2.5-indikator 13,91.", "confirmed", [ces_src, oehha]),
        ],
        claims=[
            cl("c1", "EPA skriver at San Joaquin Valley Unified Air Pollution Control District har hovedansvaret for planene etter delstatslov, og at ansvaret er delt: distriktet vurderer stasjonære kilder og arealkilder, mens CARB vurderer mobile kilder.", "confirmed", [pm_ext]),
            cl("c2", "Distriktet vedtok 2024-planen for 2012-PM2.5-standarden 20. juni 2024, og CARB vedtok den 25. juli 2024. Planen ber om å flytte Serious-fristen fra 31. desember 2025 til 31. desember 2030.", "confirmed", [pm_ext]),
            cl("c3", "Green Book fører også dalen som Serious for PM2.5-standardene fra 1997 og 2006, med 24-timers designverdi 42.", "confirmed", [green]),
            cl("c4", "Problemet rangeres som nummer to: færre mennesker enn i South Coast, men høyere årsdesignverdi og en EPA-formulering om landets høyeste årlige PM2.5.", "confirmed", [green, pm_ext]),
        ],
        geometry=fresno_high,
        map_features=[{"layer": "problem", "name": "Census tract 6019001100", "geometry": fresno_high}],
        links=[
            link("organization", "org-sjvapcd", "Luftkvalitetsdistriktet i dalen."),
            link("organization", "org-carb", "CARB har de mobile kildene."),
            link("organization", "org-crc", "California Resources rapporterer mesteparten av produksjonen sin i San Joaquin-bassenget."),
            link("organization", "org-chevron", "Chevron betalte den største olje- og gassvurderingen til CalGEM i 2023."),
            link("bill", "bill-ab-617", "AB 617 gjelder også samfunn med høy samlet belastning."),
            link("problem", "ca-problem-pesticides", "Samme jordbruksfylker har høy rapportert pesticidbruk."),
            link("problem", "ca-problem-drinking-water", "Nitratrapporten dekker Tulare Lake Basin, som overlapper dalen."),
        ],
        checked_empty=[
            empty("geometry_boundary", "EPA Green Book GIS-fil for selve nonattainment-polygonet er ikke lastet ned. Trakten er et eksempel inne i området.", ["https://www3.epa.gov/airquality/greenbook/rncl2.html"]),
        ],
        open_questions=[
            "Hvilke enkeltkilder som står for mest PM2.5 og NOx i 2024-planen, er ikke trukket ut av vedleggene i denne runden.",
            "Koblingen fra et navngitt meieri eller et navngitt oljefelt til et bestemt overskridelsesdøgn er ikke dokumentert her.",
        ],
    ))

    cards.append(card(
        id="ca-problem-drinking-water",
        type="problem",
        name="Drikkevannssystemer som ikke oppfyller standard",
        rank=3,
        summary=[
            cl("s1", "I 2025 Needs Assessment, med tall per 31. desember 2024, var 390 offentlige vannsystemer på Failing-listen. De betjente 811 964 mennesker.", "confirmed", [needs]),
            cl("s2", "Samme rapport sier at om lag 79 prosent av systemene på Failing-listen betjener disadvantaged communities, og 52 prosent betjener samfunn der flertallet er people of color.", "confirmed", [needs]),
            cl("s3", "De forurensningene som i 2024 bidro til flest systemer på Failing-listen for primære grenseverdier, var arsen, 1,2,3-triklorpropan og nitrat eller nitrat pluss nitritt. Det var de samme som i 2023.", "confirmed", [needs]),
            cl("s4", "Rapporten sier også at 98 prosent av befolkningen i 2024 fikk vann fra systemer som oppfylte drikkevannsstandardene, og at 589 systemer var at-risk og betjente 1 490 776 mennesker.", "confirmed", [needs]),
        ],
        claims=[
            cl("c1", "UC Davis-rapporten fra 2012, skrevet for State Water Board etter SB X2 1, anslo at om lag 254 000 mennesker i Tulare Lake Basin og Salinas Valley da var i risiko for nitrat i drikkevannet. 220 000 var på offentlige eller state small-systemer, og 34 000 på private brønner.", "confirmed", [harter], "Tallet er fra 2012-studien, ikke fra Failing-listen i 2024."),
            cl("c2", "Samme rapport sier at kunstgjødsel og husdyrgjødsel på dyrket mark er de klart største regionale kildene til nitrat i grunnvannet, og at grenseverdien er 45 milligram per liter som nitrat.", "confirmed", [harter]),
            cl("c3", "Census tract 6019001500 har drikkevannsindikator 1 022,76 og persentil 99,64 i CalEnviroScreen 4.0. Det er ikke et navngitt vannverk.", "confirmed", [ces_src]),
            cl("c4", "SB 200 (Monning, kapittel 120, 2019) opprettet Safe and Affordable Drinking Water Fund. Senatet samtykket 8. juli 2019 med 38 mot 1. Forsamlingen vedtok hasteklausulen 5. juli 2019 med 68 mot 0.", "confirmed", [sb200, sb200_hist]),
            cl("c5", "State Water Board skriver i sitt lovhistorikknotat at fondet årlig får fem prosent av Greenhouse Gas Reduction Fund, oppad begrenset til 130 millioner dollar, til 30. juni 2030.", "confirmed", [safer_hist], "Beløpet er hentet fra styrets sammendrag av loven, ikke gjengitt fra selve lovparagrafen i denne runden."),
        ],
        geometry=drink_tract,
        map_features=[{"layer": "problem", "name": "Census tract 6019001500", "geometry": drink_tract}],
        links=[
            link("organization", "org-swrcb", "State Water Board fører Failing-listen og SAFER."),
            link("bill", "bill-sb-200", "SB 200 og drikkevannsfondet."),
            link("lawmaker", "lawmaker-bill-monning", "Monning er oppført som forfatter på lovteksten."),
            link("organization", "org-farm-bureau", "California Farm Bureau Federation er en jordbruksorganisasjon med lobbyutgifter og kampanjebidrag i Cal-Access."),
            link("problem", "ca-problem-groundwater-overdraft", "Uttak av grunnvann henger sammen med brønner og forurensning, men er et eget vedtak hos DWR."),
        ],
        checked_empty=[
            empty("named_failing_system_geometry", "Needs Assessment nevner enkeltsystemer som Halcyon og Hillcrest, men ingen koordinat fra SDWIS er hentet for dem.", ["https://www.waterboards.ca.gov/drinking_water/certlic/drinkingwater/documents/needs/2025needsassessment.pdf"]),
            empty("fertilizer_company_sales", "Ingen primærkilde er hentet som knytter et navngitt gjødselselskaps salg til nitrat i en navngitt brønn.", []),
        ],
        open_questions=[
            "Hvilke vannverk på dagens Failing-liste som har åpent arsen- eller nitratbrudd, med PWSID og koordinat, er ikke trukket ut av SAFER-dashbordet.",
            "Mottakerne av kampanjebidragene fra Farm Bureau-pakkene er ikke åpnet post for post.",
        ],
    ))

    cards.append(card(
        id="ca-problem-oil-gas-proximity",
        type="problem",
        name="Olje og gass nær sensitive reseptorer",
        rank=4,
        summary=[
            cl("s1", "SB 1137, kapittel 365 av 2022, definerer en health protection zone som området innenfor 3 200 fot fra en sensitive receptor, og lovens funn sier at nærhet til utvinning gir helserisiko, særlig fra luftforurensning, og at belastningen uforholdsmessig treffer Black, indigenous and people of color.", "confirmed", [sb1137]),
            cl("s2", "Lovteksten sier at studier har vist skade ved avstander under om lag én kilometer, omtrent 3 200 fot. Den inneholder ikke et folketall.", "confirmed", [sb1137]),
            cl("s3", "CalGEM rapporterer at Kern County produserte 89 661 583 fat olje og kondensat i 2023, og Los Angeles County 8 674 995 fat. Chevron U.S.A. Inc. betalte 20 764 561,84 dollar i vurderinger det året, Aera Energy LLC 17 168 596,04 dollar.", "confirmed", [calgem], "Betalingene er assessment payments i årsrapporten, ikke fat og ikke lobbyutgifter."),
            cl("s4", "CalGEM skriver at loven ble stanset da et referendum kvalifiserte seg i februar 2023, og at den fikk virkning igjen da forslagsstillerne trakk forslaget i juni 2024. Etatssiden sier at loven var fullt iverksatt 28. juni 2024.", "confirmed", [isor, sb1137_page]),
        ],
        claims=[
            cl("c1", "Senatet samtykket i forsamlingens endringer 31. august 2022 med 25 mot 10. Forsamlingen vedtok lovforslaget 30. august 2022 med 46 mot 24. Guvernøren godkjente det 16. september 2022.", "confirmed", [sb1137_hist, sb1137_votes]),
            cl("c2", "Forfattere på statussiden er Gonzalez og Limón i senatet.", "confirmed", [src("https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202120220SB1137", "SB 1137 status", "California Legislative Counsel")]),
            cl("c3", "I Cal-Access, sesjon 2025-2026 og oppdatert 28. oktober 2026 kl. 08:15:07, er de største lobbybetalingene i kategorien oil and gas Chevron U.S.A., Inc. and Affiliates med 19 279 518,27 dollar (filer 1146815) og Western States Petroleum Association med 19 031 326,51 dollar (filer 1147195).", "confirmed", [lobby_search]),
            cl("c4", "Et søk på navnet AERA i samme lobbyregister og sesjon ga ingen treff.", "not_found", [lobby_search], "Søket var filernavn som inneholder AERA, alle kvartaler, sesjon 2025-2026."),
            cl("c5", "Problemet står som nummer fire fordi loven selv oppretter en helsesone og produksjonen er stor og geografisk konsentrert, mens et primært folketall inne i sonen ikke er hentet. Derfor rangeres det bak de tre problemene der en etat har telt mennesker under en brutt standard.", "confirmed", [sb1137, green, needs]),
        ],
        geometry=None,
        map_features=[],
        links=[
            link("bill", "bill-sb-1137", "Loven om health protection zones."),
            link("lawmaker", "lawmaker-lena-gonzalez", "Gonzalez er hovedforfatter."),
            link("organization", "org-calgem", "CalGEM fører brønner og vurderinger."),
            link("organization", "org-chevron", "Største vurderingsbetaling i 2023 og størst lobbybetaling i olje og gass."),
            link("organization", "org-crc", "Selskapet beskriver seg som operatør i San Joaquin og Los Angeles."),
            link("organization", "org-wspa", "Bransjeforeningen med nesten like stor lobbybetaling som Chevron."),
            link("organization", "org-cipa", "California Independent Petroleum Association."),
            link("organization", "org-berry", "Berry Corporation i samme lobbykategori."),
            link("lobbying_firm", "firm-carpenter-garcia-sievers", "Firmaet fikk betalt av WSPA i andre kvartal 2025."),
        ],
        checked_empty=[
            empty("geometry", "Ingen CalGEM-brønn med API-nummer og koordinat er hentet. Et folketall innenfor 3 200 fot finnes i et faktaark fra et senator-kontor og i en analyse som ikke er en etatsstatistikk. De er ikke brukt som bekreftet tall.", ["https://www.conservation.ca.gov/calgem/Pages/WellFinder.aspx"]),
            empty("population_inside_zone", "Lovteksten og CalGEM-årsrapporten er lest. De oppgir ikke hvor mange mennesker som bor innenfor 3 200 fot.", ["https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202120220SB1137"]),
        ],
        open_questions=[
            "Hvor mange aktive og idle brønner CalGEM selv teller innenfor health protection zones, og hvor mange mennesker som bor der, etter etatens egen metode.",
            "Om Aera fortsatt finnes som eget selskap etter fusjonsavtalen CRC beskrev i 10-K for 2023, og hvilket filernavn som i så fall brukes i Cal-Access.",
            "Hvem som mottok kampanjebidragene som står på Chevron- og CRC-navnestrengene.",
        ],
    ))

    cards.append(card(
        id="ca-problem-pesticides",
        type="problem",
        name="Plantevernmidler i jordbruksfylker",
        rank=5,
        summary=[
            cl("s1", "DPR rapporterer at det i 2022 ble brukt 181 millioner pund aktive stoffer i California, og at 92 millioner acre ble behandlet. Begge tallene var lavere enn i 2021.", "confirmed", [dpr]),
            cl("s2", "Fylkestallene for 2022 viser 26 468 541 pund i Fresno, 25 835 076 pund i Kern og 17 537 932 pund i Tulare. Monterey hadde 9 187 117 pund.", "confirmed", [dpr_county]),
            cl("s3", "DPR grupperer blant annet kreftfremkallende stoffer, fumiganter, grunnvannsforurensere og giftige luftforurensere som egne brukskategorier, og publiserer endring fra 2021 til 2022 for hver kategori.", "confirmed", [dpr]),
            cl("s4", "Census tract 6019001000 i Fresno County har pesticidindikator 1 321,97 og persentil 90,83 i CalEnviroScreen 4.0, og 4 255 innbyggere i ACS 2015-2019.", "confirmed", [ces_src]),
        ],
        claims=[
            cl("c1", "California Farm Bureau Federation, filer 1146790, har 1 436 711,70 dollar i lobbybetalinger i sesjonen 2025-2026 ifølge Cal-Access per 28. oktober 2026. Western Growers, filer 1146857, har 1 196 763,69 dollar. Corteva Agriscience LLC, filer 1146862, har 141 149,88 dollar.", "confirmed", [lobby_search], "Tallene er lobbybetalinger, ikke pund sprøytet middel."),
            cl("c2", "I bidragsregisteret, samme datofilter, er den største enkeltstrengen for Farm Bureau «CALIFORNIA FARM BUREAU FEDERATION FUND TO PROTECT THE FAMILY FARM (FARM PAC), SACRAMENTO, CA 95833» med 116 700,00 dollar. Søket ga 11 navnestrenger. De er ikke summert, fordi like organisasjoner kan være splittet på flere strenger.", "confirmed", [contrib_search]),
            cl("c3", "Problemet rangeres etter de fire der en etat har telt mennesker under en brutt standard eller der lovgiver har vedtatt en helsesone. Pundtallene er store, men DPR-sammendraget som er lest, oppgir ikke hvor mange mennesker som ble eksponert.", "confirmed", [dpr, needs, sb1137]),
        ],
        geometry=pest_tract,
        map_features=[{"layer": "problem", "name": "Census tract 6019001000", "geometry": pest_tract}],
        links=[
            link("organization", "org-dpr", "DPR publiserer bruksrapportene."),
            link("organization", "org-farm-bureau", "Farm Bureau, lobby og bidrag."),
            link("organization", "org-western-growers", "Western Growers, lobby."),
            link("organization", "org-corteva", "Corteva er registrert som lobbyemployer. Kobling til fylkenes pundtall er ikke vist."),
            link("organization", "org-oehha", "CalEnviroScreen har pesticidindikatoren."),
            link("problem", "ca-problem-san-joaquin-air", "Samme fylker har også ozon og PM2.5-brudd."),
        ],
        checked_empty=[
            empty("product_to_pound", "Ingen DPR-rad er åpnet som viser at et navngitt Corteva-produkt utgjør en oppgitt andel av Fresno-pundene.", ["https://www.cdpr.ca.gov/wp-content/uploads/2024/12/pur2022_indexed_by_chemical.pdf"]),
        ],
        open_questions=[
            "Hvilke aktive stoffer som driver persentilen i tract 6019001000, krever rådataene bak indikatoren, ikke bare samlescoren.",
            "Et konkret lovforslag om 1,3-diklorpropen er ikke hentet fra leginfo i denne runden.",
        ],
    ))

    cards.append(card(
        id="ca-problem-salton-sea",
        type="problem",
        name="Salton Sea, eksponert playa og støv",
        rank=6,
        summary=[
            cl("s1", "Imperial Irrigation District skriver at overføringen av inntil om lag 300 000 acre-fot i året med spart vann under Quantification Settlement Agreement reduserer avrenning til Salton Sea, blotlegger playa og kan øke støv.", "confirmed", [iid]),
            cl("s2", "Samme dokument sier at Imperial County er klassifisert som serious nonattainment for PM10, blant annet på grunn av vindbåret støv, og at fremtidig blotlagt playa ventes å bli en ny støvkilde.", "confirmed", [iid], "Klassifiseringen er gjengitt av IID. Egen oppslag i EPA Green Book for PM10 er ikke gjort i denne runden."),
            cl("s3", "CNRAs årsrapport for Salton Sea Management Program fra mars 2025 er skrevet til State Water Board i samsvar med Order WR 2017-0134.", "confirmed", [ssmp]),
            cl("s4", "Imperial Irrigation District, filer 1143378, har 290 134,29 dollar i lobbybetalinger i sesjonen 2025-2026 ifølge Cal-Access.", "confirmed", [lobby_search]),
        ],
        claims=[
            cl("c1", "Census tract 6025012100 i Imperial County har CalEnviroScreen-score 60,51 og persentil 96,03, med 6 779 innbyggere. PM2.5-indikatoren er 11,85. Trakten er ikke sjøens strandlinje.", "confirmed", [ces_src]),
            cl("c2", "EPA Green Book fører Imperial County som Moderate nonattainment for PM2.5-standarden fra 2012, med 2010-befolkning 154 061 og årsdesignverdi 9,8. Det er et annet tall enn IIDs omtale av PM10.", "confirmed", [green]),
            cl("c3", "Problemet rangeres bak pesticider fordi den befolkningen EPA knytter til Imperial i PM2.5-tabellen er langt mindre enn South Coast, San Joaquin Valley og Failing-listen, og fordi playa-arealet i 2025-rapporten ikke er trukket ut.", "confirmed", [green, needs]),
        ],
        geometry=imperial,
        map_features=[{"layer": "problem", "name": "Census tract 6025012100", "geometry": imperial}],
        links=[
            link("organization", "org-iid", "Imperial Irrigation District og vannoverføringen."),
            link("organization", "org-swrcb", "Årsrapporten er avgitt til State Water Board."),
            link("organization", "org-carb", "Støv er et luftproblem, men planen som er lest, er IIDs."),
        ],
        checked_empty=[
            empty("playa_acres_2025", "Innholdsfortegnelsen i SSMP-årsrapporten 2025 er lest. Et areal for blotlagt playa er ikke hentet ut av tabellene.", ["https://saltonsea.ca.gov/wp-content/uploads/2025/03/SSMP-2025-Annual-Report_Mar-28.pdf"]),
            empty("campaign_contributions", "ContributorSearch er ikke kjørt for IMPERIAL IRRIGATION.", ["https://dbsearch.sos.ca.gov/ContributorSearch.aspx"]),
        ],
        open_questions=[
            "Hvor mange acre playa SSMP regnet som blotlagt i den siste årsrapporten, og hvor mye PM10 som er målt fra playa og ikke fra ørkenen rundt.",
            "Om EPA Green Book i dag fortsatt fører Imperial som serious for PM10. IID sier det. Green Book-siden for PM10 er ikke åpnet her.",
        ],
    ))

    cards.append(card(
        id="ca-problem-refineries",
        type="problem",
        name="Petroleumsraffinerier og måling ved gjerdet",
        rank=7,
        summary=[
            cl("s1", "AB 1647 (Muratsuchi, kapittel 589, 2017) krever samfunnsmåling nær raffinerier og at eieren driver et fence-line-system. Data skal gjøres offentlige så raskt som mulig. Eieren betaler, med et unntak når distriktet også bruker stasjonen til andre kilder.", "confirmed", [ab1647]),
            cl("s2", "South Coast AQMD målte i 2015 VOC, NOx og SO2 ved seks raffinerier i bassenget. Rapporten sier at de hadde en samlet rapportert kapasitet på over 900 000 fat per dag, med henvisning til California Energy Commission 2016. Raffineriene er kalt A til F i sammendraget.", "confirmed", [flux]),
            cl("s3", "EPA ECHO viser CHEVRON EL SEGUNDO REFINERY, registry 110002899908, med status Significant Violation, 12 kvartaler med noncompliance, samlede formelle bøter på 1 078 634 dollar, siste bot 24. november 2021 og siste inspeksjon 6. april 2026.", "confirmed", [echo], "Statusen er EPAs kategori, ikke en egen rettslig konklusjon i dette kortet."),
            cl("s4", "Cal-Access viser lobbybetalinger i sesjonen 2025-2026 for Phillips 66 på 1 982 009,15 dollar, Marathon Petroleum Corporation and its subsidiaries på 1 321 231,64 dollar, PBF Holding Company på 593 436,59 dollar, Valero Services Inc på 508 895,85 dollar og PBF Energy Western Region LLC på 492 320,02 dollar.", "confirmed", [lobby_search]),
        ],
        claims=[
            cl("c1", "Forsamlingen samtykket i senatets endringer av AB 1647 den 13. september 2017 med 57 mot 19. Senatet vedtok lovforslaget 11. september 2017 med 28 mot 11.", "confirmed", [ab1647_hist]),
            cl("c2", "FRS-punktet for Chevron El Segundo er 33,916216 nord og 118,41873 vest. Torrance Refining Company LLC, registry 110070241046, ligger på 33,854967 nord og 118,336907 vest. Phillips 66 Wilmington Plant, registry 110000476235, ligger på 33,76336 nord og 118,27645 vest. Benicia Valero Refinery, registry 110071102220, ligger på 38,074169 nord og 122,144559 vest.", "confirmed", [frs_chevron, frs_torrance, frs_phillips, frs_valero]),
            cl("c3", "Problemet er skilt fra South Coast-ozon fordi loven og måleprogrammene gjelder anlegget og nabolaget, ikke bare den regionale designverdien. Befolkningen i bassenget er derfor ikke brukt på nytt som om den bare gjaldt raffineriene.", "confirmed", [ab1647, green]),
        ],
        geometry=chevron_pt,
        map_features=[
            {"layer": "facility", "name": "Chevron El Segundo Refinery", "geometry": chevron_pt},
            {"layer": "facility", "name": "Torrance Refining Company LLC", "geometry": torrance_pt},
            {"layer": "facility", "name": "Phillips 66 Wilmington Plant", "geometry": phillips_pt},
            {"layer": "facility", "name": "Benicia Valero Refinery", "geometry": valero_pt},
        ],
        links=[
            link("organization", "org-chevron", "El Segundo og ECHO-statusen."),
            link("organization", "org-torrance-refining", "FRS-posten for Torrance."),
            link("organization", "org-phillips66", "Wilmington-anlegget og lobbytallet."),
            link("organization", "org-marathon", "Lobbytallet for Marathon Petroleum."),
            link("organization", "org-pbf", "To PBF-filer i Cal-Access."),
            link("organization", "org-valero", "Benicia og Valero Services."),
            link("organization", "org-scaqmd", "2015-målingene og distriktets veiledning."),
            link("bill", "bill-ab-1647", "Kravet om fence-line-måling."),
            link("lawmaker", "lawmaker-al-muratsuchi", "Muratsuchi står som forfatter på lovteksten."),
            link("problem", "ca-problem-south-coast-air", "Regional ozon og PM2.5 i samme basseng."),
        ],
        checked_empty=[
            empty("named_fluxes", "2015-rapportens sammendrag bruker Refinery A til F og gir ikke navn på anleggene i teksten som er lest.", ["https://www.aqmd.gov/docs/default-source/fenceline_monitoring/project_1/fluxsense_scaqmd2015_project1_finalreport(040717).pdf"]),
            empty("pbf_owns_torrance", "Ingen primærkilde er hentet som sier at PBF eier FRS-posten TORRANCE REFINING COMPANY LLC.", []),
            empty("refinery_operating_status", "FRS viser at postene finnes. Driftsstatus i oktober 2026 er bare bekreftet for Chevron El Segundo via ECHO-inspeksjonen 6. april 2026, ikke for de andre anleggene.", [echo["url"]]),
        ],
        open_questions=[
            "Hvilket selskap som i dag driver Wilmington-anlegget og Torrance-anlegget, og om noen av dem er lagt om til fornybart drivstoff.",
            "Hvem som mottok lobbyfilenes kampanjebidrag. ContributorSearch er kjørt for Chevron, ikke for Phillips 66, Marathon, PBF eller Valero.",
        ],
    ))

    cards.append(card(
        id="ca-problem-aliso-canyon",
        type="problem",
        name="Aliso Canyon gasslager",
        rank=8,
        summary=[
            cl("s1", "CARB anslo at lekkasjen ved SoCalGas sitt Aliso Canyon-lager slapp ut 99 650 tonn metan, med usikkerhet 9 300 tonn. For full klimakompensasjon brukes øvre grense, 109 000 tonn.", "confirmed", [aliso_pdf]),
            cl("s2", "Lekkasjen ble rapportert 23. oktober 2015 og kontrollert 11. februar 2016. CARB kaller den den største dokumenterte metanlekkasjen i USA i rapporten, med henvisning til Conley med flere i Science.", "confirmed", [aliso_pdf]),
            cl("s3", "CARB skriver i nyhetsmeldingen at 109 000 tonn omtrent tilsvarer et års gassbruk i 190 000 boliger i Los Angeles. Det er en sammenligning, ikke et folketall for Porter Ranch.", "confirmed", [aliso_news]),
            cl("s4", "FRS-post 110001158238 heter SOUTHERN CALIFORNIA GAS COMPANY - ALISO CANYON, Porter Ranch, 12801 Tampa Ave, og har koordinatene 34,307569 nord og 118,551235 vest.", "confirmed", [frs_aliso]),
        ],
        claims=[
            cl("c1", "Cal-Access-fileren «Sempra and its affiliates: San Diego Gas & Electric Company and Southern California Gas Company», id 1146926, har 3 347 511,14 dollar i lobbybetalinger i sesjonen 2025-2026. Beløpet er ikke spesifisert til Aliso Canyon.", "confirmed", [lobby_search]),
            cl("c2", "Problemet rangeres her fordi utslippet er stort og dokumentert, men det er ett anlegg og den akutte lekkasjen skjedde i 2015-2016. Et folketall for evakuerte er ikke hentet fra en primærkilde.", "confirmed", [aliso_pdf]),
        ],
        geometry=aliso_pt,
        map_features=[{"layer": "facility", "name": "SoCalGas Aliso Canyon", "geometry": aliso_pt}],
        links=[
            link("organization", "org-sempra", "Sempra-fileren som omfatter SoCalGas."),
            link("organization", "org-carb", "CARB beregnet metanutslippet."),
            link("lobbying_firm", "firm-pillsbury", "Pillsbury er blant firmaene WSPA betalte. Det er ikke vist at firmaet representerte SoCalGas."),
        ],
        checked_empty=[
            empty("cpuc_decision", "En navngitt CPUC-beslutning om fortsatt drift av Aliso Canyon er ikke åpnet.", ["https://www.cpuc.ca.gov/"]),
            empty("campaign_contributions", "ContributorSearch er ikke kjørt for SEMPRA eller SOUTHERN CALIFORNIA GAS.", ["https://dbsearch.sos.ca.gov/ContributorSearch.aspx"]),
            empty("evacuation_count", "CARB-rapporten som er lest, oppgir ikke hvor mange mennesker som ble evakuert.", [aliso_pdf["url"]]),
        ],
        open_questions=[
            "Hvilken CPUC-beslutning som gjelder lagringskapasitet nå, og hvilke brønner som fortsatt er i bruk.",
            "Om root-cause-rapporten fra da DOGGR, nå CalGEM, konkluderte om brudd på regler. Den er ikke hentet.",
        ],
    ))

    cards.append(card(
        id="ca-problem-pfas",
        type="problem",
        name="PFAS i drikkevannskilder",
        rank=9,
        summary=[
            cl("s1", "State Water Board skriver at de tester om lag 3 600 drikkevannsbrønner i disadvantaged communities, uten kostnad for vannverkene, fra 2024 til 2026, etter bevilgning i AB 178 i 2022.", "confirmed", [pfas_page]),
            cl("s2", "Kvalitetsplanen for General Order DW-2024-0002-DDW, september 2024, sier at styret skal ta prøver av om lag 3 800 brønner som forsyner disadvantaged og severely disadvantaged communities.", "confirmed", [pfas_qapp], "3 600 og 3 800 står i to dokumenter fra samme etat. De er ikke rettet mot hverandre her."),
            cl("s3", "Et foreløpig lysbilde datert mars 2025 sier at 1 730 brønner og 337 vannsystemer var prøvetatt per 28. februar 2025. For 1 307 brønner med Method 533, prøver til og med 18. desember 2024, var det 76 PFOA-funn over CCRDL, høyeste 50 ng/L, og 84 PFOS-funn, høyeste 350 ng/L.", "confirmed", [pfas_slides], "Lysbildene er merket preliminary."),
            cl("s4", "Problemet står lavt i rangeringen fordi kartleggingen ikke er ferdig og fordi det ikke finnes et etatstall i de leste dokumentene for hvor mange mennesker som får levert vann over en grenseverdi.", "confirmed", [pfas_page, pfas_slides]),
        ],
        claims=[
            cl("c1", "Kvalitetsplanen sier at prøvene skal brukes både til å se geografiske mønstre og til å vurdere renseanlegg, som grunnlag for behandlingsbaserte regler.", "confirmed", [pfas_qapp]),
        ],
        geometry=None,
        map_features=[],
        links=[
            link("organization", "org-swrcb", "Division of Drinking Water gir pålegget og publiserer siden."),
        ],
        checked_empty=[
            empty("geometry", "Ingen brønn med koordinat og PFAS-resultat er lastet ned fra GAMA eller SDWIS.", ["https://www.waterboards.ca.gov/pfas/drinking_water.html"]),
            empty("lobbying", "LobbyIntSearch er ikke kjørt med søkeord PFAS eller for en navngitt PFAS-produsent utover Corteva, som står på pesticidkortet.", ["https://dbsearch.sos.ca.gov/LobbyIntSearch.aspx"]),
            empty("campaign_contributions", "ContributorSearch er ikke kjørt for en PFAS-produsent.", ["https://dbsearch.sos.ca.gov/ContributorSearch.aspx"]),
            empty("votes", "AB 178 er nevnt på etatssiden som bevilgning. Avstemningstallen er ikke hentet fra leginfo.", ["https://www.waterboards.ca.gov/pfas/drinking_water.html"]),
        ],
        open_questions=[
            "Hvorfor etatssiden sier om lag 3 600 brønner og kvalitetsplanen om lag 3 800.",
            "Hvor mange vannverk som har overskredet en føderal eller californisk grenseverdi etter at prøvene er ferdige.",
            "Hvilke anlegg, flyplasser eller brannøvingsfelt som er kilden der det er høye funn. Lysbildene som er lest, gir ikke anleggsnavn.",
        ],
    ))

    cards.append(card(
        id="ca-problem-groundwater-overdraft",
        type="problem",
        name="Kritisk overtrukket grunnvann",
        rank=10,
        summary=[
            cl("s1", "DWR skriver at SGMA pålegger etaten å peke ut basseng i critical overdraft, definert som at fortsatt bruk sannsynligvis gir betydelige negative miljø-, samfunns- eller økonomiske virkninger. Overdraft er når uttaket over tid er større enn tilførselen.", "confirmed", [dwr]),
            cl("s2", "DWRs kart fra januar 2020, basert på Bulletin 118-grenser publisert 11. februar 2019, lister 21 basseng og delbasseng. Elleve av dem ligger i San Joaquin Valley, fra Eastern San Joaquin 5-022.01 til Kern County 5-022.14.", "confirmed", [dwr_pdf]),
            cl("s3", "DWR skriver at virkninger kan være saltvannsinntrenging, setninger, utarming av grunnvann og vedvarende senkning av grunnvannsnivået.", "confirmed", [dwr]),
            cl("s4", "Census tract 6029006201 i Kern County har drikkevannsindikator 1 022,63 og persentil 99,63, og pesticidindikator 4 226,06. Det er en illustrasjon i fylket, ikke bassengets grense.", "confirmed", [ces_src]),
        ],
        claims=[
            cl("c1", "De elleve San Joaquin Valley-numrene på kartet er 5-022.01, 5-022.04, 5-022.05, 5-022.06, 5-022.07, 5-022.08, 5-022.09, 5-022.11, 5-022.12, 5-022.13 og 5-022.14.", "confirmed", [dwr_pdf]),
            cl("c2", "Problemet rangeres sist av de ti fordi DWR dokumenterer en ressurs- og setningsrisiko, ikke et antall mennesker som drikker vann over en grenseverdi. Det tallet ligger på drikkevannskortet.", "confirmed", [dwr, needs]),
        ],
        geometry=kern_tract,
        map_features=[{"layer": "tract", "name": "Census tract 6029006201", "geometry": kern_tract}],
        links=[
            link("organization", "org-dwr", "DWR peker ut bassengene."),
            link("organization", "org-swrcb", "Nitrat og failing-systemer er det andre kortet."),
            link("problem", "ca-problem-drinking-water", "Failing-listen og nitraten."),
            link("problem", "ca-problem-oil-gas-proximity", "Kern er også det største oljefylket i CalGEM-rapporten."),
        ],
        checked_empty=[
            empty("sgma_bill_votes", "Selve SGMA-lovene fra 2014 er ikke åpnet på leginfo. DWR-siden er brukt for definisjonen.", ["https://water.ca.gov/programs/groundwater-management/bulletin-118/critically-overdrafted-basins"]),
            empty("basin_polygon", "Bulletin 118-polygonet er ikke lastet inn. Trakten er ikke bassenget.", ["https://data.ca.gov/dataset/i08-criticallyoverdraftedbasins"]),
            empty("lobbying", "Ingen lobbyemployer er søkt spesifikt på SGMA eller grunnvannsbasseng.", ["https://dbsearch.sos.ca.gov/LobbyIntSearch.aspx"]),
        ],
        open_questions=[
            "Hvilke GSPer som er vurdert som utilstrekkelige, og hvilke vannverk som har mistet brønner på grunn av nivåsenkning.",
            "Avstemningene og kapittelnumrene for AB 1739, SB 1168 og SB 1319.",
        ],
    ))

    # Organizations, firms, bills, lawmakers continue in the same list.
    cards.extend(rest_cards(
        lobby_search, contrib_search, wspa_page, wspa_pdf, crc_10k, calgem, echo, frs_chevron,
        frs_aliso, frs_torrance, frs_phillips, frs_valero, chevron_pt, torrance_pt, phillips_pt,
        aliso_pt, valero_pt, sb1137, sb1137_hist, sb1137_votes, sb200, sb200_hist, ab617,
        ab617_votes, ab1647, ab1647_hist, gonzalez, gonzalez_dist, needs, dpr, dwr, oehha,
        aqmd, pm_ext, aliso_pdf, pfas_page, ssmp, iid,
    ))

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for item in cards:
        path = OUT / f"{item['id']}.json"
        path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(cards)} cards")


def rest_cards(
    lobby_search, contrib_search, wspa_page, wspa_pdf, crc_10k, calgem, echo, frs_chevron,
    frs_aliso, frs_torrance, frs_phillips, frs_valero, chevron_pt, torrance_pt, phillips_pt,
    aliso_pt, valero_pt, sb1137, sb1137_hist, sb1137_votes, sb200, sb200_hist, ab617,
    ab617_votes, ab1647, ab1647_hist, gonzalez, gonzalez_dist, needs, dpr, dwr, oehha,
    aqmd, pm_ext, aliso_pdf, pfas_page, ssmp, iid_src,
):
    cards = []
    cards.append(card(
        id="org-chevron",
        type="organization",
        org_kind="company",
        name="Chevron U.S.A., Inc. and Affiliates",
        summary=[
            cl("s1", "CalGEM fører Chevron U.S.A. Inc. med 20 764 561,84 dollar i mottatte vurderingsbetalinger for 2023, det høyeste beløpet i vedlegg D.", "confirmed", [calgem]),
            cl("s2", "Cal-Access, filer 1146815, kategori oil and gas, viser 19 279 518,27 dollar i lobbybetalinger i sesjonen 2025-2026 per 28. oktober 2026.", "confirmed", [lobby_search, src("https://cal-access.sos.ca.gov/Lobbying/Employers/Detail.aspx?id=1146815&session=2025&view=activity", "Cal-Access employer 1146815", "California Secretary of State")]),
            cl("s3", "ContributorSearch med navn som inneholder CHEVRON, California, 1. januar 2025 til 28. oktober 2026, ga 23 navnestrenger. Den største er «CHEVRON, SAN RAMON, CA 94583» med 5 473 000,00 dollar. «CHEVRON USA, INC., SAN RAMON, CA 94583» har 523 600,00 dollar. En rad heter «DUBLIN CHEVRON» og er et annet navn med et lite beløp. Radene er ikke summert.", "confirmed", [contrib_search]),
            cl("s4", "EPA ECHO: anlegget i El Segundo har Significant Violation, bøter på 1 078 634 dollar og inspeksjon 6. april 2026. FRS-koordinatene er 33,916216, -118,41873.", "confirmed", [echo, frs_chevron]),
        ],
        claims=[
            cl("c1", "TRI-identifikatoren i ECHO-svaret er 90245CHVRN324WE. Gateadressen er 324 W El Segundo Blvd, El Segundo.", "confirmed", [echo]),
        ],
        geometry=chevron_pt,
        map_features=[{"layer": "facility", "name": "Chevron El Segundo Refinery", "geometry": chevron_pt}],
        links=[
            link("problem", "ca-problem-oil-gas-proximity", "Vurdering og lobby i olje og gass."),
            link("problem", "ca-problem-refineries", "El Segundo-raffineriet."),
            link("problem", "ca-problem-south-coast-air", "Anlegget ligger i South Coast."),
            link("organization", "org-wspa", "WSPA er den andre store olje- og gassfileren."),
        ],
        checked_empty=[
            empty("contribution_recipients", "ContributorSearch gir sum per navnestreng, ikke mottaker. Detaljsiden for hver rad er ikke åpnet.", ["https://dbsearch.sos.ca.gov/ContributorSearch.aspx"]),
            empty("kern_wells", "CalGEM-rapporten gir ikke Chevrons fat i Kern. Bare vurderingsbetalingen og fylkets totale fat er lest.", [calgem["url"]]),
        ],
        open_questions=["Hvilke komiteer og tiltak som mottok de 5 473 000 dollarene på San Ramon-strengen, og om flere strenger er samme penger ført to ganger."],
    ))
    cards.append(card(
        id="org-crc",
        type="organization",
        org_kind="company",
        name="California Resources Corporation and subsidiaries",
        summary=[
            cl("s1", "I 10-K for 2023 skriver selskapet at netto produksjon var 86 tusen fat oljeekvivalenter per dag, hvorav San Joaquin-bassenget 64 og Los Angeles-bassenget 19. Det oppgir om lag 9 000 netto opererte brønner og nevner Elk Hills og Wilmington som de to største feltene i tabellen som er lest.", "confirmed", [crc_10k]),
            cl("s2", "Samme melding sier at selskapet 7. februar 2024 inngikk en fusjonsavtale med Aera Energy LLC, med virkningsdato 1. januar 2024, og at avtalen da var pending.", "confirmed", [crc_10k], "Senere status enn 10-K-en er ikke hentet."),
            cl("s3", "Cal-Access-filer 1374043 har 1 524 830,24 dollar i lobbybetalinger i sesjonen 2025-2026.", "confirmed", [lobby_search]),
            cl("s4", "ContributorSearch på CALIFORNIA RESOURCES CORPORATION ga 19 navnestrenger. Den største er «CALIFORNIA RESOURCES CORPORATION AND SUBSIDIARIES, LONG BEACH, CA 90831» med 1 505 900,00 dollar. En San Francisco-streng, 94108, har 841 800,00 dollar. Noen strenger har et personnavn i parentes. Rollen til det navnet er ikke tolket.", "confirmed", [contrib_search]),
        ],
        claims=[
            cl("c1", "CalGEM fører California Resources Elk Hills, LLC med 8 032 105,72 dollar i vurderingsbetalinger i 2023, og California Resources Production Corporation med 4 094 062,91 dollar.", "confirmed", [calgem]),
        ],
        geometry=None,
        map_features=[],
        links=[
            link("problem", "ca-problem-oil-gas-proximity", "Produksjon og lobby."),
            link("problem", "ca-problem-san-joaquin-air", "Selskapet sier at mesteparten av produksjonen er i San Joaquin."),
            link("organization", "org-calgem", "Vurderingsbetalingene."),
        ],
        checked_empty=[
            empty("geometry", "Ingen brønnkoordinat for Elk Hills eller Wilmington er hentet fra CalGEM. Et kraftverk treffet i FRS er ikke brukt, fordi det ikke er oljefeltet.", ["https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?facility_name=ELK%20HILLS%20POWER&state_abbr=CA&output=JSON"]),
        ],
        open_questions=["Om fusjonen med Aera er fullført, og hvilken operatør som nå står på brønnene i CalGEM."],
    ))
    cards.append(card(
        id="org-wspa",
        type="organization",
        org_kind="trade_association",
        name="Western States Petroleum Association",
        summary=[
            cl("s1", "Cal-Access-filer 1147195 har 19 031 326,51 dollar i lobbybetalinger i sesjonen 2025-2026 per 28. oktober 2026.", "confirmed", [lobby_search, wspa_page]),
            cl("s2", "Wayback-øyeblikksbildet fra 3. juli 2026 viser kvartalstallene 3 471 879,71, 3 032 226,49, 2 375 251,11, 3 525 971,27 og 4 345 731,14 dollar for de fem første kvartalene i sesjonen. Summen av disse fem er lavere enn oktobertotalen. Differansen er ikke forklart med en senere rapport her.", "confirmed", [wspa_page, lobby_search]),
            cl("s3", "Form 635, filing 3070933, for 1. april til 30. juni 2025, har samlet 3 032 226,49 dollar. Det er samme tall som andre kvartal på aktivitetssiden. Rapporten betalte blant annet Carpenter Garcia Sievers LLC 90 000 dollar, Greenberg Traurig LLP 37 500 dollar, Pillsbury Winthrop Shaw Pittman LLP 59 330,91 dollar og Leacox & Associates 6 000 dollar i perioden.", "confirmed", [wspa_pdf, wspa_page]),
            cl("s4", "ContributorSearch ga 14 navnestrenger. Den største PAC-strengen er «WESTERN STATES PETROLEUM ASSOCIATION CALIFORNIA PAC, SACRAMENTO, CA 95814» med 25 800,00 dollar. Foreningen selv, Sacramento, står med 16 044,92 dollar. Strengene er ikke summert.", "confirmed", [contrib_search]),
        ],
        claims=[
            cl("c1", "Skjemaet sier at lovene og etatene som ble lobbet, står i vedlegg A. Vedlegget er ikke lest. Derfor er det ikke oppgitt hvilke lovforslag WSPA lobbet på i det kvartalet.", "not_verified", [wspa_pdf], "Primærkilden som ville bekrefte sakene, er vedlegg A til filing 3070933."),
        ],
        geometry=None,
        map_features=[],
        links=[
            link("problem", "ca-problem-oil-gas-proximity", "Nest størst i olje- og gasskategorien."),
            link("lobbying_firm", "firm-carpenter-garcia-sievers", "90 000 dollar i andre kvartal 2025."),
            link("lobbying_firm", "firm-greenberg-traurig", "37 500 dollar i samme kvartal."),
            link("lobbying_firm", "firm-pillsbury", "59 330,91 dollar i samme kvartal."),
            link("lobbying_firm", "firm-leacox", "6 000 dollar i samme kvartal."),
        ],
        checked_empty=[
            empty("both_sides_clients", "Firmaenes øvrige oppdragsgivere er ikke hentet fra firmaenes egne Cal-Access-sider. Ingen påstand om at samme firma også representerer en klimaklient.", ["https://cal-access.sos.ca.gov/Lobbying/Firms/"]),
            empty("attachment_a", "Vedlegg A til filing 3070933 er ikke lastet ned.", [wspa_pdf["url"]]),
        ],
        open_questions=["Hva vedlegg A lister av lovforslag og etater, og hvilke senere kvartaler som forklarer gapet mellom juli-arkivet og oktobertotalen."],
    ))
    cards.append(card(
        id="org-cipa",
        type="organization",
        org_kind="trade_association",
        name="California Independent Petroleum Association",
        summary=[
            cl("s1", "Cal-Access-filer 1146650, California Independent Petroleum Association (CIPA), har 744 330,97 dollar i lobbybetalinger i sesjonen 2025-2026, kategori oil and gas.", "confirmed", [lobby_search]),
            cl("s2", "Foreningen står i samme uttrekk som Chevron, WSPA og California Resources. Uttrekket ga 40 employer-rader i kategorien, sortert alfabetisk, inkludert rader med 0 dollar.", "confirmed", [lobby_search], "Det er ikke bekreftet at 40 er et absolutt tak i databasen. Listen som kom tilbake, begynner på Berry og slutter på Woodside og inneholder både de største og nullbeløp."),
            cl("s3", "Ingen brønn, ingen lovtekst og ingen bidragssum er knyttet til CIPA ut over lobbytallet.", "not_found", [lobby_search], "ContributorSearch er ikke kjørt for CIPA."),
        ],
        claims=[
            cl("c1", "Filer-id i postback fra søket er 1146650, og interessekoden er OIL AND GAS.", "confirmed", [lobby_search]),
        ],
        geometry=None,
        map_features=[],
        links=[link("problem", "ca-problem-oil-gas-proximity", "Lobby i samme kategori som produsentene.")],
        checked_empty=[empty("campaign_contributions", "ContributorSearch er ikke kjørt for CALIFORNIA INDEPENDENT PETROLEUM.", ["https://dbsearch.sos.ca.gov/ContributorSearch.aspx"])],
        open_questions=["Hvilke lovforslag CIPA oppga i siste Form 635."],
    ))
    cards.append(card(
        id="org-berry",
        type="organization",
        org_kind="company",
        name="Berry Corporation",
        summary=[
            cl("s1", "Cal-Access-filer 1420515, Berry Corporation, har 183 000,00 dollar i lobbybetalinger i sesjonen 2025-2026, kategori oil and gas.", "confirmed", [lobby_search]),
            cl("s2", "Et navnesøk på BERRY ga også to jordbruksfiler, California Blueberry Commission og California Strawberry Commission. De er ikke Berry Corporation.", "confirmed", [lobby_search]),
            cl("s3", "Ingen CalGEM-produksjonstall for Berry er skilt ut i årsrapportens topp i den delen som er lest. Selskapet er med her fordi det er en navngitt oil-and-gas-employer, ikke fordi en fatmengde er bekreftet.", "not_verified", [calgem, lobby_search], "Primærkilden for fat ville være CalGEM produksjonsrapport per operatør."),
        ],
        claims=[cl("c1", "Filer-id 1420515 kommer fra LobbyIntSearch-postbacken.", "confirmed", [lobby_search])],
        geometry=None,
        map_features=[],
        links=[link("problem", "ca-problem-oil-gas-proximity", "Registrert i olje- og gasskategorien.")],
        checked_empty=[empty("campaign_contributions", "ContributorSearch er ikke kjørt for BERRY CORPORATION.", ["https://dbsearch.sos.ca.gov/ContributorSearch.aspx"])],
        open_questions=["Hvor mange fat Berry produserte i Kern i 2023 ifølge CalGEM."],
    ))
    cards.append(card(
        id="org-sempra",
        type="organization",
        org_kind="utility",
        name="Sempra, SDG&E og Southern California Gas",
        summary=[
            cl("s1", "Cal-Access-filer 1146926 dekker Sempra og tilknyttede selskaper, inkludert San Diego Gas & Electric og Southern California Gas Company, med 3 347 511,14 dollar i lobbybetalinger i sesjonen 2025-2026.", "confirmed", [lobby_search]),
            cl("s2", "CARB skriver at Aliso Canyon-lekkasjen var ved Southern California Gas Company sitt lager.", "confirmed", [aliso_pdf]),
            cl("s3", "FRS-post 110001158238 er SOUTHERN CALIFORNIA GAS COMPANY - ALISO CANYON i Porter Ranch.", "confirmed", [frs_aliso]),
            cl("s4", "Lobbybeløpet gjelder den samlede fileren. Det er ikke delt mellom SDG&E, SoCalGas og Aliso.", "confirmed", [lobby_search]),
        ],
        claims=[cl("c1", "Koordinatene 34,307569 og -118,551235 er Latitude83 og Longitude83 i FRS-svaret.", "confirmed", [frs_aliso])],
        geometry=aliso_pt,
        map_features=[{"layer": "facility", "name": "SoCalGas Aliso Canyon", "geometry": aliso_pt}],
        links=[link("problem", "ca-problem-aliso-canyon", "Gasslageret og metanlekkasjen.")],
        checked_empty=[empty("campaign_contributions", "ContributorSearch er ikke kjørt for SEMPRA.", ["https://dbsearch.sos.ca.gov/ContributorSearch.aspx"])],
        open_questions=["Hvor stor del av lobbybeløpet som gjelder gasslager, og hvilken CPUC-sak fileren oppga."],
    ))
    cards.append(card(
        id="org-marathon",
        type="organization",
        org_kind="company",
        name="Marathon Petroleum Corporation and its subsidiaries",
        summary=[
            cl("s1", "Cal-Access-filer 1244770 har 1 321 231,64 dollar i lobbybetalinger i sesjonen 2025-2026, kategori oil and gas.", "confirmed", [lobby_search]),
            cl("s2", "Et navnesøk på MARATHON ga også Marathon Asset Management LP i finans, med 0 dollar. Den raden er ikke raffineriselskapet.", "confirmed", [lobby_search]),
            cl("s3", "Ingen FRS-post med navnet Marathon Los Angeles ga treff i søket som ble kjørt. Derfor er ikke et anleggspunkt lagt på dette kortet.", "not_found", [src("https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?facility_name=MARATHON%20LOS%20ANGELES&state_abbr=CA&output=JSON", "FRS-søk MARATHON LOS ANGELES", "US EPA")]),
        ],
        claims=[cl("c1", "Filer-id 1244770 og interessekode OIL AND GAS kommer fra LobbyIntSearch.", "confirmed", [lobby_search])],
        geometry=None,
        map_features=[],
        links=[link("problem", "ca-problem-refineries", "Lobbytall, uten bekreftet anleggspunkt.")],
        checked_empty=[empty("geometry", "FRS-søk på MARATHON LOS ANGELES ga null treff.", [])],
        open_questions=["Hvilket raffinerinavn Marathon bruker i FRS eller ECHO i Los Angeles i 2026."],
    ))
    cards.append(card(
        id="org-phillips66",
        type="organization",
        org_kind="company",
        name="Phillips 66",
        summary=[
            cl("s1", "Cal-Access-filer 1348342, Phillips 66, har 1 982 009,15 dollar i lobbybetalinger i sesjonen 2025-2026.", "confirmed", [lobby_search]),
            cl("s2", "ConocoPhillips Company and Affiliates, filer 1147122, er en egen rad med 99 134,00 dollar. Den er ikke lagt sammen med Phillips 66.", "confirmed", [lobby_search]),
            cl("s3", "FRS har PHILLIPS 66 COMPANY WILMINGTON PLANT, registry 110000476235, 1660 W Anaheim Street, koordinater 33,76336 og -118,27645.", "confirmed", [frs_phillips]),
            cl("s4", "Driftsstatus i 2026 er ikke bekreftet. FRS viser posten. ECHO er ikke slått opp for dette registry-idet.", "not_verified", [frs_phillips], "ECHO-oppslag på 110000476235 ville bekrefte om anlegget har ny inspeksjon."),
        ],
        claims=[cl("c1", "Et annet FRS-treff i samme søk er en marine terminal, registry 110000607371. Den er ikke brukt som hovedpunkt.", "confirmed", [frs_phillips])],
        geometry=phillips_pt,
        map_features=[{"layer": "facility", "name": "Phillips 66 Wilmington Plant", "geometry": phillips_pt}],
        links=[link("problem", "ca-problem-refineries", "Wilmington-posten og lobbytallet.")],
        checked_empty=[empty("campaign_contributions", "ContributorSearch er ikke kjørt for PHILLIPS 66.", ["https://dbsearch.sos.ca.gov/ContributorSearch.aspx"])],
        open_questions=["Om Wilmington-anlegget fortsatt raffinerer råolje."],
    ))
    cards.append(card(
        id="org-pbf",
        type="organization",
        org_kind="company",
        name="PBF Energy Western Region og PBF Holding",
        summary=[
            cl("s1", "PBF Holding Company, filer 1408198, har 593 436,59 dollar i lobbybetalinger i sesjonen 2025-2026. PBF Energy Western Region LLC, filer 1382832, har 492 320,02 dollar. Begge står i oil and gas.", "confirmed", [lobby_search]),
            cl("s2", "Et søk på PBF ga også Professional Beauty Federation of California. Den raden er ikke energiselskapet.", "confirmed", [lobby_search]),
            cl("s3", "Ingen primærkilde i denne runden sier at en av PBF-filene eier Torrance Refining Company LLC. Anlegget har derfor eget kort.", "not_verified", [lobby_search, frs_torrance], "En SEC-fil eller et FRS-eierfelt ville bekrefte eierskapet."),
        ],
        claims=[cl("c1", "De to PBF-beløpene er ikke summert, fordi det er to filer.", "confirmed", [lobby_search])],
        geometry=None,
        map_features=[],
        links=[
            link("problem", "ca-problem-refineries", "Lobbytall uten bekreftet anleggskobling."),
            link("organization", "org-torrance-refining", "FRS-anlegget som ofte omtales sammen med PBF, uten at eierskapet er bekreftet her."),
        ],
        checked_empty=[empty("ownership", "SEC-søk og FRS-eierfelt er ikke hentet for Torrance.", [])],
        open_questions=["Om PBF Energy Western Region er operatør for registry 110070241046."],
    ))
    cards.append(card(
        id="org-torrance-refining",
        type="organization",
        org_kind="company",
        name="Torrance Refining Company LLC",
        summary=[
            cl("s1", "FRS har TORRANCE REFINING COMPANY LLC, registry 110070241046, 3700 W 190th St, Torrance, koordinater 33,854967 og -118,336907.", "confirmed", [frs_torrance]),
            cl("s2", "Samme navnesøk ga også eldre ExxonMobil-poster og poster uten koordinat. Hovedpunktet er 110070241046, som har koordinat.", "confirmed", [frs_torrance]),
            cl("s3", "Eierskap og drift i 2026 er ikke bekreftet ut over FRS-navnet.", "not_verified", [frs_torrance]),
        ],
        claims=[cl("c1", "Et annet treff, registry 110065691745, heter ExxonMobil Corporation Torrance Refinery og har en annen koordinat. Det er ikke slått sammen med 110070241046.", "confirmed", [frs_torrance])],
        geometry=torrance_pt,
        map_features=[{"layer": "facility", "name": "Torrance Refining Company LLC", "geometry": torrance_pt}],
        links=[link("problem", "ca-problem-refineries", "Ett av anleggene på raffinerikartet.")],
        checked_empty=[empty("echo", "ECHO er ikke slått opp for 110070241046.", ["https://echodata.epa.gov/echo/echo_rest_services.get_facility_info?p_frs=110070241046&output=JSON"])],
        open_questions=["Nåværende operatør og om anlegget har fence-line-data etter AB 1647."],
    ))
    cards.append(card(
        id="org-valero",
        type="organization",
        org_kind="company",
        name="Valero Services og Benicia-raffineriet",
        summary=[
            cl("s1", "Valero Services, Inc, filer 1237027, har 508 895,85 dollar i lobbybetalinger i sesjonen 2025-2026, kategori oil and gas.", "confirmed", [lobby_search]),
            cl("s2", "FRS har BENICIA VALERO REFINERY, registry 110071102220, koordinater 38,074169 og -122,144559.", "confirmed", [frs_valero]),
            cl("s3", "Et annet treff med samme navn, registry 110067352821, har breddegrad 32,72, som ikke ligger i Benicia. Det punktet er forkastet.", "confirmed", [frs_valero]),
        ],
        claims=[cl("c1", "Lobbyfileren heter Valero Services, Inc. FRS-anlegget heter Benicia Valero Refinery. At de er samme konsern, er ikke lest i et eget selskapsdokument.", "indication", [lobby_search, frs_valero], "Navnelikhet. Et 10-K- eller FRS-eierfelt ville bekrefte konsernet.")],
        geometry=valero_pt,
        map_features=[{"layer": "facility", "name": "Benicia Valero Refinery", "geometry": valero_pt}],
        links=[link("problem", "ca-problem-refineries", "Benicia ligger utenfor South Coast og er tatt med som eget anlegg.")],
        checked_empty=[empty("campaign_contributions", "ContributorSearch er ikke kjørt for VALERO.", ["https://dbsearch.sos.ca.gov/ContributorSearch.aspx"])],
        open_questions=["Om raffineriet i Benicia fortsatt er i drift, og hvilken luftmyndighet som har fence-line-dataene."],
    ))
    cards.append(card(
        id="org-iid",
        type="organization",
        org_kind="water_district",
        name="Imperial Irrigation District",
        summary=[
            cl("s1", "IID skrev luftprogrammet for Salton Sea fordi overføringen av inntil om lag 300 000 acre-fot i året under QSA blotlegger playa.", "confirmed", [iid_src]),
            cl("s2", "Cal-Access-filer 1143378 har 290 134,29 dollar i lobbybetalinger i sesjonen 2025-2026, kategori utilities.", "confirmed", [lobby_search]),
            cl("s3", "CNRA leverer Salton Sea-årsrapporten til State Water Board. IID er ikke forfatter av den rapporten.", "confirmed", [ssmp]),
        ],
        claims=[cl("c1", "IID skriver at Imperial County er serious nonattainment for PM10. EPA Green Book-siden for PM10 er ikke åpnet.", "indication", [iid_src], "Bekreftende primærkilde ville være EPA Green Book for PM10.")],
        geometry=None,
        map_features=[],
        links=[link("problem", "ca-problem-salton-sea", "Vannoverføring og støv.")],
        checked_empty=[empty("campaign_contributions", "ContributorSearch er ikke kjørt for IMPERIAL IRRIGATION.", ["https://dbsearch.sos.ca.gov/ContributorSearch.aspx"])],
        open_questions=["Hvilke saker filer 1143378 oppga i siste kvartal."],
    ))
    cards.append(card(
        id="org-farm-bureau",
        type="organization",
        org_kind="trade_association",
        name="California Farm Bureau Federation",
        summary=[
            cl("s1", "Filer 1146790 har 1 436 711,70 dollar i lobbybetalinger i sesjonen 2025-2026, kategori agriculture.", "confirmed", [lobby_search]),
            cl("s2", "Den største bidragstrengen i søket er FARM PAC-strengen med 116 700,00 dollar. Søket ga 11 strenger og er ikke summert.", "confirmed", [contrib_search]),
            cl("s3", "Kortet knytter ikke organisasjonen til et bestemt nitratutslipp eller et bestemt pesticidprodukt. Den er med fordi den er en stor jordbruksfiler i de samme fylkene som nitraten og pesticidene gjelder.", "confirmed", [lobby_search, dpr]),
        ],
        claims=[cl("c1", "Harter-rapporten peker på gjødsel og husdyrgjødsel som regionale nitratkilder, ikke på Farm Bureau som utslipper.", "confirmed", [src("https://groundwaternitrate.ucdavis.edu/files/138958.pdf", "Addressing Nitrate in California's Drinking Water", "UC Davis for the State Water Board")])],
        geometry=None,
        map_features=[],
        links=[
            link("problem", "ca-problem-drinking-water", "Jordbruk og nitrat, uten en direkte utslippskobling."),
            link("problem", "ca-problem-pesticides", "Lobby og pesticidbruk i samme fylker, uten produktkobling."),
        ],
        checked_empty=[empty("bills_lobbied", "Form 635 for Farm Bureau er ikke åpnet, så hvilke lovforslag som ble lobbet, er ukjent.", [])],
        open_questions=["Hvilke lovforslag om vann, gjødsel eller pesticider fileren oppga i 2025 og 2026."],
    ))
    cards.append(card(
        id="org-western-growers",
        type="organization",
        org_kind="trade_association",
        name="Western Growers",
        summary=[
            cl("s1", "Filer 1146857 har 1 196 763,69 dollar i lobbybetalinger i sesjonen 2025-2026, kategori agriculture.", "confirmed", [lobby_search]),
            cl("s2", "Ingen bidragssøk er kjørt for navnet.", "not_found", [contrib_search], "ContributorSearch ble kjørt for Farm Bureau, Chevron, CRC og WSPA, ikke for Western Growers."),
            cl("s3", "Ingen pesticidpund er koblet til organisasjonen.", "not_found", [dpr]),
        ],
        claims=[cl("c1", "Interessekoden i LobbyIntSearch er AGRICULTURE.", "confirmed", [lobby_search])],
        geometry=None,
        map_features=[],
        links=[link("problem", "ca-problem-pesticides", "Jordbruksfiler i samme tema, uten produktkobling.")],
        checked_empty=[empty("campaign_contributions", "ContributorSearch er ikke kjørt for WESTERN GROWERS.", ["https://dbsearch.sos.ca.gov/ContributorSearch.aspx"])],
        open_questions=["Hvilke saker Western Growers oppga overfor DPR eller lovgiver."],
    ))
    cards.append(card(
        id="org-corteva",
        type="organization",
        org_kind="company",
        name="Corteva Agriscience LLC",
        summary=[
            cl("s1", "Filer 1146862 har 141 149,88 dollar i lobbybetalinger i sesjonen 2025-2026. Interessekoden i søket er manufacturing/industrial.", "confirmed", [lobby_search]),
            cl("s2", "DPR-fylkestallene nevner ikke Corteva. Derfor er selskapet ikke oppgitt som kilde til Fresno- eller Kern-pundene.", "not_found", [dpr, lobby_search]),
            cl("s3", "ContributorSearch er ikke kjørt for Corteva.", "not_found", [contrib_search]),
        ],
        claims=[cl("c1", "Filer-id 1146862 kommer fra LobbyIntSearch på navnet CORTEVA.", "confirmed", [lobby_search])],
        geometry=None,
        map_features=[],
        links=[link("problem", "ca-problem-pesticides", "Registrert lobbyemployer, uten bekreftet produktandel.")],
        checked_empty=[empty("product_link", "PUR indexed by chemical er ikke gjennomgått for Corteva-produkter.", [])],
        open_questions=["Hvilke aktive stoffer i 2022-rapporten som er solgt av Corteva i California."],
    ))

    def regulator(cid, name, s1, s2, s3, sources, links_, questions, checked=None):
        cards.append(card(
            id=cid,
            type="organization",
            org_kind="regulator",
            name=name,
            summary=[s1, s2, s3],
            claims=[cl(cid + "-c1", s1["text"], s1["status"], s1["sources"], s1["note"])],
            geometry=None,
            map_features=[],
            links=links_,
            checked_empty=checked or [],
            open_questions=questions,
        ))

    regulator(
        "org-carb",
        "California Air Resources Board",
        cl("s1", "EPA skriver at CARB vurderer mobile kilder i San Joaquin Valley, og at CARB vedtok 2024 PM2.5-planen 25. juli 2024.", "confirmed", [pm_ext]),
        cl("s2", "CARB beregnet Aliso Canyon-utslippet til 99 650 tonn metan, pluss minus 9 300, og satte kompensasjonsmengden til 109 000 tonn.", "confirmed", [aliso_pdf]),
        cl("s3", "AB 617 gir CARB ansvar for en enhetlig utslippsrapportering, en overvåkingsplan og en strategi for samfunn med høy samlet belastning.", "confirmed", [ab617]),
        [pm_ext],
        [link("problem", "ca-problem-san-joaquin-air", "Mobile kilder og 2024-planen."), link("problem", "ca-problem-aliso-canyon", "Metanestimatet."), link("bill", "bill-ab-617", "AB 617.")],
        ["En egen CARB-nettside for community air protection med listen over valgte samfunn er ikke åpnet."],
    )
    regulator(
        "org-calgem",
        "California Geologic Energy Management Division",
        cl("s1", "Årsrapporten for 2023 er avgitt etter Public Resources Code avsnitt 3108 og gir olje og gass per fylke.", "confirmed", [calgem]),
        cl("s2", "Kern produserte 89 661 583 fat olje og kondensat. Los Angeles County produserte 8 674 995 fat.", "confirmed", [calgem]),
        cl("s3", "CalGEM beskriver i høringsnotatet at SB 1137 ble stanset av et referendum og fikk virkning igjen i juni 2024.", "confirmed", [src("https://www.conservation.ca.gov/calgem/Documents/SB%201137%20Initial%20Statement%20of%20Reasons.pdf", "SB 1137 Initial Statement of Reasons", "CalGEM")]),
        [calgem],
        [link("problem", "ca-problem-oil-gas-proximity", "Produksjon, vurderinger og helsesonen."), link("bill", "bill-sb-1137", "Reglene CalGEM skriver ut.")],
        ["Et maskinlesbart brønnuttrekk med avstand til bolig er ikke lastet ned."],
    )
    regulator(
        "org-swrcb",
        "State Water Resources Control Board",
        cl("s1", "2025 Needs Assessment teller 390 failing-systemer og 811 964 mennesker per 31. desember 2024.", "confirmed", [needs]),
        cl("s2", "Styret gir PFAS-pålegget og skriver at om lag 3 600 brønner i disadvantaged communities testes.", "confirmed", [pfas_page]),
        cl("s3", "Salton Sea-årsrapporten er avgitt til styret etter Order WR 2017-0134.", "confirmed", [ssmp]),
        [needs],
        [link("problem", "ca-problem-drinking-water", "Failing-listen."), link("problem", "ca-problem-pfas", "PFAS-pålegget."), link("bill", "bill-sb-200", "SAFER-fondet."), link("problem", "ca-problem-salton-sea", "Mottaker av SSMP-rapporten.")],
        ["SAFER-dashbordets dagsferske failing-liste er ikke lastet ned. PDF-en er skjæringsdatoen 31. desember 2024."],
    )
    regulator(
        "org-scaqmd",
        "South Coast Air Quality Management District",
        cl("s1", "Distriktet skriver at South Coast Air Basin er i extreme nonattainment for 2015-ozonstandarden.", "confirmed", [aqmd]),
        cl("s2", "I 2018-regnskapet i samme dokument sto tunge lastebiler for 27 prosent av NOx, og petroleumsraffinering var blant de største stasjonære NOx-kildene etter brensel i bygninger.", "confirmed", [aqmd]),
        cl("s3", "Distriktet publiserte 2015-målingene av seks raffinerier. Anleggene er anonymisert som A til F i sammendraget.", "confirmed", [src("https://www.aqmd.gov/docs/default-source/fenceline_monitoring/project_1/fluxsense_scaqmd2015_project1_finalreport(040717).pdf", "FluxSense refinery report", "South Coast AQMD")]),
        [aqmd],
        [link("problem", "ca-problem-south-coast-air", "Ozonplanen."), link("problem", "ca-problem-refineries", "Raffinerimålingene."), link("bill", "bill-ab-1647", "Distriktet skal lage veiledning for fence-line.")],
        ["Hvilke fysiske anlegg som er Refinery A til F."],
    )
    regulator(
        "org-sjvapcd",
        "San Joaquin Valley Unified Air Pollution Control District",
        cl("s1", "EPA skriver at distriktet etter delstatslov har hovedansvaret for å lage planer for å nå standardene i San Joaquin Valley, sammen med CARB.", "confirmed", [pm_ext]),
        cl("s2", "Distriktet vedtok 2024-planen for 2012-PM2.5-standarden 20. juni 2024. Planen ber om ny frist 31. desember 2030.", "confirmed", [pm_ext]),
        cl("s3", "EPA skriver at distriktet vurderte stasjonære kilder og arealkilder, mens CARB vurderte mobile kilder.", "confirmed", [pm_ext]),
        [pm_ext],
        [link("problem", "ca-problem-san-joaquin-air", "PM2.5- og ozonproblemene i dalen."), link("organization", "org-carb", "Delt ansvar med CARB.")],
        ["Distriktets egen nettside med vedtaket 20. juni 2024 er ikke åpnet. EPA gjengir datoen."],
        [empty("district_site", "Søket stoppet ved Federal Register-teksten. Distriktets nettsted er ikke åpnet.", ["https://www.valleyair.org/"])],
    )
    regulator(
        "org-dwr",
        "Department of Water Resources",
        cl("s1", "DWR peker ut kritisk overtrukne grunnvannsbasseng etter SGMA og publiserer definisjonen av critical overdraft.", "confirmed", [dwr]),
        cl("s2", "Kart-PDF-en lister 21 basseng, hvorav elleve i San Joaquin Valley.", "confirmed", [src("https://water.ca.gov/-/media/DWR-Website/Web-Pages/Programs/Groundwater-Management/Bulletin-118/Critically-Overdrafted-Basins/Files/COD-Basins.pdf", "Critically Overdrafted Basins map", "DWR")]),
        cl("s3", "Polygonet for bassengene er ikke lastet inn i kartet.", "not_found", [src("https://data.ca.gov/dataset/i08-criticallyoverdraftedbasins", "i08 CriticallyOverdraftedBasins", "data.ca.gov")]),
        [dwr],
        [link("problem", "ca-problem-groundwater-overdraft", "Utpekingen av basseng.")],
        ["Nedlasting av geodatabasen og en sjekk av hvilke trakter som ligger inni 5-022.14."],
    )
    regulator(
        "org-oehha",
        "Office of Environmental Health Hazard Assessment",
        cl("s1", "OEHHA publiserer CalEnviroScreen 4.0 med score per census tract og tilbyr nedlasting og en ArcGIS-tjeneste.", "confirmed", [oehha]),
        cl("s2", "Tjenestens metadata har tomt copyrightText-felt. Traktene i kartet er hentet derfra 28. oktober 2026 og er sitert med tract-id.", "confirmed", [src("https://services1.arcgis.com/PCHfdHz4GlDNAhBb/arcgis/rest/services/CalEnviroScreen_4_0_Results_/FeatureServer/0?f=json", "CalEnviroScreen 4.0 layer metadata", "OEHHA")]),
        cl("s3", "Verktøyet er en screening, ikke en måling av at en person er syk. Kortene bruker det som stedsangivelse og indikator, ikke som diagnose.", "confirmed", [oehha]),
        [oehha],
        [link("problem", "ca-problem-san-joaquin-air", "Tract 6019001100."), link("problem", "ca-problem-pesticides", "Pesticidindikatoren."), link("problem", "ca-problem-drinking-water", "Drikkevannsindikatoren.")],
        ["En full tract-flate for persentil over 90 er ikke lagt inn, bare seks trakter."],
    )
    regulator(
        "org-dpr",
        "Department of Pesticide Regulation",
        cl("s1", "DPR publiserer den årlige bruksrapporten. For 2022 er totalsummen 181 millioner pund aktive stoffer.", "confirmed", [dpr]),
        cl("s2", "Fylkes-PDF-en gir pund, søknader og behandlede acre. Fresno, Kern og Tulare er de tre høyeste pundtallene som er lest.", "confirmed", [src("https://www.cdpr.ca.gov/wp-content/uploads/2024/12/2022_county_total_pounds_applied_agricultural_applications_and_acres_treated.pdf", "2022 pesticide pounds by county", "DPR")], "At de er de tre høyeste i hele fylkeslisten, er sjekket mot de fylkene som står i PDF-en som ble hentet."),
        cl("s3", "Rapporten sier at pounds applied vektlegger midler som brukes i store mengder, som svovel, olje og fumiganter, og at acres treated kan være høyere enn dyrket areal fordi samme åker telles flere ganger.", "confirmed", [dpr]),
        [dpr],
        [link("problem", "ca-problem-pesticides", "Bruksrapporten.")],
        ["2023-rapporten, hvis den finnes, er ikke åpnet. 2022 er siste årsrapport som er lest."],
    )
    regulator(
        "org-epa",
        "United States Environmental Protection Agency",
        cl("s1", "Green Book, oppdatert 30. september 2026, er kilden til nonattainment-klassene og 2010-befolkningen for South Coast, San Joaquin Valley og Imperial.", "confirmed", [src("https://www3.epa.gov/airquality/greenbook/rncl2.html", "PM-2.5 Green Book", "US EPA")]),
        cl("s2", "EPA fastslo i 2025 at San Joaquin Valley ikke nådde 1997-ozonstandarden, og omtalte i 2026 dalens årlige PM2.5 som de høyeste i landet.", "confirmed", [src("https://www.federalregister.gov/documents/2025/09/25/2025-18636/finding-of-failure-to-attain-the-1997-8-hour-ozone-standards-california-san-joaquin-valley", "Ozone failure finding", "US EPA"), pm_ext]),
        cl("s3", "ECHO og FRS er kildene til anleggsnavn, registry-id, koordinater og compliance-status for raffineriene og Aliso Canyon.", "confirmed", [echo, frs_chevron]),
        [echo],
        [link("problem", "ca-problem-south-coast-air", "Nonattainment."), link("problem", "ca-problem-san-joaquin-air", "Nonattainment og ozonvedtak."), link("problem", "ca-problem-refineries", "ECHO og FRS.")],
        ["Green Book-siden for PM10 er ikke åpnet."],
    )

    cards.append(card(
        id="firm-carpenter-garcia-sievers",
        type="lobbying_firm",
        name="Carpenter Garcia Sievers LLC",
        summary=[
            cl("s1", "På WSPAs Form 635 for andre kvartal 2025 står firmaet med 90 000,00 dollar i fees, 0 i utlegg, og 90 000,00 dollar this period. Kumulativt til da: 180 396,00 dollar.", "confirmed", [wspa_pdf]),
            cl("s2", "Adressen i skjemaet er Sacramento CA 95811.", "confirmed", [wspa_pdf]),
            cl("s3", "Andre oppdragsgivere enn WSPA er ikke hentet.", "not_found", [src("https://dbsearch.sos.ca.gov/LobbyFirmsSearch.aspx", "Cal-Access Lobbying Firm search", "California Secretary of State")], "Firmaposten i Cal-Access er ikke åpnet."),
        ],
        claims=[cl("c1", "Kvartalstotalen på WSPA-skjemaet, 3 032 226,49 dollar, samsvarer med andre kvartal på aktivitetssiden.", "confirmed", [wspa_pdf, wspa_page])],
        geometry=None,
        map_features=[],
        links=[link("organization", "org-wspa", "Betalingen i andre kvartal 2025.")],
        checked_empty=[empty("other_clients", "LobbyFirmsSearch er ikke kjørt for CARPENTER GARCIA.", ["https://dbsearch.sos.ca.gov/LobbyFirmsSearch.aspx"])],
        open_questions=["Om firmaet i samme kvartal også hadde en offentlig eller klimarelatert oppdragsgiver. Det krever firmaskjemaet, ikke WSPAs skjema alene."],
    ))
    cards.append(card(
        id="firm-greenberg-traurig",
        type="lobbying_firm",
        name="Greenberg Traurig, LLP",
        summary=[
            cl("s1", "WSPAs Form 635 for andre kvartal 2025 fører Greenberg Traurig, LLP, Sacramento, med 37 500,00 dollar this period og 75 000,00 dollar kumulativt.", "confirmed", [wspa_pdf]),
            cl("s2", "Beløpet er det WSPA betalte, ikke firmaets samlede omsetning.", "confirmed", [wspa_pdf]),
            cl("s3", "Andre klienter er ikke hentet.", "not_found", [wspa_pdf]),
        ],
        claims=[cl("c1", "Fees-kolonnen i uttrekket er 37 500,00 og reimbursements 0,00.", "confirmed", [wspa_pdf])],
        geometry=None,
        map_features=[],
        links=[link("organization", "org-wspa", "Oppdragsgiver i det kvartalet.")],
        checked_empty=[empty("other_clients", "Firmaregisteret er ikke slått opp.", ["https://dbsearch.sos.ca.gov/LobbyFirmsSearch.aspx"])],
        open_questions=["Klientlisten for 2025-2026."],
    ))
    cards.append(card(
        id="firm-pillsbury",
        type="lobbying_firm",
        name="Pillsbury Winthrop Shaw Pittman LLP",
        summary=[
            cl("s1", "WSPAs Form 635 for andre kvartal 2025 fører Pillsbury Winthrop Shaw Pittman LLP, San Francisco, med fees 58 570,50 dollar, reimbursements 760,41 dollar og total this period 59 330,91 dollar. Kumulativt 97 727,91 dollar.", "confirmed", [wspa_pdf]),
            cl("s2", "Firmaet er en av flere mottakere. Det er ikke vist at det arbeidet med et bestemt lovforslag.", "not_verified", [wspa_pdf], "Vedlegg A ville vise sakene."),
            cl("s3", "Andre klienter er ikke hentet.", "not_found", [wspa_pdf]),
        ],
        claims=[cl("c1", "Skjemaet sier at summen av kolonne 4 skal føres på linje B. Enkeltfirmaene som er lest, er en del av den linjen, ikke hele linjen.", "confirmed", [wspa_pdf])],
        geometry=None,
        map_features=[],
        links=[link("organization", "org-wspa", "Betalingen i andre kvartal 2025.")],
        checked_empty=[empty("other_clients", "Firmaregisteret er ikke slått opp.", ["https://dbsearch.sos.ca.gov/LobbyFirmsSearch.aspx"])],
        open_questions=["Om samme firma også var engasjert av en offentlig klient i kvartalet."],
    ))
    cards.append(card(
        id="firm-leacox",
        type="lobbying_firm",
        name="Leacox & Associates",
        summary=[
            cl("s1", "WSPAs Form 635 for andre kvartal 2025 fører Leacox & Associates, Carmichael, med 6 000,00 dollar this period og 15 100,00 dollar kumulativt.", "confirmed", [wspa_pdf]),
            cl("s2", "Beløpet er lite sammenlignet med Carpenter Garcia Sievers i samme skjema.", "confirmed", [wspa_pdf]),
            cl("s3", "Andre klienter er ikke hentet.", "not_found", [wspa_pdf]),
        ],
        claims=[cl("c1", "Fees 6 000,00 og reimbursements 0,00 i uttrekket.", "confirmed", [wspa_pdf])],
        geometry=None,
        map_features=[],
        links=[link("organization", "org-wspa", "Oppdragsgiver i det kvartalet.")],
        checked_empty=[empty("other_clients", "Firmaregisteret er ikke slått opp.", ["https://dbsearch.sos.ca.gov/LobbyFirmsSearch.aspx"])],
        open_questions=["Klientlisten."],
    ))

    cards.append(card(
        id="bill-sb-1137",
        type="bill",
        name="SB 1137 (2021-2022), health protection zones",
        summary=[
            cl("s1", "Loven er kapittel 365 av 2022. Den legger artikkel 4.6 til Public Resources Code og definerer health protection zone som 3 200 fot.", "confirmed", [sb1137]),
            cl("s2", "Senatet samtykket 31. august 2022 med 25 ja og 10 nei. Forsamlingen stemte 30. august 2022 med 46 ja og 24 nei. Guvernøren godkjente 16. september 2022.", "confirmed", [sb1137_hist, sb1137_votes]),
            cl("s3", "Forfattere på statussiden er senatorene Gonzalez og Limón.", "confirmed", [src("https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202120220SB1137", "SB 1137 status", "California Legislative Counsel")]),
            cl("s4", "CalGEM beskriver at et referendum stanset loven fra februar 2023 til forslaget ble trukket i juni 2024.", "confirmed", [src("https://www.conservation.ca.gov/calgem/Documents/SB%201137%20Initial%20Statement%20of%20Reasons.pdf", "SB 1137 ISOR", "CalGEM")]),
        ],
        claims=[
            cl("c1", "Navnene på hver ja- og nei-stemme står på votes-siden. Dette kortet gjengir tellingene, ikke hvert navn, for å unngå avskriftsfeil. Siden er kilden.", "confirmed", [sb1137_votes]),
        ],
        geometry=None,
        map_features=[],
        links=[
            link("problem", "ca-problem-oil-gas-proximity", "Loven er kjernen i olje- og gasskortet."),
            link("lawmaker", "lawmaker-lena-gonzalez", "Hovedforfatter."),
            link("organization", "org-calgem", "Etaten som fører sonene."),
        ],
        checked_empty=[empty("lobby_position", "WSPAs vedlegg A er ikke lest, så det er ikke bekreftet at WSPA oppga SB 1137. Loven var fra 2022, mens skjemaet som er lest, er fra 2025.", [wspa_pdf["url"]])],
        open_questions=["Hvilke selskaper som leverte referendum-signaturene. CalGEM sier opponents, uten navn i avsnittet som er lest."],
    ))
    cards.append(card(
        id="bill-sb-200",
        type="bill",
        name="SB 200 (2019), Safe and Affordable Drinking Water Fund",
        summary=[
            cl("s1", "SB 200, kapittel 120 av 2019, forfatter Monning, oppretter Safe and Affordable Drinking Water Fund og viser til retten til trygt drikkevann.", "confirmed", [sb200]),
            cl("s2", "Senatet samtykket 8. juli 2019 med 38 mot 1, med hasteklausul. Forsamlingen vedtok 5. juli 2019 med 68 mot 0. Guvernøren godkjente 24. juli 2019.", "confirmed", [sb200_hist]),
            cl("s3", "State Water Board skriver at loven setter av fem prosent av klimafondet, maks 130 millioner dollar i året, til 30. juni 2030.", "confirmed", [src("https://www.waterboards.ca.gov/safer/docs/safer_program_legislative_history.pdf", "SAFER legislative history", "State Water Board")]),
            cl("s4", "Needs Assessment er et produkt av dette programmet og teller failing-systemene.", "confirmed", [needs]),
        ],
        claims=[cl("c1", "Historikklinjen for forsamlingen sier at hastevedtaket ble lagt frem av Garcia, E. Det er gjengitt som en prosedyrelinje, ikke som et forfatterskap.", "confirmed", [sb200_hist])],
        geometry=None,
        map_features=[],
        links=[
            link("problem", "ca-problem-drinking-water", "Fondet og failing-listen."),
            link("lawmaker", "lawmaker-bill-monning", "Forfatter på lovteksten."),
            link("organization", "org-swrcb", "Styret forvalter fondet."),
        ],
        checked_empty=[empty("campaign_contributions", "Ingen bidrag er koblet til avstemningen. Det ville kreve mottakerlister fra Cal-Access mot navnene på votes-siden.", [])],
        open_questions=["Hvem som stemte nei i senatet. Tellingen er 38-1. Navnet er ikke skrevet av fra siden i dette kortet."],
    ))
    cards.append(card(
        id="bill-ab-617",
        type="bill",
        name="AB 617 (2017), samfunnsovervåking av luft",
        summary=[
            cl("s1", "AB 617, kapittel 136, godkjent 26. juli 2017, forfatter Cristina Garcia. Loven krever utslippsrapportering, en overvåkingsplan og en strategi for samfunn med høy samlet belastning, og gir distriktene hjemmel til å kreve fence-line-måling.", "confirmed", [ab617]),
            cl("s2", "Forsamlingen samtykket 17. juli 2017 med 50 mot 24. Senatet vedtok samme dag med 27 mot 13.", "confirmed", [ab617_votes]),
            cl("s3", "Loven gjelder både South Coast og San Joaquin Valley fordi den er statewide og peker på samfunn med høy belastning, ikke ett basseng.", "confirmed", [ab617]),
        ],
        claims=[cl("c1", "Votes-siden har navnene. Kortet bruker tellingene.", "confirmed", [ab617_votes])],
        geometry=None,
        map_features=[],
        links=[
            link("problem", "ca-problem-south-coast-air", "Samfunnsovervåking i bassenget."),
            link("problem", "ca-problem-san-joaquin-air", "Samfunnsovervåking i dalen."),
            link("lawmaker", "lawmaker-cristina-garcia", "Forfatter på lovteksten."),
            link("organization", "org-carb", "CARB skal lage planen og strategien."),
            link("bill", "bill-ab-1647", "AB 1647 er den raffinerispesifikke måleloven samme år."),
        ],
        checked_empty=[],
        open_questions=["Hvilke communities CARB har valgt i siste års runde, og om noen av tractene i kartet er blant dem."],
    ))
    cards.append(card(
        id="bill-ab-1647",
        type="bill",
        name="AB 1647 (2017), måling ved raffinerier",
        summary=[
            cl("s1", "AB 1647, kapittel 589, godkjent 8. oktober 2017, forfatter Muratsuchi. Loven krever samfunnsmåling nær hvert raffineri og fence-line-måling drevet av eieren, senest 1. januar 2020.", "confirmed", [ab1647]),
            cl("s2", "Forsamlingen samtykket 13. september 2017 med 57 mot 19. Senatet vedtok 11. september 2017 med 28 mot 11.", "confirmed", [ab1647_hist]),
            cl("s3", "Eieren skal betale, med mindre distriktet med vilje bruker stasjonen også til andre kilder. Da skal kostnaden deles.", "confirmed", [ab1647]),
            cl("s4", "Om hvert raffineri i FRS-uttrekket faktisk har et system i drift i 2026, er ikke sjekket mot distriktenes datasider.", "not_verified", [ab1647], "Distriktets offentlige dataside for det enkelte anlegg ville bekrefte drift."),
        ],
        claims=[cl("c1", "Loven viser til veiledning i overvåkingsplanen etter AB 617, Health and Safety Code 42705.5.", "confirmed", [ab1647])],
        geometry=None,
        map_features=[],
        links=[
            link("problem", "ca-problem-refineries", "Fence-line-kravet."),
            link("lawmaker", "lawmaker-al-muratsuchi", "Forfatter."),
            link("organization", "org-scaqmd", "Distriktet i South Coast skal designe samfunnsmålingen."),
            link("bill", "bill-ab-617", "Søsterloven om samfunn og strategi."),
        ],
        checked_empty=[empty("implementation_audit", "Ingen anleggsside er åpnet for å se om fristen 1. januar 2020 er holdt.", [])],
        open_questions=["Hvilke raffinerier som mangler offentlig sanntidsdata i dag."],
    ))

    cards.append(card(
        id="lawmaker-lena-gonzalez",
        type="lawmaker",
        name="Lena A. Gonzalez",
        summary=[
            cl("s1", "Senatets distriktsside oppgir Lena A. Gonzalez som senator for distrikt 33, med capitol-kontor i 1021 O Street, Suite 7510, Sacramento.", "confirmed", [gonzalez]),
            cl("s2", "Distriktsbeskrivelsen på senatorens side omfatter Southeast Los Angeles, Long Beach og havnen, Lakewood, Signal Hill og Catalina Island.", "confirmed", [gonzalez_dist]),
            cl("s3", "Leginfo oppgir henne som lead author på SB 1137, sammen med Limón.", "confirmed", [src("https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202120220SB1137", "SB 1137 status", "California Legislative Counsel")]),
            cl("s4", "Hun står på ja-siden i senatets samtykkevotering 31. august 2022, 25 mot 10.", "confirmed", [sb1137_votes]),
        ],
        claims=[
            cl("c1", "Senatssiden oppgir at hun sitter i Environmental Quality. Komitélisten er lest som verv, ikke som en påstand om hvordan hun stemmer i komiteen.", "confirmed", [gonzalez]),
        ],
        geometry=None,
        map_features=[],
        links=[
            link("bill", "bill-sb-1137", "Forfatter."),
            link("problem", "ca-problem-oil-gas-proximity", "Loven om helsesoner."),
        ],
        checked_empty=[
            empty("campaign_contributions", "ContributorSearch er ikke kjørt med mottaker Lena Gonzalez. Giver-søkene over er ikke koblet til henne.", ["https://dbsearch.sos.ca.gov/"]),
        ],
        open_questions=["Hvor mye hun mottok fra olje- og gassfiler i 2022 og senere. Det krever et mottakersøk, ikke giversummene alene."],
    ))
    cards.append(card(
        id="lawmaker-cristina-garcia",
        type="lawmaker",
        name="Cristina Garcia",
        summary=[
            cl("s1", "AB 617, kapittel 136 av 2017, har Cristina Garcia som forfatter i lovteksten.", "confirmed", [ab617]),
            cl("s2", "Forsamlingens samtykke 17. juli 2017 var 50 mot 24. Votes-siden viser at hun sto på ja-siden i den voteringen.", "confirmed", [ab617_votes]),
            cl("s3", "Distrikt og om hun fortsatt sitter i forsamlingen, er ikke slått opp på assembly.ca.gov i denne runden.", "not_verified", [ab617], "En aktuell medlemsside ville bekrefte vervet i 2026."),
        ],
        claims=[cl("c1", "Kortet bruker bare det lovsiden og votes-siden sier. Ingen biografi er lagt til.", "confirmed", [ab617, ab617_votes])],
        geometry=None,
        map_features=[],
        links=[link("bill", "bill-ab-617", "Forfatter."), link("problem", "ca-problem-south-coast-air", "Loven brukes på begge luftbassengene.")],
        checked_empty=[empty("district", "assembly.ca.gov er ikke åpnet for tidligere distrikt.", ["https://www.assembly.ca.gov/"])],
        open_questions=["Hvilket assembly-distrikt hun representerte i 2017, fra en offisiell side."],
    ))
    cards.append(card(
        id="lawmaker-bill-monning",
        type="lawmaker",
        name="Bill Monning",
        summary=[
            cl("s1", "SB 200, kapittel 120 av 2019, har Monning som forfatter i lovteksten.", "confirmed", [sb200]),
            cl("s2", "Senatet samtykket 8. juli 2019 med 38 mot 1. Historikksiden navngir Monning i voteringsteksten.", "confirmed", [sb200_hist]),
            cl("s3", "Han står også på ja-listen i senatets votering om AB 617 den 17. juli 2017.", "confirmed", [ab617_votes]),
            cl("s4", "Nåværende eller daværende distrikt er ikke slått opp. Han er med som forfatter på lovteksten, ikke som sittende senator i 2026.", "not_verified", [sb200], "En historisk senatsside ville bekrefte distriktet."),
        ],
        claims=[cl("c1", "Ingen personbiografi er hentet.", "not_found", [sb200])],
        geometry=None,
        map_features=[],
        links=[link("bill", "bill-sb-200", "Forfatter."), link("problem", "ca-problem-drinking-water", "Drikkevannsfondet.")],
        checked_empty=[empty("district", "Senatets nåværende medlemsliste er ikke brukt til å gjette et historisk distrikt.", ["https://www.senate.ca.gov/senators"])],
        open_questions=["Distrikt i 2019 og om han fortsatt har et offentlig verv."],
    ))
    cards.append(card(
        id="lawmaker-al-muratsuchi",
        type="lawmaker",
        name="Al Muratsuchi",
        summary=[
            cl("s1", "AB 1647, kapittel 589 av 2017, har Muratsuchi som forfatter i lovteksten.", "confirmed", [ab1647]),
            cl("s2", "Forsamlingen samtykket 13. september 2017 med 57 mot 19.", "confirmed", [ab1647_hist]),
            cl("s3", "Han står også som principal coauthor på SB 1137-statussiden, sammen med flere forsamlingsmedlemmer.", "confirmed", [src("https://leginfo.legislature.ca.gov/faces/billStatusClient.xhtml?bill_id=202120220SB1137", "SB 1137 status", "California Legislative Counsel")]),
            cl("s4", "Distrikt i 2026 er ikke slått opp på assembly.ca.gov.", "not_verified", [ab1647]),
        ],
        claims=[cl("c1", "Votes-siden for AB 1647 med enkeltnavn er ikke åpnet. Historikken gir tellingene. Derfor er det ikke skrevet om han selv stemte ja, bare at han er forfatter og at flertallet vedtok loven.", "not_verified", [ab1647_hist], "billVotesClient for AB 1647 ville vise hans stemme.")],
        geometry=None,
        map_features=[],
        links=[
            link("bill", "bill-ab-1647", "Forfatter."),
            link("bill", "bill-sb-1137", "Principal coauthor på statussiden."),
            link("problem", "ca-problem-refineries", "Fence-line-loven."),
        ],
        checked_empty=[empty("district", "assembly.ca.gov er ikke åpnet.", ["https://www.assembly.ca.gov/"])],
        open_questions=["Hans stemme på AB 1647 og SB 1137, og dagens distrikt."],
    ))
    return cards


if __name__ == "__main__":
    main()
