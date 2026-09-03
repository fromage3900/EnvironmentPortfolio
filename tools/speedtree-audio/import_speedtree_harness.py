#!/usr/bin/env python3
"""Import SpeedTree exports into BS_GodFile.

Run headless:
  UnrealEditor-Cmd.exe BS_GodFile.uproject -ExecutePythonScript <this> -unattended -noP4 -nullRHI -NOSOUND

Behavior:
  - Scans a source folder (SPEEDTREE_SOURCE_DIR below, or /Game source passed via
    `-Env:SPEEDTREE_SRC=...` style env override) for *.fbx SpeedTree exports.
  - Imports each as a StaticMesh (pivot preserved at trunk base, import uniform
    scale 1.0, generate lightmap UVs off — foliage uses wind vertex animation).
  - Lands assets under /Game/Melodia/Environment/Foliage/SpeedTree/<TreeName>/.

SpeedTree Modeler export settings (see README.md):
  - Geometry -> FBX, units = centimeters, Y-up conversion per UE default.
  - Enable "Export wind data" so branches/leaves bake vertex animation channels
    that UE's foliage wind material nodes consume.
  - Texture export = separate folder; import those PNG/TGA into the same
    destination folder before wiring materials (wire_audio_foliage_materials.py).

NOTE: The project also has the SpeedTreeImporter plugin enabled; if you hold an
.spm/.srt workflow license, importing those directly gives you the wind-aware
material factory for free. This script covers the plain FBX path so the harness
runs without additional licensing.
"""
import os
import sys

import unreal

# ---------------------------------------------------------------- config ----
SPEEDTREE_SOURCE_DIR = os.environ.get("SPEEDTREE_SRC", r"c:\EnvironmentPortfolio\Imports\SpeedTree")
DEST_ROOT = "/Game/Melodia/Environment/Foliage/SpeedTree"
TEXTURE_EXTS = (".png", ".tga", ".jpg", ".jpeg", ".exr")

log = unreal.log


def _sanitize(name: str) -> str:
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in name)


def import_texture(path: str, dest: str) -> None:
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = dest
    task.automated = True
    task.save = True
    task.replace_existing = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])


def import_speedtree_fbx(path: str, tree_name: str) -> None:
    dest = f"{DEST_ROOT}/{tree_name}"
    ui = unreal.FbxImportUI()
    ui.import_mesh = True
    ui.import_materials = False          # materials are built by wire_audio_foliage_materials.py
    ui.import_textures = False
    ui.import_as_skeletal = False        # static foliage; wind is vertex data, not skeletal
    ui.static_mesh_import_data.import_uniform_scale = 1.0
    ui.static_mesh_import_data.combine_meshes = False
    ui.static_mesh_import_data.generate_lightmap_u_vs = False
    ui.static_mesh_import_data.import_translation = unreal.Vector(0.0, 0.0, 0.0)
    ui.static_mesh_import_data.normal_import_method = unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS

    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = dest
    task.options = ui
    task.automated = True
    task.save = True
    task.replace_existing = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    log(f"[SpeedTreeHarness] imported FBX: {path} -> {dest}")


def main() -> None:
    if not os.path.isdir(SPEEDTREE_SOURCE_DIR):
        log(f"[SpeedTreeHarness] source dir not found: {SPEEDTREE_SOURCE_DIR} — nothing to do. "
            f"Set SPEEDTREE_SRC env var or drop exports in that folder.")
        return

    imported = 0
    for root, _dirs, files in os.walk(SPEEDTREE_SOURCE_DIR):
        tree_name = _sanitize(os.path.basename(root) or "Tree")
        for fn in sorted(files):
            full = os.path.join(root, fn)
            ext = os.path.splitext(fn)[1].lower()
            if ext == ".fbx":
                import_speedtree_fbx(full, tree_name)
                imported += 1
            elif ext in TEXTURE_EXTS:
                import_texture(full, f"{DEST_ROOT}/{tree_name}")

    log(f"[SpeedTreeHarness] done — imported {imported} SpeedTree FBX exports into {DEST_ROOT}")
    log("[SpeedTreeHarness] next: run 'Foliage: Wire Audio-Reactive Materials' task.")


if __name__ == "__main__":
    main()
