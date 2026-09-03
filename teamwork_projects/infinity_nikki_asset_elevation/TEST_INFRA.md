# E2E Test Infra: Infinity Nikki Haute-Couture Asset Elevation

## Test Philosophy
- Opaque-box, requirement-driven, mathematically rigorous verification.
- Enforces strict Power-of-Two dimensions ($2048 \times 2048$), channel boundaries, normal unit length, DirectX tangent space $(-Y)$, exact ORM packing allocation, and UE5 Substrate node graph schema integrity.

## Feature Inventory
| # | Feature | Source (requirement) | Tier 0 | Tier 1 | Tier 2 | Tier 3 | Tier 4 | Tier 5 | Tier 6 |
|---|---------|----------------------|:------:|:------:|:------:|:------:|:------:|:------:|:------:|
| F1 | Chantilly Lace & Beading | ORIGINAL_REQUEST §R1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| F2 | Differential Growth Organza | ORIGINAL_REQUEST §R1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| F3 | Baroque Bullion Embroidery | ORIGINAL_REQUEST §R1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| F4 | Reaction-Diffusion Cloisons | ORIGINAL_REQUEST §R1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| F5 | High-to-Low Baker | ORIGINAL_REQUEST §R1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| F6-F10 | UE5 Substrate Shader Graphs | ORIGINAL_REQUEST §R2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| F11-F14 | 4 Haute-Couture PBR Suites | ORIGINAL_REQUEST §R3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| F15-F16 | Test Suite & Lookdev Sandbox | ORIGINAL_REQUEST §R4 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## Test Architecture
- Test Runner: `python -m unittest tests/test_haute_couture_pbr_verification.py`
- Shader Verification Runner: `python -m unittest tests/test_ue5_shader_specifications.py`
- Pass Semantics: 100% test pass rate with exit code 0.

### Verification Tiers
- **Tier 0: Verification Harness Self-Tests**: Verifies test metrics, synthetic normal maps, synthetic ORM packers, and synthetic heightfields.
- **Tier 1: Asset Existence & File Dimensions**: Validates existence of all 36 maps across 4 suites, exact naming conventions, and $2048 \times 2048$ POT dimensions.
- **Tier 2: Bit Depth & Dynamic Range**: Validates 8-bit dynamic range $[0, 255]$ for RGB/L maps and 16-bit dynamic range $[0, 65535]$ for height maps.
- **Tier 3: DirectX Tangent Normal Calculus**: Validates unit vector length $\|\vec{N}\| \in [0.95, 1.05]$ and DirectX Green = $-Y$ orientation (correlation with height gradient $r > 0.35$).
- **Tier 4: ORM Channel Allocation & Discrete Consistency**: Validates pixel-exact channel matching (Red = AO, Green = Roughness, Blue = Metallic) with $\text{MAD} \le 1.0$ LSB.
- **Tier 5: Information Entropy & Non-Trivial Texture Content**: Validates spatial complexity and Shannon entropy ($H \ge 3.0$).
- **Tier 6: Fabric Mask Integrity & UE5 Shader Function Validation**: Validates `_Sheen` and `_Alpha` ranges, and schema validation of all 4 UE5 Material Function JSONs and master graph.

## Acceptance Criteria
- All tests execute with exit code 0.
- Standalone lookdev dashboard `lookdev_sandbox.html` successfully renders with WebGL.
