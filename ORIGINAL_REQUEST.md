# Original User Request

## Initial Request — 2026-08-27T21:49:26-04:00

Build a comprehensive visual catalog that breaks down the 1,855 PBR textures in the project by name, specific usage context, and visual thumbnails. The visual thumbnails will be sourced by mapping the `.uasset` files back to their `.png`/`.tga` originals in the `Imports/` folder. The final output will be a standalone HTML/JS web dashboard.

### Requirements:
1. **R1. Texture Mapping & Context**: Map the project's PBR `.uasset` textures back to their source image files in `Imports/` and categorize them by name and PBR map type (BaseColor, Normal, ORM, etc.).
2. **R2. Web Dashboard**: Generate a standalone HTML/JS web dashboard that visually displays this catalog, complete with thumbnail images and basic filtering/search functionality.

### Verification Resources:
- The project contains an existing UI testing framework. Locate and hook into this framework to verify the web dashboard.

### Acceptance Criteria:
- [ ] **Data Mapping**: A programmatic script objectively confirms that at least 1,500 `.uasset` textures are successfully mapped to a valid, existing source image path in the `Imports/` directory.
- [ ] **UI Rendering & Functionality**:
  - The dashboard successfully passes the project's existing UI testing framework without throwing rendering errors.
  - A programmatic test confirms that the filtering/search functionality correctly isolates textures by their PBR map type when queried.

## Follow-up Request — 2026-08-30T01:14:11Z

# Teamwork Project Prompt — Draft

Research, mathematically formulate, and synthesize an unprecedented library of deeply surreal, high-fidelity PBR texture suites ($2048 \times 2048$ POT) driven by non-Euclidean hyperbolic tilings, 4D Hopf fibration slices, and harmonic Chladni cymatic lattices under an haute-couture and painterly aesthetic lens.

Use a standard full team of agents.

Working directory: C:\EnvironmentPortfolio\teamwork_projects\surreal_mathematical_textures
Integrity mode: development

## Requirements

### R1. Advanced Mathematical Synthesis & Formulation
Formulate and execute procedural generators implementing three niche mathematical domains:
1. **Non-Euclidean Hyperbolic Tilings**: Poincaré disk/half-plane tessellations, Escher-style infinity boundaries, and hyperbolic triangular tilings $\{p, q\}$.
2. **4D Hypersurface Slices & Hopf Fibrations**: Toroidal fiber bundle projections ($S^3 \rightarrow S^2$) and 4D hypersphere cross-sections with dimensional intersection interference.
3. **Harmonic Chladni Acoustic & Cymatic Lattices**: 2D modal standing wave equations ($\cos(n\pi x/L)\cos(m\pi y/L) - \cos(m\pi x/L)\cos(n\pi y/L) = 0$) and acoustic nodal interference patterns.

### R2. Complete PBR Texture Suite Generation
Synthesize full, production-ready $2048 \times 2048$ Power-of-Two PBR material suites for each mathematical domain. Each suite must provide:
- **BaseColor (`_BC`)**: High-dynamic color grading with painterly watercolor and jewel/metallic accents (sRGB).
- **DirectX Normal (`_N`)**: Mathematically derived tangent-space unit normal vectors with green-channel $(-Y)$ orientation.
- **Packed ORM (`_ORM`)**: Red = Ambient Occlusion, Green = Roughness, Blue = Metallic.
- **Height / Displacement (`_H`)**: Full dynamic-range micro-elevation maps.
- **Discrete Maps**: Individual `_AO`, `_R`, and `_M` files for granular engine configuration.

### R3. Automated Quality Gate & Verification Harness
Provide an automated Python verification script that objectively validates 100% of generated texture maps against Power-of-Two dimensions, bit depth, channel bounds, normal unit vector normalization, and ORM channel integrity.

## Acceptance Criteria

### Mathematical Domain Coverage & Variety
- [ ] At least 6 distinct surreal mathematical PBR texture suites are fully synthesized across the three target domains (Hyperbolic Tilings, 4D Hopf Fibrations, and Chladni Cymatic Lattices).
- [ ] Each suite exhibits distinct mathematical curvature, nodal lines, or dimensional projections distinct from standard simplex/perlin noise.

### Technical & PBR Conformance
- [ ] 100% of generated texture files strictly adhere to $2048 \times 2048$ Power-of-Two resolution.
- [ ] All `_ORM` textures have valid channel packing (Red = AO $[0, 255]$, Green = Roughness $[0, 255]$, Blue = Metallic $[0, 255]$).
- [ ] All normal maps pass mathematical unit vector validation ($\sqrt{n_x^2 + n_y^2 + n_z^2} \approx 1.0$) with DirectX green-channel orientation.
- [ ] A programmatic verification test executes with an exit code of `0`, validating all generated texture assets.


## Follow-up Request — 2026-08-30T02:10:14Z

# Teamwork Project Prompt — Draft

