#!/usr/bin/env python
"""SpeedTree -> Houdini bridge for the Sea Above P0 foliage kit.

Run with hython:
    hython.exe speedtree_bridge.py --stmat <file.stmat> [--preset KelpRibbon] [--out Imports/SeaAboveFoliage/<Asset>]

What it does (uses IDV's own shipped bridge, no reverse engineering):
  1. Adds SpeedTree Modeler's 'scripts/Houdini' folder to sys.path and imports
     the official SpeedTreeImport module (SpeedTreeImport.otl provides the
     'SpeedTreeImport' SOP; script.py provides LoadSpeedTree()).
  2. Calls LoadSpeedTree(stmat, materialCreatorFunc) to bring the tree geometry
     into /obj with SpeedTreePrincipled materials (per stmat maps: Color,
     Normal, Opacity, Gloss, Specular, Metallic).
  3. Runs the Copernicus texture bake for the matched preset
     (build_seaabove_foliage_textures.py --presets <preset>).
  4. Writes the SpeedTree-exported mesh (USD preferred; FBX fallback) into
     Imports/SeaAboveFoliage/<AssetName>/ so build_seaabove_kit.py can pick it
     up unchanged.

Prereq: export from SpeedTree Modeler v10 with 'Export wind data' enabled.
SpeedTree paths are auto-detected (see find_speedtree_scripts()).
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import sys

SPEEDTREE_ROOTS = (
    r"C:\Program Files\SpeedTree",
    r"C:\Program Files (x86)\SpeedTree",
)
PRESETS = ("KelpRibbon", "Bubbleweed", "LilyPad", "CoralFan", "DropletGrass", "SpawnGlow")
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def find_speedtree_scripts() -> str:
    """Locate the newest SpeedTree Modeler scripts/Houdini folder."""
    for root in SPEEDTREE_ROOTS:
        if not os.path.isdir(root):
            continue
        versions = sorted(
            (d for d in os.listdir(root) if "Modeler" in d), reverse=True)
        for v in versions:
            candidate = os.path.join(root, v, "scripts", "Houdini")
            if os.path.isfile(os.path.join(candidate, "script.py")):
                return candidate
    raise SystemExit("SpeedTree Modeler scripts/Houdini not found — install/repair SpeedTree Modeler")


def load_speedtree_module(scripts_dir: str):
    """Import the vendor script.py as module 'st_speedtree_import' (path-safe)."""
    spec = importlib.util.spec_from_file_location(
        "st_speedtree_import", os.path.join(scripts_dir, "script.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["st_speedtree_import"] = mod
    spec.loader.exec_module(mod)
    import hou
    mod.__dict__["hou"] = hou  # vendor script uses 'hou' without importing it
    return mod

def match_preset(asset_name: str) -> str:
    lowered = asset_name.lower()
    for p in PRESETS:
        if p.lower() in lowered:
            return p
    return PRESETS[0]


def run_copernicus_bake(preset: str, res: int) -> str:
    """Bake the preset's texture set via the sibling bake script."""
    bake = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "build_seaabove_foliage_textures.py")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "exports", "seaabove_textures")
    import subprocess
    cmd = [sys.executable, bake, "--res", str(res), "--presets", preset, "--out", out]
    print("[STBridge] bake:", " ".join(cmd))
    subprocess.check_call(cmd)
    return out


def stage_mesh_for_ue(st_dir: str, dest_dir: str) -> str:
    """Copy the SpeedTree-exported mesh (USD/FBX/OBJ/stmat) into the UE staging dir."""
    os.makedirs(dest_dir, exist_ok=True)
    staged = 0
    for fn in sorted(os.listdir(st_dir)):
        ext = os.path.splitext(fn)[1].lower()
        if ext in (".usd", ".usda", ".usdc", ".fbx", ".obj", ".stmat"):
            shutil.copy2(os.path.join(st_dir, fn), os.path.join(dest_dir, fn))
            staged += 1
    print(f"[STBridge] staged {staged} files -> {dest_dir}")
    return dest_dir


