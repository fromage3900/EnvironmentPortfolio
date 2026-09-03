#!/usr/bin/env python3
"""Place imported SpeedTree foliage via PCG (optional step).

Run headless (VS Code task: 'Foliage: Place via PCG').

Creates a minimal PCG graph asset under
/Game/Melodia/Environment/Foliage/SpeedTree/PCG_AT_FoliageScatter:
  SurfaceSampler (on landscape) -> StaticMeshSpawner pointing at every
  imported SpeedTree static mesh.

Note: the project also ships PCGExtendedToolkit and ProceduralVegetationEditor;
for authoring-heavy scatter, prefer building the graph in-editor and using this
script as a regeneration checkpoint. This script only provides the automation
baseline.
"""
import unreal

ASSETS = unreal.EditorAssetLibrary
DEST_ROOT = "/Game/Melodia/Environment/Foliage/SpeedTree"
GRAPH_PATH = f"{DEST_ROOT}/PCG_AT_FoliageScatter"


def collect_meshes():
    meshes = []
    for path in ASSETS.list_assets(DEST_ROOT, recursive=True):
        if not path.lower().endswith(".uasset"):
            continue
        obj = ASSETS.load_asset(path)
        if isinstance(obj, unreal.StaticMesh):
            meshes.append(path)
    return meshes


def main() -> None:
    meshes = collect_meshes()
    if not meshes:
        unreal.log_warning("[FoliagePCG] no SpeedTree meshes found — run the import task first.")
        return
    if ASSETS.does_asset_exist(GRAPH_PATH):
        unreal.log(f"[FoliagePCG] graph already exists at {GRAPH_PATH}; skipping creation.")
        return

    at = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.PCGGraphFactoryNew()
    graph = at.create_asset(asset_name="PCG_AT_FoliageScatter",
                            package_path=DEST_ROOT,
                            asset_class=unreal.PCGGraph, factory=factory)
    if not graph:
        unreal.log_error("[FoliagePCG] could not create PCG graph asset.")
        return

    # Sampler node (default settings sample the landscape surface in-editor).
    sampler = graph.add_node_to_default_graph(unreal.PCGSurfaceSamplerSettings())
    spawner = graph.add_node_to_default_graph(unreal.PCGStaticMeshSpawnerSettings())
    graph.try_insert_node(sampler, spawner)

    # Build mesh entries for the spawner.
    entries = []
    for path in meshes:
        e = unreal.PCGMeshSelectorWeightedEntry()
        obj = ASSETS.load_asset(path)
        e.set_editor_property("mesh", obj)
        e.set_editor_property("weight", 1.0)
        entries.append(e)
    selector = spawner.get_editor_property("mesh_selectors")
    if selector:
        weighted = selector[0]
        weighted.set_editor_property("mesh_entries", entries)
    ASSETS.save_loaded_asset(graph)
    unreal.log(f"[FoliagePCG] created {GRAPH_PATH} with {len(meshes)} mesh entries. "
               "Add a PCG component pointing at it in your level to scatter.")


if __name__ == "__main__":
    main()