Research, construct, and objectively verify an end-to-end *Infinity Nikki (无限暖暖)* haute-couture asset elevation ecosystem. The deliverable encompasses Houdini SOP/VEX procedural 3D trim and lace geometry generators, advanced Unreal Engine 5 Substrate and Material Function shading architectures (thin-film optical iridescence, dual-lobe anisotropic velvet fuzz, translucent organza subsurface scattering, and gold bullion embroidery), production PBR material suites in vibrant pinks, blues, and purples, and an interactive lookdev sandbox.

Use a standard full team of agents.

Working directory: C:\EnvironmentPortfolio\teamwork_projects\infinity_nikki_asset_elevation
Integrity mode: development

## Requirements

### R1. Houdini SOP/VEX Procedural Asset & Trim Synthesizers
Implement automated Houdini procedural generation scripts (`hython` compatible) that construct physical 3D micro-geometry and extract baked PBR maps:
- **Procedural Chantilly Lace & Micro-Beading**: Woven floral lattices with pearl and crystal seed bead scatter arrays.
- **Differential Line Growth Organza**: Organic multi-frequency ruffle petal meshes with 3D tangent flow normals.
- **Baroque Bullion Embroidery**: Braided gold and rose-gold thread coils along polar logarithmic acanthus curves.
- **High-to-Low Extraction**: Automated baking of 16-bit displacement height, DirectX tangent space normals (Green = $-Y$), curvature masks, and micro-cavity ambient occlusion.

### R2. Haute-Couture UE5 Substrate & Material Function Architecture
Author modular, production-ready Unreal Engine 5 shader graphs and Material Functions replicating *Infinity Nikki*'s signature materiality:
- **`MF_ThinFilm_Iridescence`**: Multi-stop spectral thin-film optical interference driven by view angle and surface normal curvature.
- **`MF_DualLobe_SubstrateVelvet`**: Dual-lobe anisotropic velvet/fuzz shading with customizable edge rim glow and chromatic pile shift.
- **`MF_Translucent_OrganzaSSS`**: Sheer fabric opacity, micro-twill normal blending, and dual-sided subsurface scattering.
- **`MF_Bullion_MicroRelief`**: Metallic embroidery parallax and contact occlusion mapping.

### R3. Haute-Couture PBR Material Suites ($2048 \times 2048$ POT)
Synthesize production-ready $2048 \times 2048$ Power-of-Two PBR material suites utilizing the procedural engine and vibrant *Infinity Nikki* palettes (Pinks, Blues, Purples, Rose Gold, and Pearl White):
- **BaseColor (`_BC`)**: High-dynamic color grading with painterly watercolor glazes and metallic bullion accents (sRGB).
- **DirectX Normal (`_N`)**: Unit-normalized tangent-space vectors ($\sqrt{n_x^2 + n_y^2 + n_z^2} \approx 1.0$) with green-channel $(-Y)$ orientation.
- **Packed ORM (`_ORM`)**: Red = Ambient Occlusion, Green = Roughness, Blue = Metallic (Linear).
- **Height (`_H`)** & **Discrete Channels**: `_AO`, `_R`, `_M`, `_Sheen`, and `_Alpha` where applicable.

### R4. Automated Quality Gate, Unit Tests & Interactive Lookdev Sandbox
Provide an automated Python verification test suite and an interactive HTML/JS Generative UI lookdev sandbox:
- **Automated Test Harness**: Programmatic unit tests validating 100% of generated texture maps against Power-of-Two resolution, channel bounds, normal unit length, and ORM packing.
- **Interactive Lookdev Dashboard**: A standalone HTML/JS dashboard with base64 embedded thumbnails, real-time channel isolation, and physical material parameter inspection.

## Acceptance Criteria

### Procedural Generation & Bakes
- [ ] Houdini procedural scripts successfully execute via `hython` without errors, generating 3D micro-geometry and baking out high-fidelity PBR texture channels.
- [ ] At least 4 distinct procedural asset archetypes are synthesized (Chantilly Lace/Beading, Differential Organza, Bullion Acanthus, and Reaction-Diffusion Cloisons).

### Shader Architecture & Material Functions
- [ ] Unreal Engine 5 Material Functions (`MF_ThinFilm_Iridescence`, `MF_DualLobe_SubstrateVelvet`, `MF_Translucent_OrganzaSSS`, `MF_Bullion_MicroRelief`) are structurally defined with valid input/output pins and standard parameter defaults.
- [ ] Shader graphs correctly bind BaseColor, Normal, and packed Linear ORM textures.

### PBR & Asset Conformance
- [ ] 100% of generated texture files strictly adhere to $2048 \times 2048$ Power-of-Two dimensions.
- [ ] All normal maps pass mathematical unit vector validation ($\|\vec{N}\| \approx 1.0$) with DirectX green-channel orientation.
- [ ] All `_ORM` textures have verified channel allocation ($\text{Red} = \text{AO}$, $\text{Green} = \text{Roughness}$, $\text{Blue} = \text{Metallic}$).
- [ ] The automated test harness executes with an exit code of `0`.
- [ ] A standalone interactive lookdev showcase HTML artifact is generated with embedded previews and real-time channel switching.

