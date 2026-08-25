#!/usr/bin/env python3
"""
Audit Surreal GN builders: group by 12 stack categories, families, pillars, coverage.
Outputs to Saved/Audit/gn_triage_20260825.json and prints summary.
No edits to monolith; read-only.
"""
import re, json, pathlib
from collections import Counter, defaultdict

REPO = pathlib.Path(r"C:\EnvironmentPortfolio\BS_GodFile")
MONO = REPO / "deploy" / "surreal_architecture_gen.py"
CATALOG = pathlib.Path(r"C:\EnvironmentPortfolio\generated\surreal_architecture_catalog.json")
OUT = REPO / "Saved" / "Audit" / "gn_triage_20260825.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

txt = MONO.read_text(encoding="utf-8", errors="ignore")

# --- parse _ARCH_CATEGORIES ---
# pattern: ('CAT_ID', "Label", 'ICON', [ ('TYPE', "Label"), ... ])
cat_pat = re.compile(r"\('([A-Z_]+)',\s*\"([^\"]+)\"\s*,\s*'([^']+)'\s*,\s*\[([^\]]+)\]", re.S)
cats = []
for m in cat_pat.finditer(txt):
    cat_id, label, icon, inner = m.groups()
    types = re.findall(r"\('([A-Z_]+)'", inner)
    cats.append({"id": cat_id, "label": label.strip(), "icon": icon, "count": len(types), "types": types})

# --- parse _ARCH_PICKER_STYLE_GROUPS if present ---
picker_pat = re.compile(r"_ARCH_PICKER_STYLE_GROUPS\s*=\s*\[([^\]]+)\]", re.S)
picker = []
if picker_pat.search(txt):
    block = picker_pat.search(txt).group(1)
    for sm in re.finditer(r"\('([^']+)',\s*\"([^\"]+)\"\s*,\s*\[([^\]]+)\]", block):
        sid, sname, members = sm.groups()
        cats_in = re.findall(r"'([A-Z_]+)'", members)
        picker.append({"style_id": sid, "label": sname, "categories": cats_in})

# --- load catalog families/genomes ---
cat_data = json.loads(CATALOG.read_text(encoding="utf-8"))
families = cat_data.get("families", {})
genomes = cat_data.get("genomes", [])
proof = cat_data.get("proof", {})

# Build genome -> family map
genome_by_family = defaultdict(list)
for g in genomes:
    genome_by_family[g.get("family","?")].append(g["id"])

# Count
total_builders = proof.get("gn_builders", sum(c["count"] for c in cats))
stack_cats = proof.get("gn_stack_categories", len(cats))
preset_coverage = proof.get("preset_coverage", "?")

# Pillar mapping heuristic: cat label contains Zen/Gothic etc -> pillar
def cat_pillar(cat_id, label):
    low = (cat_id + label).lower()
    if "zen" in low: return "zen (sakura pink #E7C9CE / rose #E8A9A1)"
    if "gothic" in low or "romanesque" in low: return "cathedral/cosmic (astral #8AA9D6 / iris #6E5AA6)"
    if "greybox" in low or "brutalist" in low or "sci" in low: return "grotto/plaza (gold #C9A86A / lavender #9F94C6)"
    if "art" in low or "baroque" in low or "venetian" in low: return "plaza/nikki (lavender/sakura)"
    if "nikki" in low: return "nikki (rose/parchment)"
    return "gold ivory default"

for c in cats:
    c["pillar"] = cat_pillar(c["id"], c["label"])

# Find heavy vs light categories
heavy = sorted(cats, key=lambda x: x["count"], reverse=True)

report = {
    "as_of": "2026-08-25",
    "monolith": str(MONO),
    "catalog_version": cat_data.get("version"),
    "totals": {
        "gn_builders": total_builders,
        "stack_categories": stack_cats,
        "families": len(families),
        "genomes": len(genomes),
        "preset_coverage": preset_coverage,
        "preset_looks": proof.get("preset_looks"),
    },
    "categories_sorted_by_weight": heavy,
    "style_picker_groups": picker,
    "families": [{"family": k, "count": v["count"], "samples": v["ids"][:4]} for k,v in families.items()],
    "genome_transforms": Counter(g.get("surreal_transform","?") for g in genomes),
    "recommendations": [
        "Keep 12 stack categories as NAV — they map cleanly to Wix/token pillars (see cat.pillar). Do NOT collapse.",
        "Heavy categories (GREYBOX 18, GOTHIC etc) need sub-filters: pillar accent automatically colors them in UI (gold vs sakura vs astral). The chrome pillar dots already encode this.",
        "Preset coverage 33/165 (20%) — the chrome preset grid surfaces 6 hero cards first; remaining 27 can be auto-discovered via picker groups. Add 'preset coverage' bar in Management panel.",
        "Surface preset cards with pink/rose-gold dot per family (zen = sakura #E7C9CE, greybox = gold #C9A86A, gothic = astral #8AA9D6). Already baked into melodia_chrome preset_*.png.",
        "Autosync: tools/generate_chrome_icons.py already reads wix/melodia-tokens.css; hook it to tools/figma_sync.py --chrome so token changes regenerate header_void.png/gold_rule.png without manual export.",
        "Do not move GN builder .py files — taxonomy lives in catalog + picker groups. Organizing = adding curated picker filters + pillar coloring, not filesystem churn.",
    ],
    "autosync_hook": "Add to tools/figma_sync.py: after kit export, run python tools/generate_chrome_icons.py (uses tokens.css SSOT, emits melodia_chrome/*.png). Blender reload picks them up via addon_utils._load_icons().",
}

OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {OUT}")
print(json.dumps(report["totals"], indent=2))
print("\nTop 5 heavy categories:")
for c in heavy[:5]:
    print(f"  {c['id']:18} {c['count']:3}  {c['pillar']}")
print("\nFamilies:")
for f in report["families"][:6]:
    print(f"  {f['family']:16} {f['count']:2}  {', '.join(f['samples'][:3])}")
print("\nTransforms:")
print(report["genome_transforms"])
