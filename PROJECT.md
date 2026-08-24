# Project: Melodia Melusina

**Melodia Melusina** is a single-person AAA-tier Unreal Engine 5.8 game.

This file is the project's authority statement. If any other document in this workspace
disagrees with it about what the project is, this file wins.

**Current P0 execution authority (2026-08-24):**
[`BS_GodFile/Docs/Handoffs/MELODIA_CONVERGENCE_CLOSEOUT_AND_P0_PLAN_2026-08-24.md`](BS_GodFile/Docs/Handoffs/MELODIA_CONVERGENCE_CLOSEOUT_AND_P0_PLAN_2026-08-24.md).
The active work is convergence and proof. The former nine-item economy/song/HUD/dungeon/enemy/
quest tranche is deferred post-P0 in
[`BS_GodFile/Docs/P0_TASK_LEDGER.json`](BS_GodFile/Docs/P0_TASK_LEDGER.json).

---

## The authority statement

**QuillScript** owns narrative. **The TurnBased JRPG template** owns party, turns, targeting,
damage, results, inventory and saves. These two are absolute. They are never rebuilt, wrapped,
or competed with.

The **musical layer** is not a second game. Rhythm input rides *on top of* the JRPG command
scaffolding — the same Attack/Skill/Item/Flee decisions, timed. Music enhances combat and, in the
world, acts as a key: puzzles respond to played phrases the way Zelda's ocarina and Infinity
Nikki's abilities gate traversal.

The **wardrobe** is a core pillar, not a deferred feature. Outfits are Infinity Nikki-grade
presentation on a Substrate Toon spine, and they carry gameplay meaning.

Shape reference: **OMORI**. Music-as-key reference: **Zelda**. Visual and wardrobe bar:
**Infinity Nikki**.

**The AI tooling is a tool.** Local models, MCP surfaces, agent lanes and benchmarks exist to
produce game artifacts. None of them is the product, and none may set project direction.

---

## The four pillars and their authority layers

```
              ┌──────────────────────────────────────────────────────────────┐
              │  ABSOLUTE AUTHORITY — never rebuilt, wrapped, or competed    │
              ├──────────────────────────────┬───────────────────────────────┤
              │  QuillScript                 │  TurnBased JRPG template      │
              │  narrative, dialogue,        │  party, turns, targeting,     │
              │  7-verb notifications        │  damage, results, inventory,  │
              │                              │  saves                        │
              └───────────────┬──────────────┴───────────────┬───────────────┘
                              │                              │
                              ▼                              ▼
              ┌──────────────────────────────────────────────────────────────┐
              │  THE ORCHESTRA — four pillars that converge onto the above   │
              ├───────────────┬───────────────┬───────────────┬──────────────┤
              │  RHYTHM       │  WARDROBE     │  UI           │  WORLD       │
              │               │               │               │  PUZZLE      │
              │  timing on    │  outfits with │  ONE writer   │  music as    │
              │  JRPG command │  presentation │  per surface  │  key         │
              │  input        │  + gameplay   │               │              │
              │               │  meaning      │               │              │
              └───────────────┴───────────────┴───────────────┴──────────────┘
```

Each pillar has **exactly one owner**. Where more than one implementation exists, the owner is
named and every other implementation is judged OWNER / LIVE / DEAD / MERGE in
[`BS_GodFile/Docs/ORCHESTRA_CONVERGENCE_2026-08-20.md`](BS_GodFile/Docs/ORCHESTRA_CONVERGENCE_2026-08-20.md).
Not everything that duplicates is dead — check before assuming.

The seams between the pillars and the authority layers are specified in
[`BS_GodFile/Docs/ORCHESTRA_CONTRACT_2026-08-20.md`](BS_GodFile/Docs/ORCHESTRA_CONTRACT_2026-08-20.md).

---

## The problem this project is currently solving

The systems are **not incomplete — they were built in parallel and never joined.**

- **Rhythm** has three implementations. Two of them are load-bearing; one is genuinely dead.
- **Wardrobe** has six outfit-state holders. The best one is complete and **nothing outside its
  own plugin calls it.**
- **UI** is source-converged on `UMelodiaUIBridgeSubsystem` as the Melodia battle-widget writer;
  the old overlay is now a retired compatibility observer that creates no widgets. Runtime
  `hud_single_writer` proof and instantiated-widget identity remain open.
- **World puzzle exists** — `Source/BS_GodFile/Piano/` is a complete music-as-key system with PCG
  piano keys, steppable note nodes and pattern scoring. The Narrative challenge adapter is
  source-built; live host attachment, level wiring, visible route payoff, and replay proof remain
  open.

The work is **convergence**, not construction. Almost every part is already built. Stop building
in parallel; integrate into one Melodia Melusina orchestra.

---

## Completion gates

