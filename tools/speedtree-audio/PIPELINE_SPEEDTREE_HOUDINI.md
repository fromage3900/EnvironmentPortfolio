# SpeedTree → Houdini → UE Pipeline (Sea Above P0 update)

Updated 2026-09-01. Extends `README.md` (audio harness) with the Houdini stage.
Environment facts: Houdini 22 installed (`where_hython.cmd`), Copernicus
available, HoudiniEngine + SpeedTreeImporter enabled in BS_GodFile.

## Signal chain

```
SpeedTree Modeler            Houdini 22 (hython / HoudiniEngine)         UE 5.8
─────────────────            ───────────────────────────────────         ──────
*.spm procedural  ──FBX──▶   SOP post-pass:                              import_speedtree_harness.py
+ baked wind data             - leaf-cluster scatter refinement           → /Game/Melodia/Environment/
                              - curve-plant generation (kelp/cards)         Foliage/SeaAbove/<Asset>/
                              - LOD 0/1/2 + card-ification
                              - root point attribute, pivot check         build_seaabove_kit.py
                              │                                           → meshes + textures + MIs
                              ▼                                           → MIs on slots
                    build_seaabove_foliage_textures.py
                    Copernicus (COP) bake per material preset:
                      BC  — water-tint + thin-film iridescence ramp
                      N   — from height (droplets, veining)
                      ORM — R:AO  G:Roughness  B:Metallic   (project convention)
                              │
                              ▼ exports/seaabove_textures/*.png (2K)
                              └──▶ UE intake (build_seaabove_kit.py)
```

## Stage rules

1. **Houdini is authoritative for procedural fields** (canonical rule from
   `toolchain/houdini_hython/README.md`); SpeedTree owns plant topology; UE owns
   reactivity.
2. All Copernicus bakes are **view-independent**: iridescence is authored as a
   thin-film ramp in the texture; true view-dependent response is added in UE by
   `MF_SeaAbove_Iridescent` (fresnel ramp over the baked iridescence mask).
3. ORM packing is fixed: **R = AO, G = Roughness, B = Metallic** (matches every
   existing texture suite in `teamwork_projects/`).
4. Geometry handoff uses FBX with SpeedTree wind data preserved; Houdini never
   strips vertex animation channels.
5. No sim dependency: Sea Above P0 foliage is static geo — the FLIP blocker
   (`FINDINGS_FLIP_HEADLESS_2026-08-31.md`) does not gate this kit.

## Commands

```cmd
:: bake textures (Copernicus graph if scriptable, documented fallback otherwise)
call toolchain\houdini_hython\where_hython.cmd
%HYTHON% toolchain\houdini_cops\build_seaabove_foliage_textures.py --res 2048 --out exports\seaabove_textures

:: UE intake + wiring (VS Code task 'SeaAbove: Import & Wire Foliage Kit')
UnrealEditor-Cmd.exe BS_GodFile.uproject -ExecutePythonScript tools\speedtree-audio\build_seaabove_kit.py -unattended -noP4 -nullRHI -NOSOUND
```

## SpeedTree connector (v10.1.0 verified installed)

`speedtree_bridge.py` connects the real SpeedTree Modeler install to the
pipeline using **IDV's own shipped Houdini bridge**
(`C:\Program Files\SpeedTree\SpeedTree Modeler v10.1.0\scripts\Houdini\` —
`SpeedTreeImport.otl` + `script.py::LoadSpeedTree()`). No vendor code is
duplicated or modified; the script imports it in place.

```cmd
:: after exporting <Asset>.stmat (+ USD/FBX meshes, wind data ON) from Modeler:
call toolchain\houdini_cops\run_speedtree_bridge.cmd path\to\Asset.stmat 512
```

Steps performed: official `LoadSpeedTree` import (geometry + SpeedTreePrincipled
materials from the `.stmat` maps) → Copernicus bake for the matched kit preset
(asset filename must contain e.g. `KelpRibbon`) → mesh + `.stmat` staged into
`Imports/SeaAboveFoliage/<Asset>/` for `build_seaabove_kit.py` (UE intake).

For Houdini-side interactive work, prefer Modeler's **Send to Houdini** /
install the same OTL — the headless path above is the automation equivalent.

## Copernicus fallback policy

Copernicus (Houdini 21+) is UI-first; not every node graph is creatable from
hython. `build_seaabove_foliage_textures.py` therefore:
1. Probes `hou.nodeTypeDescriptions()` for Copernicus (cop) node categories and
   builds the bake graph when found;
2. Otherwise falls back to a **dependency-free procedural generator** (same
   visual recipe: thin-film ramp + caustic noise + droplet height field) so the
   kit ships textures regardless. The fallback output is bit-identical in
   naming/layout to the Copernicus path, so UE intake is unchanged.
