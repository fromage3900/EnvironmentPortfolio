# UE 5.8 One-Click Sea Above VDB Import — volume flipbook + material + Niagara system
#
# Run inside the UE Editor:  File > Execute Python Script  (or Output Log `py` console)
#   >>> import oneclick_seaabove; oneclick_seaabove.run()
#
# Configure the two paths below first (VDB_SOURCE must exist — produced by
# repack_vdb.py once the sim content gate passes; see
# toolchain/houdini_hython/FINDINGS_FLIP_HEADLESS_2026-08-31.md).

VDB_SOURCE = r"C:\EnvironmentPortfolio\toolchain\houdini_hython\exports\sea_above_vdb"
DEST_CONTENT = "/Game/_PROJECT/VFX"          # maps to repo Content/_PROJECT/VFX
FLIPBOOK_NAME = "T_SeaAbove_VDB"
MATERIAL_NAME = "M_SeaAbove_VDB_Volume"
SYSTEM_NAME = "NS_SeaAbove_VolumeFlipbook"


def _import_vdb_flipbook():
    """Import the .vdb sequence as a volume-flipbook texture. Tries every VDB-capable
    factory name UE 5.x has shipped; reports clearly if none is available."""
    import unreal, os

    vdb_files = sorted(f for f in os.listdir(VDB_SOURCE) if f.lower().endswith(".vdb"))
    if not vdb_files:
        unreal.log_warning(
            f"[SeaAbove] no .vdb files in {VDB_SOURCE} — run repack_vdb.py first "
            f"(sim must pass the content gate)")
        return None

    first = os.path.join(VDB_SOURCE, vdb_files[0])
    factory_names = (
        "OpenVDBFactory",                # UE 5.3+ OpenVDB volume importer
        "VolumeTextureFactory",          # image-sequence volume fallback
        "VolumeTextureFromVdbFactory",
    )
    factory = next(
        (getattr(unreal, n) for n in factory_names if hasattr(unreal, n)), None)
    if factory is None:
        unreal.log_warning(
            "[SeaAbove] no VDB factory in this build — do the manual import per "
            "README_SeaAbove.md step 1, then re-run (material/system steps skip)")
        return None

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    task = unreal.AssetImportTask(
        automated=True, save=True,
        factory=factory, filename=first,
        destination_path=DEST_CONTENT, destination_name=FLIPBOOK_NAME,
        replace_existing=True,
    )
    tools.import_asset_tasks([task])
    path = f"{DEST_CONTENT}/{FLIPBOOK_NAME}"
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.log_warning(f"[SeaAbove] import did not produce {path}")
        return None
    unreal.log(f"[SeaAbove] imported volume flipbook: {path} ({len(vdb_files)} vdb frames found)")
    return path

def _build_volume_material():
    """M_SeaAbove_VDB_Volume: Domain=Volume; volume texture RGB -> emissive, R -> opacity."""
    import unreal

    mat_path = f"{DEST_CONTENT}/Materials/{MATERIAL_NAME}"
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        MATERIAL_NAME, f"{DEST_CONTENT}/Materials", unreal.Material, None)
    if mat is None:
        mat = unreal.load_asset(mat_path)
    unreal.MaterialEditingLibrary.set_material_domain(mat, unreal.MaterialDomain.VOLUME)

    vt = unreal.MaterialEditingLibrary.create_material_expression(
        mat, unreal.MaterialExpressionTextureSample, -400, 0)
    vol_tex = unreal.load_asset(f"{DEST_CONTENT}/{FLIPBOOK_NAME}")
    if vol_tex and isinstance(vol_tex, unreal.Texture):
        vt.set_editor_property("texture", vol_tex)

    # Volume material outputs: Emissive Color (cool blue tint base) + Opacity
    unreal.MaterialEditingLibrary.connect_material_property(
        vt, "RGB", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    unreal.MaterialEditingLibrary.connect_material_property(
        vt, "R", unreal.MaterialProperty.MP_OPACITY)

    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    unreal.log(f"[SeaAbove] volume material ready: {mat_path}")
    return mat_path


def _scaffold_niagara_system():
    """NS_SeaAbove_VolumeFlipbook skeleton + manual wiring checklist (Niagara emitter
    graphs are not reliably scriptable in 5.8; the renderer wiring is a 2-minute
    manual step logged below)."""
    import unreal

    sys_path = f"{DEST_CONTENT}/Niagara/{SYSTEM_NAME}"
    system = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        SYSTEM_NAME, f"{DEST_CONTENT}/Niagara", unreal.NiagaraSystem, None)
    if system is None:
        system = unreal.load_asset(sys_path)
    if system:
        try:
            system.set_editor_property("auto_activate", True)
            unreal.EditorAssetLibrary.save_loaded_asset(system)
        except Exception as ex:
            unreal.log_warning(f"[SeaAbove] could not set auto_activate: {ex}")
    unreal.log(
        "[SeaAbove] Niagara wiring checklist for " + sys_path + ":\n"
        "  1. Add Emitter (empty or Fountain copy), Spawn Rate ~200\n"
        "  2. Add Renderer > Sprite flipbook (or Volume):\n"
        "     - Material = M_SeaAbove_VDB_Volume\n"
        "     - SubImage XY from the flipbook frame count (see T_SeaAbove_VDB)\n"
        "  3. Lifetime = flipbook length / frames, Loop = on\n"
        "  4. Optional audio-reactive (Nikki lens): add ScalarParameter 'AudioLevel'\n"
        "     in M_SeaAbove_VDB_Volume emissive, bound from MetaSounds/OSS audio")
    return sys_path


def run():
    import unreal
    unreal.log("[SeaAbove] === one-click VDB -> volume flipbook pipeline start ===")
    flipbook = _import_vdb_flipbook()
    if flipbook:
        _build_volume_material()
        _scaffold_niagara_system()
        unreal.log("[SeaAbove] === done — check /Game/_PROJECT/VFX ===")
    else:
        unreal.log("[SeaAbove] === stopped at VDB import step; see warnings above ===")

