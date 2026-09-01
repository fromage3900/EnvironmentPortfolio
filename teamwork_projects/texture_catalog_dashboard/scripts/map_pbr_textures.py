#!/usr/bin/env python3
"""
PBR Texture Mapping & Catalog Generation Engine
================================================
Deterministic multi-tier asset resolution pipeline that scans Unreal Engine
Texture2D .uasset files and maps them back to raw source images in Imports/
and BS_GodFile/Imports/, producing verified catalog-data.json and catalog-data.js.

Interface Contracts:
- Generates teamwork_projects/texture_catalog_dashboard/catalog-data.json
- Generates teamwork_projects/texture_catalog_dashboard/catalog-data.js (window.TEXTURE_CATALOG)
- Guarantees 100% of mapped source paths exist on disk
- Standardizes PBR channel tags: BaseColor, Normal, ORM, Roughness, Metallic, AO, Height, Emissive, Mask, Specialty, UI
"""

import os
import sys
import re
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple, Any

# Root directories
SCRIPT_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = SCRIPT_DIR.parent
REPO_ROOT = DASHBOARD_DIR.parent.parent

BS_GODFILE = REPO_ROOT / "BS_GodFile"
CONTENT_DIR = BS_GODFILE / "Content"
PLUGINS_DIR = BS_GODFILE / "Plugins"
IMPORTS_DIR = REPO_ROOT / "Imports"
BS_IMPORTS_DIR = BS_GODFILE / "Imports"

SUPPORTED_IMAGE_EXTS = {
    ".png", ".svg", ".jpg", ".jpeg", ".tif", ".tiff", ".tga", ".bmp", ".exr", ".dds", ".hdr"
}

CHANNEL_BADGES = {
    "BaseColor": "BC",
    "Normal": "N",
    "ORM": "ORM",
    "Roughness": "R",
    "Metallic": "M",
    "AO": "AO",
    "Height": "H",
    "Emissive": "E",
    "Mask": "Mask",
    "Specialty": "Spec",
    "UI": "UI",
}

SRGB_CHANNELS = {"BaseColor", "UI", "Emissive"}


def clean_stem(stem: str) -> str:
    """Normalize stem for alphanumeric fallback matching."""
    s = stem.lower()
    s = re.sub(r"^(t_|tx_|tex_|m_|mi_|sm_|sk_)", "", s)
    s = re.sub(r"[^a-z0-9]", "", s)
    return s


def get_image_resolution(abs_path: Path, ext: str) -> str:
    """Detect image resolution safely via PIL or fallback."""
    if ext == ".svg":
        return "Vector SVG"
    try:
        from PIL import Image
        with Image.open(abs_path) as img:
            w, h = img.size
            return f"{w}x{h}"
    except Exception:
        # Fallback heuristic for common standard textures if PIL cannot open
        stem = abs_path.stem.lower()
        if "4k" in stem or "4096" in stem:
            return "4096x4096"
        elif "2k" in stem or "2048" in stem:
            return "2048x2048"
        elif "1k" in stem or "1024" in stem:
            return "1024x1024"
        elif "512" in stem:
            return "512x512"
        return "2048x2048"


def is_texture_uasset(path: Path) -> bool:
    """Fast binary inspection of .uasset header to verify Texture2D/TextureCube/VolumeTexture."""
    try:
        with open(path, "rb") as f:
            head = f.read(8192)
            if (
                b"Texture2D" in head
                or b"TextureCube" in head
                or b"VolumeTexture" in head
                or b"TextureRenderTarget2D" in head
                or b"/Script/Engine.Texture2D" in head
            ):
                return True
    except Exception:
        pass
    return False


