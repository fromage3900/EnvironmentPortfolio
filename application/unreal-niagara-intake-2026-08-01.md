# Melodia — Niagara / Lookdev portfolio intake

## Status

Use this as a current-session addendum to `generated/unreal_portfolio_intake.json`; do not replace the older render catalogue. It records only work with direct asset or preview evidence from the 2026-08-01 session.

## Project card

- **Project:** Melodia — Sakura Dream / Zen Forest
- **Engine:** Unreal Engine 5.8
- **Role framing:** Environment art, technical art, lookdev, and real-time VFX integration
- **Visual thesis:** Living storybook terrain and shrine ambience: authored Sakura petal meshes, Japanese ornament motifs, restrained SDF response, and a soft storybook post-process language.
- **Gameplay boundary:** VFX is presentation-only. Stock game systems retain authority for input, combat, rewards, quests, saves, and progression.

## Verified portfolio proof

### 1. Sakura motion language — primary VFX plate

- **Assets:** `NS_SakuraPetals_v2`, `NS_SakuraPetalGust`, `NS_SakuraLanternMotes`, `NS_ConstellationDraw`
- **What it proves:** The ambient VFX is not a stock sprite pass. Petal gusts use the project Nanite petal mesh; constellation and lantern effects use full-resolution Japanese ornament alpha cards through a reusable card material.
- **Required captures:**
  1. Zen Forest beauty frame with petals + lantern/constellation accent.
  2. Niagara editor proof showing the mesh renderer on `NS_SakuraPetalGust`.
  3. Material-instance proof for `MI_Niagara_Melodia_ConstellationRosette` or `MI_Niagara_Melodia_LanternFiligree`.
- **Recommended caption:** “A reusable Sakura VFX language built from authored petal meshes and Japanese ornament cards, with material selection matched to effect role rather than a one-sprite solution.”

### 2. Storybook render schema — secondary lookdev plate

- **Assets:** active Storybook Outline material, `M_PP_MeluColorGrade`, UDS-owned sky/weather, candidate Starry Night material
- **What it proves:** A controlled real-time lookdev stack separates gameplay readability from authored narrative/capture profiles; UDS remains environmental authority.
- **Required captures:** matched 16:9 morning, sunset, clear-night, and cloudy-night frames; one outline/material-editor close-up.
- **Do not claim yet:** eight-direction outline sampling, final high-resolution capture readiness, or final foliage treatment. Those remain A/B / HLSL approval work.

### 3. Living landscape / material-system plate

- **Assets:** authored Landscape Master baseline, `M_Master_Toon_Universal`, macro/detail research lane, height/path blending
- **What it proves:** The project maintains authored landscape lookdev while extending reusable material controls rather than replacing it with a generic technical graph.
- **Required captures:** close painted transition, traversal/path frame, wide composition, and a debug-mask frame.

## Current polish risk — do not present as finished

- Soft ambient systems (`NS_Uni_GroundWisps`, `NS_Uni_WaterMist`, `NS_Uni_MistSheet`) need a dedicated soft-field material; rectangular-card experiments are rejected.
- `NS_MagicTrail`, Dust Shafts, Ember Motes, and Fairy Dust need same-camera in-world review before a beauty shot is selected.
- `NS_SakuraPetals_v2` needs an event-chain proof capture before its ripple/pile behavior is presented as final.
- SDF foliage/fish/pulse systems have dedicated materials, but need in-world PPV alpha/emissive validation.

## Capture / upload metadata

| Slot | Suggested filename | Website group | Status |
| --- | --- | --- | --- |
| Sakura VFX beauty | `melodia-sakura-niagara-zenforest-hero.png` | `sakura_mood` | Capture next |
| Petal gust renderer proof | `melodia-niagara-petal-mesh-proof.png` | `shader_proof` | Capture next |
| Ornament card material proof | `melodia-niagara-ornament-card-proof.png` | `shader_proof` | Capture next |
| Storybook render A/B | `melodia-storybook-outline-ab.png` | `shader_proof` | Blocked on outline capture gate |

## Site integration

1. Add the approved beauty capture to `renders.hero` or `renders.materials` in the canonical Unreal package, not directly to a hand-written HTML card.
2. Run `tools/ingest_unreal_portfolio.ps1`, then rebuild the capture brief and validate the portfolio.
3. Replace the broken placeholder-generated brief with data from the current package before publishing.
4. Keep the website copy factual: distinguish verified production systems from candidate experiments.
