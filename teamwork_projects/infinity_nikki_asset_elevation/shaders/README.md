# Haute-Couture UE5 Substrate & Material Function Architecture

**Milestone**: M2  
**Target Engine**: Unreal Engine 5.3+ (Substrate / Strata Material Framework)  
**Location**: `teamwork_projects/infinity_nikki_asset_elevation/shaders/`  

---

## 1. Overview

This directory provides the complete shading architecture replicating *Infinity Nikki*'s signature haute-couture materiality. It includes four production-ready Material Functions implemented in physical HLSL and machine-readable UE5 JSON schema descriptors, along with the master multi-slab Substrate material topology.

```
shaders/
├── README.md                              # This deployment & ingestion guide
├── hlsl/
│   ├── ThinFilmIridescence.hlsl           # Airy wave interference & optical path difference
│   ├── DualLobeVelvet.hlsl                # Ashikhmin-Charlie sheen, backscatter, chromatic pile
│   ├── TranslucentOrganzaSSS.hlsl         # RNM twill blending, sheer opacity, dual-sided SSS
│   └── BullionMicroRelief.hlsl            # Dynamic-step POM & contact self-shadowing
├── json/
│   ├── MF_ThinFilm_Iridescence.json       # UE5 Material Function schema descriptor
│   ├── MF_DualLobe_SubstrateVelvet.json   # UE5 Material Function schema descriptor
│   ├── MF_Translucent_OrganzaSSS.json     # UE5 Material Function schema descriptor
│   ├── MF_Bullion_MicroRelief.json        # UE5 Material Function schema descriptor
│   └── M_Master_HauteCouture_Substrate.json # Master Substrate BSDF graph schema descriptor
└── graphs/
    └── SubstrateMasterTopology.md         # Node topology, Slab architecture & dataflow
```

---

## 2. Material Functions Catalog

### 1. `MF_ThinFilm_Iridescence`
- **File**: `hlsl/ThinFilmIridescence.hlsl` / `json/MF_ThinFilm_Iridescence.json`
- **Physical Model**: Multi-stop spectral thin-film optical interference based on Airy equations, Snell's law refraction inside the film medium, optical path difference ($\text{OPD} = 2 n_1 d \cos\theta_1$), boundary reflection phase shifts ($\Delta\phi$), and surface normal curvature thickness modulation.
- **Wavelength Bands**: Evaluated across primary RGB bands ($\lambda_R = 650\text{ nm}, \lambda_G = 532\text{ nm}, \lambda_B = 450\text{ nm}$).
- **Key Inputs**: `FilmThickness_nm` (100–1200 nm), `FilmIOR` (1.45), `SubstrateIOR` (1.55), `CurvatureMask`, `CurvatureIntensity`.
- **Key Outputs**: `IridescenceColor`, `FresnelMultiplier`, `PhaseShift`, `ModulatedRoughness`, `Substrate_F0`.

### 2. `MF_DualLobe_SubstrateVelvet`
- **File**: `hlsl/DualLobeVelvet.hlsl` / `json/MF_DualLobe_SubstrateVelvet.json`
- **Physical Model**: Dual-lobe anisotropic cloth shading combining Ashikhmin-Charlie forward grazing sheen, retro-reflective pile backscatter, and chromatic pile hue shift (simulating selective light penetration into dyed fiber pile).
- **Key Inputs**: `BaseColor`, `RimColor`, `RoughnessCore`, `RoughnessRim`, `RimExponent`, `RimIntensity`, `AnisotropyStrength`, `ChromaticShiftAmount`, `BackscatterIntensity`.
- **Key Outputs**: `CompositeBaseColor`, `SheenColor`, `SheenRoughness`, `AnisotropicTangent`, `AnisotropyAmount`, `RimMask`, `SubstrateClothWeight`.

### 3. `MF_Translucent_OrganzaSSS`
- **File**: `hlsl/TranslucentOrganzaSSS.hlsl` / `json/MF_Translucent_OrganzaSSS.json`
- **Physical Model**: Ethereal sheer fabric optics featuring view-dependent sheer opacity falloff, Reoriented Normal Mapping (RNM) blending for high-frequency $45^\circ$ micro-twill weaves, Beer-Lambert exponential absorption ($\exp(-d \cdot \sigma_a)$), and dual-sided thin-sheet subsurface scattering.
- **Key Inputs**: `BaseColor`, `SubsurfaceColor`, `MacroNormal`, `MicroTwillNormal`, `TwillWeight`, `BaseOpacity`, `AbsorptionDepth`, `SheernessAnglePower`, `DualSidedScattering`.
- **Key Outputs**: `PerturbedNormal`, `TransmittanceColor`, `SubsurfaceScatteringProfile`, `FinalOpacity`, `Thickness`, `SubstrateTranslucentBSDF_Inputs`.