Nothing is done without a ledger row. Runner: `python BS_GodFile/Tools/echo_run.py`.

### Bounded historical evidence — four captured PASS rows

Verified against `Saved/gate_ledger.json`, not against prose. Each row applies to its recorded
August 13–14 baseline. It is valuable evidence, but it does **not** certify the current shipping
baseline after later source/content changes.

| Gate | Contract | Status |
|---|---|---|
| `runtime` | Real keyboard input drives the battle path | **PASS 2026-08-13** — owner-verified, `owner-realkey-20260813` |
| `save_load` | Canonical `BP_JRPGSaveGame` slot across a full process restart | **PASS 2026-08-14** — owner-verified, `owner-verified-20260814` |
| `repeat_consume` | Flag + reward restore without duplication; `melodia:stat:` idempotent per IntentId | **PASS 2026-08-14** — `session-894e8f57` |
| `package_launch` | Development build launches and plays the route outside the editor | **PASS 2026-08-14** — packaged Gauntlet, 2782-package IoStore mounted outside the editor |

### Active P0 quality gate

| Gate | Contract | Status |
|---|---|---|
| `static_gates` | Graph reachability, live-path, BP sweep, UI lint, T3D baseline | **FAIL 2026-08-14** — `verify_baseline` drift on `M_Master_Simple_Universal` (25→26 nodes) and `M_Master_Toon_Landscape_HeightBlend` (290→304 nodes). The other four sub-gates passed. |

### Orchestra gates (P0) — the convergence

| Gate | Contract | Status |
|---|---|---|
| `rhythm_owner` | Exactly one rhythm path reaches the JRPG damage calculation | OPEN |
| `hud_single_writer` | One writer owns the battle HUD | OPEN |
| `wardrobe_equip_roundtrip` | Equip → save → restart → load → correct outfit and materials | OPEN |
| `rhythm_grade_to_result` | A real-key rhythm grade changes a JRPG battle result; Quill resumes exactly once | OPEN |
| `music_world_key` | One world object responds to one played phrase | OPEN |
| `wardrobe_gameplay_hook` | One outfit produces one observable gameplay difference | OPEN |
| `battle_integration_map` | Victory, Defeat, Fled, and unavailable each produce a typed result and resume or abort Quill exactly once | HOLD — latest row did not exercise the full matrix |

Owner observations remain bounded ground truth for their captured sessions: rhythm WORKED and
QuillScript WORKED (2026-08-12), `runtime` (2026-08-13), and `save_load` (2026-08-14). They are
not silently promoted to current-baseline or packaged certification.

**What this means.** The project has credible historical evidence for input, save/reload,
exactly-once replay, and package launch, but the current baseline is not shipping-certified. P0
exits only after the active convergence gates, the current static chain, and the four-outcome
battle/result matrix are recorded against a frozen baseline.

---

## Wardrobe visual spine (M1–M4, DONE)

The PBR material and texture architecture is the **substrate the wardrobe pillar stands on**. It
is complete. It is not the project goal, and no agent may treat it as one.

It establishes an Infinity Nikki-tier visual standard combining Substrate Toon shading, unified
ORM channel packing, high-frequency procedural and sampled micro-tactility, and harmonic
audio-reactivity across characters (`SK_Melusina`), sacred environment trims, and dynamic water
bodies (`M_Water_Master_Grand_v7/v10`).

```
                              [ Audio Infrastructure ]
                       UMelodiaMusicClockSubsystem (Harmonix/Quartz)
                                       │
                                       ▼ (TickPresentation)
                             [ MPC_Melodia_Palette ]
                    (BeatPulse, Bass, Mid, Treble, PaletteTint)
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
    [ M_Master_Toon_Universal ]                   [ M_Water_Master_Grand_v10 ]
   (Substrate Toon BSDF + ToonProfiles)           (Substrate SingleLayerWater)
   - FabricAnisoGate (Silk, Velvet, Brocade)      - 8-Wave Deterministic Gerstner WPO
   - Nikki Iridescence & Sheen Accumulator        - Dynamic Caustics & Depth Fade
   - Additive Audio Emissive/Roughness Hooks      - Audio Bioluminescence / Wave Hooks
                ▲                                             ▲
                └──────────────────────┬──────────────────────┘
                                       │
                        [ Unified PBR Texture Pipeline ]
                   Standardized Naming: T_<Family>_<Name>_<Channel>
                   Channel Packing: ORM (R=AO, G=Roughness, B=Metallic)
                   Tangents: BC5 Normal, Height: Linear R8/R16 POM
```

`MPC_Melodia_Palette` is also the **audio→world bus used by the music-as-key pillar.** Piano and
the Narrative challenge adapter are source-built; the intended live host, level attachment, and
visible player-facing route still require proof.

### Milestones

