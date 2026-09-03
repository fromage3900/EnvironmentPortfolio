# Project: Surreal Mathematical PBR Texture Suites

## Architecture
- **Mathematical Generator Core** (`generators/`):
  - `hyperbolic_generator.py`: Poincaré disk/half-plane hyperbolic tiling engine implementing Mobius transformations, non-Euclidean geodesics, and triangular Coxeter group reflections $\{p, q\}$.
  - `hopf_generator.py`: 4D Hopf fibration projection ($S^3 \rightarrow S^2$) and 4D hypersphere Clifford torus slicing with dimensional intersection interference.
  - `chladni_generator.py`: 2D modal standing wave simulator solving $\cos(n\pi x/L)\cos(m\pi y/L) - \cos(m\pi x/L)\cos(n\pi y/L) = 0$ with multi-frequency acoustic superposition.
  - `pbr_engine.py`: Haute-couture colorist, micro-elevation/heightfield derivation, DirectX tangent normal generation with Green=-Y vector normalization ($\sqrt{n_x^2+n_y^2+n_z^2}\approx 1.0$), and ORM channel packing (R=AO, G=Roughness, B=Metallic).
- **Baked Texture Output Directory** (`textures/`):
  - `textures/T_Hyperbolic_PoincareTriangular/`: Suite 1 (Poincaré Disk Hyperbolic Triangular {7,3})
  - `textures/T_Hyperbolic_HalfPlaneEscher/`: Suite 2 (Hyperbolic Half-Plane Escher Limiting {5,4})
  - `textures/T_Hopf_ToroidalFibration/`: Suite 3 (Toroidal Hopf Fibration Bundle)
  - `textures/T_Hypersphere_DimensionalInterference/`: Suite 4 (4D Hypersphere Dimensional Interference)
  - `textures/T_Chladni_ResonantModal/`: Suite 5 (Chladni Resonant Modal Cymatic Plate)
  - `textures/T_Cymatic_HarmonicLattice/`: Suite 6 (Multi-Frequency Nodal Acoustic Lattice)
- **Automated Quality Gate & Verification Harness** (`tests/`):
  - `tests/test_mathematical_pbr_verification.py`: Programmatic verification script asserting 2048x2048 POT, bit depth, channel bounds, normal unit vector normalization ($\|\vec{N}\|\approx 1.0$), DirectX green-channel orientation, and ORM packing integrity.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Non-Euclidean Hyperbolic Tilings | Poincaré disk & half-plane tessellations $\{p,q\}$, geodesic reflections | M1 | ORIGINAL_REQUEST §R1 |
