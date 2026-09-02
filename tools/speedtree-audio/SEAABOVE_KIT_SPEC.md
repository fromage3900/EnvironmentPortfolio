# Sea Above P0 — Magical Water Foliage Kit Spec

Destination in UE: `/Game/Melodia/Environment/Foliage/SeaAbove/<Asset>/`
Source FBX: `Imports/SeaAboveFoliage/<Asset>/<Asset>.fbx`
Textures (Copernicus bake): `toolchain/houdini_cops/exports/seaabove_textures/`

| Asset | Type / LODs | Material preset | Notes |
|---|---|---|---|
| `ST_Kelp_Ribbon_Tall` | curve-plant, LOD0-2 + billboard | `KelpRibbon` | tall ribbon kelp, translucent edges, baked sway |
| `ST_Bubbleweed_Bush` | broadleaf bush, LOD0-2 | `Bubbleweed` | bubble-tipped fronds, droplet height field |
| `ST_LilyPad_Carousel` | cluster (5 pads), LOD0-1 | `LilyPad` | floating pads, iridescent rim mask |
| `ST_Coral_Fan_A/B/C` | static, LOD0-1 | `CoralFan` | fan coral, pearlescent |
| `ST_Droplet_Grass_Card` | 2-plane card | `DropletGrass` | cheap PCG filler, droplet alphas |
| `ST_SpawnGlow_Mote` | sprite imposter | `SpawnGlow` | glowing motes, emissive-only |

## Shared texture set per preset (2K, PNG)
`T_WA_<Preset>_BC.png` (sRGB), `T_WA_<Preset>_N.png` (linear),
`T_WA_<Preset>_ORM.png` (R:AO G:Roughness B:Metallic, linear),
`T_WA_<Preset>_IriMask.png` (linear, iridescence strength mask).

## Material contract
- Parent: `M_WA_Foliage_Master` (Subsurface, two-sided foliage shading).
- `MF_SeaAbove_Iridescent`: fresnel (FresnelExp 2-4) → hue ramp (teal → violet →
  gold) over `IriMask` → added to BaseColor and to Emissive at low gain.
- Reactivity from `MPC_Melodia_Palette` (same contract as the audio harness):
  Bass → sway WPO, Treble → sparkle, BeatPulse → soft rim glow, zero-safe.
- Translucency: opacity from BC luminance + `IriMask`, clamped [0.25, 1].

## Intake script
`tools/speedtree-audio/build_seaabove_kit.py` imports meshes + textures, builds
`M_WA_Foliage_Master` + per-preset MIs, assigns slots, and saves everything
under the SeaAbove content root.

## Placeholder source meshes

`tools/speedtree-audio/generate_seaabove_fbx_family.py` writes dependency-free ASCII
FBX stand-ins for every asset above. These carry valid normals/UVs and a single
material slot so the intake pipeline (`build_seaabove_kit.py`) can be exercised
without SpeedTree Modeler installed. When real SpeedTree exports are available,
simply drop them into the same `Imports/SeaAboveFoliage/<Asset>/` folders; the
intake script will prefer them.

```cmd
python tools/speedtree-audio/generate_seaabove_fbx_family.py
```