| # | Name | Scope | Status |
|---|------|-------|--------|
| M1 | PBR Texture Channel Standardization & Packing Pipeline | Automated channel packer, validation harness, Melusina & trim repack | DONE |
| M2 | Tileable & Hybrid Fantasy Fabric Library (Infinity Nikki Grade) | 6 core fantasy fabric PBR sets, 4K/2K textures, Melusina wardrobe instances | DONE |
| M3 | Audio-Reactivity & Water Harmony Integration | `MPC_Melodia_Palette` wiring into water, caustics, fabric sheen, rune glow | DONE |
| M4 | Substrate Toon Master Integration & Verification | Sampler limit optimization, master shader verification, E2E test pass | DONE |

### Feature inventory

| # | Feature | Description | Milestone |
|---|---------|-------------|-----------|
| F1 | Automated ORM Packing Tool | High-throughput PIL tool packing separate AO, Roughness, Metallic, Height into unified ORM textures | M1 |
| F2 | Channel Validation & Invariant Harness | Script checking POT resolutions, sRGB settings, BC5/BC7 compression, naming conventions | M1 |
| F3 | Repack Core Staging & Character Assets | Repack Melusina wardrobe, BlingVol3 rhinestones, and trimsheet sets into standardized ORM | M1 |
| F4 | Royal Velvet PBR Set & Preset | Deep micro-fiber dual-sheen, high roughness body, inverted Fresnel grazing sheen | M2 |
| F5 | Gilded Jacquard & Brocade PBR Set | Metallic gold/silver embroidery over satin weave with height-compete relief and anisotropic split | M2 |
| F6 | Sheer Silk & Chiffon PBR Set | High anisotropic streak highlights, fine weave normal perturbation, dual-tone Fresnel shift | M2 |
| F7 | Baroque Filigree Lace PBR Set | Intricate openwork tracery, alpha-masked open threads, micro-fiber edge fuzziness | M2 |
| F8 | Gold-Threaded Embroidery PBR Set | 3D bullion thread relief, anisotropic metallic highlight glints, sacred trim integration | M2 |
| F9 | Iridescent Celestial Weave PBR Set | View-dependent color shift, sparkling diamond micro-dust motes, Quartz pulse synchronization | M2 |
| F10 | Wardrobe Material Slot Mapping | Direct instance bindings for Melusina wardrobe mesh slots (frontpanel, shawl, skirt, sleeve, shirt) | M2 |
| F11 | Dynamic Caustics & Wave Displacement Audio Modulation | `MPC_Melodia_Palette` Bass/BeatPulse into water caustics intensity and Gerstner wave chop | M3 |
| F12 | Sheen, Sparkle & Rune Glow Audio Pulsation | Quantized cos²(BeatPhase · π) beat modulation in Toon Master additive emissive chain | M3 |
| F13 | Water Bioluminescence & Niagara Harmony | Underwater grotto bioluminescent impulse and contact reaction synchronized with battle BPM | M3 |
| F14 | Substrate Sampler Optimization | Enforce `Shared: Wrap` across all texture samplers, capping hardware sampler footprint at <= 4 | M4 |
| F15 | Universal Master & Instance Verification | Verify `M_Master_Toon_Universal` and `M_Water_Master_Grand_v10` compile cleanly without warnings | M4 |
| F16 | Multi-Tier E2E Test Suite | Comprehensive opaque-box test suite (Tiers 1-4) validating textures, packing, shaders, and audio | M4 |

---

## Interface contracts

### 1. PBR texture channel standard
- **BaseColor (`_BC`)**: PNG/TGA, 8-bit RGB, sRGB = `True`, TextureGroup = `TEXTUREGROUP_World` / `TEXTUREGROUP_Character`.
- **Packed ORM (`_ORM`)**: PNG/TGA, 8-bit Linear RGB, sRGB = `False`, Compression = `TC_Masks` (BC7):
  - **R (Red)**: Ambient Occlusion (1.0 = no occlusion, 0.0 = fully occluded).
  - **G (Green)**: Micro-Roughness (0.0 = mirror smooth, 1.0 = diffuse rough).
  - **B (Blue)**: Metallic (0.0 = dielectric, 1.0 = conductor).
- **Normal (`_N` / `_DetailN`)**: PNG/TGA, 8/16-bit Linear, sRGB = `False`, Compression = `TC_Normalmap` (BC5), DirectX convention (Green = Y-).
- **Height / Displacement (`_H` / `_Disp`)**: PNG/EXR, 8/16-bit Linear Grayscale, sRGB = `False`, Compression = `TC_Grayscale` (BC4/R8).
- **Mask / Sparkle / Sheen (`_Mask` / `_Sheen`)**: PNG, 8-bit Linear Grayscale, sRGB = `False`, Compression = `TC_Grayscale` (BC4/R8).

