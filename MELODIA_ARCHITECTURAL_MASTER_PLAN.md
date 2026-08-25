# Melodia Architectural Master Plan & Live-Ops Optimization Specification

**Project:** Melodia Architecture and Live-Ops Optimization  
**Author:** Project Orchestrator  
**Date:** 2026-08-11  
**Status:** Approved & Finalized  
**Repository Working Directory:** `C:\EnvironmentPortfolio`  
**Original Request Document:** `C:\EnvironmentPortfolio\.agents\ORIGINAL_REQUEST.md`  

---

## 1. Executive Summary & Project Mandate

This Architectural Master Plan provides a comprehensive deep technical study and production specification to resolve core Melodia gameplay bottlenecks, expand the multi-stage Echo asset/automation pipeline, and establish an enterprise-grade Git workflow inspired by modern AAA gacha live-ops standards (*Genshin Impact*, *Honkai: Star Rail*, *Wuthering Waves*).

### Key Accomplishments & Deliverables
1. **Gameplay Bottlenecks & Blueprint Graph Wiring**: Diagnostic resolution for all 12 P0 foundation gates, C++ JRPG combat/dialogue state bindings, repair of the property reflection typo (`curentMP` $\rightarrow$ `currentMP`), Harmonix music clock configuration (`LogMIDI` fix), rhythm highway visual graph construction (`WBP_MelodiaRhythmHighway`), Live Coding build standardization, pre-injection graph reachability validation (`bp_live_path.py`), and level streaming route consolidation (`L_MelusinaMorning` $\rightarrow$ `L_KaleidoNave`).
2. **Echo Multi-Modal Pipeline & Bridge Architecture**: Complete topology specification across Blender 5.2, UE 5.8, TouchDesigner, and Web front-end across network ports 9876 (LiveLink UDP), 9316 (Monolith MCP HTTP), 9317 (Blender MCP HTTP), 55558 (UEBlueprintMCP TCP), 50021/50022 (Voicevox/Melusina Voice). Details automated material crosswalks (sRGB-to-Linear conversion), PCG procedural geometry, `VRM4U` avatar variant automation, TouchDesigner 4-band RMS audio streaming, and PIL-based web asset product compilation.
3. **AAA Gacha Enterprise Git & Live-Ops Workflow**: Deployment of root (`.gitattributes`) and module (`BS_GodFile\.gitattributes`) LFS asset locking configurations with `lockable` attributes across all binary asset types (`.uasset`, `.umap`, `.blend`, `.fbx`, `.png`, `.exr`, `.wav`), specification of the `UMelodiaFeatureFlagSubsystem` (`UGameInstanceSubsystem`), 6-week trunk-based live-ops release branch model, automated CI/CD staging verification, and multi-agent distributed handoff governance.

---

## 2. Root Cause Resolution of Gameplay Bottlenecks & Blueprint Wiring

### 2.1 The 12 P0 Foundation Gates Remediation Plan

| Gate # | Name | Root Cause & Bottleneck | Resolution & Verification Specification |
|:---:|:---|:---|:---|
| **1** | Battle Widget Identification | `BP_BattleUI` unbound from viewport during PIE combat start | Verify package path `/Game/TurnBasedJRPGTemplate/Blueprints/UI/BP_BattleUI`. Wire `CreateWidget` in `BP_BattleController` on `BeginPlay` with z-order 10. |
| **2** | Input Parity & Debouncing | Rapid keypresses cause double action triggers in rhythm/combat | Implement 150ms input debouncing in `UMelodiaInputContextSubsystem`. Latch active input context during state transitions. |
| **3** | Result Matrix Pass | Combat completion fails to transition back to exploration | Bind `OnBattleOver` delegate in `MelodiaExternalJRPGBridgeSubsystem` to invoke `CompleteBattle()` with typed `EBSBattleResult`. |
| **4** | Save/Load Restart Persistence | Canonical save slot fails to persist across process relaunch | Standardize save slot key `Melodia_SaveSlot_0` using `USaveGame` binary serialization. Verify file writing to `Saved/SaveGames/`. |
| **5** | Flag & Reward Restore Idempotency | Combat rewards duplicate upon level reload | Enforce idempotent flag checking in `UMelodiaGameStateSubsystem` prior to granting items or granting XP. |
| **6** | Quill Unavailable Load | Load fails gracefully when Quill dialogue asset is missing | Implement fallback null-check in `QuillScriptInterpreter` to bypass dialogue and default to free exploration mode. |
| **7** | Safe Script Rerouting | Missing narrative node crashes execution tree | Route invalid script nodes to `IMelodiaTravelProvider::DefaultSafeLocation` (`Morning_RoomShell`). |
| **8** | Interpreter Invalidation Handling | Mid-dialogue level transition causes stale pointer crash | Latch `bIsTerminating` flag in dialogue manager and flush pending script delegates before level unload. |
| **9** | Mid-Battle Save Disabling | Player can save state mid-combat, corrupting save file | Set `bCanSave = false` in `USaveGameSubsystem` upon entering `EBSBattleState::InBattle`. |
| **10** | Main Menu Wiring | Main menu buttons point to legacy level paths | Wire `New Game`, `Continue`, `Load` in `WBP_MainMenu` to route through `UMelodiaTravelSubsystem::TravelToLevel`. |
| **11** | Room Shell Validator Repair | `Morning_RoomShell` tag mismatch breaks initial spawn | Add actor tag `Melodia_RoomShell_Anchor` to `Morning_RoomShell` actor in `L_MelusinaMorning`. |
| **12** | Packaged Route Launch | Uncooked level references cause black screen in shipping | Add `L_MelusinaMorning` and `L_KaleidoNave` to `Directories to Cook` in `DefaultGame.ini`. |

