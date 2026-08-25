# Melodia Melusina — Mesh / Material / Collision Deep Intake Report

Project: `BS_GodFile` (UE 5.8) · Working root: `C:\EnvironmentPortfolio`
Date: 2026-08-15 · Purpose: sustained long-term game development prep — inventory of meshes, material instances, textures, collisions; loose ends; and environment asset-gap sourcing (Fab / BOOTH / VRM4U).

---

## 1. Scope & Canonical Paths

- UE content root: `C:\EnvironmentPortfolio\BS_GodFile\Content`
- Note: `C:\EnvironmentPortfolio\MelodiaMelusinaV2\Content` does **not** exist — `MelodiaMelusinaV2` is a clean 2-commit git repo that tracks `BS_GodFile` content.
- All environment meshes live under `Content\EnvSandbox\Meshes\`.
- All toon/material system lives under `Content\EnvSandbox\Materials\`.

---

## 2. Environment Mesh Inventory (`EnvSandbox\Meshes\`)

### 2.1 Cathedral (`Cathedral\`)
~40 `SM_Cathedral_*` static meshes (full interior/exterior cathedral kit). Inventory previously captured; all present.

### 2.2 Celestial (`Celestial\`)
| Asset | Size | Notes |
|---|---|---|
| `SM_CelestialIsle_Hero` | ~1.58 MB | Real geometry |
| `SM_MoonCore` | normal | |
| `SM_MoonShard_A` … `SM_MoonShard_D` | normal | |
| `sm_celestialisle_a.uasset` | 1,444 B | ⚠ minimal — see LFS finding |
| `sm_celestialisle_b.uasset` | 1,444 B | ⚠ minimal — see LFS finding |
| `sm_celestialisle_hero_plateau.uasset` | 1,499 B | ⚠ minimal — see LFS finding |

**LFS finding (corrected):** The three small `sm_celestialisle_*` files are **real binary `.uasset`s** (UE version-hash header present, reference `/Game/...` paths) — they are **not** LFS text pointer placeholders. They are, however, only ~1.4 KB, which is too small to contain baked geometry. Likely **empty or reference-only static meshes** (or previously-stripped imports). **Action:** verify in-editor; if empty, re-import from source or re-generate via the 42-asset TouchDesigner pipeline.

### 2.3 Environment (`Environment\`)
Large modular kit (predominantly the imported Kenney/KayKit-style low-poly kit): `wall*`, `wall-wood*`, `tower-*`, `template-*` (floor/wall/corner variants), `tree_*` (60+ trees: pine/round/tall/detailed/fat/oak/palm/plateau/small), `table*`, `tent*`, `wheel*`, `washer*`, `television*`, `toilet*`, `window*`, `doorway*`, `trashcan`, `watermill`, `windmill`, `tree-trunk/log/stump`, `weapon-bow/arrow`, etc. — plus a `Textures\` subfolder of ~150 `colormap.uasset` textures (atlas-driven). These are **atlas/low-poly** assets → will need toon-material remap to `M_Master_Toon_Universal`.

### 2.4 MathStructures (`MathStructures\`)
Procedural math-art meshes: `SM_Math_Icosahedron`, `SM_Math_LissajousRail_3_2_1`, `SM_Math_MobiusStrip`, `SM_Math_TrefoilKnot`.

### 2.5 Monuments (`Monuments\`)
`SM_EscherAscent` (single).

### 2.6 Ornament (`Ornament\`) — 19 assets
`SM_Orn_ColumnCapital, CorbelBracket, CrownMolding, DoorArchway, FiligreeRing, GothicTracery, OculusFrame, PendantFinial, QuatrefoilArch, RosetteMedallion, RoseWindow_8Petal, SpiralStaircase, TorusKnot, VaultRibs, WovenRing` (+ `Materials\MI_Material`).

### 2.7 OrnamentMusical (`OrnamentMusical\`)
`SM_Orn_MusicalCorner` (~2 MB), `NoteBeam`, `NoteHead`, `TrebleClef`, `SheetMusicRail` + `M_Musical*` / `M_Orn*` materials.

### 2.8 Ornaments (`Ornaments\`)
`SM_BaroqueArch`, `SM_RoseWindow`.

### 2.9 Orrery (`Orrery\`)
`SM_Math_Epitrochoid_Ring`, `SM_Math_TorusKnot_2_3`.

### 2.10 Sakura (`Sakura\`)
`SM_SakuraPetal` + `StaticMeshes\SM_Sakura_PetalProxy_Sphere`, `SM_UMesh_PolySphere5`.

### 2.11 WPTerrains (`WPTerrains\`) — 4 world-piece terrains
`SM_Terrain_BaroqueGrotto` (674 KB), `SM_Terrain_CosmicOrrery` (665 KB), `SM_Terrain_SakuraDream` (671 KB), `SM_Terrain_SpaceCathedral` (671 KB). These map to the 4 WP levels (`L_WP_BaroqueGrotto/CosmicOrrery/SakuraDream/SpaceCathedral`).

### 2.12 Loose root files
`HeartRailing`, `SM_Melusinas_BedFrame`/`Mattress` (fbx + uasset), `Endtable`, plus misc loose `.fbx`/`.uasset`.

### 2.13 Character meshes (non-environment)
- `Characters\Melusina\`: `SK_Melusina`, `SK_Melusina_Skeleton`, `SK_Melusina_PhysicsAsset`, `ABP_Melusina`, `BP_Melusina`, `IK_Melusina`, ~20 `AM_*` animations (Attack, Dash, DoubleAttack, FireBall, FocusAttack, GetHit, Idle, Intro, ItemUse, Spell_Shoot…).
- `Melodia\Characters\Melusina\V2Test\`: `SM_MelusinaBoots/Hair/Hair1/Shirt/Skirt` + animations.
- `Melodia\Meshes\`: `Opening\SM_MelusinaBedBedding/Frame`, `Roguelike\SM_RoomFloorDisc`, `VFX\SM_SakuraPetal`.

---

## 3. Material Instances & Texture System

### 3.1 Materials tree (`EnvSandbox\Materials\`)
Subfolders: `Candidates, Functions, Impressionist, Instances, Landscape, Masters, Niagara, PostProcess, RenderStudio, SDF, Space, ToonProfiles, _Archive, _Scratch`.

- **Masters:** `M_Master_Toon_Universal` is the Substrate toon master all imported MIs must parent to.
- **Landscape:** `Grass, Mud, Path, Rock, Wonder` + `LI_Probe_None`.
- **Functions/MPC:** `MPC_Portfolio_Audio` (in Materials\Functions).
- **SDF / DistanceField:** `Melodia\Materials\DistanceField` → `M_DF_*`, `RVT_*`.

### 3.2 ToonProfiles (`Materials\ToonProfiles\`) — 18 profiles
`TP_Character, Cosmic, Default, Foliage, Glass, Gold, Hero, Impressionist_Dry, Impressionist_Impasto, Impressionist_Wet, Melusina, NikkiDream, Ornamental, Stone, Stucco, Test, Water, Wood`.

### 3.3 Character Material Instances (`Materials\Instances\Character\`)
5 MIs: `MI_Character_Melusina_Accessory, Cloth, Eyes, Hair, Skin` — matches `SK_Melusina` part materials.

### 3.4 Environment MIs (`Materials\Instances\Environment\`)
`FlatColors, House, ImportedPacks, Magical` (StarryNight/VanGogh/Aurora/Celestial/Constellation/Dreamy/GoldLeaf/Midnight), `PatternsExtra` (`MI_pattern_000–002`).

### 3.5 .material_map.json
**Not found** in the Content tree during this intake (glob returned empty). If the Substrate-toon crosswalk file exists elsewhere, its path must be documented; otherwise the remap table is a loose end.

---

## 4. Collision Status

- Only **`SK_Melusina_PhysicsAsset`** is confirmed present (character skeletal physics — used for cloth/ragdoll).
- **No per-mesh CollisionProfile audit was performed this session.** Static-mesh collision settings (simple box/sphere/convex, complex as simple, block/overlap channels) are stored inside each `.uasset` and cannot be read reliably from the filesystem without the editor.
- **Action (in-editor):** run a collision sweep over `EnvSandbox\Meshes\*` — verify walkable pieces (`template-floor*`, `wall*`, `tower*`, `WPTerrains\SM_Terrain_*`) have **complex-as-simple + block**; verify ornament/props are **no-collision or block-light**; ensure `SM_SakuraPetal` + `SM_MoonShard_*` don't block the player.
- PCG-generated pieces (42-asset pipeline, not yet imported) will need collision defaults set at import time.

---

## 5. Loose Ends / Prep Backlog

### 5.1 42 procedural FBX assets — ⚠️ REPORT DISCREPANCY / NOT IMPORTED
**Verified ground truth (2026-08-15):**
- The TouchDesigner script `build_procedural_fbx_assets.py` **does exist** and writes 42 FBX + 10 `.material_map.json` manifests **into `MelodiaMelusinaV2\Content\...` paths** (lines 452–611).
- **BUT `MelodiaMelusinaV2\Content` does not exist**, and **none** of the claimed target dirs (`EnvSandbox\Meshes\Ornament`, `OrnamentMusical`, `Architecture`, `Foliage`, `Rocks`, `VisualReactivity`) exist under either repo. **Zero `.material_map.json` exist on disk.**
- The `MelodiaMelusinaV2_Asset_Gap_Analysis_Report.md` verification log is **not reproducible** — its stated locations are absent.
- **Where the Ornament FBX actually live:** `BS_GodFile\KitbashExport\` (81 FBX total; 35 `SM_Orn_*` under `OrnamentMusic_WIP\Gothic\` + `Musical\`), plus `BS_GodFile\Products\_Staging\OrnamentSculptReview_20260712\`. These are a **manual sculpt pass**, not the scripted 42-set.
- So the "42/42 generated & verified" pipeline output is **not present** as claimed. The script was likely authored but not executed into its target, or its output was moved/renamed. **Action:** decide whether to (a) run `build_procedural_fbx_assets.py` to regenerate into `MelodiaMelusinaV2\Content`, or (b) treat `KitbashExport\OrnamentMusic_WIP\Gothic\` as the real source and import from there into `BS_GodFile\Content\EnvSandbox\Meshes\Ornament\`. Target folders `Architecture`, `Foliage`, `Rocks`, `VisualReactivity` remain absent; the script also generates those, but they're not on disk.

### 5.2 KitBash3D Atlantis — purchased, download in progress
- `Imports\KitBash3D_Atlantis\PROVENANCE.md` present; **no assets yet** (staging prep only, as of 2026-08-15).
- Retail $249.99. Intake rule: → `Content\EnvSandbox\Meshes\Atlantis\`, MIs → `Materials\Instances\Atlantis\` parented to `M_Master_Toon_Universal`. Never overwrite existing paths.
- Automatable via `Content\Python\ingest_aaa_underwater_packs.py`.

### 5.3 Oceanology NextGen (Galidar) — purchased, download in progress
- `Imports\Oceanology\PROVENANCE.md` present; staging prep only.
- C++ FFT ocean/water plugin: buoyancy, swimming, underwater post-process, caustics, god rays, stylized support. Lands in `BS_GodFile\Plugins\Oceanology*`. **This is the ocean substrate for the Atlantis underwater content.**

### 5.4 LFS / file-health
- The three `sm_celestialisle_*` files are real (not LFS pointers) but suspiciously small — verify in editor.
- No other mesh corruption found. Small-file audit (<2 KB) across Content returned only legitimate lightweight assets (LayerInfo, PhysicalMaterials, SoundClasses, IA_*, MPC, submixes).

### 5.5 Imported pack inventory (`Imports\Environment\`)
15 staged packs with PROVENANCE.md: `AnimeFoliage_Perch, AvatarGarden, CrystalCrossroads, GothicCastle, KayKitMedievalBuilder, KenneyCastleKit, KenneyMiniForest, KenneyModularCave, KenneySkyboxes, LowPolyCrystals, LunarYear, MusicalInstruments, RetroJRPGAssets, StylizedEnchantedForest, StylizedNatureMegaKit`. Plus `Imports\Plugins\` (KawaiiPhysics, MooaToon, VRM4U).

### 5.6 Megascans
- **`Content\Megascans\` exists** with subfolders `3D_Assets, 3D_Plants, Decals, Surfaces` — a Megascans install is present in-project. (Legacy Megascans free-claim ended 2024; Fab still carries Quixel free items, e.g. `Granite Rock`, `Nordic Forest Cluster*`, `Forest Terrain`, `Stucco Facade`, `Plastered Concrete Wall`.)

---

## 6. Verified FBX Asset Locations (ground truth 2026-08-15)

| Source tree | FBX count | Notes |
|---|---|---|
| `BS_GodFile\KitbashExport\OrnamentMusic_WIP\Gothic\` (P0_Fix/P1_Heroes/P2_Detail) | 35 `SM_Orn_*` | Real sculpted gothic ornament FBX |
| `BS_GodFile\KitbashExport\OrnamentMusic_WIP\Musical\` (HandRemake/Polish/Tokens) | incl. `SM_Orn_TrebleClef`, `NoteHead`, `MelodyToken_01–03`, etc. | Musical ornament FBX |
| `BS_GodFile\KitbashExport\CathedralKit`, `MusicalOrnamentalMeshes`, `textures`, `flip_cache_melusina_waterhair` | | Supporting kits / caches |
| `BS_GodFile\Products\_Staging\OrnamentSculptReview_20260712\` | | Staging review copies |
| **Claimed target `MelodiaMelusinaV2\Content\EnvSandbox\Meshes\*`** | **0** | **Does not exist** — report's 42-set is not present |
| **`*.material_map.json` (whole workspace)** | **0** | **Missing** despite report claiming 10 |

**Conclusion:** the Ornament/Musical FBX physically exist under `KitbashExport\OrnamentMusic_WIP\`, but the 42-asset automated pipeline output + material crosswalk manifests described in the asset-gap report are **not reproducible on disk**. This must be reconciled before any import decision.

---

## 7. Environment Asset Gaps & Sourcing (Fab / BOOTH / VRM4U)

Artistic direction: **Infinity Nikki aesthetic** — soft pastel, fairytale medieval, whimsical flora, celestial cave grottoes, classical instruments, cute proportions; Substrate Toon (`M_Master_Toon_Universal`).

### 7.1 Underwater / Atlantis (HIGH PRIORITY — content is in-flight)
- **Purchased:** KitBash3D **Atlantis** (Fab, $249.99) + **Oceanology** plugin — both awaiting download. Primary gap-filler.
- Fab alternatives for fill/backup:
  - **Underwater Adventure Asset Pack** — UE 4.16–4.23 (older, Vault/migrate only).
  - **Low Poly Underwater Environment Pack** — Fab, updated 2026-08-13.
  - ITHappy **Platformer 12 Underwater** — 136 assets, 3 levels, FBX/OBJ/GLTF, VR-ready; on Fab + Unity.
  - Quixel free water/ocean materials on Fab (e.g. ocean/fresh-water material categories).
- BOOTH (pixiv): low signal for 3D underwater environments in the searches run; the `free asset` / `free world asset` catalogs (5,626 / 642 items) are dominated by VRM/avatar & 2D content. Prefer Fab for underwater geo.

### 7.2 Brutalist Architecture (MEDIUM PRIORITY — deliberate aesthetic contrast zone)
- **Brutalis Backrooms: Modular Brutalist Environment Kit** — UE 5.5+, Nanite-enabled, modular concrete/liminal. Best fit found.
- Fab has abundant modular medieval/city kits (Synty, ithappy, StylArts, Leartes) but those overlap the fairytale aesthetic; brutalist is the gap.

### 7.3 VRM avatars / VR asset usage (VRM4U path)
- **VRM4U is confirmed present** in-project at `BS_GodFile\Plugins\VRM4U` (plus `Imports\Plugins\VRM4U`).
- `VRM4U.uplugin`: `VersionName 1.0`, `EngineVersion 5.8.0` → **declares UE 5.8**, matching the project.
- Latest upstream release: **v1.2026.07.22** (`github.com/ruyo/VRM4U`, ~1.9k stars, 230 forks). ruyo confirmed UE 5.8 support on 2026-06-22 (X post).
- Capabilities relevant here: runtime VRM import, MToon/Substrate reproduction, spring-bone/collision physics, humanoid RIG retargeting → enables BOOTH VRM avatars/outfits to drive Melusina/companion characters.
- **BOOTH** is the correct source for VRM avatars, outfits, hair, accessories (all 0 JPY/free options abundant). For 3D *environment* geometry, BOOTH is weaker — use Fab/KitBash3D/Megascans.

### 7.4 Recommended priority order for sustained development
1. **Reconcile the 42-FBX discrepancy (§5.1/§6):** either run `build_procedural_fbx_assets.py` (regenerates into `MelodiaMelusinaV2\Content`) or import from the real source `BS_GodFile\KitbashExport\OrnamentMusic_WIP\Gothic\`. Regenerate the missing `.material_map.json` manifests. Then import with UE5.8 FBX importer (100x scale, cm) + collision defaults.
2. Land Atlantis + Oceanology (complete downloads) -> ingest via `ingest_aaa_underwater_packs.py`.
3. Verify/replace the 3 small `sm_celestialisle_*` meshes.
4. Remap imported atlas pack meshes (Kenney/KayKit/Atlantis) to `M_Master_Toon_Universal` via the toon crosswalk (recreate `.material_map.json` if missing).
5. Run in-editor collision sweep.
6. Optional: Brutalist kit for the contrast zone; VRM4U + BOOTH VRM content for avatar/outfit expansion.

---

## 8. Related Prior Reports
- `MelodiaMelusinaV2_Asset_Gap_Analysis_Report.md` (42/42 FBX claimed generated & verified — **see §5.1: not reproducible on disk as of 2026-08-15**).
- `MelodiaMelusinaV2_Analysis_Report.md`.
- `MELODIA_ARCHITECTURAL_MASTER_PLAN.md`.
- `asset_recommendations.md` (Infinity Nikki aesthetic, staged imports with SHA-256 + PROVENANCE).
- `TODO.md`, `AGENT_HANDOFF.md` (loose-end tracking).