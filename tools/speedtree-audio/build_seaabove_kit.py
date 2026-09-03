#!/usr/bin/env python3
"""Sea Above P0 foliage kit intake — import meshes + Copernicus textures, wire MIs.

Run headless (VS Code task: 'SeaAbove: Import & Wire Foliage Kit'):
  UnrealEditor-Cmd.exe BS_GodFile.uproject -ExecutePythonScript <this> -unattended -noP4 -nullRHI -NOSOUND

Implements SEAABOVE_KIT_SPEC.md:
  - meshes from Imports/SeaAboveFoliage/<Asset>/<Asset>.fbx
  - textures from toolchain/houdini_cops/exports/seaabove_textures/
  - content root /Game/Melodia/Environment/Foliage/SeaAbove/
  - M_WA_Foliage_Master (Subsurface, two-sided) + per-preset MIs reading
    MPC_Melodia_Palette (same zero-safe contract as the audio harness)
"""
import os
import unreal

MT = unreal.MaterialEditingLibrary
ASSETS = unreal.EditorAssetLibrary
AT = unreal.AssetToolsHelpers.get_asset_tools()

FBX_SRC = r"C:\EnvironmentPortfolio\Imports\SeaAboveFoliage"
TEX_SRC = r"C:\EnvironmentPortfolio\toolchain\houdini_cops\exports\seaabove_textures"
DEST_ROOT = "/Game/Melodia/Environment/Foliage/SeaAbove"
TEX_DEST = f"{DEST_ROOT}/Textures"
MPC_NAME = "/Game/Melodia/_PROJECT/04_Materials/MPC_Melodia_Palette"

PRESETS = ("KelpRibbon", "Bubbleweed", "LilyPad", "CoralFan", "DropletGrass", "SpawnGlow")


def import_texture(path, dest, srgb):
    tex = None
    name = os.path.splitext(os.path.basename(path))[0]
    asset_path = f"{dest}/{name}"
    if ASSETS.does_asset_exist(asset_path):
        tex = ASSETS.load_asset(asset_path)
        if isinstance(tex, unreal.Texture2D):
            tex.set_editor_property("srgb", srgb)
            ASSETS.save_loaded_asset(tex)
        return tex
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path = dest
    task.automated = True
    task.save = True
    task.replace_existing = False
    AT.import_asset_tasks([task])
    if ASSETS.does_asset_exist(asset_path):
        tex = ASSETS.load_asset(asset_path)
        if isinstance(tex, unreal.Texture2D):
            tex.set_editor_property("srgb", srgb)
            ASSETS.save_loaded_asset(tex)
    return tex


def import_textures() -> dict:
    texs = {}
    if not os.path.isdir(TEX_SRC):
        unreal.log_warning(f"[SeaAboveKit] texture dir missing: {TEX_SRC} — run the Copernicus bake first")
        return texs
    for fn in sorted(os.listdir(TEX_SRC)):
        if not fn.lower().endswith(".png"):
            continue
        srgb = fn.endswith("_BC.png")
        tex = import_texture(os.path.join(TEX_SRC, fn), TEX_DEST, srgb)
        if tex:
            texs[os.path.splitext(fn)[0]] = tex
    unreal.log(f"[SeaAboveKit] imported {len(texs)} textures")
    return texs