### 2.2 C++ JRPG Combat Bindings & Typo Repair
- **Property Reflection Fix**: Repair line 84 of `BS_GodFile/Source/BS_GodFile/MelodiaIntegration/MelodiaJRPGPostBattleLibrary.cpp`:
  ```cpp
  // REPAIRED: Search for canonical 'currentMP' first, falling back to legacy 'curentMP'
  FIntProperty* MapCurrentMP = CastField<FIntProperty>(FindAuthoredStructMember(UnitStateStruct, TEXT("currentMP")));
  if (!MapCurrentMP) {
      MapCurrentMP = CastField<FIntProperty>(FindAuthoredStructMember(UnitStateStruct, TEXT("curentMP")));
  }
  ```
- **Combat Bridge Bindings**: `UMelodiaExternalJRPGBridgeSubsystem::StartTaggedJRPGBattle(FName EncounterId)` binds battle completion to `UMelodiaJRPGPostBattleLibrary::RestorePartyAfterBattle`, ensuring party HP/MP and status effects are restored accurately upon returning to exploration.

### 2.3 Harmonix Music Clock & Rhythm Highway Visuals
- **Beat Map Configuration**: `EnsureBattleControllerMusicClock()` validates `128BPMarpeggiomelody_beatgrid` before populating `FSongMaps` (TempoMap, BarMap, BeatMap), eliminating `LogMIDI: SongMaps does not contain a Beat Map` error spam.
- **Rhythm Highway Execution**: `WBP_MelodiaRhythmHighway` uses `UseSkillWithRhythm(StockSkill)` to defer damage calculation until `FinishSession()` latches `PendingDamageMultiplier` (~3.05s), preventing premature anim-notify damage resolution (~0.51s).

### 2.4 Live Coding & Blueprint Graph Reachability
- **Closed-Editor Build Standard**: Hot-reloading header changes during Live Coding is blocked by modal popups. Standardize closed-editor compilation via `BS_GodFile\Build.bat` or MSBuild on `BS_GodFile.sln`.
- **Pre-Injection Graph Reachability**: Run `python BS_GodFile/Tools/bp_live_path.py <BlueprintPath>` prior to graph modifications to confirm the target Blueprint connects to engine entry points (`GlobalDefaultGameMode`, `GameDefaultMap`).

### 2.5 Level Streaming Route Consolidation
- The primary playability route is consolidated: `L_MelusinaMorning` $\rightarrow$ `L_KaleidoNave` (containing the 18 actors merged from `L_Melodia_Dreamstate`). Level streaming portal triggers invoke `UMelodiaTravelSubsystem::SeamlessTravel` to load target sub-levels asynchronously.

---

## 3. Echo Multi-Stage Asset Pipeline & Multi-Modal Bridge Architecture

### 3.1 Network Topology & Port Allocations

```
  +--------------------------------------------------------------------+
  |                     Melodia Multi-Modal Backbone                   |
  +--------------------------------------------------------------------+
       |                  |                 |                |
  (Port 9876 UDP)   (Port 9316 HTTP) (Port 9317 HTTP) (Port 55558 TCP)
       |                  |                 |                |
       v                  v                 v                v
  [LiveLink MoCap]  [Monolith MCP]   [Blender MCP]     [UEBlueprintMCP]
  (Motion Capture)  (16 Query Tools) (DCC Automation) (Socket Graph API)
       |                  |                 |                |
       +------------------+-----------------+----------------+
                                   |
                +------------------+------------------+
                |                                     |
         (Port 50021 REST)                     (Port 50022 REST)
                |                                     |
                v                                     v
       [VOICEVOX Engine]                     [Melusina TTS Proxy]
       (Japanese Audio)                      (Character Dialogue)
```

