#!/usr/bin/env python3
"""Build map GeoJSON and a card bundle from the JSON cards."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import PUBLIC_DATA, ROOT, load_cards


def feature(card: dict, item: dict) -> dict:
    geo = item["geometry"]
    return {
        "type": "Feature",
        "geometry": {"type": geo["type"], "coordinates": geo["coordinates"]},
        "properties": {
            "card_id": card["id"],
            "name": item["name"],
            "layer": item["layer"],
            "card_type": card["type"],
            "rank": card.get("rank"),
            "source_name": geo["source_name"],
            "source_record_id": geo["source_record_id"],
            "source_url": geo["source_url"],
            "source_retrieved": geo["retrieved"],
            "source_note": geo["note"],
        },
    }


def build() -> tuple[dict, dict]:
    cards = load_cards()
    features = []
    for card in cards:
        for item in card.get("map_features") or []:
            features.append(feature(card, item))
    geojson = {"type": "FeatureCollection", "features": features}
    bundle = {"cards": cards}
    return geojson, bundle


def main() -> int:
    check = "--check" in sys.argv
    geojson, bundle = build()
    PUBLIC_DATA.mkdir(parents=True, exist_ok=True)
    targets = {
        PUBLIC_DATA / "map.geojson": geojson,
        PUBLIC_DATA / "cards.json": bundle,
        ROOT / "data" / "site" / "map.geojson": geojson,
        ROOT / "data" / "site" / "cards.json": bundle,
    }
    drifted = []
    for path, payload in targets.items():
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                drifted.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    if drifted:
        print("geojson drift:", ", ".join(drifted))
        return 1
    print(f"geojson {'ok' if check else 'wrote'} features={len(geojson['features'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
