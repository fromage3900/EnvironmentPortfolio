# PBR Texture Catalog Dashboard

Standalone, zero-dependency single-page application that visualizes the mapped
PBR texture catalog (3,537 textures across 11 PBR channels). Open `index.html`
directly in a browser (`file://` works — data loads from the local
`catalog-data.js`).

## Files

- `index.html` — semantic dashboard shell (header, search, filter chips, grid)
- `styles.css` — dark theme, CSS design tokens, responsive grid, `content-visibility`
- `app.js` — search + channel filtering, chunked/IntersectionObserver DOM render
- `catalog-data.js` / `catalog-data.json` — generated catalog payload (from `scripts/`)
- `scripts/map_pbr_textures.py` — data mapping engine (`.uasset` → `Imports/` source)
- `scripts/verify_catalog_data.py` — data integrity verification
- `assets/` — favicon + placeholder thumbnail (SVG `onerror` fallback)

## Verify the data layer

```powershell
python scripts/verify_catalog_data.py
```

## Run the E2E test suite

```powershell
python -m pytest tests/test_texture_catalog_dashboard.py -q
```

The suite (via `wix/tests/dom_harness.py`) asserts the DOM/CSS/JS contracts,
data mapping thresholds, filter isolation, asset paths, and zero-slop hygiene.

## Channels covered

BaseColor · Normal · ORM · Roughness · Metallic · AO · Height · Emissive · Mask ·
Specialty · UI