| Port | Protocol | Host / Endpoint | Purpose & Subsystem |
|:---:|:---:|:---|:---|
| **9876** | UDP | `localhost:9876` | Unreal Engine LiveLink pose and facial motion capture stream |
| **9316** | HTTP / JSON-RPC | `http://localhost:9316/mcp` | Monolith MCP engine automation server (16 query tools, `/health`) |
| **9317** | HTTP | `http://localhost:9317` | Blender MCP automation bridge for DCC mesh/rig processing |
| **9877** | HTTP | `http://localhost:9877` | Surreal Architecture procedural building generator endpoint |
| **9878** | HTTP | `http://localhost:9878` | Blender Scene Graph synchronization bridge |
| **55558** | TCP Socket | `localhost:55558` | UEBlueprintMCP socket interface for length-prefixed graph node edits |
| **50021** | HTTP REST | `http://localhost:50021` | VOICEVOX Japanese neural speech synthesis engine |
| **50022** | HTTP REST | `http://localhost:50022` | Melusina custom voice synthesis proxy |

### 3.2 Monolith MCP Proxy & Audit Logging
- `monolith_proxy.exe` wraps stdio-to-HTTP JSON-RPC communications, exposing `GET http://localhost:9316/health` for connection monitoring.
- All automation tool invocations log structured telemetry to `Saved/Logs/MonolithCalls.jsonl`:
  ```json
  {"ts":"2026-08-11T14:20:00Z","namespace":"blueprint_query","action":"find_node","params_hash":"a1b2c3d4","duration_ms":12.4,"ok":true,"error_code":0,"result_bytes":1024}
  ```

### 3.3 Automated Material Crosswalks & Toon Profile Math
- **sRGB-to-Linear Transformation Formula**:
  $$\text{Linear}(c) = \begin{cases} \frac{c}{12.92} & c \le 0.04045 \\ \left(\frac{c + 0.055}{1.055}\right)^{2.4} & c > 0.04045 \end{cases}$$
- **Hex `#352D40` Warm-Violet Conversion**:
  $$R: 53/255 = 0.20784 \rightarrow \text{Linear}(0.20784) = \left(\frac{0.20784 + 0.055}{1.055}\right)^{2.4} = 0.035133$$
  $$G: 45/255 = 0.17647 \rightarrow \text{Linear}(0.17647) = \left(\frac{0.17647 + 0.055}{1.055}\right)^{2.4} = 0.026330$$
  $$B: 64/255 = 0.25098 \rightarrow \text{Linear}(0.25098) = \left(\frac{0.25098 + 0.055}{1.055}\right)^{2.4} = 0.052814$$
  **Evaluated Result**: `LinearColor(0.035133, 0.026330, 0.052814, 1.0)`.
- **Toon Profile Parameters**: `create_tp_melusina.py` duplicates `/Game/EnvSandbox/Materials/ToonProfiles/TP_Hero` to `TP_Melusina`, configuring `DiffuseRamp`, `SpecularRamp`, `IndirectDiffuseIntensity` (0.3), `IndirectSpecularIntensity` (0.3), `ShadowingExtinction` (0.3), and assigning `T_HatchPattern`.

### 3.4 Procedural Geometry & Asset Variant Generation
- **PCG Plugins**: `PCGExtendedToolkit` and `ProceduralModelingToolkit` drive environment scatter and architectural ornament generation in `L_KaleidoNave`.
- **VRM & Avatar Automation**: `VRM4U` Python utilities (`VRM4U_ConvBoneToControlUE5.py`, `VRM4U_CreateHumanoidControllerUE5.py`) map VRM humanoid bones to UE 5.8 Control Rig and apply `KawaiiPhysics` for hair/clothing dynamics.

### 3.5 TouchDesigner Real-Time Audio Streamer
- `build_harmonic_audio_streamer.py` constructs a 4-band RMS audio processing CHOP network:
  1. **Sub-Bass (20–100Hz)**: Driving camera shake and low-frequency Niagara pulse.
  2. **Mid-Range (250–2500Hz)**: Driving vocal/instrumental lighting intensity.
  3. **High-Frequency (4k–12kHz)**: Driving particle sparkle and highway note highlights.
  4. **Full Spectrum RMS**: Master audio amplitude envelope.

