#!/usr/bin/env python3
"""
Verification Script for PBR Texture Catalog Artifacts
"""
import os
import sys
import json
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(line_buffering=True)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DASHBOARD_DIR = REPO_ROOT / "teamwork_projects" / "texture_catalog_dashboard"
JSON_FILE = DASHBOARD_DIR / "catalog-data.json"
JS_FILE = DASHBOARD_DIR / "catalog-data.js"

print("Starting verification...", flush=True)

# 1. Existence
assert JSON_FILE.exists(), f"Missing {JSON_FILE}"
assert JS_FILE.exists(), f"Missing {JS_FILE}"
print(f"[OK] Found files: json={JSON_FILE.stat().st_size:,} bytes, js={JS_FILE.stat().st_size:,} bytes", flush=True)

# 2. JSON Parse
with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)
print(f"[OK] Parsed JSON. Total items: {len(data):,}", flush=True)

# 3. Assert count
assert len(data) >= 1500, f"Count {len(data)} < 1500"
assert len(data) >= 1855, f"Count {len(data)} < 1855"

# 4. Check disk paths
missing = []
for item in data:
    p = REPO_ROOT / item["source_image_path"]
    if not p.is_file():
        missing.append(item["source_image_path"])

print(f"[OK] Checked disk paths. Missing count: {len(missing)}", flush=True)
assert len(missing) == 0, f"Missing files: {missing[:5]}"

# 5. Check JS file
js_text = JS_FILE.read_text(encoding="utf-8")
assert "window.TEXTURE_CATALOG = [" in js_text
assert js_text.strip().endswith("];")
print("[OK] JS structure valid.", flush=True)

# 6. Channels
channels = Counter(item["channel"] for item in data)
print(f"[OK] Channel breakdown: {dict(channels)}", flush=True)
assert len(channels) == 11, f"Expected 11 channels, got {len(channels)}"

print("\n>>> ALL VERIFICATIONS PASSED SUCCESSFULLY! <<<", flush=True)
