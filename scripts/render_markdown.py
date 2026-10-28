#!/usr/bin/env python3
"""Write a Norwegian Markdown card next to each JSON card."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CARDS_DIR, load_cards

LABEL = {
    "confirmed": "bekreftet",
    "indication": "indikasjon",
    "not_found": "ikke funnet",
    "not_verified": "ikke verifisert",
}
TYPE_LABEL = {
    "problem": "Miljøproblem",
    "organization": "Organisasjon",
    "lobbying_firm": "Lobbyfirma",
    "lawmaker": "Folkevalgt",
    "bill": "Lovforslag",
}


def sources_md(sources: list[dict]) -> str:
    lines = []
    for source in sources:
        archive = source.get("archive_url") or "ikke arkivert"
        lines.append(
            f"  - [{source['title']}]({source['url']}) ({source['publisher']}, hentet {source['retrieved']}). "
            f"Arkiv: {archive}. {source.get('archive_note', '')}".rstrip()
        )
    return "\n".join(lines)


def claim_md(claim: dict) -> str:
    note = f" {claim['note']}" if claim.get("note") else ""
    return (
        f"- [{LABEL[claim['status']]}] {claim['text']}{note}\n"
        f"{sources_md(claim['sources'])}"
    )


def render(card: dict) -> str:
    lines = [
        f"# {card['name']}",
        "",
        f"Type: {TYPE_LABEL.get(card['type'], card['type'])}. Id: `{card['id']}`. Oppdatert: {card['updated']}.",
        "",
    ]
    if card.get("rank"):
        lines.append(f"Rangering i California-oversikten: {card['rank']}.")
        lines.append("")
    lines.append("## Sammendrag")
    lines.append("")
    for claim in card["summary"]:
        lines.append(claim_md(claim))
        lines.append("")
    lines.append("## Funn")
    lines.append("")
    for claim in card["claims"]:
        lines.append(claim_md(claim))
        lines.append("")
    if card.get("geometry"):
        geo = card["geometry"]
        lines += [
            "## Kilde for plassering",
            "",
            f"{geo['note']} Kilde: {geo['source_name']}, post `{geo['source_record_id']}`. "
            f"[Post]({geo['source_url']}). Hentet {geo['retrieved']}.",
            "",
        ]
    for block_name, title in (
        ("population", "Befolkning"),
        ("demographics", "Demografi"),
        ("health_outcomes", "Helseutfall"),
    ):
        block = card.get(block_name)
        if not block:
            continue
        lines += [
            f"## {title}",
            "",
            f"Geografi: {block['geography']}. Årgang: {block['vintage']}. Sammenligning: {block['comparison']}.",
            "",
        ]
        for claim in block["claims"]:
            lines.append(claim_md(claim))
            lines.append("")
    if card["links"]:
        lines.append("## Lenker til andre kort")
        lines.append("")
        for link in card["links"]:
            lines.append(f"- {link['text']} (`{link['target_id']}`)")
        lines.append("")
    if card["checked_empty"]:
        lines.append("## Sjekket uten funn")
        lines.append("")
        for item in card["checked_empty"]:
            urls = ", ".join(item["urls"]) if item["urls"] else "ingen egen treff-URL"
            lines.append(
                f"- {item['field']}: {item['searched']} Resultat: {LABEL.get(item['result'], item['result'])}. "
                f"URL: {urls}. Dato: {item['retrieved']}."
            )
        lines.append("")
    if card["open_questions"]:
        lines.append("## Åpne spørsmål")
        lines.append("")
        for question in card["open_questions"]:
            lines.append(f"- {question}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    check = "--check" in sys.argv
    drifted = []
    for card in load_cards():
        path = CARDS_DIR / f"{card['id']}.md"
        text = render(card)
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                drifted.append(path.name)
        else:
            path.write_text(text, encoding="utf-8")
    if drifted:
        print("markdown drift:", ", ".join(drifted))
        return 1
    print(f"markdown {'ok' if check else 'wrote'} for {len(load_cards())} cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
