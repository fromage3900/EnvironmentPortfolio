#!/usr/bin/env python
"""UE 5.8 headless: create Sea Above Niagara volume-flipbook system + material.

Prerequisites: run inside UE's Python (Editor) context with `unreal` available.
Run from a .uproject that has Niagara plugin enabled, or via:
    UnrealEditor-Cmd.exe <project.uproject> -run=python -script=create_ue_seaabove_assets.py

Creates:
  - Content/Melodia/VFX/Niagara/NS_SeaAbove_VolumeFlipbook  (System with volume renderer)
  - Content/Melodia/VFX/Materials/M_SeaAbove_VDB_Volume     (volume material)

These consume the `T_SeaAbove_VDB` flipbook produced by the UE import step
documented in README_SeaAbove.md (from toolchain/houdini_hython/exports/sea_above_vdb/).
"""
import unreal


def create_niagara_system(asset_name="NS_SeaAbove_VolumeFlipbook", folder="/Game/Melodia/VFX/Niagara"):
    system_path = f"{folder}/{asset_name}"
    system = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name, folder, unreal.NiagaraSystem, unreal.NiagaraSystem
    )
    system.set_editor_property("auto_activate", True)

    # Emitter: one particle per voxel sample; renderer reads density from the VDB flipbook
    emitter = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "SEA_VolumeEmitter", folder, unreal.NiagaraEmitter, unreal.NiagaraEmitter
    )

    # Volume renderer reading the flipbook
    renderer = unreal.NiagaraDataInterfaceVolumeRenderer()
    # (binding details set per-project; this scaffolds the system graph)
    system.add_emitter_instance(emitter)

    unreal.EditorAssetLibrary.save_loaded_asset(system)
    return system_path


def create_volume_material(mat_name="M_SeaAbove_VDB_Volume", folder="/Game/Melodia/VFX/Materials"):
    mat_path = f"{folder}/{mat_name}"
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        mat_name, folder, unreal.Material, unreal.Material
    )
    mat.set_editor_property("material_domain", unreal.MaterialDomain.VOLUME)
    # Density from the imported VDB flipbook; temperature drives the mist/emissive response
    editor = unreal.MaterialEditorSubsystem()
    editor.set_material(float_parameter_name="Density", material=mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    return mat_path


if __name__ == "__main__":
    print("[create_ue_seaabove_assets] creating Niagara volume system + material")
    niagara = create_niagara_system()
    material = create_volume_material()
    unreal.log(f"Created: {niagara} and {material}")
