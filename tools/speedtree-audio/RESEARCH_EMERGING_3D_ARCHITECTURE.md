# Emerging 3D Architecture — Research Notes (2026)

Scope: open standards relevant to a procedural vegetation / audio-reactive
environment pipeline in this repo (BS_GodFile, UE 5.8, SpeedTree, TouchDesigner,
MelodiaCore). Verified against the project's actual plugin set on 2026-09-01.

## 1. SpeedTree's position in the pipeline

SpeedTree is a **procedural vegetation modeler, not a reactive system**. It owns:
- Procedural tree generation (`.spm` Modeler files, `.srt` runtime format)
- **Baked wind vertex animation data** (branch sway / leaf flutter channels
  embedded in exports; the UE `SpeedTreeImporter` plugin + engine foliage wind
  material nodes consume them)
- The SpeedTree Games SDK for direct runtime LOD generation

It has **no audio, no timeline, no reactivity**. Everything reactive downstream
is engine-side. This project already solves that side — see §4.

## 2. Interchange standards (the "emerging 3D architecture")

| Standard | Role in this pipeline | Verdict |
|---|---|---|
| **OpenUSD** | Scene composition, layering, variant sets (season/wind LOD variants), references across tools (Houdini already in-repo via HoudiniEngine) | Strategic long-term; UE 5.8 USD importer is production-grade. Prefer USD for scene/terrain/asset handoff, keep SpeedTree FBX for foliage geometry since the wind data path is FBX-oriented. |
| **glTF 2.0** | Web/portfolio delivery (the Wix portfolio site in this repo), KHR_materials_variants for lookdev review, KHR_animation_pointer for simple wind-less preview motion | Use for review/shipping thumbnails and web viewers, not as the working asset format. |
| **3D Tiles** | Streaming massive environments to web (Cesium-style) | Relevant only if the portfolio adds a web map view. |
| **MaterialX** | Portable material graphs between Houdini/SpeedTree/UE | Partial support in UE; useful for sharing base PBR lookdev, but the toon/Substrate + audio-reactive graph is UE-specific and not portable. Do not try to express MPC-driven reactivity in MaterialX. |
| **MetaSounds** (UE-native, not open) | The actual audio→parameter engine. Harmonix (enabled here) adds beat/quantization. | The correct substrate for reactive foliage; already wired via MelodiaCore. |

## 3. Key takeaway for this project

Do **not** build a new interchange or audio pipeline. The project already has:
- `SpeedTreeImporter` enabled (no SpeedTree assets imported yet — the gap)
- `MPC_Melodia_Palette` driven by the MelodiaCore rhythm reactivity subsystem
  (`Bass/Mid/Treble/BeatPulse/BeatPhase/BeatIntensity/GlobalReactivity`),
  zero-safe, mirrored to Niagara (`NPC_Melodia_Palette`)
- TouchDesigner FFT/5-band analysis + OSC bridge (port 9000) on the TD side
- PCG suite for placement

The missing piece is only the join: import SpeedTree output and bind its
materials to the existing MPC contract — which is exactly what the harness
scripts in this folder do.

## 4. Reactive foliage binding contract (authoritative)

1. All reactivity reads `MPC_Melodia_Palette` — never sample audio in foliage
   materials, never add a second time source (drift risk documented in
   `Docs/ZENFOREST_MUSICAL_GLAM_HANDOFF_2026-08-25.md`).
2. Beat modulation shape: `cos²(BeatPhase·π)` — derivative zero at beat
   boundaries, no popping.
3. Zero-safe: absent clock ⇒ params = 0 ⇒ flat foliage.
4. Emissive scaled by `GlobalReactivity` and kept sub-blowout; roughness
   modulated `±10%` and clamped `[0.02, 1.0]`.
5. Wind = baked SpeedTree vertex animation for ambient motion; audio adds an
   additive WPO term `(AudioWindStrength + Bass)·sin(t)`.

## 5. Recommended follow-ups

- Evaluate USD export from Houdini (already in-repo) for the wider environment;
  keep foliage on the FBX+wind path until SpeedTree USD wind support matures.
- If licensing allows, import `.srt` directly through `SpeedTreeImporter` to get
  its wind-aware material factory, then patch those materials with the MPC
  expressions via `wire_audio_foliage_materials.py`.
- For the web portfolio, consider a glTF preview of hero trees with
  `KHR_materials_variants` for the "audio-reactive vs. calm" comparison shots.
