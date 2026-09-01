# Project: PBR Texture Catalog Dashboard

## Architecture
- **Data Engine**: Deterministic Python extraction & mapping pipeline (`teamwork_projects/texture_catalog_dashboard/scripts/map_pbr_textures.py`) that indexes source images in `Imports/` (12,961 files) and maps them to Unreal `Texture2D` `.uasset` files (15,074 files), categorizing each into standard PBR channels (`BaseColor`, `Normal`, `ORM`, `Roughness`, `Metallic`, `AO`, `Height`, `Emissive`, `Mask`, `Specialty`, `UI`) and usage contexts.
- **Data Artifacts**:
  - `teamwork_projects/texture_catalog_dashboard/catalog-data.json` (Structured JSON catalog for programmatic tests & tools).
  - `teamwork_projects/texture_catalog_dashboard/catalog-data.js` (`window.TEXTURE_CATALOG = [...]` for zero-dependency standalone `file://` execution).
- **Web Dashboard**: Standalone Single-Page Application (`index.html`, `styles.css`, `app.js`) in `teamwork_projects/texture_catalog_dashboard/`. Uses modern CSS custom properties, responsive grid, native lazy loading (`loading="lazy"` + `decoding="async"`), CSS `content-visibility: auto`, and chunked DOM mounting (`IntersectionObserver` sentinel) for smooth 60 FPS scrolling and sub-3ms search/filter latency across the catalog.
- **Testing Track**: Pytest test suite (`tests/test_texture_catalog_dashboard.py` and `wix/tests/test_texture_catalog.py`) integrating with `wix/tests/dom_harness.py` to assert data mapping thresholds (>=1,500 mapped textures), DOM structure, filter channel isolation, and asset existence on disk.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Imports Indexing | Recursive discovery & lookup table indexing of 12,961 source images across `Imports/` | M1 | Survey |
| 2 | UAsset Scanning | Identification and binary inspection of Unreal `Texture2D` `.uasset` files in `BS_GodFile/Content` | M1 | Survey |
| 3 | Multi-Tier Mapping Algorithm | 7-tier resolution engine (exact stem, prefix stripping, suffix synonymy, alphanumeric normalization, folder disambiguation) mapping ≥1,500 textures | M1 | ORIGINAL_REQUEST R1 |
| 4 | PBR Channel Categorization | Deterministic classification into BaseColor, Normal, ORM, Roughness, Metallic, AO, Height, Emissive, Mask, Specialty, UI | M1 | ORIGINAL_REQUEST R1 |
| 5 | Usage Context Tagging | Domain contextualization across Environment, Props, Architecture, Characters, Materials, UI, VFX | M1 | ORIGINAL_REQUEST R1 |
| 6 | Catalog Data Generation | Output generation of `catalog-data.json` and standalone `catalog-data.js` | M1 | Survey |
| 7 | Standalone HTML5 Shell | Semantic DOM container (`.melodia-shell`, header, search, filters, grid, empty state) | M2 | ORIGINAL_REQUEST R2 |
| 8 | Responsive CSS Grid & Tokens | Modern dark theme, badge color tokens, responsive grid, `content-visibility: auto` | M2 | Survey |
| 9 | High-Performance DOM Renderer | Chunked DOM mounting (48 cards batch + `IntersectionObserver` sentinel) for 60 FPS scroll | M2 | Survey |
| 10 | Real-Time Search Engine | Substring and multi-term search across texture name, family, context, and path | M2 | ORIGINAL_REQUEST R2 |
| 11 | PBR Map Type Filter Chips | Interactive toggle chips isolating textures strictly by PBR channel (`BaseColor`, `Normal`, `ORM`, etc.) | M2 | ORIGINAL_REQUEST R2 |
| 12 | Visual Thumbnail Rendering | Thumbnail images with lazy loading and SVG fallback placeholder | M2 | ORIGINAL_REQUEST R2 |
| 13 | E2E Test Suite | Automated Pytest suite hooking into `dom_harness.py` asserting DOM, data, and filtering | M3 / E2E Track | ORIGINAL_REQUEST Criteria |
| 14 | Data Mapping Verification | Programmatic verification that ≥1,500 `.uasset` textures map to existing `Imports/` files | M3 / E2E Track | Acceptance Criteria |
| 15 | Filter Isolation Verification | Programmatic verification of 100% precision when filtering by channel | M3 / E2E Track | Acceptance Criteria |
| 16 | Adversarial Hardening & Audit | Stress-testing, edge case verification, zero-slop audit, and forensic integrity verification | Final Milestone | Audit Policy |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Test Suite Creation | Design & write opaque-box test suite `tests/test_texture_catalog_dashboard.py` hooking into `dom_harness.py` | none | PLANNED |
| M1 | Texture Mapping & Data Generation Engine | Implement `scripts/map_pbr_textures.py` and produce `catalog-data.json` and `catalog-data.js` mapping >=1,500 textures | none | PLANNED |
| M2 | Standalone Web Dashboard | Implement `index.html`, `styles.css`, `app.js`, and SVG placeholders in `teamwork_projects/texture_catalog_dashboard/` | M1 | PLANNED |
| M3 | E2E Verification & Integration | Run complete test suite, verify 100% pass across data mapping, UI DOM, and filter isolation | M1, M2, E2E | PLANNED |
| M4 | Adversarial Hardening & Forensic Integrity Audit | Challenger stress tests and Forensic Auditor integrity verification (anti-cheating, clean logic) | M3 | PLANNED |

