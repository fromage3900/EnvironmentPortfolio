# -*- coding: utf-8 -*-
"""Milestone 1 Challenger Comprehensive Audit Script with Deep Quality Checks."""
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIX_DIR = os.path.join(REPO_ROOT, 'wix')

print("=== COMPREHENSIVE CHALLENGER AUDIT ===")
print(f"Target Directory: {WIX_DIR}\n")

forbidden_patterns = [
    (r'SK_Melusina', 'Internal Skeleton Name'),
    (r'SK_MelusinaHair', 'Internal Hair Skeletal Name'),
    (r'SK_Melusina_Skeleton', 'Internal Skeleton Asset Name'),
    (r'A_Melusina_Idle', 'Internal Animation Asset Name'),
    (r'F_Melodia_UI', 'Internal Struct/Asset Name'),
    (r'BlenderMCP', 'Internal Tooling String'),
    (r':9876\b', 'Raw Socket Port 9876'),
    (r':9316\b', 'Raw Socket Port 9316'),
    (r':9317\b', 'Raw Socket Port 9317'),
    (r':55558\b', 'Raw Socket Port 55558'),
    (r':50021\b', 'Raw Socket Port 50021'),
    (r'L_Melusina\b', 'Internal Level Asset L_Melusina'),
    (r'L_MelusinaMorning\b', 'Internal Level L_MelusinaMorning'),
    (r'L_Kaleido\b', 'Internal Level L_Kaleido'),
    (r'owner-lock', 'Agent Lock String'),
    (r'A1 stock battle', 'Agent Battle Status'),
    (r'33/165|presets 33', 'Fraction Progress Slop'),
    (r'bald cache|globules|max Z\s*≈', 'Geometry Debug Jargon'),
    (r'\bWORKED\b', 'Agent Worked Status'),
    (r'P0 heroes smoked', 'Internal Test Status'),
    (r'RQ_MEL_', 'Review Queue Internal Code'),
    (r'WBP_MelodiaRhythmHighway', 'Raw Widget Blueprint Name'),
    (r'RTG_Mocap_to_Melusina', 'Raw Retarget Asset Name'),
    (r'MonolithCalls\.jsonl', 'Internal MCP Log Path'),
    (r'PARTIAL/FALSE', 'Internal Agent Dispute Tag'),
    (r'SK fallback', 'Pipeline Shorthand Slop'),
    (r'not wired', 'Pipeline Shorthand Slop'),
    (r'Alembic 1[–-]240', 'Pipeline Shorthand Slop'),
    (r'<<<<<<<', 'Git Conflict Start Marker'),
    (r'>>>>>>>', 'Git Conflict End Marker')
]

mojibake_tokens = [
    'ΓÇö', 'ΓåÆ', 'Γëê', 'ΓÇô', '┬╖', 'â€', '\ufffd', 'Ã©', 'Ã¢', 'Ã '
]

all_html = glob.glob(os.path.join(WIX_DIR, '**', '*.html'), recursive=True)

findings_slop = []
findings_mojibake = []

for filepath in sorted(all_html):
    rel_path = os.path.relpath(filepath, REPO_ROOT)
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        lines = content.splitlines()

    for idx, line in enumerate(lines, 1):
        for pat, label in forbidden_patterns:
            flags = re.IGNORECASE if label in [
                'Internal Skeleton Name', 
                'Internal Hair Skeletal Name',
                'Internal Skeleton Asset Name',
                'Internal Animation Asset Name', 
                'Internal Struct/Asset Name', 
                'Internal Tooling String', 
                'Internal Level Asset L_Melusina',
                'Internal Level L_MelusinaMorning',
                'Internal Level L_Kaleido',
                'Agent Lock String', 
                'Agent Battle Status', 
                'Agent Worked Status'
            ] else 0
            m = re.search(pat, line, flags)
            if m:
                findings_slop.append((rel_path, idx, label, m.group(0), line.strip()))

        for token in mojibake_tokens:
            if token in line:
                findings_mojibake.append((rel_path, idx, token, line.strip()))

print(f"Scanned {len(all_html)} HTML files in wix/.")
print(f"Total Slop / Leaked Artifact Findings: {len(findings_slop)}")
print(f"Total Mojibake / Corrupted Char Findings: {len(findings_mojibake)}")

if findings_slop:
    print("\n--- SLOP / LEAKED ARTIFACT FINDINGS ---")
    for fp, lno, label, matched, line_text in findings_slop:
        print(f"  [{label}] {fp}:{lno} (matched: '{matched}') -> {line_text[:120]}")
else:
    print("  [PASS] 0 slop / leaked artifact matches.")

if findings_mojibake:
    print("\n--- MOJIBAKE / ENCODING FINDINGS ---")
    for fp, lno, token, line_text in findings_mojibake:
        print(f"  [Mojibake '{token}'] {fp}:{lno} -> {line_text[:120]}")
else:
    print("  [PASS] 0 mojibake matches.")

# Deep Quality audit on the 12 target files
m1_targets = [
    'wix/application-hub.html',
    'wix/index.html',
    'wix/design-specs.html',
    'wix/credits.html',
    'wix/geometry-nodes.html',
    'wix/melodia-gameplay-loop.html',
    'wix/melodia-melusina.html',
    'wix/melodia-stage-character.html',
    'wix/pipeline.html',
    'wix/surreal-architecture.html',
    'wix/t3d-catalog.html',
    'wix/agent-dashboard-t3d.html'
]

hedging_regex = re.compile(r'\b(tried to|attempted|helped with)\b', re.IGNORECASE)
raw_hex_regex = re.compile(r'style=["\'][^"\']*(?:#[0-9a-fA-F]{3,8}|rgba?\([^)]+\))[^"\']*["\']')

print("\n=== DEEP QUALITY AUDIT ON 12 MILESTONE 1 TARGET FILES ===")
for target in m1_targets:
    full_path = os.path.join(REPO_ROOT, target)
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    hedges = hedging_regex.findall(content)
    raw_styles = raw_hex_regex.findall(content)
    has_hero = bool(re.search(r'<section\s+class="[^"]*hero[^"]*"', content))
    
    print(f"\n[{target}]")
    print(f"  - Hero Section Present: {has_hero}")
    print(f"  - Hedging Instances: {len(hedges)} {set(hedges) if hedges else ''}")
    print(f"  - Raw Inline Hex/RGBA Styles: {len(raw_styles)}")
