#!/usr/bin/env python3
"""Wire audio-reactive foliage materials onto imported SpeedTree meshes.

Run headless (VS Code task: 'Foliage: Wire Audio-Reactive Materials').

Contract — MUST match the project's established audio-reactive convention
(see Docs/ZENFOREST_MUSICAL_GLAM_HANDOFF_2026-08-25.md):

  - All reactivity is read from Material Parameter Collection MPC_Melodia_Palette
    (owned every tick by the MelodiaCore rhythm reactivity subsystem):
    Bass, Mid, Treble, BeatPulse, BeatPhase, BeatIntensity, GlobalReactivity.
  - Zero-safe: no music clock -> all params 0 -> flat foliage, no invented tempo.
  - Beat pulse uses cos^2(BeatPhase * pi) (derivative zero at beat boundaries).
  - Roughness clamped to [0.02, 1.0]; emissive scaled by GlobalReactivity.

Builds per imported tree (under /Game/Melodia/Environment/Foliage/SpeedTree/<Tree>/):
  M_AT_<Mesh>   audio-reactive foliage material (Subsurface shading)
  MI_AT_<Mesh>  material instance, assigned to every slot of the static mesh
"""
import unreal

MT = unreal.MaterialEditingLibrary
ASSETS = unreal.EditorAssetLibrary
DEST_ROOT = "/Game/Melodia/Environment/Foliage/SpeedTree"
MPC_NAME = "/Game/Melodia/_PROJECT/04_Materials/MPC_Melodia_Palette"

WIND_PARAM = "AudioWindStrength"
EMISSIVE_PARAM = "AudioFoliageEmissiveIntensity"
COLOR_PARAM = "AudioFoliageBaseColor"


def _col_param(mat, collection, name):
    node = MT.create_material_expression(mat, unreal.MaterialExpressionCollectionParameter)
    node.collection = collection
    node.set_editor_property("parameter_name", name)
    return node


def _scalar(mat, name, default):
    node = MT.create_material_expression(mat, unreal.MaterialExpressionScalarParameter)
    node.set_editor_property("parameter_name", name)
    node.set_editor_property("default_value", default)
    return node


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

