#!/usr/bin/env python3
"""Write the media catalog, lobbying network, and says-vs-votes tables.

Reads the Cal-Access extracts already parsed into /tmp/ca. Re-running needs
those files. The committed JSON is the record.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRMS = json.loads(Path("/tmp/ca/firms.json").read_text(encoding="utf-8"))
EXTRACT = json.loads(Path("/tmp/ca/extract.json").read_text(encoding="utf-8"))

RETRIEVED = "2026-10-28"
ZIP = "https://campaignfinance.cdn.sos.ca.gov/dbwebexport.zip"
ZIP_ARCHIVE = "http://web.archive.org/web/20260930110449/https://campaignfinance.cdn.sos.ca.gov/dbwebexport.zip"
ZIP_NOTE = "Wayback-øyeblikksbilde av zip-filen. Radene er lest i uttrekket som var datert 28. oktober 2026 i filhodet."

EMPLOYER_CARD = {
    "1146815": "org-chevron",
    "1147195": "org-wspa",
    "1146650": "org-cipa",
    "1374043": "org-crc",
    "1420515": "org-berry",
    "1244770": "org-marathon",
    "1408198": "org-pbf",
    "1382832": "org-pbf",
    "1348342": "org-phillips66",
    "1147122": "org-phillips66",
    "1146926": "org-sempra",
    "1237027": "org-valero",
    "1143378": "org-iid",
    "1146790": "org-farm-bureau",
    "1146857": "org-western-growers",
    "1146862": "org-corteva",
}

ORG_NAME = {
    "org-chevron": "Chevron U.S.A. Inc. and Affiliates",
    "org-wspa": "Western States Petroleum Association",
    "org-cipa": "California Independent Petroleum Association",
    "org-crc": "California Resources Corporation",
    "org-berry": "Berry Corporation",
    "org-marathon": "Marathon Petroleum",
    "org-pbf": "PBF",
    "org-phillips66": "Phillips 66",
    "org-sempra": "Sempra and affiliates, including SoCalGas",
    "org-valero": "Valero Services, Inc.",
    "org-iid": "Imperial Irrigation District",
    "org-farm-bureau": "California Farm Bureau Federation",
    "org-western-growers": "Western Growers",
    "org-corteva": "Corteva Agriscience LLC",
}

ORG_PROBLEMS = {
    "org-chevron": ["ca-problem-oil-gas-proximity", "ca-problem-refineries"],
    "org-wspa": ["ca-problem-oil-gas-proximity", "ca-problem-refineries"],
    "org-cipa": ["ca-problem-oil-gas-proximity"],
    "org-crc": ["ca-problem-oil-gas-proximity"],
    "org-berry": ["ca-problem-oil-gas-proximity"],
    "org-marathon": ["ca-problem-refineries", "ca-problem-oil-gas-proximity"],
    "org-pbf": ["ca-problem-refineries"],
    "org-phillips66": ["ca-problem-refineries"],
    "org-sempra": ["ca-problem-aliso-canyon"],
    "org-valero": ["ca-problem-refineries"],
    "org-iid": ["ca-problem-salton-sea"],
    "org-farm-bureau": ["ca-problem-pesticides", "ca-problem-groundwater-overdraft"],
    "org-western-growers": ["ca-problem-pesticides", "ca-problem-groundwater-overdraft"],
    "org-corteva": ["ca-problem-pesticides"],
}

POLITICIANS = {
    "grove": ("lawmaker-shannon-grove", "Shannon Grove", "senat 12", ["ca-problem-oil-gas-proximity", "ca-problem-san-joaquin-air", "ca-problem-pesticides", "ca-problem-groundwater-overdraft"]),
    "hurtado": ("lawmaker-melissa-hurtado", "Melissa Hurtado", "senat 16", ["ca-problem-oil-gas-proximity", "ca-problem-san-joaquin-air", "ca-problem-pesticides", "ca-problem-drinking-water", "ca-problem-groundwater-overdraft"]),
    "caballero": ("lawmaker-anna-caballero", "Anna M. Caballero", "senat 14", ["ca-problem-san-joaquin-air", "ca-problem-pesticides", "ca-problem-groundwater-overdraft", "ca-problem-drinking-water"]),
    "limon": ("lawmaker-monique-limon", "Monique Limón", "senat 21", ["ca-problem-oil-gas-proximity"]),
    "stern": ("lawmaker-henry-stern", "Henry Stern", "senat 27", ["ca-problem-aliso-canyon", "ca-problem-oil-gas-proximity"]),
    "padilla": ("lawmaker-steve-padilla", "Steve Padilla", "senat 18", ["ca-problem-salton-sea", "ca-problem-pesticides"]),
    "allen": ("lawmaker-benjamin-allen", "Benjamin Allen", "senat 24", ["ca-problem-refineries", "ca-problem-pfas", "ca-problem-south-coast-air"]),
    "alvarado": ("lawmaker-marie-alvarado-gil", "Marie Alvarado-Gil", "senat 4", ["ca-problem-groundwater-overdraft", "ca-problem-pesticides", "ca-problem-san-joaquin-air"]),
    "grayson": ("lawmaker-tim-grayson", "Tim Grayson", "senat 9", ["ca-problem-refineries", "ca-problem-south-coast-air"]),
    "ochoa": ("lawmaker-rosilicie-ochoa-bogh", "Rosilicie Ochoa Bogh", "senat 19", ["ca-problem-south-coast-air", "ca-problem-salton-sea"]),
    "reyes": ("lawmaker-eloise-gomez-reyes", "Eloise Gómez Reyes", "senat 29", ["ca-problem-south-coast-air"]),
    "laird": ("lawmaker-john-laird", "John Laird", "senat 17", ["ca-problem-pesticides", "ca-problem-drinking-water"]),
    "valladares": ("lawmaker-suzette-valladares", "Suzette Martinez Valladares", "senat 23", ["ca-problem-oil-gas-proximity", "ca-problem-south-coast-air"]),
    "menjivar": ("lawmaker-caroline-menjivar", "Caroline Menjivar", "senat 20", ["ca-problem-south-coast-air"]),
    "bains": ("lawmaker-jasmeet-bains", "Jasmeet Kaur Bains", "forsamling 35", ["ca-problem-oil-gas-proximity", "ca-problem-san-joaquin-air", "ca-problem-pesticides"]),
    "schiavo": ("lawmaker-pilar-schiavo", "Pilar Schiavo", "forsamling 40", ["ca-problem-aliso-canyon"]),
    "arambula": ("lawmaker-joaquin-arambula", "Joaquin Arambula", "forsamling 31", ["ca-problem-san-joaquin-air", "ca-problem-drinking-water", "ca-problem-pesticides"]),
    "gipson": ("lawmaker-mike-gipson", "Mike A. Gipson", "forsamling 65", ["ca-problem-refineries", "ca-problem-south-coast-air"]),
    "wilson": ("lawmaker-lori-wilson", "Lori D. Wilson", "forsamling 11", ["ca-problem-refineries"]),
    "muratsuchi": ("lawmaker-al-muratsuchi", "Al Muratsuchi", "forsamling 66", ["ca-problem-refineries", "ca-problem-south-coast-air"]),
    "connolly": ("lawmaker-damon-connolly", "Damon Connolly", "forsamling 12", ["ca-problem-pesticides"]),
    "soria": ("lawmaker-esmeralda-soria", "Esmeralda Z. Soria", "forsamling 27", ["ca-problem-san-joaquin-air", "ca-problem-pesticides", "ca-problem-groundwater-overdraft"]),
    "macedo": ("lawmaker-alexandra-macedo", "Alexandra M. Macedo", "forsamling 33", ["ca-problem-pesticides", "ca-problem-san-joaquin-air"]),
    "flora": ("lawmaker-heath-flora", "Heath Flora", "forsamling 9", ["ca-problem-san-joaquin-air", "ca-problem-pesticides", "ca-problem-oil-gas-proximity"]),
    "bennett": ("lawmaker-steve-bennett", "Steve Bennett", "forsamling 38", ["ca-problem-oil-gas-proximity"]),
    "wicks": ("lawmaker-buffy-wicks", "Buffy Wicks", "forsamling 14", ["ca-problem-refineries", "ca-problem-south-coast-air"]),
    "lowenthal": ("lawmaker-josh-lowenthal", "Josh Lowenthal", "forsamling 69", ["ca-problem-refineries", "ca-problem-south-coast-air"]),
    "gonzalez-lena": ("lawmaker-lena-gonzalez", "Lena A. Gonzalez", "senat 33", ["ca-problem-oil-gas-proximity", "ca-problem-south-coast-air", "ca-problem-refineries"]),
    "gonzalez-jeff": ("lawmaker-jeff-gonzalez", "Jeff Gonzalez", "forsamling 36", ["ca-problem-salton-sea", "ca-problem-pesticides"]),
}

VOTE_ARCHIVE = {
    "202120220SB1137": "http://web.archive.org/web/20250920054954/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202120220SB1137",
    "202320240AB1864": "http://web.archive.org/web/20260117220802/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202320240AB1864",
    "202320240AB3233": "http://web.archive.org/web/20250918105303/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202320240AB3233",
    "202120220SB1486": "http://web.archive.org/web/20250918170037/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202120220SB1486",
    "202320240SB305": "http://web.archive.org/web/20260118213538/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202320240SB305",
    "201920200SB1044": "http://web.archive.org/web/20250918223637/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201920200SB1044",
    "202120220AB1817": "http://web.archive.org/web/20250525034750/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202120220AB1817",
    "201920200AB756": "http://web.archive.org/web/20250321182546/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201920200AB756",
    "202120220AB1200": "http://web.archive.org/web/20251010130847/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202120220AB1200",
    "201920200SB200": "http://web.archive.org/web/20250529021927/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201920200SB200",
    "201720180AB617": "http://web.archive.org/web/20250531134318/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201720180AB617",
    "201720180AB1647": "http://web.archive.org/web/20250919093406/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201720180AB1647",
    "201520160SB380": "http://web.archive.org/web/20250923160035/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201520160SB380",
}

BILLS = {
    "bill-sb-1137": ("SB 1137 (2021-2022)", "202120220SB1137", ["ca-problem-oil-gas-proximity"], "bill-sb-1137"),
    "bill-ab-1864": ("AB 1864 (2023-2024)", "202320240AB1864", ["ca-problem-pesticides"], ""),
    "bill-ab-3233": ("AB 3233 (2023-2024)", "202320240AB3233", ["ca-problem-oil-gas-proximity"], ""),
    "bill-sb-1486": ("SB 1486 (2021-2022)", "202120220SB1486", ["ca-problem-aliso-canyon"], ""),
    "bill-sb-305": ("SB 305 (2023-2024)", "202320240SB305", ["ca-problem-aliso-canyon"], ""),
    "bill-sb-1044": ("SB 1044 (2019-2020)", "201920200SB1044", ["ca-problem-pfas"], ""),
    "bill-ab-1817": ("AB 1817 (2021-2022)", "202120220AB1817", ["ca-problem-pfas"], ""),
    "bill-ab-756": ("AB 756 (2019-2020)", "201920200AB756", ["ca-problem-pfas", "ca-problem-drinking-water"], ""),
    "bill-ab-1200": ("AB 1200 (2021-2022)", "202120220AB1200", ["ca-problem-pfas"], ""),
    "bill-sb-200": ("SB 200 (2019-2020)", "201920200SB200", ["ca-problem-drinking-water"], "bill-sb-200"),
    "bill-ab-617": ("AB 617 (2017-2018)", "201720180AB617", ["ca-problem-south-coast-air", "ca-problem-san-joaquin-air"], "bill-ab-617"),
    "bill-ab-1647": ("AB 1647 (2017-2018)", "201720180AB1647", ["ca-problem-refineries"], "bill-ab-1647"),
    "bill-sb-380": ("SB 380 (2015-2016)", "201520160SB380", ["ca-problem-aliso-canyon"], ""),
}

PROBLEMS = [
    ("ca-problem-south-coast-air", "South Coast-luft"),
    ("ca-problem-san-joaquin-air", "San Joaquin-luft"),
    ("ca-problem-drinking-water", "Drikkevann"),
    ("ca-problem-oil-gas-proximity", "Olje og gass nær boliger"),
    ("ca-problem-pesticides", "Plantevernmidler"),
    ("ca-problem-salton-sea", "Salton Sea"),
    ("ca-problem-refineries", "Raffinerier"),
    ("ca-problem-aliso-canyon", "Aliso Canyon"),
    ("ca-problem-pfas", "PFAS"),
    ("ca-problem-groundwater-overdraft", "Kritisk overtrekk av grunnvann"),
]


def source(url: str, title: str, publisher: str, archive: str, note: str) -> dict:
    return {
        "url": url,
        "title": title,
        "publisher": publisher,
        "retrieved": RETRIEVED,
        "archive_url": archive,
        "archive_note": note,
    }


def zip_source(title: str) -> dict:
    return source(ZIP, title, "California Secretary of State", ZIP_ARCHIVE, ZIP_NOTE)


def vote_source(bill_key: str) -> dict:
    live = f"https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id={bill_key}"
    return source(
        live,
        f"Bill votes {bill_key}",
        "California Legislative Counsel",
        VOTE_ARCHIVE[bill_key],
        "Direkte kall til leginfo fikk HTTP 403 den 2026-10-28. Navnelisten er lest i dette Wayback-øyeblikksbildet.",
    )


def main() -> None:
    nodes = []
    edges = []
    seen = set()

    def add_node(node: dict) -> None:
        if node["id"] in seen:
            return
        seen.add(node["id"])
        nodes.append(node)

    def add_edge(edge: dict) -> None:
        edges.append(edge)

    for pid, name in PROBLEMS:
        add_node({
            "id": pid,
            "type": "problem",
            "name": name,
            "card_id": pid,
            "problems": [pid],
            "detail": "Problemkortet i data/cards.",
            "sources": [],
        })

    for bid, (name, key, problems, card) in BILLS.items():
        add_node({
            "id": bid,
            "type": "bill",
            "name": name,
            "card_id": card,
            "problems": problems,
            "detail": "Tittelen er hentet fra tittel-feltet på den arkiverte stemmesiden.",
            "sources": [vote_source(key)],
        })
        for problem in problems:
            add_edge({
                "id": f"relates-{bid}-{problem}",
                "type": "relates_to",
                "from": bid,
                "to": problem,
                "status": "confirmed",
                "note": "",
                "detail": "Stemmesidens tittel navngir saken. Det er ikke en vurdering av hele lovteksten.",
                "sources": [vote_source(key)],
            })

    for key, (pid, name, seat, problems) in POLITICIANS.items():
        add_node({
            "id": pid,
            "type": "politician",
            "name": name,
            "card_id": pid,
            "problems": problems,
            "detail": f"Sete i 2025-26-håndboken: {seat}. Kortet fylles i egne filer der det ikke fantes fra før.",
            "sources": [source(
                "https://www.senate.ca.gov/system/files/2026-09/joint_handbook_2025-26_web_1.pdf",
                "California Legislature Handbook 2025-26",
                "California State Senate",
                "",
                "Wayback er ikke slått opp for PDF-en i dette steget. Siden er lest 2026-10-28 via senatets fil.",
            )],
        })

    for employer, card in EMPLOYER_CARD.items():
        add_node({
            "id": card,
            "type": "organization",
            "name": ORG_NAME.get(card, card),
            "card_id": card,
            "problems": ORG_PROBLEMS[card],
            "detail": f"Cal-Access-filer {employer}. Navn og lobbytall står på organisasjonskortet.",
            "sources": [zip_source(f"FILER_LINKS_CD and employer filer {employer}")],
        })

    firm_clients: dict[str, list[dict]] = {}
    for firm in FIRMS["firms"]:
        fid = f"firm-{firm['id']}"
        targets = [EMPLOYER_CARD[item] for item in firm["targets"] if item in EMPLOYER_CARD]
        problems = sorted({p for card in targets for p in ORG_PROBLEMS.get(card, [])})
        firm_clients[fid] = firm["clients"]
        add_node({
            "id": fid,
            "type": "lobbying_firm",
            "name": firm["name"],
            "card_id": "",
            "problems": problems,
            "detail": (
                f"Filer {firm['id']}. Siste navnestreng i FILERNAME_CD. "
                f"Oppdragsgivere i sesjon 2025, aktive 12004-rader: {len(firm['clients'])}. "
                f"Lobbyister på 12008: {len(firm['lobbyists'])}."
            ),
            "clients": firm["clients"],
            "sources": [zip_source("FILER_LINKS_CD session 2025 LINK_TYPE 12004 and FILERNAME_CD")],
        })
        for client in firm["clients"]:
            if client["id"] not in EMPLOYER_CARD:
                continue
            add_edge({
                "id": f"represents-{firm['id']}-{client['id']}",
                "type": "represents",
                "from": fid,
                "to": EMPLOYER_CARD[client["id"]],
                "status": "confirmed",
                "note": "",
                "detail": f"12004, A={firm['id']} ({firm['name']}), B={client['id']} ({client['name']}). Aktiv, ingen sluttdato.",
                "sources": [zip_source("FILER_LINKS_CD session 2025 LINK_TYPE 12004")],
            })
        for person in firm["lobbyists"]:
            lid = f"lobbyist-{person['id']}"
            add_node({
                "id": lid,
                "type": "lobbyist",
                "name": person["name"],
                "card_id": "",
                "problems": problems,
                "firm_id": fid,
                "firm_name": firm["name"],
                "clients": firm["clients"],
                "detail": "Registrert på firmaet i sesjon 2025. Klientlisten er firmaets, ikke en personlig saksliste.",
                "sources": [zip_source("FILER_LINKS_CD session 2025 LINK_TYPE 12008")],
            })
            add_edge({
                "id": f"employed-{person['id']}-{firm['id']}",
                "type": "employed_by",
                "from": lid,
                "to": fid,
                "status": "confirmed",
                "note": "",
                "detail": f"12008, A={firm['id']}, B={person['id']}.",
                "sources": [zip_source("FILER_LINKS_CD session 2025 LINK_TYPE 12008")],
            })
            for client in firm["clients"]:
                if client["id"] not in EMPLOYER_CARD:
                    continue
                add_edge({
                    "id": f"roster-{person['id']}-{client['id']}",
                    "type": "firm_roster",
                    "from": lid,
                    "to": EMPLOYER_CARD[client["id"]],
                    "status": "indication",
                    "note": "Personen er registrert på firmaet, og firmaet er registrert for oppdragsgiveren. Skjemaet navngir ikke personen på den enkelte saken.",
                    "detail": f"12008 pluss 12004. Firma {firm['name']}.",
                    "sources": [zip_source("FILER_LINKS_CD session 2025 LINK_TYPE 12008 and 12004")],
                })

    for person in FIRMS["inhouse"]:
        lid = f"lobbyist-{person['id']}"
        employer = person["employer"]
        card = EMPLOYER_CARD.get(employer, "")
        add_node({
            "id": lid,
            "type": "lobbyist",
            "name": person["name"],
            "card_id": "",
            "problems": ORG_PROBLEMS.get(card, []),
            "firm_id": "",
            "firm_name": "",
            "employer_id": employer,
            "clients": [{"id": employer, "name": person["employer_name"]}],
            "detail": "Intern lobbyist, LINK_TYPE 12002. A er oppdragsgiver, B er personen.",
            "sources": [zip_source("FILER_LINKS_CD session 2025 LINK_TYPE 12002")],
        })
        if card:
            add_edge({
                "id": f"inhouse-{person['id']}-{employer}",
                "type": "employed_by",
                "from": lid,
                "to": card,
                "status": "confirmed",
                "note": "",
                "detail": f"12002, A={employer} ({person['employer_name']}), B={person['id']} ({person['name']}).",
                "sources": [zip_source("FILER_LINKS_CD session 2025 LINK_TYPE 12002")],
            })

    for row in EXTRACT["contributions"]:
        pol = POLITICIANS.get(row["politician_key"])
        if not pol:
            continue
        add_edge({
            "id": f"money-{row['filing_id']}-{row['politician_key']}-{row['date'].replace('/', '')}-{row['amount']}",
            "type": "contributed_to",
            "from": row["employer_card"],
            "to": pol[0],
            "status": "confirmed",
            "note": "Beløpet er det skjema 635 fører. Det sier ikke at bidraget endret en stemme.",
            "detail": f"{row['date']}: {row['amount']} dollar til «{row['recipient']}», mottaker-id {row['recipient_id']}, filing {row['filing_id']}, giver-filer {row['employer_id']}.",
            "amount_usd": row["amount"],
            "date": row["date"],
            "sources": [zip_source(f"LCCM_CD filing {row['filing_id']} joined to CVR_LOBBY_DISCLOSURE_CD")],
        })

    # Curated floor votes. side is yes, no, or nvr. Counts are the page totals.
    votes = [
        ("2022-08-31", "202120220SB1137", "bill-sb-1137", "Senate Floor", "25", "10", "Unfinished Business SB1137 Gonzalez et al. Concurrence", {
            "grove": "no", "hurtado": "no", "caballero": "yes", "limon": "yes", "stern": "yes", "allen": "yes", "ochoa": "no", "laird": "yes", "gonzalez-lena": "yes",
        }),
        ("2022-08-30", "202120220SB1137", "bill-sb-1137", "Assembly Floor", "46", "24", "SB 1137 Gonzalez Senate Third Reading By BRYAN", {
            "muratsuchi": "yes", "valladares": "no", "arambula": "nvr", "gipson": "yes", "flora": "no", "grayson": "nvr", "reyes": "yes", "wicks": "yes", "wilson": "yes", "bennett": "yes",
        }),
        ("2022-05-12", "202120220SB1137", "bill-sb-1137", "Senate Floor", "35", "0", "Consent Calendar SB1137", {
            "grove": "nvr", "hurtado": "yes", "caballero": "yes", "limon": "yes", "stern": "yes", "allen": "yes", "ochoa": "yes", "laird": "yes",
        }),
        ("2024-08-28", "202320240AB1864", "bill-ab-1864", "Assembly Floor", "64", "10", "AB 1864 Connolly Concurrence in Senate Amendments", {
            "muratsuchi": "yes", "bains": "yes", "schiavo": "yes", "arambula": "yes", "gipson": "yes", "connolly": "yes", "soria": "yes", "flora": "yes", "grayson": "yes", "reyes": "yes", "wicks": "yes", "wilson": "yes", "lowenthal": "yes", "bennett": "yes",
        }),
        ("2024-08-27", "202320240AB1864", "bill-ab-1864", "Senate Floor", "33", "5", "Assembly 3rd Reading AB1864 Connolly et al. By Hurtado", {
            "grove": "no", "hurtado": "yes", "caballero": "yes", "limon": "yes", "stern": "yes", "allen": "yes", "ochoa": "nvr", "laird": "yes", "padilla": "yes", "menjivar": "yes", "alvarado": "nvr",
        }),
        ("2024-05-21", "202320240AB1864", "bill-ab-1864", "Assembly Floor", "47", "14", "AB 1864 Connolly Assembly Third Reading", {
            "bains": "nvr", "soria": "nvr", "flora": "no", "connolly": "yes", "muratsuchi": "yes", "schiavo": "yes", "arambula": "yes", "gipson": "yes", "grayson": "yes", "reyes": "yes", "wicks": "yes", "wilson": "yes", "lowenthal": "yes", "bennett": "yes",
        }),
        ("2024-08-31", "202320240AB3233", "bill-ab-3233", "Assembly Floor", "46", "15", "AB 3233 Addis Concurrence in Senate Amendments", {
            "bains": "no", "muratsuchi": "yes", "schiavo": "yes", "arambula": "yes", "gipson": "nvr", "connolly": "yes", "soria": "nvr", "flora": "nvr", "grayson": "nvr", "reyes": "yes", "wicks": "yes", "wilson": "nvr", "lowenthal": "yes", "bennett": "yes",
        }),
        ("2024-08-31", "202320240AB3233", "bill-ab-3233", "Senate Floor", "21", "12", "Assembly 3rd Reading AB3233 Addis et al. By Laird", {
            "grove": "no", "hurtado": "no", "caballero": "yes", "limon": "yes", "stern": "yes", "allen": "yes", "ochoa": "no", "laird": "yes", "padilla": "yes", "menjivar": "yes", "alvarado": "no",
        }),
        ("2022-05-26", "202120220SB1486", "bill-sb-1486", "Senate Floor", "5", "12", "Senate 3rd Reading SB1486 Stern et al.", {
            "grove": "yes", "hurtado": "nvr", "caballero": "nvr", "limon": "no", "stern": "no", "allen": "no", "ochoa": "yes", "laird": "nvr",
        }),
        ("2023-05-15", "202320240SB305", "bill-sb-305", "Senate Floor", "38", "0", "Senate 3rd Reading SB305 Stern et al.", {
            "grove": "yes", "hurtado": "yes", "caballero": "yes", "limon": "yes", "stern": "yes", "allen": "yes", "ochoa": "yes", "laird": "yes", "padilla": "yes", "menjivar": "yes", "alvarado": "yes",
        }),
        ("2020-08-30", "201920200SB1044", "bill-sb-1044", "Senate Floor", "39", "0", "Unfinished Business SB1044 Allen et al. Concurrence", {
            "grove": "yes", "hurtado": "yes", "caballero": "yes", "stern": "yes", "allen": "yes",
        }),
        ("2022-08-29", "202120220AB1817", "bill-ab-1817", "Senate Floor", "28", "8", "Assembly 3rd Reading AB1817 Ting et al. By McGuire", {
            "grove": "no", "hurtado": "nvr", "caballero": "yes", "limon": "yes", "stern": "yes", "allen": "yes", "ochoa": "nvr", "laird": "yes",
        }),
        ("2022-08-30", "202120220AB1817", "bill-ab-1817", "Assembly Floor", "56", "2", "AB 1817 Ting Concurrence in Senate Amendments", {
            "muratsuchi": "yes", "valladares": "yes", "flora": "no", "arambula": "yes", "gipson": "yes", "grayson": "yes", "reyes": "yes", "wicks": "yes", "wilson": "yes", "bennett": "yes",
        }),
        ("2019-07-05", "201920200AB756", "bill-ab-756", "Senate Floor", "21", "3", "Assembly 3rd Reading AB756 Cristina Garcia By Allen", {
            "grove": "nvr", "hurtado": "yes", "caballero": "nvr", "stern": "nvr", "allen": "yes",
        }),
        ("2019-07-08", "201920200SB200", "bill-sb-200", "Senate Floor", "38", "1", "Unfinished Business SB200 Monning et al. Urgency Clause Concurrence", {
            "grove": "yes", "hurtado": "yes", "caballero": "yes", "stern": "yes", "allen": "yes",
        }),
    ]
    for date, key, bid, location, ayes, noes, motion, people in votes:
        for person, side in people.items():
            pol = POLITICIANS[person]
            note = ""
            status = "confirmed"
            if key == "202120220SB1137" and date == "2022-05-12":
                note = "Dette er samtykkekalenderen i mai. Filen sammenligner ikke den teksten med august-versjonen som ble den vedtatte loven."
                status = "confirmed"
            if "Reconsider" in motion:
                note = "Forslaget er en omkamp, ikke selve loven."
            if key == "202120220SB1486" and person == "stern" and side == "no":
                note = "Forfatteren står i nei-kolonnen. Det finnes ikke et golvreferat i denne filen som forklarer nei-stemmen."
            add_edge({
                "id": f"vote-{date}-{key}-{location.split()[0]}-{person}",
                "type": "voted_on",
                "from": pol[0],
                "to": bid,
                "status": status,
                "note": note,
                "detail": f"{date} {location}. {motion}. Totalt {ayes} ja og {noes} nei. {pol[1]} er ført som {side}. NVR betyr fraværende, avstår eller ikke stemt, slik siden selv forklarer forkortelsen.",
                "vote": side,
                "date": date,
                "sources": [vote_source(key)],
            })

    statements = [
        ("lawmaker-shannon-grove", "bill-sb-1137", "confirmed", "",
         "Kontorsiden gjengir 16. september 2022 at SB 1137 vil tvinge tusenvis av oljebrønner til å stoppe produksjonen, og at loven flytter produksjon til land med svakere regler.",
         "https://sr12.senate.ca.gov/content/senator-grove-reacts-signing-senate-bill-1137",
         "Senator Grove Reacts to Signing of Senate Bill 1137", "Office of Senator Shannon Grove"),
        ("lawmaker-monique-limon", "bill-sb-1137", "confirmed", "Sitatet står på senator Gonzalez sin nyhetsside, og siden tilskriver det senator Limón.",
         "Siden siterer Limón 16. september 2022: hun er stolt av å ha stått sammen med Gonzalez for en lov som skal verne lokalsamfunn, etter flere år med arbeid om avstandskrav.",
         "https://sd33.senate.ca.gov/news/senator-gonzalez-and-senator-limons-historic-bill-end-neighborhood-oil-and-gas-drilling-signed",
         "Senator Gonzalez and Senator Limon bill signed, quote attributed to Limon", "Office of Senator Lena A. Gonzalez"),
        ("lawmaker-lena-gonzalez", "bill-sb-1137", "confirmed", "",
         "Samme side siterer Gonzalez 16. september 2022 om at nærhet til brønner treffer lokalsamfunn som allerede har høyere risiko for astma, hjertesykdom og kreft, og at SB 1137 skal endre det.",
         "https://sd33.senate.ca.gov/news/senator-gonzalez-and-senator-limons-historic-bill-end-neighborhood-oil-and-gas-drilling-signed",
         "Senator Gonzalez and Senator Limon bill signed", "Office of Senator Lena A. Gonzalez"),
        ("lawmaker-henry-stern", "ca-problem-aliso-canyon", "confirmed", "",
         "5. desember 2024 sier Stern at målet er å stenge Aliso, og at en forlengelse til 2039 går mot det han omtaler som signaler fra guvernøren, lovgiveren og lokalsamfunnet.",
         "https://sd27.senate.ca.gov/news/sen-stern-asm-schiavo-look-expedite-closure-aliso-canyon-discounts-energy-upgrades-san",
         "Stern and Schiavo on Aliso Canyon closure funding", "Office of Senator Henry Stern"),
        ("lawmaker-pilar-schiavo", "ca-problem-aliso-canyon", "confirmed", "Sitatet står på senator Stern sin nyhetsside og tilskrives Schiavo.",
         "Samme melding siterer Schiavo: hun gjentar kravet om å stenge Aliso Canyon, og omtaler 71 millioner dollar fra bøter etter lekkasjen til elektriske oppvarmingsløsninger i dalen.",
         "https://sd27.senate.ca.gov/news/sen-stern-asm-schiavo-look-expedite-closure-aliso-canyon-discounts-energy-upgrades-san",
         "Stern and Schiavo on Aliso Canyon closure funding", "Office of Senator Henry Stern"),
    ]
    for index, (pid, target, status, note, detail, url, title, publisher) in enumerate(statements):
        add_edge({
            "id": f"stated-{index}-{pid}",
            "type": "stated",
            "from": pid,
            "to": target,
            "status": status,
            "note": note,
            "detail": detail,
            "sources": [source(url, title, publisher, "", "Wayback er ikke slått opp for denne nyhetssiden i dette steget. Siden er lest 2026-10-28.")],
        })

    # WSPA Form 635 activity, from the archived PDF text read 2026-10-28.
    add_edge({
        "id": "lobbied-wspa-setback-2025q2",
        "type": "lobbied_on",
        "from": "org-wspa",
        "to": "ca-problem-oil-gas-proximity",
        "status": "indication",
        "note": "Skjemaet sier «DEPARTMENT OF CONSERVATION/CALGEM: SETBACK RULE». Det skriver ikke SB 1137 og ikke om WSPA støttet eller motarbeidet regelen.",
        "detail": "Form 635, filing 3070933, periode 1. april til 30. juni 2025. Tekststrengen i PDF-en nevner også en rekke AB- og SB-numre og «AB 617 IMPLEMENTATION» hos CARB.",
        "sources": [source(
            "https://cal-access.sos.ca.gov/PDFGen/pdfgen.prg?filingid=3070933&amendid=0",
            "Form 635 filing 3070933, Western States Petroleum Association",
            "California Secretary of State",
            "http://web.archive.org/web/20251002191218/https://cal-access.sos.ca.gov/PDFGen/pdfgen.prg?filingid=3070933&amendid=0",
            "PDF-teksten er lest fra Wayback-øyeblikksbildet 2026-10-28.",
        )],
    })
    add_edge({
        "id": "lobbied-wspa-ab617-2025q2",
        "type": "lobbied_on",
        "from": "org-wspa",
        "to": "bill-ab-617",
        "status": "confirmed",
        "note": "",
        "detail": "Samme PDF inneholder strengen «CALIFORNIA AIR RESOURCES BOARD: AB 617 IMPLEMENTATION». Posisjon er ikke skrevet.",
        "sources": [source(
            "https://cal-access.sos.ca.gov/PDFGen/pdfgen.prg?filingid=3070933&amendid=0",
            "Form 635 filing 3070933, Western States Petroleum Association",
            "California Secretary of State",
            "http://web.archive.org/web/20251002191218/https://cal-access.sos.ca.gov/PDFGen/pdfgen.prg?filingid=3070933&amendid=0",
            "PDF-teksten er lest fra Wayback-øyeblikksbildet 2026-10-28.",
        )],
    })

    payload_nodes = {"schema_version": "1.0.0", "retrieved": RETRIEVED, "nodes": nodes}
    payload_edges = {"schema_version": "1.0.0", "retrieved": RETRIEVED, "edges": edges}
    for folder in (ROOT / "data" / "network", ROOT / "public" / "data" / "network"):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "nodes.json").write_text(json.dumps(payload_nodes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (folder / "edges.json").write_text(json.dumps(payload_edges, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"nodes {len(nodes)} edges {len(edges)}")


if __name__ == "__main__":
    main()