### 2. Fabric material instance parameters
- `FabricType`: Scalar (0=Default, 1=Cotton, 2=Silk, 3=Satin, 4=Velvet, 5=Wool, 6=Chiffon, 7=Sequins).
- `FabricAnisoLevel`: Scalar (-1.0 to 1.0).
- `FabricWeaveScale`: Scalar (1.0 to 128.0).
- `FabricWeaveStrength`: Scalar (0.0 to 2.0).
- `FabricSheen`: Scalar (0.0 to 2.0).
- `SheenTint`: Vector (RGBA).
- `SheenPower`: Scalar (0.5 to 10.0).
- `Iridescence`: Scalar (0.0 to 1.0).
- `SparkleIntensity`: Scalar (0.0 to 2.0).
- `SparkleThreshold`: Scalar (0.0 to 1.0).

### 3. Audio synchronization parameters (`MPC_Melodia_Palette`)
- `GlobalReactivity`: Scalar (0.0 or 1.0 master gate).
- `BeatPulse`: Scalar (cos²(BeatPhase · π), 0.0 to 1.0 peak on downbeat).
- `BeatPhase`: Scalar (0.0 to 1.0 sawtooth phase).
- `Bass` / `BassIntensity`: Scalar (0.0 to 1.0).
- `Mid` / `MidIntensity`: Scalar (0.0 to 1.0).
- `Treble` / `TrebleIntensity`: Scalar (0.0 to 1.0).
- `PaletteTint`: Vector (RGBA global tone harmony).

---

## Code layout

### Authority layers
- QuillScript: `BS_GodFile/Plugins/QuillScript/`
- TurnBased JRPG template: `BP_MelodiaJRPGGameMode`, `BP_MelodiaJRPGGameInstance`, `BP_BattleController`, `BP_BattleUI`, `BP_JRPGSaveGame`
- The bridge between them: `BS_GodFile/Source/BS_GodFile/MelodiaIntegration/MelodiaNarrativeSubsystem.*` + `MelodiaExternalJRPGBridgeSubsystem.*`

### Pillars
- Rhythm: `BS_GodFile/Source/BS_GodFile/MelodiaIntegration/MelodiaRhythmCombatSubsystem.*`, `RhythmBeatTracker.*`, `MelodiaJRPGPresentationRhythmComponent.*`, `MelodiaRhythmSkillDefinition.h`
- Beat authority: `MelodiaMusicClockSubsystem.*` (Harmonix/Quartz)
- Wardrobe: `BS_GodFile/Plugins/MelodiaWardrobe/` + `BS_GodFile/specs/wardrobe/wardrobe_catalog_contract.v1.json`
- UI: `MelodiaUIBridgeSubsystem.*` (Melodia widget writer), `MelodiaUIWiringComponent.*`,
  `MelodiaUIFeedbackSubsystem.*`; `MelodiaJRPGBattleOverlaySubsystem.*` is a retired no-widget
  compatibility observer pending reference-safe removal.
- World puzzle: `BS_GodFile/Source/BS_GodFile/Piano/` plus
  `MelodiaPCGNarrativeChallengeBridgeComponent.*` (source-built; live host/route proof pending).

### Wardrobe visual spine
- Packing & validation tools: `BS_GodFile/Content/Python/` (`melodia_pbr_packer.py`, `universal_melodia_texture_pipeline.py`, `validate_melodia_pipeline.py`).
- PBR fabric textures: `BS_GodFile/Content/Textures/Fabrics/` (`T_Fabric_<Type>_<Channel>.png`).
- Melusina standardized textures: `BS_GodFile/Content/Melodia/Characters/Melusina/Textures/` (`T_Melusina_<Slot>_<Channel>.png`).
- Material functions: `BS_GodFile/Content/EnvSandbox/Materials/Functions/` (`MF_ColorRamp3`, `MF_Nikki*`).
- Master materials: `BS_GodFile/Content/EnvSandbox/Materials/Masters/` (`M_Master_Toon_Universal`, `M_Water_Master_Grand_v10_Upgrade`).
- Material instances: `BS_GodFile/Content/EnvSandbox/Materials/Instances/Character/Cloth/` (`MI_Fabric_*`, `MI_Melusina_*`).
- Automated test suite: `Tests/` & `BS_GodFile/Content/Python/Tests/`.

### Tooling (a tool, not the product)
- Model routing: `BS_GodFile/Tools/model_router.py`
- Gate ledger: `BS_GodFile/Tools/echo_run.py`, `BS_GodFile/specs/echo_pipeline.json`, `BS_GodFile/Saved/gate_ledger.json`
- Tool policy (default-deny): `BS_GodFile/Tools/mcp_policy.py`
- In-engine LLM routing: `BS_GodFile/Source/BS_GodFile/MelodiaIntegration/MelodiaLLMRouter.*`
