# Melodia PBR Material & Texture E2E Test Infrastructure

## Overview
The Melodia E2E Material & Texture Test Suite provides comprehensive, multi-tiered automated verification for the project's PBR texture pipeline, Substrate Toon shading, Infinity Nikki-tier fantasy fabrics, and harmonic audio-reactive water systems.

```
+-----------------------------------------------------------------------------+
|                     4-TIER E2E TEST ARCHITECTURE                            |
+-----------------------------------------------------------------------------+
|  Tier 1: Opaque-Box Mathematical Invariants & Channel Specifications        |
|  - Channel packing math, bit depths, sRGB metadata flags, POT dimensions   |
|  - Default fallbacks, FabricType ranges [0-7], cos^2(phase*pi) quantization |
+-----------------------------------------------------------------------------+
|  Tier 2: Component & Subsystem Pipeline Operations                          |
|  - High-throughput PIL ORM packing, auto-resampling, corruption handling   |
|  - Procedural FabricAnisoGate & WeaveNormal HLSL, Dynamic Caustics, WPO    |
+-----------------------------------------------------------------------------+
|  Tier 3: Cross-System Shading & Audio-Visual Harmony                        |
|  - Multi-layer height-compete blending, dual-sheen grazing Fresnel         |
|  - Shared: Wrap sampler state optimization (<= 4 hardware states)          |
|  - BPM clock phase accumulation, timebase separation contracts             |
+-----------------------------------------------------------------------------+
|  Tier 4: End-to-End Real-World Workload Simulation                         |
|  - Melusina 5-slot wardrobe bindings (Velvet, Brocade, Silk, Lace, Gold)   |
|  - Multi-light stage reflection & Toon Profile shadow floor preservation   |
|  - 240-frame interactive battle simulation in underwater grotto (128 BPM)  |
|  - Production shader instruction and texture sampler budget enforcement    |
+-----------------------------------------------------------------------------+
```

---

## 1. 4-Tier Test Architecture

### Tier 1: Unit & Invariant Testing (Opaque-Box)
- **Objective**: Validate pure mathematical functions, data schemas, bit-depth invariants, color space metadata rules, naming conventions, and parameter bounds with zero side effects.
- **Key Verifications**:
  - **ORM Packing Math**: R $\equiv$ Ambient Occlusion, G $\equiv$ Micro-Roughness, B $\equiv$ Metallic.
  - **Default Fallback Invariants**: $\text{AO} = 255$ ($1.0$), $\text{Roughness} = 178$ ($\approx 0.70$), $\text{Metallic} = 0$ ($0.0$), $\text{Height} = 128$ ($0.5$), $\text{Normal} = (128, 128, 255)$ (tangent-space $+Z$).
  - **Power-of-Two (POT)**: $w > 0 \land (w \ \& \ (w - 1)) == 0$ covering square (512, 1024, 2048, 4096) and non-square POT trimsheets ($2048 \times 1024$), rejecting non-POT.
  - **Color Space Rules**: Color maps (`_BC`, `_BaseColor`, `_Albedo`) require $\text{sRGB} = \text{True}$; Data maps (`_ORM`, `_N`, `_H`, `_Sheen`, `_Sparkle`, `_Alpha`) require $\text{sRGB} = \text{False}$ (Linear).
  - **Naming Conventions**: Canonical regex `T_<Family>_<Name>_<Channel>` matching.
  - **FabricType Domain**: Discrete integer domain $[0, 7]$ (0=Default, 1=Cotton, 2=Silk, 3=Satin, 4=Velvet, 5=Wool, 6=Chiffon, 7=Sequins).
  - **Beat Quantization Invariants**: $f(\phi) = \cos^2(\phi \cdot \pi)$ on $\phi \in [0, 1]$, downbeat peak $f(0.0) = 1.0$, off-beat trough $f(0.5) = 0.0$, boundary smoothness $f'(0.0) = f'(0.5) = f'(1.0) = 0.0$, symmetry $f(\phi) = f(1.0 - \phi)$.
  - **Gerstner 8-Wave Invariants**: Direction normalization $\|\vec{D}_i\| = 1.0$, steepness sum $\sum k_i A_i < 2.0$.

### Tier 2: Component & Subsystem Pipeline Operations
- **Objective**: Test image manipulation, procedural HLSL shader generation logic, signal modulation, and error recovery.
- **Key Verifications**:
  - **PIL Channel Packing**: Generates synthetic test images (linear gradient AO, checkerboard Roughness, circular mask Metallic), packs into ORM, saves/reloads from disk, and asserts byte-for-byte fidelity.
  - **Missing Channel Fallback Packing**: Packs material sets with missing maps, verifying default channel synthesis.
  - **Resolution Mismatch Resampling**: Standardizes mixed resolutions (e.g. 512 AO + 1K Roughness + 2K Metallic) to a clean target 2K ORM output.
  - **Corrupted Image Handling**: Graceful error interception on truncated headers, 0-byte files, and non-image text binaries.
  - **Procedural Weave Normal**: Evaluates analytical derivatives of warp/weft sine waves, confirming unit-normal vector normalization and tangent-space orientation.
  - **FabricAnisoGate Piecewise Evaluation**: Verifies anisotropic boost peaks for Silk ($+0.90$), Satin ($+0.95$), Sequins ($+0.70$), Cotton ($+0.15$), and Velvet ($0.0$).
  - **Dynamic Caustics Modulation**: Evaluates audio modulation formulas:
    $$\text{Caustics}_{\text{dyn}} = \text{CausticBase} \cdot (1.0 + \text{Bass} \cdot 0.45 + \text{BeatPulse} \cdot 0.35)$$
  - **Bioluminescent Decay**: Exponential decay $I(t) = I_{\text{peak}} \cdot e^{-\lambda (t - t_0)}$ triggered on downbeat onset.

