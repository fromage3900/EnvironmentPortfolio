# SpeedTree → Audio-Reactive Foliage Harness

Connects SpeedTree tree exports to **BS_GodFile's existing audio-reactive
system** (`MPC_Melodia_Palette`, driven by the MelodiaCore rhythm reactivity
subsystem from Harmonix/music-clock state). No new audio pipeline is built —
this harness only joins SpeedTree geometry to the already-running signal.

## Signal chain

```
SpeedTree Modeler ──FBX(+baked wind data)──▶ import_speedtree_harness.py
        │                                            │
        │ meshes + textures under                    ▼
        │ /Game/Melodia/Environment/Foliage/SpeedTree/<Tree>/
        │                                            │
        └──▶ wire_audio_foliage_materials.py ──▶ M_AT_* / MI_AT_* materials
                 read MPC_Melodia_Palette:         assigned to mesh slots
                 Bass·Mid·Treble·BeatPulse·
                 BeatPhase·GlobalReactivity
                                                    │
        MelodiaCore rhythm subsystem ──▶ MPC_Melodia_Palette (every tick)
        (Harmonix music clock, 128 BPM default, zero-safe)

        place_foliage_pcg.py ──▶ PCG_AT_FoliageScatter (scatter graph)
```

## SpeedTree Modeler export settings

1. Export → **Geometry → FBX**, units **centimeters**, UE conversion.
2. Enable **Export wind data** (bakes branch/leaf vertex animation the engine
   foliage wind nodes consume).
3. Textures: separate folder (PNG/TGA) — imported automatically.
4. One tree per subfolder of `Imports/SpeedTree/` (or set `SPEEDTREE_SRC` env
   var). `.fbx` files import as StaticMeshes; textures land beside them.

## Usage (VS Code tasks, from the repo root)

| Task | Does |
|---|---|
| `Foliage: Import SpeedTree Assets` | Imports all FBX/textures under `Imports/SpeedTree/` |
| `Foliage: Wire Audio-Reactive Materials` | Builds `M_AT_*` + `MI_AT_*`, assigns to mesh slots |
| `Foliage: Place via PCG` | Creates `PCG_AT_FoliageScatter` scatter graph |

Or headless:
```powershell
& "C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe" `
  "c:/EnvironmentPortfolio/BS_GodFile/BS_GodFile.uproject" `
  -ExecutePythonScript "c:/EnvironmentPortfolio/tools/speedtree-audio/import_speedtree_harness.py" `
  -unattended -noP4 -nullRHI -NOSOUND
```

## Reactivity contract (do not break)

- Foliage materials read **only** `MPC_Melodia_Palette` (single musical time
  source; zero-safe when no clock runs).
- Beat pulse: `cos²(BeatPhase·π)`; emissive ≤ sub-blowout, scaled by
  `GlobalReactivity`; roughness clamped `[0.02, 1.0]`.
- Ambient motion = baked SpeedTree wind vertex data; audio adds
  `(AudioWindStrength + Bass)·sin(t)` as WPO.

Per-tree tunables (Scalar/Vector params on the material instance):
`AudioWindStrength` (0.35 default), `AudioFoliageEmissiveIntensity` (1.0),
`AudioFoliageBaseColor` (leaf tint).

## Notes / caveats

- Material graph construction via `unreal.MaterialEditingLibrary` is
  version-sensitive; if a node class fails on your 5.8 build, run the script in
  the live editor and check the log — it lists the failing expression.
- If you hold SpeedTree licensing for `.srt`, prefer the `SpeedTreeImporter`
  plugin path (its material factory is wind-aware), then run
  `wire_audio_foliage_materials.py` to patch in the MPC reactivity.
- MPC path constant `MPC_NAME` in `wire_audio_foliage_materials.py` — verify it
  matches the actual asset location in the project (search `MPC_Melodia_Palette`).
