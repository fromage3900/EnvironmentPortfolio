# Melodia Workspace — Project Handoff & Expansion Specification

## Executive Summary
This document serves as the formal architectural handoff for the next AI agent on the **Melodia Dual-Track Production Platform** project (`c:/EnvironmentPortfolio`). All foundational production build gates, asset verification, site claim facts, starfield depth-parallax canvas (`<canvas id="ambient-starfield">`), and cursor sparkle motion trail particle systems are 100% verified and operational.

---

## Current Architecture & System State

### 1. Build & Deployment Pipeline
- **Vite Bundler Configuration**: `vite.config.js` builds static HTML/JS/CSS bundles from `wix/` into `my-site-deploy/`.
- **GitHub Pages Sync Target**: Local Git repository checkout `my-site-clean/` maps to remote `https://github.com/fromage3900/my-site.git` (`https://fromage3900.github.io/my-site/wix/`).
- **Current source-control checkpoint (2026-08-13)**: Unreal `BS_GodFile/main` and `MelodiaMelusinaV2/main` are synchronized at `840b7650`. The website checkout is at local tip `3cfa5f0`, but its configured remote has unrelated history and is not synchronized; do not force-push or merge unrelated histories.
- **Path Normalization**: `python tools/normalize-paths.py [wix|github]` manages local relative vs. GitHub Pages absolute URLs.

### 2. Automated Fact & Asset Verification Matrix
- **`npm run verify:all`**: Executes token linter (`tools/lint-tokens.js`), site facts check (`tools/_verify_site_facts.py`), and asset validator (`tools/validate_assets.py`). Current status (2026-08-13): token lint **FAILS** with `99` hard errors and `1113` warnings; the site facts and asset checks pass separately with `0` issues and `0` missing assets.
- **`python tools/_verify_site_facts.py`**: Validates project SSOT claims (Brand: Brennan Shepherd, Engine: EEVEE, Stage v7, 15 FBX kitbash items, Humber education claim, zero forbidden ephemeral claims). Current status: **0 issues**.

### 3. Motion & Visual System
- **Starfield Canvas Engine** (`wix/melodia-starfield.js`): Full-viewport `<canvas id="ambient-starfield">` with thin-film spectrum wave math, watercolor wash layering, cursor depth parallax, and 4-point sparkle motion trails on `pointermove`.
- **Accessibility Safeguard**: Evaluates `prefers-reduced-motion: reduce` to automatically suspend animation loops and draw static background frames.

---

## Recommended Next-Phase Expansion Plan

### Feature 1: Site-Wide Interactive Harmonix Rhythm Highway
- **Objective**: Extend the 128 BPM Harmonix rhythm highway from a section breakdown to a site-wide interactive audio-visual layer.
- **Key Modules**:
  - `wix/melodia-game-ui.js` / `wix/melodia-game-ui.css`: Add a global floating rhythm HUD component (`.rhythm-highway-bar`) togglable across all pages.
  - **Input Bindings**: Capture keypress events (`[Space]`, `[Z]`, `[X]`) aligned with 128 BPM timing windows (`~3.05s` window, `±150ms` perfect hit accuracy).
  - **FX Feedback**: Trigger combo counter floaters (`+100 Perfect!`, `Combo x12`), screen-shake micro-animations, and audio pulse synthesized through Web Audio API oscillator fallback.

### Feature 2: Magical Girl & Non-Euclidean Escher UI Polish
- **Objective**: Deepen the Infold / Magical Girl aesthetic across all site modules.
- **Key Modules**:
  - `wix/melodia-magical-girl.css` & `wix/melodia-dream-shaders.css`: Introduce dynamic iridescent foil borders (`devinIridescence` shader math), filigree crest card frames, and floating crystal badges.
  - `wix/melodia-escher-interact.js`: Add interactive non-Euclidean card rotation on hover, where cards tilt in 3D perspective with reflective thin-film sheen.

### Feature 3: Live Monolith MCP & DCC Pipeline Telemetry Dashboard
- **Objective**: Turn `pipeline.html` and `agent-dashboard-t3d.html` into active telemetry monitoring dashboards.
- **Key Modules**:
  - `wix/agent-dashboard-t3d.html` & `tools/figma_mcp.py`: Add simulated active port status indicators for Monolith MCP (Port 9316), Blender Bridge (Port 9317), UEBlueprintMCP (Port 55558), and LiveLink MoCap (Port 9876).
  - **Interactive Controls**: Sliders for PCG scatter density, toon shader R/G/B ramp tuning, and LiveLink skeletal pose previews.

---

## Execution Instructions for Incoming Agent

1. **Verify Environment Baseline**:
   ```powershell
   # Run full verification suite
   npm run verify:all
   python tools/_verify_site_facts.py
   ```
2. **Execute Vite Build Verification**:
   ```powershell
   npx vite build
   ```
3. **Branching & Sync Workflow**:
   - Make source edits in `wix/` and `content/`.
   - Copy updated files to `my-site-clean/wix/` and `my-site-clean/content/`.
   - Re-run the site facts and asset checks; resolve token-linter errors separately before claiming the full `verify:all` suite is green.

---
*Document updated on 2026-08-13. Environment state: Unreal branch synchronized; website remote reconciliation and token-linter cleanup remain open.*