| 2 | Escher-Style Infinity Boundaries | Limit circle hyperbolic tiling with asymptotic boundary scaling | M1 | ORIGINAL_REQUEST §R1 |
| 3 | 4D Hopf Fibrations | Toroidal fiber bundle projections $S^3 \rightarrow S^2$ via stereographic mapping | M2 | ORIGINAL_REQUEST §R1 |
| 4 | 4D Hypersurface Slices | 4D hypersphere cross-sections with dimensional interference ripples | M2 | ORIGINAL_REQUEST §R1 |
| 5 | Chladni Modal Standing Waves | 2D modal acoustic standing wave equations $\cos(n\pi x/L)\cos(m\pi y/L) - \cos(m\pi x/L)\cos(n\pi y/L) = 0$ | M3 | ORIGINAL_REQUEST §R1 |
| 6 | Cymatic Nodal Lattices | Acoustic nodal line interference patterns and sand accumulation | M3 | ORIGINAL_REQUEST §R1 |
| 7 | Haute-Couture BaseColor (`_BC`) | 2048x2048 sRGB painterly watercolor wash + jewel/metallic accents | M1, M2, M3 | ORIGINAL_REQUEST §R2 |
| 8 | DirectX Tangent Normal (`_N`) | 2048x2048 tangent-space unit normal vectors with Green=-Y orientation | M1, M2, M3 | ORIGINAL_REQUEST §R2 |
| 9 | Packed ORM (`_ORM`) | 2048x2048 R=AO, G=Roughness, B=Metallic linear channel packing | M1, M2, M3 | ORIGINAL_REQUEST §R2 |
| 10 | Height / Micro-Elevation (`_H`) | 2048x2048 full dynamic-range micro-elevation maps | M1, M2, M3 | ORIGINAL_REQUEST §R2 |
| 11 | Discrete PBR Maps (`_AO`, `_R`, `_M`) | 2048x2048 individual linear maps for granular engine configuration | M1, M2, M3 | ORIGINAL_REQUEST §R2 |
| 12 | Automated Verification Quality Gate | Automated Python verification test script exiting with 0 | M0, M4 | ORIGINAL_REQUEST §R3 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M0 | E2E Test Suite & Harness | Implement test harness and `TEST_INFRA.md` / `TEST_READY.md` | none | DONE |
| M1 | Domain 1: Hyperbolic Tilings (Suites 1 & 2) | Procedural generator & full map baking for Suites 1 and 2 | M0 | DONE |
| M2 | Domain 2: 4D Hopf & Hypersurface (Suites 3 & 4) | Procedural generator & full map baking for Suites 3 and 4 | M0 | DONE |
| M3 | Domain 3: Chladni Cymatics (Suites 5 & 6) | Procedural generator & full map baking for Suites 5 and 6 | M0 | DONE |
| M4 | Verification & Quality Gate Run | Run automated test suite against all 42 generated maps | M1, M2, M3 | DONE |
| M5 | Adversarial Review & Forensic Audit | Multi-reviewer inspection, challenger stress test, forensic audit | M4 | DONE |

## Interface Contracts
### PBR Texture Maps Standard (Per Suite)
Each suite directory `textures/<SuiteName>/` must contain exactly:
- `<SuiteName>_BC.png`: 2048x2048, 8-bit RGB/RGBA (sRGB), Painterly / Haute-Couture color palette.
- `<SuiteName>_N.png`: 2048x2048, 8-bit RGB (Linear), DirectX Tangent Normal (R=X+, G=Y-, B=Z+), $\|\vec{N}\| = \sqrt{n_x^2+n_y^2+n_z^2} \approx 1.0$.
- `<SuiteName>_ORM.png`: 2048x2048, 8-bit RGB (Linear), R=AO [0, 255], G=Roughness [0, 255], B=Metallic [0, 255].
- `<SuiteName>_H.png`: 2048x2048, 8-bit or 16-bit Grayscale/RGB (Linear), Micro-elevation heightfield.
- `<SuiteName>_AO.png`: 2048x2048, 8-bit Grayscale/RGB (Linear), Ambient Occlusion channel.
- `<SuiteName>_R.png`: 2048x2048, 8-bit Grayscale/RGB (Linear), Roughness channel.
- `<SuiteName>_M.png`: 2048x2048, 8-bit Grayscale/RGB (Linear), Metallic channel.

## Code Layout
```
C:\EnvironmentPortfolio\teamwork_projects\surreal_mathematical_textures\
├── PROJECT.md
├── TEST_INFRA.md
├── TEST_READY.md
├── generators/
│   ├── __init__.py
│   ├── pbr_engine.py
│   ├── hyperbolic_generator.py
│   ├── hopf_generator.py
│   ├── chladni_generator.py
│   └── run_batch_synthesis.py
├── textures/
│   ├── T_Hyperbolic_PoincareTriangular/
│   ├── T_Hyperbolic_HalfPlaneEscher/
│   ├── T_Hopf_ToroidalFibration/
│   ├── T_Hypersphere_DimensionalInterference/
│   ├── T_Chladni_ResonantModal/
│   └── T_Cymatic_HarmonicLattice/
└── tests/
    ├── __init__.py
    └── test_mathematical_pbr_verification.py
```