def import_meshes() -> list:
    imported = 0
    if not os.path.isdir(FBX_SRC):
        unreal.log_warning(f"[SeaAboveKit] FBX source missing: {FBX_SRC} — drop SpeedTree exports there")
        return []
    for entry in sorted(os.listdir(FBX_SRC)):
        asset_dir = os.path.join(FBX_SRC, entry)
        if not os.path.isdir(asset_dir):
            continue
        ui = unreal.FbxImportUI()
        ui.import_mesh = True
        ui.import_materials = False
        ui.import_textures = False
        ui.import_as_skeletal = False
        ui.static_mesh_import_data.import_uniform_scale = 1.0
        ui.static_mesh_import_data.generate_lightmap_u_vs = False
        ui.static_mesh_import_data.normal_import_method = unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
        for fn in sorted(os.listdir(asset_dir)):
            if not fn.lower().endswith(".fbx"):
                continue
            fbx_path = os.path.join(asset_dir, fn)
            mesh_name = os.path.splitext(fn)[0]
            mesh_asset_path = f"{DEST_ROOT}/{entry}/{mesh_name}"
            if ASSETS.does_asset_exist(mesh_asset_path):
                continue
            task = unreal.AssetImportTask()
            task.filename = fbx_path
            task.destination_path = f"{DEST_ROOT}/{entry}"
            task.options = ui
            task.automated = True
            task.save = True
            task.replace_existing = False
            AT.import_asset_tasks([task])
            imported += 1
    unreal.log(f"[SeaAboveKit] imported {imported} FBX assets")
    return [p for p in ASSETS.list_assets(DEST_ROOT, recursive=True)
            if p.lower().endswith(".uasset")
            and isinstance(ASSETS.load_asset(p), unreal.StaticMesh)]

def _mul(mat, a, b):
    n = MT.create_material_expression(mat, unreal.MaterialExpressionMultiply)
    MT.connect_material_expressions(a, "", n, "A")
    MT.connect_material_expressions(b, "", n, "B")
    return n


def _add(mat, a, b):
    n = MT.create_material_expression(mat, unreal.MaterialExpressionAdd)
    MT.connect_material_expressions(a, "", n, "A")
    MT.connect_material_expressions(b, "", n, "B")
    return n


def _col_param(mat, collection, name):
    node = MT.create_material_expression(mat, unreal.MaterialExpressionCollectionParameter)
    node.collection = collection
    node.set_editor_property("parameter_name", name)
    return node


def build_master_material(texs: dict) -> unreal.Material:
    mat_path = f"{DEST_ROOT}/M_WA_Foliage_Master"
    if ASSETS.does_asset_exist(mat_path):
        return ASSETS.load_asset(mat_path)
    factory = unreal.MaterialFactoryNew()
    mat = AT.create_asset(
        asset_name="M_WA_Foliage_Master", package_path=DEST_ROOT,
        asset_class=unreal.Material, factory=factory)
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.SUBSURFACE)
    return _wire_master(mat, texs)

def _tex_param(mat, name, key, texs):
    node = MT.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D)
    node.set_editor_property("parameter_name", name)
    node.set_editor_property("texture", texs.get(key))
    return node


