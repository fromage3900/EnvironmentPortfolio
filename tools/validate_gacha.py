#!/usr/bin/env python3
"""Validate Melodia gacha banners and economy config."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
LIVEOPS = ROOT / "liveops"
BANNER_DIR = LIVEOPS / "banners"
ECONOMY_PATH = LIVEOPS / "economy.json"
ERRORS: list[str] = []
WARNINGS: list[str] = []


def _load(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        ERRORS.append(f"{path}: invalid JSON: {exc}")
        return None


def _validate_banner(path: pathlib.Path, banner: dict[str, Any], currencies: set[str]) -> None:
    for key in ("id", "name", "start_utc", "end_utc", "currency", "pools", "pity"):
        if key not in banner:
            ERRORS.append(f"{path}: missing '{key}'")
    bid = banner.get("id")
    if bid and not re.match(r"^[A-Z][A-Z0-9_]*$", bid):
        ERRORS.append(f"{path}: id '{bid}' must be UPPER_SNAKE_CASE")
    if banner.get("currency") not in currencies:
        ERRORS.append(f"{path}: currency '{banner.get('currency')}' not in economy.json")
    pools = banner.get("pools", [])
    if not isinstance(pools, list) or not pools:
        ERRORS.append(f"{path}: pools must be non-empty list")
        return
    seen_rarities: set[int] = set()
    total = 0.0
    all_items: set[str] = set()
    for idx, pool in enumerate(pools):
        if not isinstance(pool, dict):
            ERRORS.append(f"{path}: pool[{idx}] not an object")
            continue
        for f in ("rarity", "rate", "items"):
            if f not in pool:
                ERRORS.append(f"{path}: pool[{idx}] missing '{f}'")
        r = pool.get("rarity")
        if isinstance(r, int) and 1 <= r <= 6:
            if r in seen_rarities:
                ERRORS.append(f"{path}: duplicate rarity {r}")
            seen_rarities.add(r)
        else:
            ERRORS.append(f"{path}: pool[{idx}] rarity must be 1-6")
        rate = pool.get("rate")
        if isinstance(rate, (int, float)) and 0 < rate <= 1:
            total += float(rate)
        else:
            ERRORS.append(f"{path}: pool[{idx}] rate must be in (0,1]")
        items = pool.get("items", [])
        if isinstance(items, list) and items:
            for item in items:
                if item in all_items:
                    ERRORS.append(f"{path}: item '{item}' in multiple pools")
                all_items.add(item)
        else:
            ERRORS.append(f"{path}: pool[{idx}] items must be non-empty list")
    if abs(total - 1.0) > 1e-4:
        ERRORS.append(f"{path}: rates sum to {total:.6f}, expected 1.0")
    pity = banner.get("pity", {})
    soft, hard = pity.get("soft"), pity.get("hard")
    if isinstance(soft, int) and isinstance(hard, int):
        if soft >= hard or soft < 1:
            ERRORS.append(f"{path}: pity must satisfy 0 < soft < hard")
    else:
        ERRORS.append(f"{path}: pity.soft and pity.hard must be positive ints")
    gr = pity.get("guarantee_rarity")
    if gr not in seen_rarities:
        ERRORS.append(f"{path}: guarantee_rarity {gr} missing from pools")
    missing = set(banner.get("featured_items", [])) - all_items
    if missing:
        ERRORS.append(f"{path}: featured items not in pools: {sorted(missing)}")


def _validate_economy(economy: dict[str, Any]) -> set[str]:
    currencies = economy.get("currencies", [])
    if not isinstance(currencies, list) or not currencies:
        ERRORS.append(f"{ECONOMY_PATH}: currencies must be non-empty list")
        return set()
    ids = [c.get("id") for c in currencies if isinstance(c, dict)]
    if len(ids) != len(set(ids)):
        ERRORS.append(f"{ECONOMY_PATH}: duplicate currency ids")
    for c in currencies:
        if isinstance(c, dict):
            for key in ("id", "name", "type"):
                if key not in c:
                    ERRORS.append(f"{ECONOMY_PATH}: currency {c.get('id')} missing '{key}'")
    return set(ids)


def _check_overlaps(banners: list[tuple[pathlib.Path, dict[str, Any]]]) -> None:
    by_currency: dict[str, list[tuple[pathlib.Path, str, str]]] = {}
    for path, banner in banners:
        by_currency.setdefault(banner.get("currency", ""), []).append(
            (path, banner.get("start_utc", ""), banner.get("end_utc", ""))
        )
    for currency, entries in by_currency.items():
        if not currency:
            continue
        entries.sort(key=lambda x: x[1])
        for i in range(len(entries) - 1):
            p1, _s1, e1 = entries[i]
            p2, s2, _e2 = entries[i + 1]
            if e1 and s2 and e1 >= s2:
                WARNINGS.append(f"Overlap for {currency}: {p1.name} ends {e1}, {p2.name} starts {s2}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate gacha/economy configs")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()
    economy = _load(ECONOMY_PATH)
    if economy is None:
        return 1
    currencies = _validate_economy(economy)
    banners: list[tuple[pathlib.Path, dict[str, Any]]] = []
    seen_ids: set[str] = set()
    for path in sorted(BANNER_DIR.glob("*.json")):
        banner = _load(path)
        if banner is None:
            continue
        _validate_banner(path, banner, currencies)
        banners.append((path, banner))
        bid = banner.get("id")
        if bid in seen_ids:
            ERRORS.append(f"{path}: duplicate banner id '{bid}'")
        seen_ids.add(bid)
    _check_overlaps(banners)
    for w in WARNINGS:
        print(f"::warning::{w}")
    for e in ERRORS:
        print(f"::error::{e}")
    if ERRORS or (args.strict and WARNINGS):
        print(f"\nFailed: {len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
        return 1
    print(f"Passed: {len(banners)} banner(s), {len(currencies)} currency/currencies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