### 4. `MF_Bullion_MicroRelief`
- **File**: `hlsl/BullionMicroRelief.hlsl` / `json/MF_Bullion_MicroRelief.json`
- **Physical Model**: Tangent-space Parallax Occlusion Mapping (POM) with dynamic step count ($\text{lerp}(N_{\text{max}}, N_{\text{min}}, |V_z|)$), secant linear interpolation refinement, directional contact self-shadowing, smoothstep dielectric/conductor boundary masking, and micro-cavity normal gradient derivation.
- **Key Inputs**: `UVs`, `HeightMap`, `HeightScale`, `MinSteps`, `MaxSteps`, `ShadowSteps`, `ShadowHardness`, `BullionMetallic`, `BullionRoughness`, `FabricRoughness`, `HeightThreshold`, `BlendContrast`.
- **Key Outputs**: `DisplacedUV`, `ParallaxHeight`, `SelfShadowAO`, `BullionMask`, `BlendedRoughness`, `BlendedMetallic`, `ContactCavityNormal`.

---

## 3. Engine Ingestion & Setup Guide

### 3.1. Enable Substrate in Unreal Engine 5.3+
To enable the Substrate material framework in your UE5 project:
1. Open `Config/DefaultEngine.ini`.
2. Add or update the following flags under `[/Script/Engine.RendererSettings]`:
   ```ini
   r.Substrate=1
   r.Substrate.BytesPerPixel=96
   r.Substrate.RoughRefraction=1
   ```
3. Restart the Unreal Editor to compile Substrate shaders.

### 3.2. Importing Shaders into UE5
1. **Option A: Python Automation / Editor Utility**:
   Run the project asset ingestion script to convert `json/*.json` definitions into native `.uasset` Material Functions and Master Material in `/Game/Materials/`.
2. **Option B: Manual Custom HLSL Expression Wiring**:
   - Create a new Material Function in UE5 (e.g. `MF_ThinFilm_Iridescence`).
   - Add a `Custom` expression node.
   - Set the `Code` field to the HLSL function call or paste the body from `hlsl/*.hlsl`.
   - Add matching Function Inputs and Outputs as listed in the corresponding `json/*.json` schema.

---

## 4. Master Material PBR Texture Ingestion Contract

All Material Instances derived from `M_Master_HauteCouture_Substrate` ingest the standardized $2048 \times 2048$ POT texture suite:

| Slot | Suffix | Color Space | Compression | Channel Layout | Description |
|---|---|---|---|---|---|
| `Texture_BaseColor` | `_BC` | sRGB | BC7 | RGB (8/16-bit) | Watercolor dye & bullion base |
| `Texture_Normal` | `_N` | Linear | BC5 (Normalmap) | R=$+X$, G=$-Y$, B=Derived | DirectX tangent space normal |
| `Texture_ORM` | `_ORM` | Linear | BC7 / Linear | R=AO, G=Roughness, B=Metallic | Packed linear PBR masks |
| `Texture_Height` | `_H` | Linear | Float16 / Grayscale | R = Elevation $[0.0, 1.0]$ | 16-bit displacement relief |
| `Texture_Sheen` | `_Sheen` | Linear | BC7 / Linear | R = Sheen intensity / rim | Microfiber fuzz mask |
| `Texture_Alpha` | `_Alpha` | Linear | Grayscale | R = Physical fabric coverage | Cutout or sheer opacity |

---

## 5. Material Parameter Tweaking Reference

### Iridescent Silk / Crystal Preset:
- `bEnableThinFilm` = `True`
- `FilmThickness_nm` = `380.0` (Vibrant magenta/cyan interference)
- `FilmIOR` = `1.45`
- `SubstrateIOR` = `1.55`
- `CurvatureIntensity` = `0.80`

### Royal Velvet Preset:
- `bEnableVelvetSheen` = `True`
- `RoughnessCore` = `0.85`
- `RoughnessRim` = `0.25`
- `RimExponent` = `3.5`
- `RimIntensity` = `2.0`
- `ChromaticShiftAmount` = `0.70`
- `BackscatterIntensity` = `0.50`

### Ethereal Organza Ruffles Preset:
- `bEnableOrganzaSSS` = `True`
- `BaseOpacity` = `0.35`
- `SheernessAnglePower` = `2.2`
- `AbsorptionDepth` = `2.5`
- `TwillWeight` = `0.45`
- `DualSidedScattering` = `0.85`

### 24k Imperial Gold Bullion Preset:
- `bEnableParallaxRelief` = `True`
- `HeightScale` = `0.045`
- `MinSteps` = `10.0`
- `MaxSteps` = `36.0`
- `ShadowSteps` = `8.0`
- `ShadowHardness` = `4.5`
- `BullionMetallic` = `1.0`
- `BullionRoughness` = `0.20`
- `HeightThreshold` = `0.35`