## Interface Contracts
### Data Mapping Script ↔ Web Dashboard
- `catalog-data.js` exposes global: `window.TEXTURE_CATALOG = [...]`
- `catalog-data.json` schema: Array of objects with keys:
  - `id`: String (unique identifier)
  - `name`: String (texture name)
  - `uasset_path`: String (relative to repo root)
  - `source_image_path`: String (relative path in `Imports/`)
  - `source_rel_path`: String (relative path from dashboard HTML: `../../Imports/...`)
  - `thumbnail_path`: String (relative path from dashboard HTML)
  - `channel`: String (`"BaseColor" | "Normal" | "ORM" | "Roughness" | "Metallic" | "AO" | "Height" | "Emissive" | "Mask" | "Specialty" | "UI"`)
  - `channel_badge`: String (`"BC" | "N" | "ORM" | "R" | "M" | "AO" | "H" | "E" | "Mask" | "Spec" | "UI"`)
  - `family`: String (e.g. `"Atlantis KitBash"`, `"Kenney UI"`, `"Melusina Character"`, `"Environment"`)
  - `usage_context`: String (human-readable descriptive context)
  - `resolution`: String (e.g. `"4096x4096"`, `"2048x2048"`, `"1024x1024"`, `"Vector SVG"`)
  - `format`: String (`"PNG" | "SVG" | "TIF" | "JPG" | "BMP" | "TGA"`)
  - `mapped`: Boolean (`true`)

### Web Dashboard ↔ DOM Testing Harness
- Container: `.melodia-shell[data-page="texture-catalog"]`
- Title: `#page-title`
- Search Input: `#texture-search`
- Filter Chips Container: `#filter-group`
- Individual Filter Chips: `.filter-chip[data-filter="..."]` (e.g. `data-filter="all"`, `data-filter="BaseColor"`, `data-filter="Normal"`, `data-filter="ORM"`, `data-filter="Roughness"`, `data-filter="Metallic"`, `data-filter="AO"`, `data-filter="Height"`, `data-filter="Emissive"`, `data-filter="Mask"`) with `aria-pressed="true|false"`
- Grid: `#texture-grid`
- Texture Cards: `.texture-card[data-channel="..."][data-family="..."]`
- Card Thumbnail: `img[loading="lazy"]` with `onerror` fallback

## Code Layout
```
teamwork_projects/texture_catalog_dashboard/
├── index.html                      # Standalone Dashboard Single-Page Application
├── styles.css                      # Modern responsive CSS (Dark theme, Tokens, Grid)
├── app.js                          # Vanilla JS controller (Search, Filter, Virtualization)
├── catalog-data.js                 # Standalone JS payload (window.TEXTURE_CATALOG)
├── catalog-data.json               # Raw JSON catalog data
├── assets/
│   ├── favicon.svg                 # Dashboard icon
│   └── placeholder_texture.svg    # Fallback SVG preview
├── scripts/
│   └── map_pbr_textures.py         # Data mapping engine (.uasset -> Imports/ source)
└── README.md                       # Documentation & usage

tests/
└── test_texture_catalog_dashboard.py # E2E & Unit test suite for dashboard & mapping
```
