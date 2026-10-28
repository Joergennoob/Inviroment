#!/usr/bin/env python3
"""Write a coverage table: what was checked on each card."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_cards

OUT = ROOT / "data" / "coverage.md"


def flag(ok: bool) -> str:
    return "sjekket" if ok else "mangler"


def row(card: dict) -> str:
    claims = card["summary"] + card["claims"]
    statuses = {c["status"] for c in claims}
    empty_fields = {item["field"] for item in card["checked_empty"]}
    has_lobby = any("lobby" in c["text"].lower() or "dollar" in c["text"].lower() for c in claims) or "lobbying" in empty_fields
    has_contrib = any("bidrag" in c["text"].lower() or "kampanje" in c["text"].lower() for c in claims) or "campaign_contributions" in empty_fields
    has_vote = any("stemme" in c["text"].lower() or c["text"].lower().startswith("sb ") or "ayes" in c["text"].lower() or "ja-stemmer" in c["text"].lower() for c in claims) or "votes" in empty_fields
    has_geo = bool(card.get("geometry")) or "geometry" in empty_fields
    archives = []
    for claim in claims:
        for source in claim["sources"]:
            archives.append(bool(source.get("archive_url")))
    archive_txt = f"{sum(archives)}/{len(archives)}" if archives else "0/0"
    return (
        f"| `{card['id']}` | {card['type']} | {flag('confirmed' in statuses)} | "
        f"{flag(has_lobby)} | {flag(has_contrib)} | {flag(has_vote)} | {flag(has_geo)} | "
        f"{archive_txt} | {len(card['open_questions'])} |"
    )


def render(cards: list[dict]) -> str:
    lines = [
        "# Dekning",
        "",
        "Tabellen leser kortene. «Sjekket» betyr at kortet har et funn eller et tomt felt med søk som er logget. "
        "Arkivkolonnen teller kilder med Wayback-URL.",
        "",
        "| Kort | Type | Primærpåstand | Lobby | Kampanjebidrag | Stemmer | Plassering | Arkiv | Åpne spørsmål |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for card in sorted(cards, key=lambda c: (c["type"] != "problem", c.get("rank") or 99, c["id"])):
        lines.append(row(card))
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    check = "--check" in sys.argv
    text = render(load_cards())
    if check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("coverage drift")
            return 1
        print("coverage ok")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