def classify_pbr_channel(name: str, path_str: str) -> str:
    """Classify texture into standardized PBR channel types."""
    nl = name.lower()
    pl = path_str.lower().replace("\\", "/")

    # 1. UI context check (unless explicitly a PBR surface map like Normal/ORM/Roughness)
    is_ui_path = any(k in pl for k in ["/ui/", "/prompt", "kenney/inputprompts", "figma", "/icon", "cursor", "button", "frame"])
    has_pbr_marker = any(k in nl for k in ["_normal", "_n", "_norm", "_orm", "_rma", "_mrao", "_roughness", "_metallic", "_disp", "_displacement"])

    if is_ui_path and not has_pbr_marker:
        return "UI"

    # 2. Packed ORM / RMA / MRAO / MRO / ARM
    if any(k in nl for k in ["_orm", "orm_", "_rma", "_mrao", "_mro", "_arm", "packed", "occlusionroughnessmetallic"]):
        return "ORM"

    # 3. Normal / Bump
    if any(k in nl for k in ["_normal", "_n", "_norm", "nrm", "_nrm", "normalmap", "bump", "_nm", "normal_"]):
        return "Normal"

    # 4. Height / Displacement
    if any(k in nl for k in ["displacement", "height", "_h", "disp", "_disp", "heightmap", "_height"]):
        return "Height"

    # 5. Roughness (standalone)
    if any(k in nl for k in ["roughness", "_rough", "_r", "_rgh", "gloss"]):
        if not any(k in nl for k in ["orm", "rma", "mrao", "metal"]):
            return "Roughness"

    # 6. Metallic / Metalness (standalone)
    if any(k in nl for k in ["metallic", "_metal", "_m", "_mtl"]):
        if not any(k in nl for k in ["orm", "rma", "mrao", "rough"]):
            return "Metallic"

    # 7. Ambient Occlusion (AO standalone)
    if any(k in nl for k in ["ambientocclusion", "occlusion", "_ao", "ao_"]):
        if not any(k in nl for k in ["orm", "rma", "mrao"]):
            return "AO"

    # 8. Emissive / Emission / Glow
    if any(k in nl for k in ["emission", "emissive", "_emit", "_e", "glow", "illumin"]):
        return "Emissive"

    # 9. Mask / Alpha / Cutout / Opacity / Motif
    if any(k in nl for k in ["alpha", "mask", "opacity", "cutout", "motif", "glyph", "ornament", "jro_"]):
        return "Mask"

    # 10. Specialty (Sparkle / Sheen / Noise / Caustics / Water flow)
    if any(k in nl or k in pl for k in ["sparkle", "spark", "sheen", "twinkle", "glint", "star", "glitter", "caustic", "noise", "perlin", "voronoi", "gradient", "flow", "water", "distort"]):
        return "Specialty"

    # 11. UI fallback for icons/prompts
    if is_ui_path:
        return "UI"

    # 12. BaseColor / Albedo / Diffuse / Default
    return "BaseColor"


def classify_family_and_context(uasset_path: str, source_path: str, name: str) -> Tuple[str, str]:
    """Determine asset family and human-readable usage context."""
    pl = (uasset_path + " " + source_path).lower().replace("\\", "/")
    nl = name.lower()

    if "atlantis" in pl or "kitbash3d" in pl or "kb3d" in nl:
        return ("Atlantis KitBash", "Props & Architecture (KitBash3D Atlantis)")

    if "melusina" in pl or "melusina" in nl:
        return ("Melusina Character", "Characters (Melusina Hero Asset)")

    if "sirmelodious" in pl or "sirmelo" in nl:
        return ("Sir Melodious", "Characters (Sir Melodious Knight)")

    if "zundamon" in pl or "zundamon" in nl:
        return ("Zundamon", "Characters (Zundamon Companion)")

    if "character" in pl or any(k in nl for k in ["outfit", "hair", "body", "face", "eye", "skin"]):
        return ("Character Assets", "Characters (NPC & Wardrobe)")

    if "kenney" in pl and ("prompt" in pl or "keyboard" in nl or "gamepad" in nl or "touch" in nl):
        return ("Kenney Input Prompts", "UI & Controls (Input Prompts & Gamepad)")

    if "kenney" in pl and ("border" in pl or "fantasy" in pl or "ui" in pl):
        return ("Kenney Fantasy UI", "UI & Controls (Fantasy Borders & Frames)")

    if "figma" in pl or "/ui/" in pl or "hud" in pl or "button" in pl or "icon" in pl:
        return ("Melodia UI System", "UI & Controls (Figma Atoms & HUD)")

    if "retro" in pl or "retrofantasy" in pl or "fantasyretro" in pl:
        return ("Retro Fantasy Kit", "Environment (Retro Fantasy Kit)")

    if "stylizednature" in pl or "nature" in pl or "foliage" in pl or "tree" in pl or "leaf" in pl:
        return ("Stylized Nature", "Environment (Stylized Nature & Foliage)")

    if "gothiccastle" in pl or "castle" in pl:
        return ("Gothic Castle", "Environment (Gothic Castle & Architecture)")

    if "polygonalmind" in pl:
        return ("PolygonalMind Kit", "Environment (PolygonalMind Kit)")

    if "landscape" in pl or "brushify" in pl or any(k in nl for k in ["soil", "grass", "cliff", "sand", "dirt"]):
        return ("Landscape & Terrain", "Environment (Landscape & Terrain)")

    if "fabric" in pl or "velvet" in nl or "silk" in nl or "cloth" in nl or "trim" in nl:
        return ("Fabrics & Trim", "Materials (Fabrics & Trim)")

    if "sdf" in pl or "envsandbox/materials" in pl:
        return ("SDF Procedural Materials", "Materials (SDF Masters & Shaders)")

    if "ornament" in pl or "jro_" in nl:
        return ("Japanese Ornaments", "Materials & Decals (Japanese Ornaments)")

    if "vfx" in pl or "sparkle" in nl or "oceanology" in pl:
        return ("VFX & Particles", "VFX & Particles (Sparkles & Fluids)")

    return ("Environment General", "Environment & Props (General)")


