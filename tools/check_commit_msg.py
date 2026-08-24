#!/usr/bin/env python3
"""Commit-message validator for Conventional Commits + live-ops safety tags."""
from __future__ import annotations

import re
import sys

PATTERN = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|liveops)"
    r"(\([a-z0-9_-]+\))?"
    r"!?"
    r": .{1,120}$"
)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: check_commit_msg.py <commit-msg-file>")
        return 1

    msg_path = sys.argv[1]
    with open(msg_path, encoding="utf-8") as f:
        first_line = f.readline().strip()

    if not PATTERN.match(first_line):
        print("::error::Commit message does not follow Conventional Commits.")
        print("Expected: <type>[optional scope]: <description>")
        print("Allowed types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert, liveops")
        return 1

    if first_line.startswith("liveops"):
        if not re.search(r"\[(player-visible|backend|banner|economy|flag)\]", first_line):
            print("::error::liveops commits must include a player-impact tag: [player-visible|backend|banner|economy|flag]")
            return 1

    print("[OK] Commit message format valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
