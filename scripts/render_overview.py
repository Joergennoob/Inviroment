#!/usr/bin/env python3
"""Readable California ranking page from the problem cards plus the method note."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_cards

OUT = ROOT / "data" / "ca" / "oversikt.md"
METHOD = ROOT / "data" / "ca" / "metode.md"


def main() -> int:
    check = "--check" in sys.argv
    method = METHOD.read_text(encoding="utf-8").rstrip()
    problems = sorted((c for c in load_cards() if c["type"] == "problem"), key=lambda c: c["rank"])
    lines = [
        method,
        "",
        "## Rangert liste",
        "",
    ]
    for card in problems:
        lines.append(f"### {card['rank']}. {card['name']}")
        lines.append("")
        for claim in card["summary"]:
            lines.append(f"- {claim['text']}")
        lines.append("")
        lines.append(f"Kort: `{card['id']}`.")
        lines.append("")
    text = "\n".join(lines)
    if check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("oversikt drift")
            return 1
        print("oversikt ok")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