def export_fbx_from_houdini(asset_name: str, st_dir: str, dest_dir: str) -> str | None:
    """Ensure a UE-ready FBX exists in dest_dir. Prefer the SpeedTree-exported
    FBX (Modeler writes one next to the .stmat); fall back to Houdini FBX ROP
    only when needed. Houdini Apprentice blocks the ROP — in that case we
    warn and rely on the vendor FBX."""
    os.makedirs(dest_dir, exist_ok=True)
    fbx_path = os.path.join(dest_dir, f"{asset_name}.fbx")
    vendor_fbx = os.path.join(st_dir, f"{asset_name}.fbx")
    if os.path.isfile(vendor_fbx):
        shutil.copy2(vendor_fbx, fbx_path)
        print(f"[STBridge] staged vendor FBX: {fbx_path}")
        return fbx_path

    obj_node = hou.node(f"/obj/{asset_name}")
    if obj_node is None:
        print(f"[STBridge] WARNING: /obj/{asset_name} not found; skipping FBX export")
        return None
    rop = hou.node("/out").createNode("filmboxfbx")
    rop.setName(f"stbridge_fbx_{asset_name}")
    rop.parm("startnode").set(obj_node.path())
    rop.parm("sopoutput").set(fbx_path)
    rop.parm("execute").pressButton()
    ok = os.path.isfile(fbx_path)
    print(f"[STBridge] FBX export {'OK' if ok else 'FAILED'}: {fbx_path}")
    return fbx_path if ok else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stmat", required=True, help="SpeedTree .stmat export")
    ap.add_argument("--res", type=int, default=512)
    args = ap.parse_args()

    import hou  # hython only from here on
    stmat = os.path.abspath(args.stmat)
    if not os.path.isfile(stmat):
        raise SystemExit(f"stmat not found: {stmat}")
    asset_name = os.path.splitext(os.path.basename(stmat))[0]
    preset = match_preset(asset_name)
    print(f"[STBridge] asset={asset_name} preset={preset}")

    # 1) official IDV import
    scripts_dir = find_speedtree_scripts()
    print(f"[STBridge] SpeedTree scripts: {scripts_dir}")
    sys.path.insert(0, scripts_dir)
    st = load_speedtree_module(scripts_dir)
    # hython already starts in a default untitled session — do NOT reload the
    # hip file (a failed load can drop /obj, and the vendor swallows the error).
    if hou.node("/obj") is None:
        hou.node("/").createNode("obj", "obj")
    otl = os.path.join(scripts_dir, "SpeedTreeImport.otl")
    if os.path.isfile(otl):
        try:
            hou.hda.installFile(otl)
            print("[STBridge] installed SpeedTreeImport.otl")
        except Exception as ex:
            print(f"[STBridge] OTL install skipped: {ex}")
    st.LoadSpeedTree(stmat, None, [0.0, 0.0, 0.0])
    if hou.node(f"/obj/{asset_name}") is None:
        print(f"[STBridge] WARNING: LoadSpeedTree did not produce /obj/{asset_name} "
              "(vendor swallowed the error — check the stmat/mesh above)")
    print(f"[STBridge] LoadSpeedTree done for {stmat}")

    # 2) bake the preset textures (Copernicus recipe / fallback)
    run_copernicus_bake(preset, args.res)

    # 3) export FBX (UE intake format) + stage mesh exports for UE intake
    st_dir = os.path.dirname(stmat)
    dest_dir = os.path.join(REPO, "Imports", "SeaAboveFoliage", asset_name)
    export_fbx_from_houdini(asset_name, st_dir, dest_dir)
    stage_mesh_for_ue(st_dir, dest_dir)
    print(f"[STBridge] done — next: run 'SeaAbove: Import & Wire Foliage Kit' in VS Code")


if __name__ == "__main__":
    main()