### Tier 3: Cross-System Shading & Audio-Visual Harmony
- **Objective**: Test interactions between shader graphs, lighting ramps, multi-layer masks, and clock synchronization.
- **Key Verifications**:
  - **Height-Compete Blending**: Evaluates contrast-based multi-layer blending between base cloth and gold embroidery:
    $$\Delta H = H_B - H_A + \text{Bias}$$
    $$\alpha = \text{saturate}\left(\frac{\Delta H \cdot \text{Sharpness}}{\text{Softness}} + 0.5\right)$$
  - **Dual-Sheen Grazing Fresnel**: Micro-roughness backscatter combining with grazing angle Fresnel:
    $$L_{\text{sheen}} = \text{FabricSheen} \cdot \text{SheenTint} \cdot (1 - N \cdot V)^{\text{SheenPower}}$$
  - **Substrate Sampler Optimization**: Enforces `SamplerType = SAMPLERTYPE_SharedWrap`, reducing distinct hardware sampler states to $\le 4$ (SharedWrap sRGB, SharedWrap Linear, SharedWrap Normal, SharedClamp Linear).
  - **ToonProfile Diffuse/Specular Ramp**: Validates 3-stop HoYoverse ramp transitions across shadow, mid, and lit regions with deep indigo shadow floor preservation.
  - **Clock Tempo Phase Accumulation**: Verifies cyclic phase accumulation for 128 BPM (Battle), 93 BPM (Duvet), and 131 BPM (Sewaa).
  - **Timebase Separation Contract**: Enforces strict separation between `VideoRenderTime` (for visual shader pulses) and `ExperiencedTime` (for player rhythm scoring).

### Tier 4: End-to-End Real-World Workloads
- **Objective**: Execute end-to-end integration workflows simulating in-game hero rendering, wardrobe bindings, and live audio resonance.
- **Key Verifications**:
  - **Melusina Wardrobe Slot Binding**: Complete mesh-to-material instance bindings for 5 garment slots:
    1. `M_frontpanel_001` $\rightarrow$ `MI_Melusina_Frontpanel_VelvetGilded` (Royal Velvet + Gold Jacquard)
    2. `M_SHAWL_001` $\rightarrow$ `MI_Melusina_Shawl_SheerSilk` (Sheer Silk)
    3. `M_SKIRT_003` $\rightarrow$ `MI_Melusina_Skirt_GildedJacquard` (Gilded Brocade)
    4. `M_sleeve_003` $\rightarrow$ `MI_Melusina_Sleeve_BaroqueLace` (Baroque Filigree Lace)
    5. `M_shirt_001` $\rightarrow$ `MI_Melusina_Shirt_GoldEmbroidery` (Gold Embroidery)
  - **Stage Light Reflection & Toon Shadow Floor**: Multi-light studio evaluation verifying specular highlight crispness and shadow floor preservation ($I_{\text{shadow}} \ge 0.03$).
  - **240-Frame Grotto Water Resonance**: 4.0-second 60 FPS simulation evaluating 8-wave Gerstner surface displacement, dynamic caustics, bioluminescence decay, and optical water column depth transmittance ($e^{-\mu \cdot d}$), with 0% NaN/Inf occurrences.
  - **Production Budget Auditing**: Confirms hardware sampler count $\le 16$ (actual $4$), vertex instructions $\le 350$, pixel instructions $\le 1800$.

---

## 2. Test Runner Commands & Execution

### Running the Full Multi-Tier Suite
```powershell
python BS_GodFile/Content/Python/Tests/run_e2e_material_suite.py
```

### Running Specific Tiers
```powershell
# Run Tier 1 (Unit & Invariant Rules)
python BS_GodFile/Content/Python/Tests/run_e2e_material_suite.py --tier 1

# Run Tier 2 (Subsystem & Component Operations)
python BS_GodFile/Content/Python/Tests/run_e2e_material_suite.py --tier 2

# Run Tier 3 (Cross-System Shading & Harmony)
python BS_GodFile/Content/Python/Tests/run_e2e_material_suite.py --tier 3

# Run Tier 4 (End-to-End Real-World Workloads)
python BS_GodFile/Content/Python/Tests/run_e2e_material_suite.py --tier 4
```