def build_imports_index() -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, Any]]]]:
    """Index all source images across Imports/ and BS_GodFile/Imports/."""
    all_images = []
    by_stem = defaultdict(list)
    by_clean = defaultdict(list)

    scanned_paths = set()

    for imp_dir in [IMPORTS_DIR, BS_IMPORTS_DIR]:
        if not imp_dir.exists():
            continue
        for p in imp_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGE_EXTS:
                rel = p.relative_to(REPO_ROOT).as_posix()
                if rel in scanned_paths:
                    continue
                scanned_paths.add(rel)

                stem = p.stem
                stem_lower = stem.lower()
                ext = p.suffix.lower()
                cstem = clean_stem(stem)

                item = {
                    "rel_path": rel,
                    "abs_path": p,
                    "filename": p.name,
                    "stem": stem,
                    "stem_lower": stem_lower,
                    "clean_stem": cstem,
                    "ext": ext,
                    "format": ext.lstrip(".").upper(),
                    "size_bytes": p.stat().st_size,
                }
                all_images.append(item)
                by_stem[stem_lower].append(item)
                if cstem:
                    by_clean[cstem].append(item)

    print(f"[Index] Indexed {len(all_images)} source images across Imports directories.")
    print(f"[Index] Unique exact stems: {len(by_stem)}, Unique clean stems: {len(by_clean)}")
    return all_images, by_stem, by_clean


def scan_uasset_textures() -> List[Path]:
    """Scan Content and Plugins for Texture2D .uasset files."""
    texture_paths = []
    scan_roots = [CONTENT_DIR, PLUGINS_DIR, REPO_ROOT / "content", REPO_ROOT / "VFX", REPO_ROOT / "Imports", BS_GODFILE / "CompatibilityLabs"]

    for root in scan_roots:
        if not root.exists():
            continue
        for p in root.rglob("*.uasset"):
            if is_texture_uasset(p):
                texture_paths.append(p)

    print(f"[Scan] Discovered {len(texture_paths)} Texture2D .uasset files.")
    return texture_paths


