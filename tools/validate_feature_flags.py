#!/usr/bin/env python3
"""Validate Melodia runtime feature-flag configuration."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FLAG_PATH = ROOT / "liveops" / "feature_flags.json"

ALLOWED_OWNERS = {
    "level-design",
    "character-art",
    "audio-design",
    "liveops",
    "economy",
    "ui",
    "engineering",
    "qa",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate feature_flags.json")
    parser.add_argument("--path", type=pathlib.Path, default=FLAG_PATH)
    args = parser.parse_args()

    if not args.path.exists():
        print(f"::error::feature_flags.json not found at {args.path}")
        return 1

    try:
        data = json.loads(args.path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"::error::{args.path}: invalid JSON: {exc}")
        return 1

    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        errors.append("feature_flags.json root must be an object")
        _emit(errors, warnings)
        return 1

    flags = data.get("flags", [])
    if not isinstance(flags, list):
        errors.append("'flags' must be an array")
        _emit(errors, warnings)
        return 1

    seen_ids: set[str] = set()
    for idx, flag in enumerate(flags):
        prefix = f"flags[{idx}]"
        if not isinstance(flag, dict):
            errors.append(f"{prefix} is not an object")
            continue
        for key in ("id", "default", "owner", "requires_restart", "description"):
            if key not in flag:
                errors.append(f"{prefix}: missing '{key}'")
        fid = flag.get("id")
        if fid:
            if not re.match(r"^FEATURE_[A-Z][A-Z0-9_]*$", fid):
                errors.append(f"{prefix}: id '{fid}' must match ^FEATURE_[A-Z][A-Z0-9_]*$")
            if fid in seen_ids:
                errors.append(f"{prefix}: duplicate id '{fid}'")
            seen_ids.add(fid)
        if flag.get("owner") not in ALLOWED_OWNERS:
            errors.append(f"{prefix}: owner '{flag.get('owner')}' not in allowed list")
        if not isinstance(flag.get("default"), bool):
            errors.append(f"{prefix}: 'default' must be boolean")
        if not isinstance(flag.get("requires_restart"), bool):
            errors.append(f"{prefix}: 'requires_restart' must be boolean")
        if not isinstance(flag.get("description"), str) or not flag.get("description"):
            errors.append(f"{prefix}: 'description' must be a non-empty string")

    _emit(errors, warnings)
    if errors:
        print(f"\nFeature-flag validation failed: {len(errors)} error(s)")
        return 1
    print(f"[OK] Feature-flag validation passed ({len(flags)} flag(s))")
    return 0


def _emit(errors: list[str], warnings: list[str]) -> None:
    for w in warnings:
        print(f"::warning::{w}")
    for e in errors:
        print(f"::error::{e}")


if __name__ == "__main__":
    sys.exit(main())
