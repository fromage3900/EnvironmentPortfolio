# Project: Infinity Nikki Haute-Couture Asset Elevation Ecosystem

## Architecture
This project delivers a studio-grade procedural generation and shading pipeline for Infinity Nikki (无限暖暖) haute-couture assets. It integrates Houdini SOP/VEX 3D micro-geometry synthesis, headless high-to-low PBR map extraction, advanced Unreal Engine 5 Substrate Material Functions, 4 complete $2048 \times 2048$ POT PBR material suites, a multi-tier automated test harness, and an interactive WebGL lookdev sandbox dashboard.

```
┌─────────────────────────────────────────────────────────────┐
│                 1. HOUDINI: GEOMETRY & SIMULATION           │
│  - SOP Chantilly Lace & Micro-Beading Lattice               │
│  - SOP Differential Line Growth Organza Petals              │
│  - SOP Baroque Bullion Acanthus Embroidery                  │
│  - SOP Reaction-Diffusion Cloisons / Micro-Filigree         │
│  - High-to-Low Baker -> 16-bit Height / DirectX Normal / AO │
└──────────────────────────────┬──────────────────────────────┘
                               │ (16-bit Height & Tangent Normals)
┌──────────────────────────────▼──────────────────────────────┐
│           2. PROCEDURAL PBR MATERIAL SUITES (2048x2048)     │
│  - Suite 1: Chantilly Lace & Pearl Beading (Pearl/Pink/Blue)│
│  - Suite 2: Differential Organza Petals (Hydrangea/Lilac)   │
│  - Suite 3: Baroque Bullion Acanthus (24k Gold/Rose Gold)   │
│  - Suite 4: Reaction-Diffusion Cloisonné (Amethyst/Turquoise│
│  - Maps: _BC, _N, _ORM, _H, _AO, _R, _M, _Sheen, _Alpha     │
└──────────────────────────────┬──────────────────────────────┘
                               │ (PBR Texture Maps)
┌──────────────────────────────▼──────────────────────────────┐
│            3. UNREAL ENGINE 5: SUBSTRATE ARCHITECTURE       │
│  - MF_ThinFilm_Iridescence (Multi-stop Airy interference)   │
│  - MF_DualLobe_SubstrateVelvet (Dual-lobe anisotropic fuzz) │
│  - MF_Translucent_OrganzaSSS (Angle opacity & dual-sided SSS│
│  - MF_Bullion_MicroRelief (Parallax occlusion & relief)     │
│  - Master Material M_Master_HauteCouture_Substrate          │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│            4. QA & LOOKDEV VERIFICATION HARNESS             │
│  - Multi-tier Pytest/Unittest Suite (Tiers 0-6)             │
│  - Interactive WebGL Lookdev Sandbox Dashboard              │
└─────────────────────────────────────────────────────────────┘
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | Chantilly Lace & Beading SOP | Woven floral Voronoi/Delaunay lattice with pearl/crystal seed bead scatter | M1 | ORIGINAL_REQUEST §R1 |
| F2 | Differential Growth Organza SOP | Organic multi-frequency ruffle petal meshes with 3D tangent flow normals | M1 | ORIGINAL_REQUEST §R1 |
| F3 | Baroque Bullion Embroidery SOP | Polar logarithmic acanthus curves and braided gold thread coils | M1 | ORIGINAL_REQUEST §R1 |
| F4 | Reaction-Diffusion Cloisons SOP | Gray-Scott PDE filigree and cloisonné vitreous enamel cell ridges | M1 | ORIGINAL_REQUEST §R1 |
| F5 | High-to-Low Extraction Baker | 16-bit displacement height, DirectX normals (Green=-Y), curvature, AO | M1 | ORIGINAL_REQUEST §R1 |
| F6 | MF_ThinFilm_Iridescence | Multi-stop spectral thin-film optical interference shader function | M2 | ORIGINAL_REQUEST §R2 |
| F7 | MF_DualLobe_SubstrateVelvet | Dual-lobe anisotropic velvet/fuzz shading with chromatic pile shift | M2 | ORIGINAL_REQUEST §R2 |
| F8 | MF_Translucent_OrganzaSSS | Sheer fabric opacity, micro-twill normal blending, dual-sided SSS | M2 | ORIGINAL_REQUEST §R2 |
| F9 | MF_Bullion_MicroRelief | Metallic embroidery parallax occlusion mapping and contact occlusion | M2 | ORIGINAL_REQUEST §R2 |
| F10 | Master Substrate Material Graph | Full Substrate BSDF Slab wiring & BaseColor/Normal/Linear ORM binding | M2 | ORIGINAL_REQUEST §R2 |
| F11 | PBR Suite 1: Chantilly Lace | 9 maps at 2048x2048 POT (Pearl White, Blush Pink, Crystal Sheen) | M3 | ORIGINAL_REQUEST §R3 |
| F12 | PBR Suite 2: Differential Organza | 9 maps at 2048x2048 POT (Hydrangea Blue, Wisteria Lilac, Gossamer) | M3 | ORIGINAL_REQUEST §R3 |
| F13 | PBR Suite 3: Baroque Bullion | 9 maps at 2048x2048 POT (24k Imperial Gold, Rose Gold, Royal Blue) | M3 | ORIGINAL_REQUEST §R3 |
| F14 | PBR Suite 4: Reaction-Diffusion | 9 maps at 2048x2048 POT (Amethyst Purple, Opaline Turquoise, Gold) | M3 | ORIGINAL_REQUEST §R3 |
| F15 | Automated Verification Test Suite | 7-tier automated test harness validating 100% texture files & contracts | M_TEST / M4 | ORIGINAL_REQUEST §R4 |
| F16 | Interactive Lookdev Sandbox | Standalone HTML/JS/CSS WebGL lookdev dashboard with channel switching | M4 | ORIGINAL_REQUEST §R4 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M_TEST | E2E Test Suite Creation | Authored multi-tier test harness and published `TEST_READY.md` | none | DONE |
| M1 | Houdini Procedural Synthesizers & Baker | Houdini SOP/VEX scripts, standalone Python generators & High-to-Low Baker | none | DONE |
| M2 | UE5 Substrate & Material Functions | 4 Material Functions, Master Substrate Material, HLSL & JSON specs | none | DONE |
| M3 | Haute-Couture PBR Material Suites | 4 suites (36 maps, 2048x2048 POT) in `textures/` | M1 | DONE |
| M4 | Lookdev Sandbox Dashboard | Interactive HTML/JS WebGL dashboard with embedded previews & channel isolation | M3 | DONE |
| M5 | Final Milestone: Full E2E & Adversarial Pass | Pass 100% test suite, run Challenger stress tests and Forensic Audit | M_TEST, M1, M2, M3, M4 | IN_PROGRESS |

## Interface Contracts

### 1. Houdini Generator & Baker CLI Interface
- `python generators/generate_all.py --res 2048 --out textures/ --geo models/`
- Output maps per suite:
  * `T_HauteCouture_<Archetype>_BC.png` (sRGB 8-bit, 2048x2048)
  * `T_HauteCouture_<Archetype>_N.png` (DirectX Green=-Y, Unit Normalized, 2048x2048)
  * `T_HauteCouture_<Archetype>_ORM.png` (Linear 8-bit RGB: R=AO, G=Roughness, B=Metallic, 2048x2048)
  * `T_HauteCouture_<Archetype>_H.png` (Linear 16-bit Grayscale, 2048x2048)
  * `T_HauteCouture_<Archetype>_AO.png` (Linear 8-bit Grayscale, 2048x2048)
  * `T_HauteCouture_<Archetype>_R.png` (Linear 8-bit Grayscale, 2048x2048)
  * `T_HauteCouture_<Archetype>_M.png` (Linear 8-bit Grayscale, 2048x2048)
  * `T_HauteCouture_<Archetype>_Sheen.png` (Linear 8-bit Grayscale / RGB, 2048x2048)
  * `T_HauteCouture_<Archetype>_Alpha.png` (Linear 8-bit Grayscale, 2048x2048)

### 2. UE5 Substrate Material Function Contracts
- JSON schemas located in `shaders/json/`
- HLSL implementations located in `shaders/hlsl/`
- Node graph definitions located in `shaders/graphs/`
- Primary functions:
  * `MF_ThinFilm_Iridescence.json` (Inputs: ViewDir, Normal, Curvature, FilmThicknessNM, FilmIOR, SubstrateIOR; Output: IridescenceColor)
  * `MF_DualLobe_SubstrateVelvet.json` (Inputs: BaseColor, Normal, AnisotropyDir, SheenRoughness, PileShiftColor; Output: SheenBSDF, VelvetAlbedo)
  * `MF_Translucent_OrganzaSSS.json` (Inputs: BaseColor, Normal, MicroTwillNormal, Thickness, SSSColor, MFP; Output: TranslucentBSDF, Opacity)
  * `MF_Bullion_MicroRelief.json` (Inputs: UV, ViewDirTS, HeightMap, ParallaxScale, Steps; Output: OffsetUV, ContactOcclusion)

### 3. Automated Test Verification Contract
- Command: `python -m unittest tests/test_haute_couture_pbr_verification.py`
- Exit Code: `0`
- Zero tolerance for dimensional, mathematical, or channel discrepancies.

## Code Layout
```
teamwork_projects/infinity_nikki_asset_elevation/
├── PROJECT.md
├── TEST_INFRA.md
├── TEST_READY.md
├── DEAD_ENDS.md
├── generators/
│   ├── __init__.py
│   ├── base_synthesizer.py
│   ├── high_to_low_baker.py
│   ├── chantilly_lace_synthesizer.py
│   ├── differential_organza_synthesizer.py
│   ├── baroque_bullion_synthesizer.py
│   ├── reaction_diffusion_synthesizer.py
│   ├── houdini_hython_runner.py
│   └── generate_all.py
├── shaders/
│   ├── README.md
│   ├── hlsl/
│   │   ├── ThinFilmIridescence.hlsl
│   │   ├── DualLobeVelvet.hlsl
│   │   ├── TranslucentOrganzaSSS.hlsl
│   │   └── BullionMicroRelief.hlsl
│   ├── json/
│   │   ├── MF_ThinFilm_Iridescence.json
│   │   ├── MF_DualLobe_SubstrateVelvet.json
│   │   ├── MF_Translucent_OrganzaSSS.json
│   │   ├── MF_Bullion_MicroRelief.json
│   │   └── M_Master_HauteCouture_Substrate.json
│   └── graphs/
│       └── SubstrateMasterTopology.md
├── textures/
│   ├── T_HauteCouture_ChantillyLace_PearlBeading_*.png
│   ├── T_HauteCouture_DifferentialOrganza_Petals_*.png
│   ├── T_HauteCouture_BaroqueBullion_Acanthus_*.png
│   └── T_HauteCouture_ReactionDiffusion_Cloisonne_*.png
├── tests/
│   ├── __init__.py
│   ├── test_haute_couture_pbr_verification.py
│   └── test_ue5_shader_specifications.py
└── lookdev_sandbox.html
```
