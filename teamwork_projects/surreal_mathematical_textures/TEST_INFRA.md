# Automated Test Infrastructure: Surreal Mathematical PBR Verification

## 1. Architecture Overview

The verification test harness (`tests/test_mathematical_pbr_verification.py`) provides an automated, production-grade quality gate for the 6 Surreal Mathematical PBR Texture Suites. It validates the geometric, numerical, physical, and packaging integrity of 42 generated Power-of-Two ($2048 \times 2048$) texture maps across three mathematical domains.

```
C:\EnvironmentPortfolio\teamwork_projects\surreal_mathematical_textures\
├── tests/
│   ├── __init__.py
│   └── test_mathematical_pbr_verification.py  <-- Automated Quality Gate Harness
├── TEST_INFRA.md                              <-- Architecture & Specification (this document)
├── TEST_READY.md                              <-- Test Readiness State & Sign-off Matrix
└── textures/                                  <-- Target Suites Under Verification
    ├── T_Hyperbolic_PoincareTriangular/
    ├── T_Hyperbolic_HalfPlaneEscher/
    ├── T_Hopf_ToroidalFibration/
    ├── T_Hypersphere_DimensionalInterference/
    ├── T_Chladni_ResonantModal/
    └── T_Cymatic_HarmonicLattice/
```

---

## 2. Suites & Texture Inventory Under Test

The test harness evaluates **6 material suites** $\times$ **7 maps per suite** = **42 total texture maps**:

| Suite Name | Domain | Mathematical Model |
|------------|--------|---------------------|
| `T_Hyperbolic_PoincareTriangular` | Hyperbolic Tilings | Poincaré Disk $\{7, 3\}$ Triangular Coxeter Group Reflections |
| `T_Hyperbolic_HalfPlaneEscher` | Hyperbolic Tilings | Upper Half-Plane Limiting $\{5, 4\}$ Asymptotic Boundary Tessellation |
| `T_Hopf_ToroidalFibration` | 4D Hopf Fibrations | Toroidal Fiber Bundle Projections ($S^3 \rightarrow S^2$) via Stereographic Mapping |
| `T_Hypersphere_DimensionalInterference` | 4D Hypersurface Slices | 4D Hypersphere Cross-Sections with Dimensional Intersection Waves |
| `T_Chladni_ResonantModal` | Chladni Cymatic Plates | 2D Acoustic Standing Wave Equation $\cos(n\pi x/L)\cos(m\pi y/L) - \cos(m\pi x/L)\cos(n\pi y/L) = 0$ |
| `T_Cymatic_HarmonicLattice` | Chladni Cymatics | Multi-Frequency Acoustic Superposition & Nodal Sand Lattices |

### Required Texture Maps per Suite:
1. `<SuiteName>_BC.png`: BaseColor (sRGB 8-bit RGB/RGBA, painterly palette, jewel/metallic accents)
2. `<SuiteName>_N.png`: DirectX Tangent Normal (Linear 8-bit RGB, $\|\vec{N}\|\approx 1.0$, Green=-Y)
3. `<SuiteName>_ORM.png`: Packed ORM (Linear 8-bit RGB: Red=AO, Green=Roughness, Blue=Metallic)
4. `<SuiteName>_H.png`: Height / Micro-Elevation (Linear 8/16-bit Grayscale or RGB)
5. `<SuiteName>_AO.png`: Ambient Occlusion (Linear 8-bit Grayscale/RGB)
6. `<SuiteName>_R.png`: Roughness (Linear 8-bit Grayscale/RGB)
7. `<SuiteName>_M.png`: Metallic (Linear 8-bit Grayscale/RGB)

---

## 3. Verification Tiers & Methodologies

The test harness executes 6 discrete tiers of assertions:

### Tier 0: Harness Math & Self-Test Verification
- **Purpose**: Validates the numerical precision and correctness of the testing algorithms themselves on synthetic calibration buffers.
- **Checks**:
  - Power-of-two bitwise logic validation ($2^1$ to $2^{12}$).
  - Shannon entropy mathematical formulation calibration ($H = 0.0$ for constant, $H = 1.0$ for 50/50 binary, $H = 3.0$ for 8-state uniform, $H = 8.0$ for 256-state uniform).
  - 2D discrete Laplacian filter variance calibration on flat vs high-frequency checkerboard.
  - Tangent-space normal vector decoding and unit normalization validation.
  - ORM packing discrepancy detection and Mean Absolute Difference (MAD) sensitivity.

### Tier 1: Directory Structure, File Naming, & POT Dimensions
- **Purpose**: Structural existence and resolution compliance.
- **Checks**:
  - Validates `textures/` root directory and all 6 suite subdirectories exist.
  - Asserts 100% presence of all 42 required texture files matching exact naming schema.
  - Validates image dimensions strictly equal $(2048, 2048)$ and conform to Power-of-Two ($2^{11} \times 2^{11}$) constraints.

