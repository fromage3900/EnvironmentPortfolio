#!/usr/bin/env python3
"""Bump the monorepo version, update CHANGELOG, and optionally commit/tag."""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
CHANGELOG = ROOT / "CHANGELOG.md"


def _current_version() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def _bump(version: str, part: str) -> str:
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version)
    if not m:
        raise ValueError(f"VERSION must be semver; got {version!r}")
    major, minor, patch = map(int, m.groups())
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def _update_changelog(new_version: str) -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    header = f"## [{new_version}] - {today}"
    if "## [Unreleased]" not in text:
        raise ValueError("CHANGELOG.md is missing an [Unreleased] section")
    # Insert new version section below Unreleased.
    new_section = f"## [Unreleased]\n\n### Added\n\n### Changed\n\n### Fixed\n\n{header}\n\n### Added\n"
    updated = text.replace("## [Unreleased]\n", new_section, 1)
    CHANGELOG.write_text(updated, encoding="utf-8")


def _git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git"] + args, cwd=ROOT, check=False, text=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump Melodia monorepo version")
    parser.add_argument("part", choices=["major", "minor", "patch"], help="Semver segment to bump")
    parser.add_argument("--message", default="", help="Extra release note line")
    parser.add_argument("--no-commit", action="store_true", help="Do not commit or tag")
    args = parser.parse_args()

    current = _current_version()
    new = _bump(current, args.part)
    print(f"Bumping {current} -> {new}")

    VERSION_FILE.write_text(new + "\n", encoding="utf-8")
    _update_changelog(new)

    if args.no_commit:
        print(f"Version bumped to {new}. Review VERSION and CHANGELOG, then commit/tag manually.")
        return 0

    _git(["add", str(VERSION_FILE.relative_to(ROOT)), str(CHANGELOG.relative_to(ROOT))])
    commit_msg = f"liveops(release): bump version {current} -> {new} [backend]\n\n{args.message}"
    rc = _git(["commit", "-m", commit_msg]).returncode
    if rc != 0:
        print("::error::git commit failed")
        return rc

    rc = _git(["tag", "-a", f"v{new}", "-m", f"Release v{new}"]).returncode
    if rc != 0:
        print("::error::git tag failed")
        return rc

    print(f"[OK] Created commit and tag v{new}")
    print("  Push with: git push origin main && git push origin v{new}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