def build_foliage_material(mat_path: str) -> unreal.Material:
    if ASSETS.does_asset_exist(mat_path):
        return ASSETS.load_asset(mat_path)

    pkg_path, mat_name = mat_path.rsplit("/", 1)
    mat = MT.create_material_asset(
        asset_name=mat_name, package_path=pkg_path,
        shading_model=unreal.MaterialShadingModel.SUBSURFACE)

    collection = (ASSETS.load_asset(MPC_NAME)
                  if ASSETS.does_asset_exist(MPC_NAME) else None)
    if not collection:
        unreal.log_warning(f"[FoliageAudio] MPC not found at {MPC_NAME}; "
                           "CollectionParameter nodes will bind by name only.")

    bass = _col_param(mat, collection, "Bass")
    treble = _col_param(mat, collection, "Treble")
    beat_phase = _col_param(mat, collection, "BeatPhase")
    reactivity = _col_param(mat, collection, "GlobalReactivity")

    # Beat pulse: cos^2(BeatPhase * pi)
    const_pi = MT.create_material_expression(mat, unreal.MaterialExpressionConstant)
    const_pi.set_editor_property("r", 3.14159265)
    phase_scaled = _mul(mat, beat_phase, const_pi)
    cos_node = MT.create_material_expression(mat, unreal.MaterialExpressionCosine)
    MT.connect_material_expressions(phase_scaled, "", cos_node, "Input")
    pulse = _mul(mat, cos_node, cos_node)

    # Wind WPO: sway = (AudioWindStrength + Bass) * sin(Time)
    wind = _scalar(mat, WIND_PARAM, 0.35)
    time_node = MT.create_material_expression(mat, unreal.MaterialExpressionTime)
    sway_amp = _add(mat, wind, bass)
    amp_t = _mul(mat, sway_amp, time_node)
    sin_sway = MT.create_material_expression(mat, unreal.MaterialExpressionSine)
    MT.connect_material_expressions(amp_t, "", sin_sway, "Input")
    wpo_scalar = _mul(mat, sin_sway, sway_amp)
    append = MT.create_material_expression(mat, unreal.MaterialExpressionAppendVector)
    zero = MT.create_material_expression(mat, unreal.MaterialExpressionConstant)
    zero.set_editor_property("r", 0.0)
    MT.connect_material_expressions(wpo_scalar, "", append, "A")
    MT.connect_material_expressions(zero, "", append, "B")
    MT.connect_material_property(append, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)

    # Emissive: tint * (Treble + BeatPulse) * GlobalReactivity
    color_param = MT.create_material_expression(mat, unreal.MaterialExpressionVectorParameter)
    color_param.set_editor_property("parameter_name", COLOR_PARAM)
    color_param.set_editor_property("default_value", unreal.LinearColor(0.18, 0.42, 0.16, 1.0))
    glow_sum = _add(mat, treble, pulse)
    glow_react = _mul(mat, glow_sum, reactivity)
    tinted = _mul(mat, color_param, glow_react)
    emissive_gain = _scalar(mat, EMISSIVE_PARAM, 1.0)
    emissive = _mul(mat, tinted, emissive_gain)
    MT.connect_material_property(emissive, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    # Base color + roughness: base * (1 - 0.10 * BeatPulse), clamp [0.02, 1]
    MT.connect_material_property(color_param, "", unreal.MaterialProperty.MP_BASE_COLOR)
    rough_base = MT.create_material_expression(mat, unreal.MaterialExpressionConstant)
    rough_base.set_editor_property("r", 0.55)
    inv_pulse = MT.create_material_expression(mat, unreal.MaterialExpressionOneMinus)
    MT.connect_material_expressions(pulse, "", inv_pulse, "Input")
    small = MT.create_material_expression(mat, unreal.MaterialExpressionConstant)
    small.set_editor_property("r", 0.10)
    delta = _mul(mat, inv_pulse, small)
    rough_final = _add(mat, rough_base, delta)
    clamp = MT.create_material_expression(mat, unreal.MaterialExpressionClamp)
    clamp.set_editor_property("min_default", 0.02)
    clamp.set_editor_property("max_default", 1.0)
    MT.connect_material_expressions(rough_final, "", clamp, "Input")
    MT.connect_material_property(clamp, "", unreal.MaterialProperty.MP_ROUGHNESS)

    MT.recompile_material(mat)
    ASSETS.save_loaded_asset(mat)
    return mat

def wire_tree(mesh_path: str) -> None:
    obj = ASSETS.load_asset(mesh_path)
    if not isinstance(obj, unreal.StaticMesh):
        return
    mesh_name = mesh_path.rsplit("/", 1)[-1].replace(".uasset", "")
    tree_name = mesh_path.split(DEST_ROOT + "/", 1)[-1].rsplit("/", 1)[0] or tree_name_from(mesh_name)
    mat_path = f"{DEST_ROOT}/{tree_name}/M_AT_{mesh_name}"
    mat = build_foliage_material(mat_path)
    mi_path = f"{DEST_ROOT}/{tree_name}/MI_AT_{mesh_name}"
    if ASSETS.does_asset_exist(mi_path):
        mi = ASSETS.load_asset(mi_path)
    else:
        mi = MT.create_material_instance_asset(
            asset_name=f"MI_AT_{mesh_name}",
            package_path=f"{DEST_ROOT}/{tree_name}",
            parent_material=mat)
    for i in range(obj.get_num_material_slots()):
        obj.set_material(i, mi)
    ASSETS.save_loaded_asset(obj)
    unreal.log(f"[FoliageAudio] wired {mesh_path} -> {mi_path}")


def tree_name_from(mesh_name: str) -> str:
    return mesh_name.rsplit("_", 1)[0]


def main() -> None:
    if not ASSETS.does_directory_exist(DEST_ROOT):
        unreal.log_warning(f"[FoliageAudio] {DEST_ROOT} missing — run the import task first.")
        return
    count = 0
    for mesh_path in ASSETS.list_assets(DEST_ROOT, recursive=True):
        if not mesh_path.lower().endswith(".uasset"):
            continue
        obj = ASSETS.load_asset(mesh_path)
        if isinstance(obj, unreal.StaticMesh):
            wire_tree(mesh_path)
            count += 1
    if count:
        ASSETS.save_directory(DEST_ROOT, only_if_is_dirty=True)
    unreal.log(f"[FoliageAudio] done — {count} meshes wired to audio-reactive materials")


if __name__ == "__main__":
    main()


