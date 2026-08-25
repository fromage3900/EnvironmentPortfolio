# ZenForestTest Musical Glam — Beautiful Renders Today (2026-08-25)

> **Owner:** you. **Scope:** ZenForestTest ONLY. **Ship today:** hero loop + glam sequence.
> Built as source-control / material / VFX expert pass. 1 editor, no P0 authority changes.

## Source Control Expert — How We Shipped Safely

**Branch:** `feature/zenforest-musical-glam` (from `main` @ 645eaa5). One feature, one folder.
**LFS guard:** `tools/git_lfs_guard.py` — `[OK] No lockable binaries modified` pre-commit.
**Asset validation:** `tools/validate_assets.py --strict` — `[OK] hard 0 missing`.
**`.gitattributes` already correct:** `*.uasset *.umap *.png *.exr *.wav lockable filter=lfs` (line 31,45). No edit needed.
**NEVER run:** `git clean -fd`, `git checkout -- .`, `delete_asset` blindly (see `BS_GodFile/AGENTS.md` § NEVER RUN THESE — bulk Content is untracked, clean deletes protagonist).
**Commit contract (Conventional Commits + hooks):**
```
feat(zenforest): add musical glam pass (MPC-reactive mats + 4 Niagara + LS + MRQ)
  - Content/ZenForestTest_MusicalGlam/** (new folder, 3 mats + textures)
  - ZenForestTest.umap (LFS lockable — `git lfs lock BS_GodFile/Content/ZenForestTest.umap` before edit if team)
  - Content/Python/setup_zenforest_musical_glam.py
  - Content/Python/setup_zenforest_musical_sequence.py
  - Content/Python/audit_zenforest_musical.py
docs(zenforest): add musical glam capture brief
```
**PR gate:** `liveops-ci.yml` + `lfs-guard.yml` run `validate_assets + validate_gacha --strict + validate_feature_flags`. Push only the glam folder + 3 Python tools + docs.

## Material Expert — What Makes It Beautiful

**Engine baseline (no ini edit needed, verified `audit_zenforest_musical.py`):**
```
r.CustomDepth=3          // M_PP_StorybookOutline per-object + rhythm stencil hit flash
r.Substrate=True         // layered toon BSDF (M_Master_Toon_Universal)
r.Shadow.Virtual.Enable=1 + r.MegaLights.EnableForProject=True  // soft fantasy GI
r.DynamicGlobalIlluminationMethod=1 + r.ReflectionMethod=1       // Lumen
r.DefaultFeature.MotionBlur=False  // crisp 1920x1080 portfolio; cinematics opt-in via PPV
```

**Single musical time source (no drift):**
- `UMelodiaAudioReactivePresentationSubsystem` owns MPC_Melodia_Palette `BeatPulse/BeatPhase/BeatIntensity/Bass/Mid/Treble/GlobalReactivity` every tick from `UMelodiaMusicClockSubsystem.GetBeatPhase(VisualTimebase)` (128 BPM default, real tempo overrides).
- Same tick mirrors to `NPC_Melodia_Palette` for Niagara via `GetNiagaraParameterCollection()` — materials + FX pulse to **identical** `cos^2(BeatPhase*pi)` (1.0 ON beat). TouchDesigner gets `NotifyBeat` on phase wrap -> OSC 9000.
- Materials that read `MPC_Melodia_Palette.BeatPulse` are zero-safe: if no clock, BeatPulse=0, PPV stays flat rather than invented tempo.

**3 new mats in `ZenForestTest_MusicalGlam/Materials/`:**
| Mat | Alpha | Reactive params | Look |
|---|---|---|---|
| `M_Zen_Musical_SoundwavePulse` | `T_Zen_SoundwavePulse` (Rune Soundwave) | BeatPulse, BeatPhase, Bass, GlobalReactivity | Expanding ring, bass emissive 1.2 + beat 0.8 |
| `M_Zen_Musical_ClefScroll` | `T_Zen_ClefScroll` (MusicalClefScroll) | Treble, BeatPulse, GlobalReactivity | Scrolling clef staff, treble sparkle |
| `M_Zen_Ghibli_PetalVortex` | `T_Zen_PetalVortex` (Ghibli PetalVortex) + FlowMap | BeatPulse, BeatPhase, Mid | Swirling petals, flowmap-driven drift |

Tune: `wire_audio_material_pulsation.py` math — `BeatPulse=cos^2(phase*pi)` derivative zero at boundaries (no pop), `Roughness*(1-0.10*BeatPulse)` clamped 0.02-1.0, emissive never HDR blowout.

**Sky + Post:**
- `UltraDynamicSky` volumetric god rays (warm pastel LUT from `MATERIAL_LOOKDEV_PIPELINE.md`) + Imperfecter PPV stack (`PP_Zen_MusicalGlam_Hint` unbound, bloom 0.8, vignette, CA on BeatPulse).
- PPV is a hint volume — artist tunes bloom/tint in viewport; MPC tint rides live.

## VFX Expert — What Makes It Musical

**Alpha library (LFS, already in `Content/Alphas_Sparkles/`):**
`T_Alpha_Rune_SoundwavePulse.png 66k`, `T_Alpha_Rune_MusicalClefScroll.png 133k`, `T_Alpha_Rune_HarmonicStaff.png`, `T_Alpha_Ghibli_PetalVortex.png 59k`, `T_Alpha_Ghibli_WindSwirl.png 148k`, `T_Alpha_Ghibli_MeadowSigil.png`, `T_Alpha_Rune_BaroqueFiligree.png 114k`, `T_Alpha_sparkle_cluster_alpha.png`. Plus `T_FlowMap_WaterVortex_RGA.png` (R=Vx,G=Vy,A=falloff), `T_Normal_RuneRelief_N.png`, `T_Packed_Rune_PBR.png`.

