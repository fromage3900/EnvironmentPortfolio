#!/usr/bin/env python3
"""Pull the recommended local model fleet (2026-09-01) for the Melodia pipeline.

Worker/JSON tiers must be pulled for the daemon to get fast; the reasoner tier is
optional (large). Writes progress to logs/overnight/fleet_pull.log.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "logs" / "overnight" / "fleet_pull.log"

FLEET = [
    ("granite4.2:3b", "micro worker (health ping)"),
    ("granite4.2:8b", "worker (structured JSON)"),
    ("muse-glimmer:30b", "reasoner/agent tier"),
]


def log(msg: str) -> None:
    print(msg, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(msg + "\n")


def main() -> int:
    models = sys.argv[1:]
    if not models:
        models = [m for m, _ in FLEET]
    for model in models:
        label = next((d for m, d in FLEET if m == model), model)
        log(f"[PULL] {model} ({label}) ...")
        try:
            proc = subprocess.run(
                ["ollama", "pull", model],
                capture_output=True, text=True, timeout=1800,
            )
        except subprocess.TimeoutExpired:
            log(f"[PULL] {model} TIMEOUT")
            continue
        tail = (proc.stdout or proc.stderr or "").strip().splitlines()
        ok = "success" in (proc.stdout or "").lower() or proc.returncode == 0
        log(f"[PULL] {model} done ok={ok} returncode={proc.returncode}")
        if tail:
            log(f"[PULL] {model} tail: {tail[-1][:200]}")
    log("[PULL] fleet pull script finished")
    return 0


if __name__ == "__main__":
    sys.exit(main())