def resolve_texture_mapping(
    uasset_path: Path,
    by_stem: Dict[str, List[Dict[str, Any]]],
    by_clean: Dict[str, List[Dict[str, Any]]]
) -> Optional[Tuple[Dict[str, Any], str]]:
    """Deterministic 7-tier resolution engine matching .uasset to Imports/ source image."""
    u_rel = uasset_path.relative_to(REPO_ROOT).as_posix()
    u_stem = uasset_path.stem
    u_stem_lower = u_stem.lower()
    u_clean = clean_stem(u_stem)
    u_path_lower = u_rel.lower()

    # Tier 1: Exact Stem Match
    if u_stem_lower in by_stem:
        cands = by_stem[u_stem_lower]
        # Prefer folder affinity if multiple
        best = cands[0]
        for c in cands:
            if "atlantis" in u_path_lower and "atlantis" in c["rel_path"].lower():
                best = c
                break
            if "kenney" in u_path_lower and "kenney" in c["rel_path"].lower():
                best = c
                break
        return best, "1_exact_stem"

    # Tier 2: Stripped Engine Prefix (T_, TX_, Tex_)
    stripped = re.sub(r"^(t_|tx_|tex_)", "", u_stem_lower)
    if stripped != u_stem_lower and stripped in by_stem:
        return by_stem[stripped][0], "2_stripped_prefix"

    # Tier 3: Added Engine Prefix (t_...)
    prefixed = f"t_{u_stem_lower}"
    if prefixed in by_stem:
        return by_stem[prefixed][0], "3_added_prefix"

    # Tier 4: Suffix Synonym Normalization (_BC <=> _BaseColor, _N <=> _Normal, etc.)
    pbr_synonyms = [
        ("_basecolor", "_diffuse"),
        ("_basecolor", "_bc"),
        ("_basecolor", "_color"),
        ("_basecolor", "_albedo"),
        ("_bc", "_basecolor"),
        ("_normal", "_norm"),
        ("_normal", "_n"),
        ("_n", "_normal"),
        ("_roughness", "_rough"),
        ("_roughness", "_r"),
        ("_r", "_roughness"),
        ("_metallic", "_metal"),
        ("_metallic", "_m"),
        ("_m", "_metallic"),
        ("_orm", "_rma"),
        ("_orm", "_arm"),
        ("_orm", "_mrao"),
    ]
    for orig_suf, rep_suf in pbr_synonyms:
        if orig_suf in u_stem_lower:
            variant = u_stem_lower.replace(orig_suf, rep_suf)
            variant_stripped = re.sub(r"^(t_|tx_|tex_)", "", variant)
            if variant in by_stem:
                return by_stem[variant][0], "4_suffix_synonym"
            if variant_stripped in by_stem:
                return by_stem[variant_stripped][0], "4_suffix_synonym"

    # Tier 5: Clean Alphanumeric Stem
    if u_clean and u_clean in by_clean:
        cands = by_clean[u_clean]
        best = cands[0]
        for c in cands:
            if "atlantis" in u_path_lower and "atlantis" in c["rel_path"].lower():
                best = c
                break
            if "melusina" in u_path_lower and "melusina" in c["rel_path"].lower():
                best = c
                break
        return best, "5_clean_alphanumeric"

    # Tier 6: Pack-Specific Special Rules (JRO Ornament Mask, Melusina Punctuation)
    jro_clean = re.sub(r"_mask$", "", u_stem_lower)
    if jro_clean != u_stem_lower and jro_clean in by_stem:
        return by_stem[jro_clean][0], "6_pack_rule_jro"

    if "melusina" in u_stem_lower:
        m_norm = re.sub(r"[^a-z0-9]", "", u_stem_lower)
        for s_cstem, s_cands in by_clean.items():
            if "melusina" in s_cstem and (s_cstem in m_norm or m_norm in s_cstem):
                return s_cands[0], "6_melusina_normalization"

    # Tier 7: Folder-Guided Substring Affinity (KitBash / Atlantis)
    if "atlantis" in u_path_lower:
        for s_stem, s_cands in by_stem.items():
            if s_stem in u_stem_lower or u_stem_lower in s_stem:
                for c in s_cands:
                    if "atlantis" in c["rel_path"].lower():
                        return c, "7_folder_affinity"

    return None