**4 Niagara actors spawned in ZenForestTest meadow (focal derived from TORII/SHRINE/Landscape bounds):**
| Actor | Template (fallback) | Musical behavior (NPC_Melodia_Palette) |
|---|---|---|
| `VFX_Zen_SoundwavePulse` | `NS_Uni_MistSheet` → `NS_Melodia_ClickSparkle` | Scale `1 + 0.6*BeatPulse`, burst on beat wrap ( NotifyBeat ) |
| `VFX_Zen_PetalVortex` | `NS_SakuraPetalGust` → `NS_SakuraPetals_v2` | Drift speed `BeatPulse*GlobalReactivity`, WindSwirl flowmap |
| `VFX_Zen_SparkleChoir` | `NS_SakuraDreamSparkle` → `NS_Melodia_CursorTrail` | Spawn rate `Treble*GlobalReactivity + RhythmPulse`, combo glint |
| `VFX_Zen_MeadowSigil` | `NS_SakuraGroundPetals` | Ground filigree + meadow sigil, Bass-reactive glow |

All sample `NPC_Melodia_Palette` (`BeatPulse, BeatPhase, Bass, Mid, Treble, RhythmPulse, ComboNormalized, GlobalReactivity`) — already declared on `NPC_Melodia_Palette` and consumed by `NS_Melodia_ClickSparkle/CursorTrail/Arc/...` so no new collection needed.

**Flowmap tip (UE Material):** sample `T_FlowMap_WaterVortex_RGA` → `V = (R*2-1, G*2-1)` → `UVflow = UV + V * Time * Speed` → sample diffuse; alpha = `A` radial falloff.

## Today's Render Systems — Run Order (10 min kit)

```powershell
# 1) Audit (no writes, proves engine ready)
py Content/Python/audit_zenforest_musical.py

# 2) Glam pass — wires alphas/mats/actors/cams/PPV into ZenForestTest
py Content/Python/setup_zenforest_musical_glam.py          # full
# or preview: py Content/Python/setup_zenforest_musical_glam.py --dry-run
# or verify:  py Content/Python/setup_zenforest_musical_glam.py --verify-only

# 3) Hero cams (if you want the portfolio framing)
py Content/Python/setup_zenforest_hero_cameras.py

# 4) 10s LevelSequence + MRQ preset
py Content/Python/setup_zenforest_musical_sequence.py

# 5) Capture
py Content/Python/render_exporter.py --width 1920 --height 1080   # hero+breakdown PNGs -> Saved/Portfolio/Renders/
# MRQ: Window > Cinematics > Movie Render Queue -> LS_ZenForest_MusicalGlam_001 + MRQ_ZenForest_MusicalGlam (1920x1080 PNG -> Saved/Portfolio/MRQ/ZenForest_MusicalGlam/)

# 6) Encode loops for web (optional)
powershell tools/encode_material_loops.ps1
powershell tools/encode_melusina_loops.ps1
python tools/build_social_upload_kit.py

# 7) Re-audit + commit
py Content/Python/audit_zenforest_musical.py
python tools/git_lfs_guard.py; python tools/validate_assets.py
git add BS_GodFile/Content/ZenForestTest_MusicalGlam/ BS_GodFile/Content/Python/setup_zenforest_musical*.py BS_GodFile/Content/Python/audit_zenforest_musical.py Docs/ZENFOREST_MUSICAL_GLAM_HANDOFF_2026-08-25.md Saved/Audit/zenforest_musical*.json
git commit -m "feat(zenforest): add musical glam pass (MPC-reactive mats + 4 Niagara + LS + MRQ)"
```

**New files on this branch:**
- `Content/Python/setup_zenforest_musical_glam.py` ✓ compiles
- `Content/Python/setup_zenforest_musical_sequence.py` ✓ compiles
- `Content/Python/audit_zenforest_musical.py` ✓ compiles — engine ini + alphas OK (5/5), standalone mode
- `Docs/ZENFOREST_MUSICAL_GLAM_HANDOFF_2026-08-25.md` (this file)
- `Saved/Audit/zenforest_musical_audit.json` (evidence, no writes)

LFS/validate: `git_lfs_guard [OK]`, `validate_assets [OK]`.

## Capture Brief — Beauty Settings to Use Live

- **Time of day:** UDS sunset (volumetric god rays through `FX/MistCards` fog), Lumen `HighlightContrast 0.8 / ShadowContrast 0.8`.
- **Framing:** Pilot `Cam_ZenGlam_Establishing` (28mm) → `Route` (40mm) → `Materials` (75mm). Materials cam is 75mm for fabric/toon sheen close-up.
- **Music lock:** Ensure `128BPMarpeggiomelody_beatgrid` MIDI loaded (real tempo from `MakeDefaultSongMap` tempo+bar+beat maps) so MRQ rides true 128, not invention.
- **Imperfecter:** Warm pastel LUT, bloom 0.8, vignette, chromatic aberration lerp on `BeatPulse` (PP_Zen_MusicalGlam_Hint).
- **Output:** 1920x1080 PNG sequence + hero PNGs; keep `r.CustomDepth=3` for outline stencil in captures.

## What NOT to do today (guardrails)

- Don't add a second combat/HUD/wardrobe/progression subsystem (P0 is convergence, not construction).
- Don't hand-build a song map (`Init(ticksPerQuarter)+bar map` required or HarmonixMidi crashes at `0x4`).
- Don't `git clean` / checkout -- .  while Content is largely untracked — you'll delete the protagonist.
- Don't invent a second BPM source — `LastKnownBPM` seeds at 128 then overwrites from the clock every tick.