### 3.6 Web Asset Product Compiler
- `tools/build_asset_products.py` automates production of distribution assets:
  - **Twitch Emote Packs**: 135 PNG files across 15 emote types, 3 resolutions (28x28, 56x56, 112x112), and 3 background modes.
  - **OBS Overlay Packs**: 7 1080p stream templates + individual UI elements.
  - **Wallpaper Packs**: 78 files across 3 mobile phone screen aspect ratios.
  - **Postcards**: 12 300dpi print-ready front designs + 1 canonical back template.

---

## 4. AAA Gacha-Inspired Enterprise Git & Live-Ops Branching Workflow

### 4.1 Atomic Git LFS Asset Locking Configuration

To eliminate unmergeable binary asset conflicts, mandatory asset locking is active at both the workspace root (`.gitattributes`) and project level (`BS_GodFile\.gitattributes`):

```gitattributes
# ====================================================================
# Git LFS & Atomic Binary Asset Locking Configuration
# ====================================================================

# Unreal Engine Binary Content Assets
*.uasset filter=lfs diff=lfs merge=lfs -text lockable
*.umap filter=lfs diff=lfs merge=lfs -text lockable

# DCC 3D Models & Animations
*.blend filter=lfs diff=lfs merge=lfs -text lockable
*.fbx filter=lfs diff=lfs merge=lfs -text lockable
*.obj filter=lfs diff=lfs merge=lfs -text lockable
*.vrm filter=lfs diff=lfs merge=lfs -text lockable
*.usd filter=lfs diff=lfs merge=lfs -text lockable
*.usda filter=lfs diff=lfs merge=lfs -text lockable
*.usdc filter=lfs diff=lfs merge=lfs -text lockable

# High-Resolution Textures & Audio
*.png filter=lfs diff=lfs merge=lfs -text lockable
*.exr filter=lfs diff=lfs merge=lfs -text lockable
*.hdr filter=lfs diff=lfs merge=lfs -text lockable
*.psd filter=lfs diff=lfs merge=lfs -text lockable
*.tga filter=lfs diff=lfs merge=lfs -text lockable
*.wav filter=lfs diff=lfs merge=lfs -text lockable
*.mp3 filter=lfs diff=lfs merge=lfs -text lockable
*.ogg filter=lfs diff=lfs merge=lfs -text lockable
```

#### Asset Locking CLI & Editor Workflow
1. **Locking an Asset**: `git lfs lock BS_GodFile/Content/Melodia/Levels/L_KaleidoNave.umap`
2. **Checking Active Locks**: `git lfs locks`
3. **Unlocking an Asset**: `git lfs unlock BS_GodFile/Content/Melodia/Levels/L_KaleidoNave.umap`
4. **Editor Integration**: Unreal Engine 5.8 Source Control Plugin and Blender pre-save hooks automatically acquire locks when editing binary files.

### 4.2 Runtime Feature-Flag Subsystem Architecture (`UMelodiaFeatureFlagSubsystem`)

The live-ops branching workflow relies on `UMelodiaFeatureFlagSubsystem` (`UGameInstanceSubsystem`) to decouple code deployment from feature activation:

```cpp
// Source/BS_GodFile/MelodiaIntegration/MelodiaFeatureFlagSubsystem.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MelodiaFeatureFlagSubsystem.generated.h"

UCLASS(BlueprintType, Blueprintable)
class BS_GODFILE_API UMelodiaFeatureFlagSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    UFUNCTION(BlueprintCallable, Category = "Melodia|LiveOps")
    bool IsFeatureEnabled(FName FeatureName) const;

    UFUNCTION(BlueprintCallable, Category = "Melodia|LiveOps")
    void SetFeatureOverride(FName FeatureName, bool bEnabled);

private:
    TMap<FName, bool> FeatureFlags;
    void LoadDefaultConfig();
    void ParseCommandLineFlags();
};
```

- **Configuration File**: Defined in `Config/DefaultGame.ini`:
  ```ini
  [/Script/BS_GodFile.MelodiaFeatureFlagSettings]
  bEnableKaleidoNaveExperimental=false
  bEnableMelusinaV7Model=false
  bEnableRhythmHighwayHardMode=true
  ```
- **CLI Overrides**: Override via launch flags: `-FeatureFlag:EnableKaleidoNaveExperimental=true`.

### 4.3 AAA Gacha Live-Ops Branching & Staging Model

```
  main (Trunk) ----------------*-----------------*-----------------> (Always Stable)
                               \                 /
  feature/rhythm-v2 -----------*-- [PR + CI] --*                   (Short-lived PRs)
                                                 \
  release/v1.1 (Week 5 Freeze) -------------------*--- [Staging] ---> Release Tag v1.1.0
                                                       \
  hotfix/v1.1.1 ----------------------------------------*------------> Back-port to main
```

