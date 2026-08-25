# Melodia — Mobile iOS Phone Pipeline & AI Workflow Integration Specification

**Created:** 2026-08-11  
**Status:** Approved & Canonical  
**Target Platform:** iOS (Metal 3.1 / Apple Silicon A15+ & M-Series)  
**Engine Baseline:** Unreal Engine 5.8 (Substrate Mobile / Forward+ / Metal Shading Language 3)  
**Primary Repository Working Directory:** `C:\EnvironmentPortfolio`

---

## 1. Executive Summary & Architectural Scope

This specification establishes the **Mobile iOS Phone Pipeline** and **AI Workflow Integration Architecture** for Melodia. It details metal-shader optimizations, mobile render settings, touch/haptic input context stacks, mobile-optimized UI/UX layouts, and local/cloud AI workflow bridges (On-Device Neural Engine ML + Remote Multi-Agent Bridge) tailored for iOS deployment.

---

## 2. 📱 Mobile iOS Phone Pipeline Architecture

### 2.1 Target Specs & iOS Engine Configuration

| Property | Value / Target | Notes |
|---|---|---|
| **Minimum Device Target** | iPhone 13 / A15 Bionic (4GB RAM) | 30 FPS Target Baseline |
| **Recommended Device** | iPhone 15 Pro / A17 Pro (8GB RAM) | 60 FPS Dynamic Scale Target |
| **Graphics API** | Metal 3.1 (Metal Shading Language 3.0) | Forward+ Clustered Renderer |
| **Shader Model** | Mobile Substrate / Deferred-Lite | Custom Toon Shading Forward Pass |
| **Memory Budget (iOS)** | 2.8 GB Maximum Active Heap | Enforced via `FApplePlatformMemory` |
| **Texture Format** | ASTC 6x6 / 4x4 (HDR Color) | Automatic Crunch Compression |

### 2.2 iOS `DefaultEngine.ini` Mobile Configuration Profile

```ini
[/Script/IOSRuntimeSettings.IOSRuntimeSettings]
MinimumiOSVersion=IOS_16
bEnableMetal=True
bEnableMetalV2=True
bSupportsMetalMRT=True
+CustomSupportedComponentTypes=Metal3
bGeneratedMetalCode=True
bBuildForArm64=True
bUseRSIC=True

[/Script/Engine.RendererSettings]
r.Mobile.Forward.EnableClusteredReflections=1
r.Mobile.Forward.EnableLocalLights=1
r.Mobile.DisableVertexFog=1
r.Mobile.AntiAliasing=3 ; TemporalAA / Metal FX Spatial Scaling
r.Metal.EnableCustomPrepass=1
r.Mobile.TonemapperFilm=1
r.MobileContentScaleFactor=2.0 ; Native Retina Scaling
```

### 2.3 iOS Input Context & Tactile Haptic System (`UMelodiaIOSInputSubsystem`)

To maintain parity with the PC `UMelodiaInputContextSubsystem`, iOS relies on `CoreHaptics` and dynamic multi-touch gestures:

```cpp
// Source/BS_GodFile/MelodiaIntegration/MelodiaIOSInputSubsystem.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MelodiaIOSInputSubsystem.generated.h"

UENUM(BlueprintType)
enum class EMelodiaHapticFeedbackPattern : uint8
{
    LightTap,
    MediumImpact,
    RhythmBeatHit,
    PerfectSkillBurst,
    FailureWarning
};

UCLASS(BlueprintType, Blueprintable)
class BS_GODFILE_API UMelodiaIOSInputSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Melodia|iOS|Haptics")
    void TriggerCoreHapticFeedback(EMelodiaHapticFeedbackPattern Pattern);

    UFUNCTION(BlueprintCallable, Category = "Melodia|iOS|Touch")
    void SetMobileVirtualJoystickVisible(bool bVisible);

    UFUNCTION(BlueprintCallable, Category = "Melodia|iOS|Touch")
    void PushMobileTouchContext(FName ContextName);
};
```

---

## 3. 🤖 AI Workflow Integration Architecture

