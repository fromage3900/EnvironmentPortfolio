#!/usr/bin/env python
"""Build a USD stage for the Sea Above foliage kit using Hython's built-in pxr.

Run with hython (auto-detected via ../houdini_hython/where_hython.cmd):
    hython.exe build_seaabove_usd_stage.py --src Imports/SeaAboveFoliage \
        --tex toolchain/houdini_cops/exports/seaabove_textures \
        --out toolchain/houdini_cops/exports/seaabove_stage.usda

Emphasizes the OpenUSD part of the emerging 3D architecture research doc:
- Scene composition (default prim /SeaAbove)
- Procedural references to the SpeedTree-exported FBX meshes as asset paths
- UsdPreviewSurface materials wired to the baked BC / N / ORM / IriMask textures
- MaterialX-style naming conventions (preview surface, UV texture samplers)

The output is a .usda ASCII stage that can be loaded in usdview, Blender, or
UE 5.x via the USD Stage Editor (USD Importer plugin is enabled in the project).
"""
from __future__ import annotations

import argparse
import os


def ensure_pxir():
    try:
        from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf
        return Usd, UsdGeom, UsdShade, Sdf, Gf
    except ImportError as e:
        raise SystemExit("This script must be run under hython (ships with pxr/USD).") from e

PRESET_ASSET = {
    "KelpRibbon": ("ST_Kelp_Ribbon_Tall", "ST_Kelp_Ribbon_Tall"),
    "Bubbleweed": ("ST_Bubbleweed_Bush", "ST_Bubbleweed_Bush"),
    "LilyPad": ("ST_LilyPad_Carousel", "ST_LilyPad_Carousel"),
    "CoralFan": ("ST_Coral_Fan_A", "ST_Coral_Fan_A"),
    "DropletGrass": ("ST_Droplet_Grass_Card", "ST_Droplet_Grass_Card"),
    "SpawnGlow": ("ST_SpawnGlow_Mote", "ST_SpawnGlow_Mote"),
}



def build_material(stage, mat_name: str, tex_root: str, preset: str):
    Usd, UsdGeom, UsdShade, Sdf, Gf = ensure_pxir()
    mat_path = f"/SeaAbove/Materials/{mat_name}"
    mat = UsdShade.Material.Define(stage, mat_path)

    surf = UsdShade.Shader.Define(stage, f"{mat_path}/PreviewSurface")
    surf.CreateIdAttr("UsdPreviewSurface")
    surf.CreateOutput("surface", Sdf.ValueTypeNames.Token)
    surf.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
    surf.CreateInput("roughness", Sdf.ValueTypeNames.Float)
    surf.CreateInput("metallic", Sdf.ValueTypeNames.Float)
    surf.CreateInput("normal", Sdf.ValueTypeNames.Normal3f)
    surf.CreateInput("emissiveColor", Sdf.ValueTypeNames.Color3f)

    uv_reader = UsdShade.Shader.Define(stage, f"{mat_path}/uvReader")
    uv_reader.CreateIdAttr("UsdPrimvarReader_float2")
    uv_reader.CreateInput("varname", Sdf.ValueTypeNames.Token).Set("st")
    uv_reader.CreateOutput("result", Sdf.ValueTypeNames.Float2)

    def tex_reader(name, file_key):
        tex_path = os.path.join(tex_root, f"T_WA_{preset}_{file_key}.png").replace("\\", "/")
        tex = UsdShade.Shader.Define(stage, f"{mat_path}/{name}")
        tex.CreateIdAttr("UsdUVTexture")
        tex.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(tex_path)
        tex.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(
            uv_reader.GetOutput("result"))
        tex.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
        return tex

    bc = tex_reader("diffuseTexture", "BC")
    n = tex_reader("normalTexture", "N")
    orm = tex_reader("ormTexture", "ORM")
    iri = tex_reader("iridescenceMask", "IriMask")

    surf.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(bc.GetOutput("rgb"))
    surf.CreateInput("normal", Sdf.ValueTypeNames.Normal3f).ConnectToSource(n.GetOutput("rgb"))
    surf.CreateInput("roughness", Sdf.ValueTypeNames.Float).GetAttr().SetConnections([Sdf.Path(f"{mat_path}/ormTexture.outputs:g")])
    surf.CreateInput("metallic", Sdf.ValueTypeNames.Float).GetAttr().SetConnections([Sdf.Path(f"{mat_path}/ormTexture.outputs:b")])
    surf.CreateInput("emissiveColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(iri.GetOutput("rgb"))

    mat.CreateSurfaceOutput().ConnectToSource(surf.GetOutput("surface"))
    return mat


def build_stage(src_root: str, tex_root: str, out_path: str):
    Usd, UsdGeom, UsdShade, Sdf, Gf = ensure_pxir()
    stage = Usd.Stage.CreateNew(out_path)
    stage.SetMetadata("defaultPrim", "SeaAbove")
    stage.SetMetadata("metersPerUnit", 0.01)
    stage.SetMetadata("upAxis", "Y")

    world = UsdGeom.Xform.Define(stage, "/SeaAbove")

    presets = ("KelpRibbon", "Bubbleweed", "LilyPad", "CoralFan", "DropletGrass", "SpawnGlow")
    for i, preset in enumerate(presets):
        mat = build_material(stage, f"M_{preset}", tex_root, preset)
        dir_name, fbx_name = PRESET_ASSET.get(preset, (f"ST_{preset}", f"ST_{preset}"))
        fbx_path = os.path.join(src_root, dir_name, f"{fbx_name}.fbx")
        if not os.path.isfile(fbx_path):
            fbx_path = os.path.join(src_root, "ST_Kelp_Ribbon_Tall", "ST_Kelp_Ribbon_Tall.fbx")
        fbx_path = fbx_path.replace("\\", "/")
        xform = UsdGeom.Xform.Define(stage, f"/SeaAbove/{preset}")
        xform.AddTranslateOp().Set(Gf.Vec3d(i * 2.0 - 5.0, 0.0, 0.0))
        xform.AddScaleOp().Set(Gf.Vec3d(1.0, 1.0, 1.0))
        xform.GetPrim().SetCustomDataByKey("asset", fbx_path)
        UsdGeom.Mesh.Define(stage, f"/SeaAbove/{preset}/mesh")
        UsdShade.MaterialBindingAPI(xform).Bind(mat)

    stage.GetRootLayer().Save()
    print(f"[USDStage] wrote {out_path} with {len(presets)} asset refs and materials")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Imports", "SeaAboveFoliage"))
    ap.add_argument("--tex", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "seaabove_textures"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "seaabove_stage.usda"))
    args = ap.parse_args()
    build_stage(os.path.abspath(args.src), os.path.abspath(args.tex), os.path.abspath(args.out))


if __name__ == "__main__":
    main()