1. **`main` (Trunk)**: Primary development branch. Must remain green at all times. Unfinished features sit behind `UMelodiaFeatureFlagSubsystem` toggles.
2. **6-Week Release Cadence**:
   - **Weeks 1–4**: Parallel feature development via short-lived feature branches (`feature/<name>`).
   - **Week 5**: Code freeze and release branch creation (`release/vX.Y`). Only bug fixes permitted.
   - **Week 6**: Automated headless PIE smoke verification, staging approval, and production tag release (`vX.Y.0`).
3. **Hotfix Protocol**: Emergency fixes branch directly from release tags (`hotfix/vX.Y.Z`) and must be back-merged into `main` immediately upon deployment.
4. **CI/CD Staging Pipeline**: GitHub Actions workflow runs static validation (`tools/validate_assets.py`), C++ compilation, and headless PIE smoke testing on every Pull Request.

### 4.4 Multi-Agent Distributed Handoff & Governance Standards
1. **Workspace Folder Isolation**: All agent metadata, plans, and reports reside strictly within designated `.agents/<agent_name>/` directories. No agent may modify source files inside another agent's workspace.
2. **5-Component Handoff Protocol**: Every agent handoff report must contain:
   - **Section 1: Observation** (Verified facts and file paths)
   - **Section 2: Logic Chain** (Step-by-step reasoning)
   - **Section 3: Caveats** (Scope limits and assumptions)
   - **Section 4: Conclusion** (Actionable output summary)
   - **Section 5: Verification Method** (Independent verification commands)
3. **MCP Tool Safety Halt Rule**: If required MCP tools (`monolith` on port 9316, `it-is-unreal`) are missing from the tool list, agents must halt immediately and notify the user. Writing custom script workarounds to bypass missing MCP servers is strictly prohibited.

---

## 5. Verification Matrix & Action Plan

| Domain | Verification Command / Method | Expected Result | Status |
|:---|:---|:---|:---:|
| **Closed-Editor Build** | Run `BS_GodFile\Build.bat` | 0 Compilation Errors, `UnrealEditor-BS_GodFile.dll` generated | **VERIFIED** |
| **Blueprint Reachability** | `python BS_GodFile/Tools/bp_live_path.py Content/TurnBasedJRPGTemplate/Blueprints/BP_BattleController.uasset` | Returns `REACHABLE` (Exit Code 0) | **VERIFIED** |
| **Git LFS Lock Attributes** | `git check-attr -a -- BS_GodFile/Content/Melodia/Levels/L_KaleidoNave.umap` | Displays `lockable: set`, `filter: lfs` | **VERIFIED** |
| **Monolith Proxy Health** | `curl http://localhost:9316/health` | Returns `{"status":"ok","tools":16}` | **VERIFIED** |
| **Material Crosswalk Math** | Run `python create_tp_melusina.py` | Generates `TP_Melusina` with `LinearColor(0.0351, 0.0263, 0.0528, 1.0)` | **VERIFIED** |
| **Asset Product Compiler** | Run `python tools/build_asset_products.py` | Generates 135 emotes, 7 OBS overlays, 78 wallpapers, 12 postcards | **VERIFIED** |

---

## 6. Deliverables Index & Artifact References

- `C:\EnvironmentPortfolio\PROJECT.md` — Project Master Index, Architecture, Feature Inventory & Milestones
- `C:\EnvironmentPortfolio\MELODIA_ARCHITECTURAL_MASTER_PLAN.md` — Authoritative Architectural Master Plan (This File)
- `C:\EnvironmentPortfolio\.gitattributes` — Workspace Root Git LFS Lock Configuration
- `C:\EnvironmentPortfolio\BS_GodFile\.gitattributes` — Unreal Engine Project Git LFS Lock Configuration
- `C:\EnvironmentPortfolio\.agents\orchestrator\GATE_STATUS.md` — Milestone Gate Verdict Tracker
- `C:\EnvironmentPortfolio\.agents\worker_m1\gameplay_bottlenecks_solution.md` — Milestone 1 Solution Guide
- `C:\EnvironmentPortfolio\.agents\worker_m2\echo_pipeline_architecture.md` — Milestone 2 Echo Pipeline Specification
- `C:\EnvironmentPortfolio\.agents\worker_m3\gacha_git_liveops_workflow.md` — Milestone 3 AAA Gacha Git & Live-Ops Manual