```
                      +----------------------------------+
                      |  Melodia iOS Local/Remote AI Hub |
                      +----------------------------------+
                                       |
                +----------------------+----------------------+
                |                                             |
   (Local On-Device CoreML / NPU)              (Remote Multi-Agent MCP Bridge)
                |                                             |
   +------------v------------+                   +------------v------------+
   | Apple Neural Engine ML  |                   | Monolith / Ollama API   |
   | (Local Voice / Gesture) |                   | (Port 9316 / Port 11434)|
   +------------+------------+                   +------------+------------+
                |                                             |
                +----------------------+----------------------+
                                       |
                         +-------------v-------------+
                         | Narrative & Live-Ops Loop |
                         | (QuillScript Interpreter) |
                         +---------------------------+
```

### 3.1 Dual-Tier AI Topology (On-Device + Cloud Bridge)

1. **Tier 1: On-Device AI (Apple CoreML / Neural Engine)**
   - **Local Speech Recognition (SFSpeechRecognizer)**: Zero-latency voice command parsing for combat skill triggers ("Cadence Strike!", "Petal Refrain").
   - **Local Sentiment Inference**: Neural Engine execution of small GGUF/CoreML models (e.g. MobileBERT / Llama-3-8B-Instruct via `MelodiaOllamaValidation.h`).

2. **Tier 2: Remote Multi-Agent Bridge (Monolith & Ollama MCP)**
   - **Monolith MCP Bridge (`http://localhost:9316/mcp`)**: Remote agent tool execution for content updates, dynamic level streaming requests, and asset variant downloads.
   - **Ollama LLM Orchestration (`http://localhost:11434/api/generate`)**: Real-time narrative NPC dialogue synthesis passing QuillScript state arrays.

### 3.2 Ollama C++ Validation Subsystem (`UMelodiaOllamaValidation`)

```cpp
// Source/BS_GodFile/MelodiaIntegration/MelodiaOllamaValidation.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "MelodiaOllamaValidation.generated.h"

DECLARE_DYNAMIC_DELEGATE_TwoParams(FOnOllamaResponseReceived, bool, bSuccess, const FString&, ResponseText);

UCLASS(BlueprintType)
class BS_GODFILE_API UMelodiaOllamaValidation : public UEngineSubsystem
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Melodia|AI|Ollama")
    void QueryOllamaModel(const FString& ModelName, const FString& Prompt, FOnOllamaResponseReceived OnComplete);
};
```

---

## 4. 📐 Mobile UI/UX & Dynamic Aspect Ratio Specs

### 4.1 Safe Area Insets & Notch Avoidance (`WBP_MelodiaMobileHUD`)

- **Safe Area Anchors**: All HUD widgets (`BP_BattleUI`, `WBP_MelodiaRhythmHighway`, `QuillScript` dialogue boxes) must anchor to `Safe Zone` containers using Unreal Engine `USafeZone` widgets to avoid iPhone Dynamic Island / Notch cutouts.
- **Aspect Ratio Matrix**:
  - **19.5:9 (iPhone 13 / 14 / 15 / 16)**: Standard dynamic scaling.
  - **4:3 (iPad Pro / Air)**: Expanded viewport with side-fill UI borders.

---

## 5. 🛠️ Mobile Build & Packaging Checklist

- [ ] **Provisioning Profile**: Valid Apple Developer Signing Certificate + iOS Game Provisioning Profile.
- [ ] **Packaging Target**: `Development` / `Shipping` build configuration targeting `IOS`.
- [ ] **Metal Shader Precompilation**: Run `r.Metal.PrecompileShaders=1` during build pass to prevent runtime shader stutter.
- [ ] **Remote AI Fallback**: Verify `UMelodiaOllamaValidation` gracefully handles missing network connections by reverting to local authored QuillScript dialogue buffers.

---
*Document Location: [`Docs/MOBILE_IOS_PIPELINE_AND_AI_WORKFLOWS_2026-08-11.md`](file:///C:/EnvironmentPortfolio/Docs/MOBILE_IOS_PIPELINE_AND_AI_WORKFLOWS_2026-08-11.md)*