def _wire_master(mat, texs):
    collection = (ASSETS.load_asset(MPC_NAME)
                  if ASSETS.does_asset_exist(MPC_NAME) else None)
    bass = _col_param(mat, collection, "Bass")
    treble = _col_param(mat, collection, "Treble")
    beat_phase = _col_param(mat, collection, "BeatPhase")
    reactivity = _col_param(mat, collection, "GlobalReactivity")

    bc = _tex_param(mat, "WA_BaseColor", "T_WA_KelpRibbon_BC", texs)
    normal = _tex_param(mat, "WA_Normal", "T_WA_KelpRibbon_N", texs)
    orm = _tex_param(mat, "WA_ORM", "T_WA_KelpRibbon_ORM", texs)
    iri_mask = _tex_param(mat, "WA_IriMask", "T_WA_KelpRibbon_IriMask", texs)

    # beat pulse: cos^2(BeatPhase * pi)
    const_pi = MT.create_material_expression(mat, unreal.MaterialExpressionConstant)
    const_pi.set_editor_property("r", 3.14159265)
    cos_node = MT.create_material_expression(mat, unreal.MaterialExpressionCosine)
    MT.connect_material_expressions(_mul(mat, beat_phase, const_pi), "", cos_node, "Input")
    pulse = _mul(mat, cos_node, cos_node)

    # iridescence: fresnel x mask -> teal-violet lerp (MF-style, inlined)
    fres = MT.create_material_expression(mat, unreal.MaterialExpressionFresnel)
    fres.set_editor_property("exponent", 3.0)
    fres.set_editor_property("base_reflect_fraction", 0.04)
    teal = MT.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector)
    teal.set_editor_property("constant", unreal.LinearColor(0.15, 0.65, 0.60, 1.0))
    violet = MT.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector)
    violet.set_editor_property("constant", unreal.LinearColor(0.45, 0.25, 0.85, 1.0))
    lerp = MT.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate)
    MT.connect_material_expressions(teal, "", lerp, "A")
    MT.connect_material_expressions(violet, "", lerp, "B")
    MT.connect_material_expressions(iri_mask, "RGB", lerp, "Alpha")
    iri_out = _mul(mat, lerp, fres)
    iri_tinted = _mul(mat, iri_out, iri_mask)

    base = _add(mat, bc, iri_tinted)
    MT.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    MT.connect_material_property(normal, "RGB", unreal.MaterialProperty.MP_NORMAL)

    # emissive = iridescence * (Treble + BeatPulse) * GlobalReactivity (zero-safe)
    glow = _mul(mat, iri_out, _add(mat, treble, pulse))
    emissive = _mul(mat, glow, reactivity)
    MT.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    # ORM packed: R=AO G=Roughness B=Metallic (project convention)
    MT.connect_material_property(orm, "G", unreal.MaterialProperty.MP_ROUGHNESS)
    MT.connect_material_property(orm, "B", unreal.MaterialProperty.MP_METALLIC)

    # wind WPO: (0.3 + Bass) * sin(Time)
    time_node = MT.create_material_expression(mat, unreal.MaterialExpressionTime)
    wind_base = MT.create_material_expression(mat, unreal.MaterialExpressionConstant)
    wind_base.set_editor_property("r", 0.3)
    sway = _mul(mat, _add(mat, wind_base, bass), time_node)
    sin_sway = MT.create_material_expression(mat, unreal.MaterialExpressionSine)
    MT.connect_material_expressions(sway, "", sin_sway, "Input")
    append = MT.create_material_expression(mat, unreal.MaterialExpressionAppendVector)
    zero = MT.create_material_expression(mat, unreal.MaterialExpressionConstant)
    zero.set_editor_property("r", 0.0)
    MT.connect_material_expressions(_mul(mat, sin_sway, sway), "", append, "A")
    MT.connect_material_expressions(zero, "", append, "B")
    MT.connect_material_property(append, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)

    MT.recompile_material(mat)
    ASSETS.save_loaded_asset(mat)
    return mat


def wire_mis(mat, meshes) -> None:
    for mesh_path in meshes:
        mesh = ASSETS.load_asset(mesh_path)
        preset = next((p for p in PRESETS if p.lower() in mesh_path.lower()), PRESETS[0])
        mi_path = f"{DEST_ROOT}/MI_WA_{preset}"
        if ASSETS.does_asset_exist(mi_path):
            mi = ASSETS.load_asset(mi_path)
        else:
            mi = MT.create_material_instance_asset(
                asset_name=f"MI_WA_{preset}", package_path=DEST_ROOT, parent_material=mat)
        for i in range(mesh.get_num_material_slots()):
            mesh.set_material(i, mi)
        ASSETS.save_loaded_asset(mesh)
        unreal.log(f"[SeaAboveKit] {mesh_path} -> {mi_path}")
    ASSETS.save_directory(DEST_ROOT, only_if_is_dirty=True)


def main() -> None:
    texs = import_textures()
    meshes = import_meshes()
    if not texs and not meshes:
        unreal.log_warning("[SeaAboveKit] nothing to import — check FBX_SRC / TEX_SRC")
        return
    mat = build_master_material(texs)
    if meshes:
        wire_mis(mat, meshes)
    unreal.log("[SeaAboveKit] done — kit ready under " + DEST_ROOT)


if __name__ == "__main__":
    main()