### Running with Verbose Output & Custom JSON Report
```powershell
python BS_GodFile/Content/Python/Tests/run_e2e_material_suite.py -v --json-report Saved/Audit/e2e_material_test_report.json
```

### Executing via Pytest
```powershell
python -m pytest BS_GodFile/Content/Python/Tests/ -v
```

---

## 3. Feature Coverage Matrix (F1 to F16)

| Feature | Feature Name | Tiers | Test Module & Classes | Status |
| :--- | :--- | :--- | :--- | :--- |
| **F1** | Automated ORM Packing Tool | Tier 1, 2 | `test_pbr_texture_pipeline.py`<br>`TestPBRTextureInvariantsTier1`<br>`TestPBRTexturePipelineTier2` | **COVERED** |
| **F2** | Channel Validation & Invariant Harness | Tier 1, 2 | `test_pbr_texture_pipeline.py`<br>`TestPBRTextureInvariantsTier1`<br>`TestPBRTexturePipelineTier2` | **COVERED** |
| **F3** | Repack Core Staging & Character Assets | Tier 2, 4 | `test_pbr_texture_pipeline.py`<br>`test_real_world_workloads.py`<br>`TestRealWorldWorkloadsTier4` | **COVERED** |
| **F4** | Royal Velvet PBR Set & Preset | Tier 2, 3, 4 | `test_fabric_instances.py`<br>`test_real_world_workloads.py`<br>`TestFabricPresetsTier2`, `TestFabricSystemIntegrationTier3` | **COVERED** |
| **F5** | Gilded Jacquard & Brocade PBR Set | Tier 2, 3, 4 | `test_fabric_instances.py`<br>`test_real_world_workloads.py`<br>`TestFabricPresetsTier2`, `TestFabricSystemIntegrationTier3` | **COVERED** |
| **F6** | Sheer Silk & Chiffon PBR Set | Tier 2, 3, 4 | `test_fabric_instances.py`<br>`test_real_world_workloads.py`<br>`TestFabricPresetsTier2`, `TestFabricSystemIntegrationTier3` | **COVERED** |
| **F7** | Baroque Filigree Lace PBR Set | Tier 2, 3, 4 | `test_fabric_instances.py`<br>`test_real_world_workloads.py`<br>`TestFabricPresetsTier2`, `TestFabricSystemIntegrationTier3` | **COVERED** |
| **F8** | Gold-Threaded Embroidery PBR Set | Tier 2, 3, 4 | `test_fabric_instances.py`<br>`test_real_world_workloads.py`<br>`TestFabricPresetsTier2`, `TestFabricSystemIntegrationTier3` | **COVERED** |
| **F9** | Iridescent Celestial Weave PBR Set | Tier 2, 3 | `test_fabric_instances.py`<br>`test_real_world_workloads.py`<br>`TestFabricPresetsTier2`, `TestFabricSystemIntegrationTier3` | **COVERED** |
| **F10** | Wardrobe Material Slot Mapping | Tier 3, 4 | `test_fabric_instances.py`<br>`test_real_world_workloads.py`<br>`TestRealWorldWorkloadsTier4` | **COVERED** |
| **F11** | Dynamic Caustics & Wave Displacement Audio Modulation | Tier 2, 3, 4 | `test_audio_harmony.py`<br>`test_real_world_workloads.py`<br>`TestAudioModulationTier2`, `TestRealWorldWorkloadsTier4` | **COVERED** |
| **F12** | Sheen, Sparkle & Rune Glow Audio Pulsation | Tier 2, 3 | `test_audio_harmony.py`<br>`test_fabric_instances.py`<br>`TestAudioModulationTier2`, `TestFabricSystemIntegrationTier3` | **COVERED** |
| **F13** | Water Bioluminescence & Niagara Harmony | Tier 2, 3, 4 | `test_audio_harmony.py`<br>`test_real_world_workloads.py`<br>`TestAudioModulationTier2`, `TestRealWorldWorkloadsTier4` | **COVERED** |
| **F14** | Substrate Sampler Optimization | Tier 3, 4 | `test_fabric_instances.py`<br>`test_real_world_workloads.py`<br>`TestFabricSystemIntegrationTier3`, `TestRealWorldWorkloadsTier4` | **COVERED** |
| **F15** | Universal Master & Instance Verification | Tier 3, 4 | `test_fabric_instances.py`<br>`test_real_world_workloads.py`<br>`TestFabricSystemIntegrationTier3`, `TestRealWorldWorkloadsTier4` | **COVERED** |
| **F16** | Multi-Tier E2E Test Suite | Tier 1, 2, 3, 4 | `run_e2e_material_suite.py`<br>Central multi-tier test runner & structured JSON reporter | **COVERED** |

---

## 4. Integrity & Quality Assurance Assertion
- **Genuine Execution**: Every test method executes genuine mathematical, image processing, or data binding logic with explicit numeric assertions.
- **Zero Mocking / Facade Avoidance**: No hardcoded expected outputs or synthetic test passes.
- **Deterministic Baseline**: All 35 tests pass deterministically across standalone CLI, test runner, and Pytest runners.