### Tier 2: Bit Depth, Color Formats, & Dynamic Range Integrity
- **Purpose**: Channel depth, color spaces, and non-trivial signal ranges.
- **Checks**:
  - BaseColor (`_BC`): Mode `RGB`/`RGBA`, `uint8`, dynamic span $> 30$, channel $\sigma > 5.0$.
  - Heightfield (`_H`): Mode `L`, `I;16`, `I`, `RGB`, or `RGBA`; dynamic span $\ge 64$ (for 8-bit) or $\ge 10000$ (for 16-bit); $\sigma > 2.0$.
  - Discrete Maps (`_AO`, `_R`, `_M`): Mode `L` or `RGB`, `uint8`, strictly bounded in $[0, 255]$.

### Tier 3: DirectX Normal Vector Math & Orientation
- **Purpose**: Mathematical unit vector normalization and tangent-space orientation.
- **Checks**:
  - Tangent vector decoding: $n_x = \frac{R}{255}\times 2 - 1$, $n_y = \frac{G}{255}\times 2 - 1$, $n_z = \frac{B}{255}\times 2 - 1$.
  - Mean normal vector length: $\|\vec{N}\| = \sqrt{n_x^2 + n_y^2 + n_z^2} \in [0.95, 1.05]$.
  - Vector length variance: $\sigma_{\|\vec{N}\|} < 0.08$.
  - $\ge 95\%$ of all pixels satisfy $\|\vec{N}\| \in [0.90, 1.10]$.
  - Tangent space outward dominance: Mean $B > 180$, Min $B \ge 64$.
  - DirectX Green Channel ($-Y$): Vertical height gradient $-\nabla_y H$ exhibits positive correlation ($\rho > 0.40$) with tangent $n_y$.

### Tier 4: ORM Channel Packing vs Discrete Maps Consistency
- **Purpose**: Linear channel alignment between packed ORM and standalone texture maps.
- **Checks**:
  - Packed ORM format: Mode `RGB`/`RGBA`, `uint8`, channels exhibit active variance ($\sigma > 1.0$).
  - Red Channel $\leftrightarrow$ Discrete AO (`_AO.png`): $\text{MAD} \le 1.0$ LSB, $\max(|\Delta|) \le 3$ LSB.
  - Green Channel $\leftrightarrow$ Discrete Roughness (`_R.png`): $\text{MAD} \le 1.0$ LSB, $\max(|\Delta|) \le 3$ LSB.
  - Blue Channel $\leftrightarrow$ Discrete Metallic (`_M.png`): $\text{MAD} \le 1.0$ LSB, $\max(|\Delta|) \le 3$ LSB.

### Tier 5: Mathematical Non-Triviality, Shannon Entropy, & Spatial Frequency
- **Purpose**: Asset richness, preventing solid colors, blank textures, or flat noise.
- **Checks**:
  - Shannon Entropy: $H(X) = -\sum p_i \log_2(p_i) \ge 3.0$ bits for BaseColor, Normal, and Height.
  - 2D Discrete Laplacian Variance: $\text{Var}(\nabla^2 I) > 5.0$ on BaseColor, $> 3.0$ on Height.
  - Palette Richness: $\ge 256$ unique RGB color samples in BaseColor.

---

## 4. Test Execution Commands

### Run Complete Verification Suite (All Tiers, All Suites)
```bash
python -m unittest tests/test_mathematical_pbr_verification.py
```

### Run Self-Verification (Tier 0 Harness Logic)
```bash
python tests/test_mathematical_pbr_verification.py --tier 0
```

### Run Specific Test Tier (Tiers 0 - 5)
```bash
# Tier 1: Directory Structure & Dimensions
python tests/test_mathematical_pbr_verification.py --tier 1

# Tier 2: Bit Depth & Dynamic Range
python tests/test_mathematical_pbr_verification.py --tier 2

# Tier 3: DirectX Normal Vector Mathematics
python tests/test_mathematical_pbr_verification.py --tier 3

# Tier 4: ORM Channel Consistency
python tests/test_mathematical_pbr_verification.py --tier 4

# Tier 5: Mathematical Entropy & Non-Triviality
python tests/test_mathematical_pbr_verification.py --tier 5
```

### Run Verification for a Single Texture Suite
```bash
python tests/test_mathematical_pbr_verification.py --suite T_Hyperbolic_PoincareTriangular
```

### Display Visual Summary Table
```bash
python tests/test_mathematical_pbr_verification.py --summary
```

---

## 5. Pass / Fail Quality Gate Standards

A build passes the automated quality gate if and only if:
1. Exit code is `0`.
2. All 42 texture maps are present on disk.
3. 100% of tests across Tiers 0 through 5 succeed with 0 failures and 0 errors.