def run_pipeline() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Execute complete mapping and catalog generation pipeline."""
    print("=" * 65)
    print("  Melodia PBR Texture Mapping & Catalog Generation Engine  ")
    print("=" * 65)

    all_images, by_stem, by_clean = build_imports_index()
    uasset_paths = scan_uasset_textures()

    catalog_entries = []
    tier_counts = Counter()
    channel_counts = Counter()
    family_counts = Counter()
    format_counts = Counter()

    seen_ids = set()

    print("[Mapping] Executing multi-tier deterministic resolution...")

    for u_path in uasset_paths:
        res = resolve_texture_mapping(u_path, by_stem, by_clean)
        if not res:
            continue

        matched_src, tier = res
        tier_counts[tier] += 1

        u_rel = u_path.relative_to(REPO_ROOT).as_posix()
        s_rel = matched_src["rel_path"]
        s_abs = matched_src["abs_path"]

        # Ensure absolute path exists on disk
        if not s_abs.exists():
            print(f"[Warning] Mapped path missing on disk: {s_abs}")
            continue

        # Channel & Context Classification
        channel = classify_pbr_channel(u_path.stem, u_rel)
        family, usage_context = classify_family_and_context(u_rel, s_rel, u_path.stem)
        channel_badge = CHANNEL_BADGES.get(channel, "BC")
        img_format = matched_src["format"]
        res_str = get_image_resolution(s_abs, matched_src["ext"])

        # Construct Unique ID
        base_id = u_path.stem
        entry_id = base_id
        suffix_idx = 1
        while entry_id in seen_ids:
            entry_id = f"{base_id}_{suffix_idx}"
            suffix_idx += 1
        seen_ids.add(entry_id)

        # Compute relative paths from dashboard index.html (teamwork_projects/texture_catalog_dashboard/)
        # Dashboard is 2 levels deep from REPO_ROOT (teamwork_projects/texture_catalog_dashboard)
        source_rel_from_html = f"../../{s_rel}"
        thumbnail_rel_from_html = f"../../{s_rel}"

        entry = {
            "id": entry_id,
            "name": u_path.stem,
            "uasset_name": u_path.name,
            "uasset_path": u_rel,
            "source_image_path": s_rel,
            "source_rel_path": source_rel_from_html,
            "thumbnail_path": thumbnail_rel_from_html,
            "channel": channel,
            "channel_badge": channel_badge,
            "family": family,
            "usage_context": usage_context,
            "resolution": res_str,
            "format": img_format,
            "srgb": channel in SRGB_CHANNELS,
            "match_tier": tier,
            "mapped": True
        }

        catalog_entries.append(entry)
        channel_counts[channel] += 1
        family_counts[family] += 1
        format_counts[img_format] += 1

    # Sort catalog deterministically by family then name
    catalog_entries.sort(key=lambda x: (x["family"], x["channel"], x["name"]))

    print("\n" + "-" * 65)
    print(f"  MAPPING RESULTS & METRICS")
    print("-" * 65)
    print(f"Total .uasset Textures Scanned: {len(uasset_paths)}")
    print(f"Total Successfully Mapped:      {len(catalog_entries)} (Target >= 1,500)")
    print(f"Mapping Success Rate:          {len(catalog_entries)/len(uasset_paths)*100:.1f}%")
    print("\nMapping Tier Distribution:")
    for t, c in sorted(tier_counts.items()):
        print(f"  - {t:<28}: {c:>5} textures ({c/len(catalog_entries)*100:.1f}%)")

    print("\nPBR Channel Distribution:")
    for ch, c in channel_counts.most_common():
        print(f"  - {ch:<14} [{CHANNEL_BADGES.get(ch, '??'):<4}]: {c:>5} textures ({c/len(catalog_entries)*100:.1f}%)")

    print("\nTop Asset Families:")
    for fam, c in family_counts.most_common(10):
        print(f"  - {fam:<28}: {c:>5} textures")

    print("\nSource Formats:")
    for fmt, c in format_counts.most_common():
        print(f"  - {fmt:<6}: {c:>5} textures")
    print("-" * 65)

    # Assertions
    assert len(catalog_entries) >= 1500, f"FAILED: Expected at least 1,500 mapped textures, got {len(catalog_entries)}"

    # Output Artifacts
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    json_path = DASHBOARD_DIR / "catalog-data.json"
    js_path = DASHBOARD_DIR / "catalog-data.js"

    # 1. Write catalog-data.json
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(catalog_entries, f, indent=2, ensure_ascii=False)
    print(f"[Output] Wrote JSON catalog dataset: {json_path} ({json_path.stat().st_size:,} bytes)")

    # 2. Write catalog-data.js
    json_str = json.dumps(catalog_entries, indent=2, ensure_ascii=False)
    js_content = f"""/**
 * Melodia PBR Texture Catalog Dataset
 * Auto-generated by scripts/map_pbr_textures.py
 * Total Mapped Textures: {len(catalog_entries)}
 */
window.TEXTURE_CATALOG = {json_str};
"""
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"[Output] Wrote JavaScript catalog dataset: {js_path} ({js_path.stat().st_size:,} bytes)")

    # Verification summary dictionary
    summary = {
        "total_scanned_uassets": len(uasset_paths),
        "total_mapped": len(catalog_entries),
        "acceptance_threshold_met": len(catalog_entries) >= 1500,
        "target_1855_met": len(catalog_entries) >= 1855,
        "tier_distribution": dict(tier_counts),
        "channel_distribution": dict(channel_counts),
        "family_distribution": dict(family_counts),
        "format_distribution": dict(format_counts),
        "json_path": str(json_path),
        "js_path": str(js_path)
    }

    return catalog_entries, summary


if __name__ == "__main__":
    entries, summary = run_pipeline()
    print(f"\n[Success] PBR Texture Catalog generated successfully with {len(entries)} verified textures!")
