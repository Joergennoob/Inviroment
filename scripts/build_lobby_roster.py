#!/usr/bin/env python3
"""Build data/lobby/roster.json from the Cal-Access firm extract and existing cards.

The both-sides flag stays off unless a firm’s 2025 clients include both a
fossil-fuel filer and an environmental or clean-energy filer. A name that only
sounds green is not enough.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRMS = json.loads(Path("/tmp/ca/firms.json").read_text(encoding="utf-8"))
EXTRACT = json.loads(Path("/tmp/ca/extract.json").read_text(encoding="utf-8"))

EMPLOYER = {
    "1146815": ("org-chevron", ["ca-problem-oil-gas-proximity", "ca-problem-refineries"], 19279518.27),
    "1147195": ("org-wspa", ["ca-problem-oil-gas-proximity", "ca-problem-refineries", "ca-problem-south-coast-air", "ca-problem-san-joaquin-air"], 19031326.51),
    "1146650": ("org-cipa", ["ca-problem-oil-gas-proximity"], 744330.97),
    "1374043": ("org-crc", ["ca-problem-oil-gas-proximity"], 1524830.24),
    "1420515": ("org-berry", ["ca-problem-oil-gas-proximity"], 183000.00),
    "1244770": ("org-marathon", ["ca-problem-refineries", "ca-problem-oil-gas-proximity"], 1321231.64),
    "1408198": ("org-pbf", ["ca-problem-refineries"], 593436.59),
    "1382832": ("org-pbf", ["ca-problem-refineries"], 492320.02),
    "1348342": ("org-phillips66", ["ca-problem-refineries"], 1982009.15),
    "1146926": ("org-sempra", ["ca-problem-aliso-canyon"], 3347511.14),
    "1237027": ("org-valero", ["ca-problem-refineries"], 508895.85),
    "1143378": ("org-iid", ["ca-problem-salton-sea"], 290134.29),
    "1146790": ("org-farm-bureau", ["ca-problem-pesticides", "ca-problem-groundwater-overdraft"], 1436711.70),
    "1146857": ("org-western-growers", ["ca-problem-pesticides", "ca-problem-groundwater-overdraft"], 1196763.69),
    "1146862": ("org-corteva", ["ca-problem-pesticides"], 141149.88),
}

FIRM_CARD = {
    "1276988": "firm-greenberg-traurig",
    "1385058": "firm-leacox",
}

# Quarterly fees where the payee name on Form 635 matches the registration name.
MATCHED_FEES = {
    "1276988": "Oljebransjens forening betalte firmaet 37 500 dollar våren 2025. Til da i året var summen 75 000 dollar.",
    "1385058": "Oljebransjens forening betalte firmaet 6 000 dollar våren 2025. Til da i året var summen 15 100 dollar.",
}

POLITICIAN_CARD = {
    "lawmaker-lena-gonzalez": "lawmaker-lena-gonzalez",
    "lawmaker-al-muratsuchi": "lawmaker-al-muratsuchi",
}

PROBLEMS = [
    ("ca-problem-south-coast-air", "South Coast-luft"),
    ("ca-problem-san-joaquin-air", "San Joaquin-luft"),
    ("ca-problem-drinking-water", "Drikkevann"),
    ("ca-problem-oil-gas-proximity", "Olje nær boliger"),
    ("ca-problem-pesticides", "Sprøytemidler"),
    ("ca-problem-salton-sea", "Salton Sea"),
    ("ca-problem-refineries", "Raffinerier"),
    ("ca-problem-aliso-canyon", "Aliso Canyon"),
    ("ca-problem-pfas", "PFAS"),
    ("ca-problem-groundwater-overdraft", "Grunnvann"),
]

LOBBY_SOURCE = {
    "url": "https://campaignfinance.cdn.sos.ca.gov/dbwebexport.zip",
    "title": "CAL-ACCESS rådata, FILER_LINKS_CD sesjon 2025",
    "publisher": "California Secretary of State",
    "retrieved": "2026-10-28",
    "archive_url": "http://web.archive.org/web/20260930110449/https://campaignfinance.cdn.sos.ca.gov/dbwebexport.zip",
    "archive_note": "Koblingene er lest i uttrekket datert 28. oktober 2026.",
}
FEE_SOURCE = {
    "url": "https://cal-access.sos.ca.gov/PDFGen/pdfgen.prg?filingid=3070933&amendid=0",
    "title": "Form 635 filing 3070933, Western States Petroleum Association, april–juni 2025",
    "publisher": "California Secretary of State",
    "retrieved": "2026-10-28",
    "archive_url": "http://web.archive.org/web/20251002191218/https://cal-access.sos.ca.gov/PDFGen/pdfgen.prg?filingid=3070933&amendid=0",
    "archive_note": "Beløpene er lest i PDF-en.",
}
ACTIVITY = {
    "text": "Våren 2025 skrev oljebransjens forening at de jobbet med regelen om avstand mellom oljebrønner og hus, og med loven om lokal luft. Skjemaet sier ikke om de var for eller mot, og ikke hvilket firma som tok hvilken sak.",
    "journalist": "Form 635, filing 3070933, april–juni 2025. Teksten nevner CalGEM SETBACK RULE, CARB AB 617 IMPLEMENTATION, og lovnumrene AB 626, 751, 839, 881, 914, 1207, 1243, 1448 og SB 34, 57, 222, 282, 237, 285, 318, 348, 542, 613, 614, 643, 684, 767, 840.",
    "sources": [FEE_SOURCE],
}

SEARCH_SOURCE = {
    "url": "https://dbsearch.sos.ca.gov/LobbyIntSearch.aspx",
    "title": "Cal-Access Lobbyist Employer Category Search, sesjon 2025-2026",
    "publisher": "California Secretary of State",
    "retrieved": "2026-10-28",
    "archive_url": "http://web.archive.org/web/20250525150615/https://dbsearch.sos.ca.gov/LobbyIntSearch.aspx",
    "archive_note": "Sesjonsbeløpene er de samme som på organisasjonskortene.",
}


def lobby_claim_text(card_id: str) -> str:
    card = json.loads((ROOT / "data" / "cards" / f"{card_id}.json").read_text(encoding="utf-8"))
    for claim in card["summary"]:
        if "lobby" in claim["text"].lower():
            return claim["text"]
    for claim in card["claims"]:
        if "lobby" in claim["text"].lower():
            return claim["text"]
    return ""


def main() -> None:
    names = {}
    for firm in FIRMS["firms"]:
        for client in firm["clients"]:
            names[client["id"]] = client["name"]
    for person in FIRMS["inhouse"]:
        names[person["employer"]] = person["employer_name"]

    contributions: dict[str, list[dict]] = {}
    for row in EXTRACT["contributions"]:
        contributions.setdefault(row["employer_id"], []).append({
            "date": row["date"],
            "amount": row["amount"],
            "recipient": row["recipient"],
            "politician_card": "",
            "filing_id": row["filing_id"],
        })

    employers = []
    for employer_id, (card_id, problems, amount) in EMPLOYER.items():
        employers.append({
            "filer_id": employer_id,
            "name": names.get(employer_id, card_id),
            "card_id": card_id,
            "problems": problems,
            "session_lobby_usd": amount,
            "session_text": lobby_claim_text(card_id),
            "sources": [SEARCH_SOURCE],
            "activity": ACTIVITY if employer_id == "1147195" else None,
            "contributions": contributions.get(employer_id, []),
        })

    inhouse_by = {}
    for person in FIRMS["inhouse"]:
        inhouse_by.setdefault(person["employer"], []).append({"id": person["id"], "name": person["name"]})

    firms = []
    for firm in FIRMS["firms"]:
        clients = []
        problems = set()
        for client in firm["clients"]:
            mapped = EMPLOYER.get(client["id"])
            card_id = mapped[0] if mapped else ""
            client_problems = mapped[1] if mapped else []
            problems.update(client_problems)
            clients.append({
                "filer_id": client["id"],
                "name": client["name"],
                "card_id": card_id,
                "problems": client_problems,
            })
        firms.append({
            "filer_id": firm["id"],
            "name": firm["name"],
            "card_id": FIRM_CARD.get(firm["id"], ""),
            "problems": sorted(problems),
            "lobbyists": firm["lobbyists"],
            "clients": clients,
            "fee_text": MATCHED_FEES.get(firm["id"], ""),
            "fee_sources": [FEE_SOURCE] if firm["id"] in MATCHED_FEES else [],
            "both_sides": False,
            "bills_note": (
                "Vi vet at oljebransjens forening jobbet med avstandsregelen og med loven om lokal luft. Vi vet ikke om det var dette firmaet som gjorde den jobben."
                if "1147195" in firm["targets"]
                else "Vi har ikke lest hvilke lover dette firmaet jobbet med."
            ),
        })

    roster = {
        "retrieved": "2026-10-28",
        "both_sides_count": 0,
        "both_sides_note": "Vi lette etter firmaer som jobber både for olje eller sprøytemidler og for en miljøgruppe. Vi fant ingen.",
        "both_sides_journalist": (
            "Merket krever at samme firma i sesjon 2025 er registrert både for en olje-, gass- eller sprøytemiddelklient "
            "og for en miljø- eller ren-energi-klient. CLEAN ENERGY, filer 1254491, står sammen med Chevron. "
            "MONARCH BIO ENERGY, LLC, filer 1463713, står sammen med Sempra. Navnet alene sier ikke at de er miljøorganisasjoner."
        ),
        "registration_source": LOBBY_SOURCE,
        "problems": [{"id": pid, "title": title} for pid, title in PROBLEMS],
        "employers": employers,
        "inhouse": [
            {"filer_id": employer_id, "people": people, "card_id": EMPLOYER.get(employer_id, ("",))[0]}
            for employer_id, people in sorted(inhouse_by.items())
        ],
        "firms": firms,
        "unmatched_payments": [
            {
                "payee": "Pillsbury Winthrop Shaw Pittman LLP",
                "text": "Oljebransjens forening betalte 58 570 dollar i honorar og 760 dollar i utlegg våren 2025.",
                "card_id": "firm-pillsbury",
                "note": "Navnet på betalingen er Pillsbury Winthrop. Registeret har et eldre navn, Pillsbury Madison and Sutro, på samme nummer. Vi har ikke slått dem sammen.",
            },
            {
                "payee": "Carpenter Garcia Sievers LLC",
                "text": "Oljebransjens forening betalte 90 000 dollar våren 2025.",
                "card_id": "firm-carpenter-garcia-sievers",
                "note": "Registeret har også et firma som heter Carpenter Hawkins for samme oppdragsgiver. Navnene er ikke like, så vi har ikke slått dem sammen.",
            },
        ],
    }
    path = ROOT / "data" / "lobby" / "roster.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(roster, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    public = ROOT / "public" / "data" / "lobby" / "roster.json"
    public.parent.mkdir(parents=True, exist_ok=True)
    public.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    print(path, "firms", len(firms), "both", roster["both_sides_count"])


if __name__ == "__main__":
    main()
