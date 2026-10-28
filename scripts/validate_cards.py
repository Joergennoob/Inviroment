#!/usr/bin/env python3
"""Validate every card against the project rules and schema/card.schema.json."""

from __future__ import annotations

import json
import sys

from common import CARDS_DIR, SCHEMA_PATH, STATUS, TYPES, card_paths, load_cards, source_ok

DATE = r"^\d{4}-\d{2}-\d{2}$"
import re


def fail(errors: list[str], path: str, msg: str) -> None:
    errors.append(f"{path}: {msg}")


def check_claim(errors: list[str], path: str, claim: dict, seen_ids: set[str]) -> None:
    for key in ("id", "text", "status", "note", "sources"):
        if key not in claim:
            fail(errors, path, f"claim missing {key}")
            return
    if not claim["text"].strip():
        fail(errors, path, "empty claim text")
    if claim["status"] not in STATUS:
        fail(errors, path, f"bad status {claim['status']}")
    if claim["status"] == "indication" and not claim["note"].strip():
        fail(errors, path, "indication requires note")
    if claim["id"] in seen_ids:
        fail(errors, path, f"duplicate claim id {claim['id']}")
    seen_ids.add(claim["id"])
    if not claim["sources"]:
        fail(errors, path, "claim has no sources")
    for source in claim["sources"]:
        err = source_ok(source)
        if err:
            fail(errors, path, err)
        if not re.match(DATE, source.get("retrieved", "")):
            fail(errors, path, "bad retrieved date")


def check_geometry(errors: list[str], path: str, geo: dict) -> None:
    for key in (
        "type",
        "coordinates",
        "source_name",
        "source_record_id",
        "source_url",
        "retrieved",
        "note",
    ):
        if key not in geo or geo[key] in ("", None):
            fail(errors, path, f"geometry missing {key}")
            return
    if geo["type"] not in ("Point", "Polygon", "MultiPolygon"):
        fail(errors, path, "bad geometry type")
    if not str(geo["source_url"]).startswith("http"):
        fail(errors, path, "geometry source_url")
    if "fminus.org" in geo["source_url"].lower():
        fail(errors, path, "fminus geometry source")
    if len(geo["note"]) < 8:
        fail(errors, path, "geometry note too short")
    coords = geo["coordinates"]
    if geo["type"] == "Point":
        if not (isinstance(coords, list) and len(coords) == 2):
            fail(errors, path, "point coordinates")
        else:
            lon, lat = coords
            if not (-125 < lon < -114 and 32 < lat < 43):
                fail(errors, path, f"point outside California bbox {coords}")
    elif not coords:
        fail(errors, path, "empty coordinates")


def main() -> int:
    errors: list[str] = []
    if not SCHEMA_PATH.exists():
        print("missing schema", file=sys.stderr)
        return 1
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if schema.get("properties", {}).get("schema_version", {}).get("const") != "1.0.0":
        errors.append("schema version const drifted")
    paths = card_paths()
    if not paths:
        errors.append("no cards")
    cards = []
    ids: set[str] = set()
    for path in paths:
        try:
            card = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}: invalid json {exc}")
            continue
        cards.append(card)
        cid = card.get("id")
        if cid in ids:
            errors.append(f"duplicate id {cid}")
        ids.add(cid)
        if path.stem != cid:
            errors.append(f"{path.name}: filename must match id {cid}")
        rel = path.name
        for key in (
            "schema_version",
            "id",
            "type",
            "name",
            "state",
            "updated",
            "summary",
            "claims",
            "links",
            "geometry",
            "map_features",
            "checked_empty",
            "open_questions",
        ):
            if key not in card:
                fail(errors, rel, f"missing {key}")
        if card.get("schema_version") != "1.0.0":
            fail(errors, rel, "schema_version")
        if card.get("type") not in TYPES:
            fail(errors, rel, "type")
        if card.get("state") != "CA":
            fail(errors, rel, "state")
        if not re.match(DATE, card.get("updated", "")):
            fail(errors, rel, "updated")
        if card.get("type") == "problem" and not isinstance(card.get("rank"), int):
            fail(errors, rel, "problem needs rank")
        summary = card.get("summary") or []
        if not (3 <= len(summary) <= 5):
            fail(errors, rel, "summary must have 3-5 items")
        seen: set[str] = set()
        extra = []
        for block_name in ("population", "demographics", "health_outcomes"):
            block = card.get(block_name)
            if block:
                for claim in block.get("claims") or []:
                    extra.append(claim)
        if card.get("type") == "problem":
            for block_name in ("population", "demographics", "health_outcomes"):
                if not card.get(block_name):
                    fail(errors, rel, f"problem missing {block_name}")
        for claim in summary + (card.get("claims") or []) + extra:
            check_claim(errors, rel, claim, seen)
        if card.get("geometry"):
            check_geometry(errors, rel, card["geometry"])
        elif card.get("type") == "problem":
            empties = card.get("checked_empty") or []
            if not any(item.get("field") == "geometry" for item in empties):
                fail(errors, rel, "problem without geometry needs checked_empty geometry")
        for feature in card.get("map_features") or []:
            if feature.get("layer") not in ("problem", "facility", "tract"):
                fail(errors, rel, "bad map layer")
            check_geometry(errors, rel, feature.get("geometry") or {})
        for item in card.get("checked_empty") or []:
            if item.get("result") not in ("not_found", "not_verified"):
                fail(errors, rel, "checked_empty result")
            if len(item.get("searched", "")) < 8:
                fail(errors, rel, "checked_empty searched")
        blob = json.dumps(card).lower()
        if "fminus.org" in blob or "f-minus" in blob:
            fail(errors, rel, "fminus citation")

    by_id = {c.get("id"): c for c in cards}
    ranks = [c.get("rank") for c in cards if c.get("type") == "problem"]
    if sorted(r for r in ranks if isinstance(r, int)) != list(range(1, 11)):
        errors.append(f"expected problem ranks 1..10, got {sorted(ranks)}")
    for card in cards:
        for link in card.get("links") or []:
            target = link.get("target_id")
            if target not in by_id:
                errors.append(f"{card.get('id')}: link target missing {target}")

    if errors:
        print(f"{len(errors)} validation error(s):")
        for err in errors:
            print(" -", err)
        return 1
    print(f"OK {len(cards)} cards in {CARDS_DIR}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
    raise SystemExit(main())
