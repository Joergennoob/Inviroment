"""Shared helpers for card scripts. Standard library only."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS_DIR = ROOT / "data" / "cards"
SCHEMA_PATH = ROOT / "schema" / "card.schema.json"
PUBLIC_DATA = ROOT / "public" / "data"
STATUS = {"confirmed", "indication", "not_found", "not_verified"}
TYPES = {"problem", "organization", "lobbying_firm", "lawmaker", "bill"}


def card_paths() -> list[Path]:
    return sorted(CARDS_DIR.glob("*.json"))


def load_cards() -> list[dict]:
    cards = []
    for path in card_paths():
        cards.append(json.loads(path.read_text(encoding="utf-8")))
    return cards


def source_ok(source: dict) -> str | None:
    for key in ("url", "title", "publisher", "retrieved", "archive_url", "archive_note"):
        if key not in source:
            return f"missing source.{key}"
    if not str(source["url"]).startswith("http"):
        return "source url must be http(s)"
    if "fminus.org" in source["url"].lower() or "fminus.org" in source.get("archive_url", "").lower():
        return "fminus.org is not an allowed source"
    if not source["archive_url"] and not source["archive_note"]:
        return "empty archive_url needs archive_note"
    if source["archive_url"] and "web.archive.org" not in source["archive_url"] and "archive.org" not in source["archive_url"]:
        return "archive_url should be an Internet Archive URL"
    return None
