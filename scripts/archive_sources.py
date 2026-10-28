#!/usr/bin/env python3
"""Fill archive_url from the Wayback availability API. Does not invent snapshots."""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import card_paths

AVAIL = "https://archive.org/wayback/available?url="


def available(url: str) -> tuple[str, str]:
    today = time.strftime("%Y-%m-%d")
    query = AVAIL + urllib.parse.quote(url, safe="")
    req = urllib.request.Request(query, headers={"User-Agent": "miljokart-archive-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=40) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        return "", f"Wayback availability feilet {today}: {exc.__class__.__name__}."
    snap = (payload.get("archived_snapshots") or {}).get("closest") or {}
    if snap.get("available") and snap.get("url"):
        return snap["url"], f"Wayback availability {today} fant et øyeblikksbilde."
    save = "https://web.archive.org/save/" + url
    save_req = urllib.request.Request(save, headers={"User-Agent": "miljokart-archive-check/1.0"})
    try:
        with urllib.request.urlopen(save_req, timeout=50) as response:
            final = response.geturl()
        if "web.archive.org/web/" in final:
            return final, f"Save Page Now {today} opprettet et øyeblikksbilde."
        return "", f"Save Page Now {today} svarte uten arkiv-URL ({final[:120]})."
    except Exception as exc:  # noqa: BLE001
        return "", f"Wayback availability {today} fant ikke et øyeblikksbilde. Save Page Now feilet: {exc.__class__.__name__}."


def main() -> int:
    cache: dict[str, tuple[str, str]] = {}
    for path in card_paths():
        card = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for claim in card["summary"] + card["claims"]:
            for source in claim["sources"]:
                if source.get("archive_url"):
                    continue
                url = source["url"]
                if url not in cache:
                    cache[url] = available(url)
                    time.sleep(0.4)
                archive_url, note = cache[url]
                source["archive_url"] = archive_url
                source["archive_note"] = note
                changed = True
        if changed:
            path.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"checked {len(cache)} urls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
