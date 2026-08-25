"""
Melodia Asset Product Builder
Generates 4 product lines from existing game UI textures and renders:
  1. Twitch Emote Pack (15 emotes × 3 sizes × 3 bg variants = 135 files)
  2. OBS Overlay Pack (6 overlay templates at 1920×1080)
  3. Wallpaper Packs (26 images × 3 phone sizes = 78 files)
  4. Postcards (12 front designs + 1 back template at 300dpi)

Usage: python tools/build_asset_products.py
Requires: Pillow (pip install Pillow)
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import json
import math
import sys
import io

# Fix Windows console encoding for emoji output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ─── CONFIG ───────────────────────────────────────────────────────────────────

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_UI = os.path.join(ROOT, "generated", "assets", "melodia-game-ui")
CHAR_DIR = os.path.join(ROOT, "generated", "assets", "character")
LAND_DIR = os.path.join(ROOT, "generated", "assets", "landscape-loops")
MAT_DIR = os.path.join(ROOT, "generated", "assets", "material-loops")
PRODUCTS = os.path.join(ROOT, "generated", "products")

BRAND_DARK = (20, 26, 48)       # #141A30
BRAND_GOLD = (201, 168, 106)    # #C9A86A
BRAND_PARCHMENT = (245, 240, 232)  # #F5F0E8

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path

def smart_crop_to_ratio(img, target_ratio):
    """Center-crop an image to a target aspect ratio."""
    w, h = img.size
    img_ratio = w / h
    if img_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def center_crop_square(img):
    """Center-crop to square."""
    w, h = img.size
    s = min(w, h)
    left = (w - s) // 2
    top = (h - s) // 2
    return img.crop((left, top, left + s, top + s))

def add_padding(img, padding_px, bg_color=(0, 0, 0, 0)):
    """Add transparent padding around an image."""
    w, h = img.size
    new_w = w + 2 * padding_px
    new_h = h + 2 * padding_px
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    padded = Image.new("RGBA", (new_w, new_h), bg_color)
    padded.paste(img, (padding_px, padding_px), img)
    return padded

def generate_preview_grid(images, cols, cell_size, bg_color=BRAND_DARK):
    """Generate a preview grid from a list of PIL images."""
    rows = math.ceil(len(images) / cols)
    grid_w = cols * cell_size
    grid_h = rows * cell_size
    grid = Image.new("RGB", (grid_w, grid_h), bg_color)
    for idx, img in enumerate(images):
        r, c = divmod(idx, cols)
        resized = img.resize((cell_size, cell_size), Image.LANCZOS)
        if resized.mode == "RGBA":
            grid.paste(resized, (c * cell_size, r * cell_size), resized)
        else:
            grid.paste(resized, (c * cell_size, r * cell_size))
    return grid


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT 1: TWITCH EMOTE PACK
# ═══════════════════════════════════════════════════════════════════════════════

EMOTE_MAP = {
    "T_Melodia_FiligreeGradeHalo_Perfect.png": "melodia_perfect",
    "T_Melodia_FiligreeGradeHalo_Great.png": "melodia_great",
    "T_Melodia_FiligreeGradeHalo_Good.png": "melodia_good",
    "T_Melodia_FiligreeGradeHalo_Miss.png": "melodia_miss",
    "T_Melodia_GradePerfect.png": "melodia_perfect_v2",
    "T_Melodia_GradeGreat.png": "melodia_great_v2",
    "T_Melodia_GradeGood.png": "melodia_good_v2",
    "T_Melodia_GradeMiss.png": "melodia_miss_v2",
    "T_Melodia_ComboBurst.png": "melodia_combo",
    "T_Melodia_SkillRing.png": "melodia_skill",
    "T_Melodia_ElementWheel.png": "melodia_spin",
    "T_Melodia_FiligreeCrest_Finale.png": "melodia_finale",
    "T_Melodia_FiligreeMedallionRosette.png": "melodia_rosette",
    "T_Melodia_SoftMG_SealSP.png": "melodia_seal",
    "T_Melodia_SoftMG_PillowChip.png": "melodia_pillow",
}

EMOTE_SIZES = [(112, 112), (56, 56), (28, 28)]
EMOTE_SIZE_LABELS = ["1x", "2x", "3x"]

def build_twitch_emotes():
    print("\n" + "=" * 60)
    print("📊 BUILDING: Twitch Emote Pack")
    print("=" * 60)

    out_base = ensure_dir(os.path.join(PRODUCTS, "twitch-emotes"))

    for variant in ["transparent", "dark", "gold"]:
        ensure_dir(os.path.join(out_base, variant))

    preview_images = []
    count = 0

    for src_file, emote_name in EMOTE_MAP.items():
        src_path = os.path.join(GAME_UI, src_file)
        if not os.path.exists(src_path):
            print(f"  ⚠️  SKIP: {src_file} not found")
            continue

        img = Image.open(src_path).convert("RGBA")
        img = center_crop_square(img)

        # Add 2px padding for breathing room at small sizes
        img = add_padding(img, 2)

        for size_idx, (tw, th) in enumerate(EMOTE_SIZES):
            resized = img.resize((tw, th), Image.LANCZOS)
            label = EMOTE_SIZE_LABELS[size_idx]

            # Transparent variant
            resized.save(os.path.join(out_base, "transparent", f"{emote_name}_{label}.png"), "PNG")

            # Dark bg variant
            dark_bg = Image.new("RGBA", (tw, th), (*BRAND_DARK, 255))
            dark_bg.paste(resized, (0, 0), resized)
            dark_bg.convert("RGB").save(os.path.join(out_base, "dark", f"{emote_name}_{label}.png"), "PNG")

            # Gold bg variant
            gold_bg = Image.new("RGBA", (tw, th), (*BRAND_GOLD, 51))  # 20% opacity
            gold_bg = Image.alpha_composite(gold_bg, resized)
            gold_bg.convert("RGB").save(os.path.join(out_base, "gold", f"{emote_name}_{label}.png"), "PNG")

            count += 3

        # Collect 1x size for preview grid
        preview_img = img.resize((112, 112), Image.LANCZOS)
        preview_images.append(preview_img)
        print(f"  ✅ {emote_name} (3 sizes × 3 variants = 9 files)")

    # Generate preview grid
    if preview_images:
        grid = generate_preview_grid(preview_images, cols=5, cell_size=112)
        grid.save(os.path.join(out_base, "preview_grid.png"), "PNG")
        print(f"  ✅ preview_grid.png ({len(preview_images)} emotes)")

    # Write README
    readme = f"""# Melodia Twitch Emote Pack

**{len(EMOTE_MAP)} emotes** × 3 sizes × 3 background variants = {count} files

## Emote List

| Name | Meaning |
|------|---------|
| melodia_perfect | PERFECT grade halo — hype emote |
| melodia_great | GREAT grade halo — approval emote |
| melodia_good | GOOD grade halo — chill emote |
| melodia_miss | MISS grade halo — fail emote |
| melodia_combo | Combo burst — hype emote |
| melodia_skill | Skill ring — skill emote |
| melodia_spin | Element wheel — spin emote |
| melodia_finale | Finale crest — finale emote |
| melodia_rosette | Medallion rosette — fancy emote |
| melodia_seal | SoftMG seal — stamp emote |
| melodia_pillow | Pillow chip — cute emote |

## Sizes
- 1x = 112×112 (large)
- 2x = 56×56 (medium)
- 3x = 28×28 (small)

## Background Variants
- `transparent/` — transparent bg (for dark-mode streams)
- `dark/` — #141A30 bg (for light-mode streams)
- `gold/` — gold tint bg (branded feel)

## Install
1. Go to Twitch Dashboard → Settings → Channel → Emotes
2. Upload each size to the corresponding slot
3. Or distribute as a subscriber emote pack

## Credits
Art from Melodia — a stylized rhythm-action game project.
Portfolio: https://fromage3900.github.io/my-site/
"""
    with open(os.path.join(out_base, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"\n🎉 Twitch Emote Pack complete: {count} files in {out_base}/")
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT 2: OBS OVERLAY PACK
# ═══════════════════════════════════════════════════════════════════════════════

CANVAS = (1920, 1080)

def load_ui_texture(name):
    path = os.path.join(GAME_UI, name)
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    return None

def build_gothic_frame():
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    corner = load_ui_texture("T_Melodia_GothicFrameCorner.png")
    rail = load_ui_texture("T_Melodia_GothicFrameRail.png")
    if not corner or not rail:
        return None

    corner_size = int(CANVAS[0] * 0.12)
    corner = corner.resize((corner_size, corner_size), Image.LANCZOS)

    # 4 corners
    canvas.paste(corner, (0, 0), corner)
    canvas.paste(corner.transpose(Image.FLIP_LEFT_RIGHT), (CANVAS[0] - corner_size, 0), corner)
    canvas.paste(corner.transpose(Image.FLIP_TOP_BOTTOM), (0, CANVAS[1] - corner_size), corner)
    canvas.paste(corner.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM),
                 (CANVAS[0] - corner_size, CANVAS[1] - corner_size), corner)

    # Rails
    rail_w = CANVAS[0] - 2 * corner_size
    rail_h_target = max(corner_size // 3, 20)
    rail_scaled = rail.resize((rail_w, rail_h_target), Image.LANCZOS)
    canvas.paste(rail_scaled, (corner_size, 0), rail_scaled)
    canvas.paste(rail_scaled, (corner_size, CANVAS[1] - rail_h_target), rail_scaled)

    return canvas

def build_baroque_frame():
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    corner = load_ui_texture("T_Melodia_FiligreeCornerBaroque.png")
    brace = load_ui_texture("T_Melodia_FiligreeBraceVolute.png")
    if not corner:
        return None

    corner_size = int(CANVAS[0] * 0.14)
    corner = corner.resize((corner_size, corner_size), Image.LANCZOS)

    canvas.paste(corner, (0, 0), corner)
    canvas.paste(corner.transpose(Image.FLIP_LEFT_RIGHT), (CANVAS[0] - corner_size, 0), corner)
    canvas.paste(corner.transpose(Image.FLIP_TOP_BOTTOM), (0, CANVAS[1] - corner_size), corner)
    canvas.paste(corner.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM),
                 (CANVAS[0] - corner_size, CANVAS[1] - corner_size), corner)

    if brace:
        brace_size = int(CANVAS[0] * 0.08)
        brace = brace.resize((brace_size, brace_size), Image.LANCZOS)
        # Top center and bottom center braces
        canvas.paste(brace, ((CANVAS[0] - brace_size) // 2, 0), brace)
        canvas.paste(brace.transpose(Image.FLIP_TOP_BOTTOM),
                     ((CANVAS[0] - brace_size) // 2, CANVAS[1] - brace_size), brace)

    return canvas

def build_lower_third():
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    parchment = load_ui_texture("T_Melodia_SoftMG_Parchment.png")
    divider = load_ui_texture("T_Melodia_FiligreeDividerScroll.png")
    crest = load_ui_texture("T_Melodia_FiligreeCrestBaroque.png")

    bar_h = 120
    bar_y = CANVAS[1] - bar_h - 40

    # Parchment background bar
    if parchment:
        parch = parchment.resize((CANVAS[0], bar_h), Image.LANCZOS)
        # Add dark overlay for readability
        overlay = Image.new("RGBA", (CANVAS[0], bar_h), (*BRAND_DARK, 180))
        parch = Image.alpha_composite(parch, overlay)
        canvas.paste(parch, (0, bar_y), parch)
    else:
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([(0, bar_y), (CANVAS[0], bar_y + bar_h)], fill=(*BRAND_DARK, 200))

    # Divider line at top of bar
    if divider:
        div_w = int(CANVAS[0] * 0.6)
        div_h = 20
        div = divider.resize((div_w, div_h), Image.LANCZOS)
        canvas.paste(div, ((CANVAS[0] - div_w) // 2, bar_y - div_h // 2), div)

    # Crest at center
    if crest:
        crest_size = 60
        crest = crest.resize((crest_size, crest_size), Image.LANCZOS)
        canvas.paste(crest, ((CANVAS[0] - crest_size) // 2, bar_y - crest_size - 5), crest)

    return canvas

def build_alert_box():
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    corner = load_ui_texture("T_Melodia_FiligreeCorner.png")
    parchment = load_ui_texture("T_Melodia_SoftMG_Parchment.png")
    seal = load_ui_texture("T_Melodia_SoftMG_SealSP.png")

    box_w, box_h = 500, 200
    box_x = (CANVAS[0] - box_w) // 2
    box_y = (CANVAS[1] - box_h) // 2

    # Background
    if parchment:
        bg = parchment.resize((box_w, box_h), Image.LANCZOS)
        overlay = Image.new("RGBA", (box_w, box_h), (*BRAND_DARK, 160))
        bg = Image.alpha_composite(bg, overlay)
        canvas.paste(bg, (box_x, box_y), bg)

    # Corners
    if corner:
        c_size = 50
        c = corner.resize((c_size, c_size), Image.LANCZOS)
        canvas.paste(c, (box_x, box_y), c)
        canvas.paste(c.transpose(Image.FLIP_LEFT_RIGHT), (box_x + box_w - c_size, box_y), c)
        canvas.paste(c.transpose(Image.FLIP_TOP_BOTTOM), (box_x, box_y + box_h - c_size), c)
        canvas.paste(c.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM),
                     (box_x + box_w - c_size, box_y + box_h - c_size), c)

    # Seal
    if seal:
        seal_size = 40
        s = seal.resize((seal_size, seal_size), Image.LANCZOS)
        canvas.paste(s, (box_x + box_w - seal_size - 10, box_y + 10), s)

    return canvas

def build_starting_soon():
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    parchment = load_ui_texture("T_Melodia_SoftMG_Parchment.png")
    medallion = load_ui_texture("T_Melodia_FiligreeMedallionRosette.png")
    scroll_edge = load_ui_texture("T_Melodia_SoftMG_ScrollEdge.png")

    # Full parchment background with heavy dark overlay
    if parchment:
        bg = parchment.resize(CANVAS, Image.LANCZOS)
        overlay = Image.new("RGBA", CANVAS, (*BRAND_DARK, 210))
        bg = Image.alpha_composite(bg, overlay)
        canvas = bg

    # Medallion center
    if medallion:
        m_size = 200
        m = medallion.resize((m_size, m_size), Image.LANCZOS)
        canvas.paste(m, ((CANVAS[0] - m_size) // 2, (CANVAS[1] - m_size) // 2 - 60), m)

    # Scroll edges top and bottom
    if scroll_edge:
        edge_w = int(CANVAS[0] * 0.5)
        edge_h = 30
        edge = scroll_edge.resize((edge_w, edge_h), Image.LANCZOS)
        canvas.paste(edge, ((CANVAS[0] - edge_w) // 2, 80), edge)
        canvas.paste(edge.transpose(Image.FLIP_TOP_BOTTOM),
                     ((CANVAS[0] - edge_w) // 2, CANVAS[1] - 80 - edge_h), edge)

    return canvas

def build_scene_transition():
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    batch = load_ui_texture("T_Melodia_FiligreeBatchO_Baroque.png")
    grain = load_ui_texture("T_Melodia_Grain.png")

    # Baroque batch centered
    if batch:
        b_size = int(CANVAS[0] * 0.4)
        b = batch.resize((b_size, b_size), Image.LANCZOS)
        canvas.paste(b, ((CANVAS[0] - b_size) // 2, (CANVAS[1] - b_size) // 2), b)

    # Grain overlay
    if grain:
        g = grain.resize(CANVAS, Image.LANCZOS)
        canvas = Image.alpha_composite(canvas, g)

    return canvas

def build_minimal_corners():
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    corner = load_ui_texture("T_Melodia_FiligreeCorner.png")
    if not corner:
        return None

    c_size = 80
    c = corner.resize((c_size, c_size), Image.LANCZOS)
    canvas.paste(c, (20, 20), c)
    canvas.paste(c.transpose(Image.FLIP_LEFT_RIGHT), (CANVAS[0] - c_size - 20, 20), c)

    return canvas

OVERLAY_BUILDERS = {
    "gothic_frame": build_gothic_frame,
    "baroque_frame": build_baroque_frame,
    "lower_third": build_lower_third,
    "alert_box": build_alert_box,
    "starting_soon": build_starting_soon,
    "scene_transition": build_scene_transition,
    "minimal_corners": build_minimal_corners,
}

def build_obs_overlays():
    print("\n" + "=" * 60)
    print("🖥️  BUILDING: OBS Overlay Pack")
    print("=" * 60)

    out_base = ensure_dir(os.path.join(PRODUCTS, "obs-overlays", "overlays"))
    elements_dir = ensure_dir(os.path.join(PRODUCTS, "obs-overlays", "individual_elements"))

    preview_images = []
    count = 0

    for name, builder in OVERLAY_BUILDERS.items():
        result = builder()
        if result:
            result.save(os.path.join(out_base, f"{name}.png"), "PNG")
            preview_images.append(result.convert("RGB"))
            count += 1
            print(f"  ✅ {name}.png (1920×1080)")
        else:
            print(f"  ⚠️  SKIP: {name} (missing source textures)")

    # Copy individual elements for modular use
    element_categories = {
        "corners": ["T_Melodia_FiligreeCorner.png", "T_Melodia_FiligreeCornerBaroque.png",
                     "T_Melodia_GothicFrameCorner.png"],
        "dividers": ["T_Melodia_FiligreeDivider.png", "T_Melodia_FiligreeDividerScroll.png",
                      "T_Melodia_FiligreeCrest_Finale.png", "T_Melodia_FiligreeCrestBaroque.png"],
        "backgrounds": ["T_Melodia_SoftMG_Parchment.png", "T_Melodia_SheetParchment.png",
                         "T_Melodia_Grain.png"],
        "accents": ["T_Melodia_FiligreeMedallionRosette.png", "T_Melodia_SoftMG_SealSP.png",
                     "T_Melodia_SoftMG_ScrollEdge.png", "T_Melodia_SkillChipBG.png",
                     "T_Melodia_SkillRing.png", "T_Melodia_FiligreeBraceVolute.png",
                     "T_Melodia_FiligreeBatchO_Baroque.png"],
    }

    for category, files in element_categories.items():
        cat_dir = ensure_dir(os.path.join(elements_dir, category))
        for fname in files:
            src = os.path.join(GAME_UI, fname)
            if os.path.exists(src):
                import shutil
                shutil.copy2(src, os.path.join(cat_dir, fname))

    # Preview grid
    if preview_images:
        grid = generate_preview_grid(preview_images, cols=4, cell_size=320)
        grid.save(os.path.join(PRODUCTS, "obs-overlays", "preview_grid.png"), "PNG")
        print(f"  ✅ preview_grid.png ({len(preview_images)} overlays)")

    # README
    readme = f"""# Melodia OBS Overlay Pack

**{count} overlay templates** at 1920×1080 with transparency.

## Overlays

| Name | Description |
|------|-------------|
| gothic_frame | Full webcam border with gothic corners + rails |
| baroque_frame | Ornate border with baroque corners + braces |
| lower_third | Name/title bar with scroll divider + crest |
| alert_box | Popup frame for follows/subs/raids |
| starting_soon | Title card with medallion + scroll edges |
| scene_transition | Full-screen wipe with baroque batch + grain |
| minimal_corners | Subtle corner accents only |

## Individual Elements

The `individual_elements/` folder contains all source textures organized by category:
- `corners/` — corner ornaments (gothic, baroque, filigree)
- `dividers/` — divider lines and crests
- `backgrounds/` — parchment, grain textures
- `accents/` — medallions, seals, rings, braces

## Install (OBS)
1. Copy overlay PNGs to your OBS images folder
2. Add as Image Source in your scene
3. Or import `obs-scene-collection.json` for pre-built scenes

## Install (Streamlabs/Other)
1. Use overlay PNGs as browser source or image layer
2. Individual elements can be arranged in any compositing tool

## Credits
Art from Melodia — a stylized rhythm-action game project.
Portfolio: https://fromage3900.github.io/my-site/
"""
    with open(os.path.join(PRODUCTS, "obs-overlays", "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"\n🎉 OBS Overlay Pack complete: {count} overlays + elements in {PRODUCTS}/obs-overlays/")
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT 3: WALLPAPER PACKS
# ═══════════════════════════════════════════════════════════════════════════════

WALLPAPER_SIZES = {
    "iphone": (1290, 2796),
    "android": (1080, 2400),
    "universal": (1080, 1920),
}

WALLPAPER_PACKS = {
    "01_character_portraits": [
        ("generated/assets/character/melusina_portrait_face.png", "melusina_portrait_face"),
        ("generated/assets/character/melusina_eevee_portrait.png", "melusina_eevee_portrait"),
        ("generated/assets/character/melusina_eevee_front.png", "melusina_eevee_front"),
        ("generated/assets/character/melusina_eevee_three_quarter.png", "melusina_eevee_three_quarter"),
        ("generated/assets/character/melusina_beauty_34.png", "melusina_beauty_34"),
        ("generated/assets/character/melusina_verify_beauty.png", "melusina_verify_beauty"),
    ],
    "02_beauty_plates": [
        ("generated/assets/character/melusina_beauty_nikki_001.png", "melusina_beauty_nikki"),
        ("generated/assets/character/melusina_beauty_void_iri.png", "melusina_beauty_void_iri"),
        ("generated/assets/character/melusina_beauty_jewelry_001.png", "melusina_beauty_jewelry"),
        ("generated/assets/character/melusina_diorama_beauty.png", "melusina_diorama_beauty"),
        ("generated/assets/character/melusina_eevee_glam_20260715c_01.png", "melusina_glam_c01"),
        ("generated/assets/character/melusina_eevee_glam_20260715c_03.png", "melusina_glam_c03"),
    ],
    "03_worlds": [
        ("generated/assets/landscape-loops/WP_SakuraDream_terrain.png", "WP_SakuraDream"),
        ("generated/assets/landscape-loops/WP_SpaceCathedral_terrain.png", "WP_SpaceCathedral"),
        ("generated/assets/landscape-loops/WP_CosmicOrrery_terrain.png", "WP_CosmicOrrery"),
        ("generated/assets/landscape-loops/WP_BaroqueGrotto_terrain.png", "WP_BaroqueGrotto"),
    ],
    "04_materials_cosmic": [
        ("generated/assets/material-loops/MI_Cosmic_AuroraVeil.png", "MI_Cosmic_AuroraVeil"),
        ("generated/assets/material-loops/MI_Cosmic_BlueNebulaA.png", "MI_Cosmic_BlueNebulaA"),
        ("generated/assets/material-loops/MI_Cosmic_EclipseHalo.png", "MI_Cosmic_EclipseHalo"),
        ("generated/assets/material-loops/MI_Cosmic_PurpleNebulaA.png", "MI_Cosmic_PurpleNebulaA"),
        ("generated/assets/material-loops/MI_Cosmic_StarfieldA.png", "MI_Cosmic_StarfieldA"),
        ("generated/assets/material-loops/MI_Cosmic_VoidDeep.png", "MI_Cosmic_VoidDeep"),
    ],
    "05_materials_sdf": [
        ("generated/assets/material-loops/MI_SDF_Aurora_Band.png", "MI_SDF_Aurora_Band"),
        ("generated/assets/material-loops/MI_SDF_CelestialVinyl.png", "MI_SDF_CelestialVinyl"),
        ("generated/assets/material-loops/MI_SDF_IvoryScrollwork.png", "MI_SDF_IvoryScrollwork"),
        ("generated/assets/material-loops/MI_SDF_Nebula_Veil.png", "MI_SDF_Nebula_Veil"),
        ("generated/assets/material-loops/MI_SDF_RosyQuartz.png", "MI_SDF_RosyQuartz"),
        ("generated/assets/material-loops/MI_SDF_VoidStarlight.png", "MI_SDF_VoidStarlight"),
    ],
}

def build_wallpaper_packs():
    print("\n" + "=" * 60)
    print("📱 BUILDING: Wallpaper Packs")
    print("=" * 60)

    out_base = ensure_dir(os.path.join(PRODUCTS, "wallpaper-packs"))
    total = 0

    for pack_name, sources in WALLPAPER_PACKS.items():
        pack_dir = os.path.join(out_base, pack_name)
        pack_count = 0

        for size_name, (tw, th) in WALLPAPER_SIZES.items():
            size_dir = ensure_dir(os.path.join(pack_dir, size_name))
            target_ratio = tw / th

            for src_rel, out_name in sources:
                src_path = os.path.join(ROOT, src_rel)
                if not os.path.exists(src_path):
                    print(f"  ⚠️  SKIP: {src_rel} not found")
                    continue

                img = Image.open(src_path).convert("RGB")
                img = smart_crop_to_ratio(img, target_ratio)
                img = img.resize((tw, th), Image.LANCZOS)

                out_path = os.path.join(size_dir, f"{out_name}.png")
                img.save(out_path, "PNG", quality=95)
                pack_count += 1
                total += 1

        print(f"  ✅ {pack_name}: {pack_count} wallpapers × {len(WALLPAPER_SIZES)} sizes")

    # README
    readme = f"""# Melodia Wallpaper Packs

**5 packs** × **3 phone sizes** = **{total} wallpapers**

## Packs

### 01 Character Portraits
Melusina portrait renders — clean, centered compositions perfect for phone lock screens.

### 02 Beauty Plates
Full beauty renders — iridescent, gothic, and glam variants.

### 03 Worlds
Landscape environments — Sakura Dream (L_SakuraDream), Space Cathedral (L_KaleidoNave), Melusina Stage (L_MelusinasMorning), Fallen Moon / Cosmic Orrery (L_FallenMoon).

### 04 Materials (Cosmic)
Abstract cosmic material renders — aurora veils, nebulae, starfields.

### 05 Materials (SDF)
Ornamental SDF material renders — scrollwork, quartz, void starlight.

## Sizes
- `iphone/` — 1290×2796 (iPhone 14 Pro Max)
- `android/` — 1080×2400 (common Android)
- `universal/` — 1080×1920 (safe minimum)

## Credits
Art from Melodia — a stylized rhythm-action game project.
Portfolio: https://fromage3900.github.io/my-site/
"""
    with open(os.path.join(out_base, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    print(f"\n🎉 Wallpaper Packs complete: {total} files in {out_base}/")
    return total


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT 4: POSTCARDS
# ═══════════════════════════════════════════════════════════════════════════════

POSTCARD_DPI = 300
POSTCARD_SIZE = (1875, 1275)  # 6.25×4.25" with bleed

POSTCARD_FRONTS = [
    ("generated/assets/character/melusina_beauty_34.png", "classic_beauty"),
    ("generated/assets/character/melusina_beauty_nikki_001.png", "nikki_dream"),
    ("generated/assets/character/melusina_beauty_void_iri.png", "void_celestial"),
    ("generated/assets/character/melusina_beauty_jewelry_001.png", "court_formal"),
    ("generated/assets/character/melusina_eevee_glam_20260715c_01.png", "soft_glam"),
    ("generated/assets/character/melusina_eevee_glam_20260715c_05.png", "alt_glam"),
    ("generated/assets/character/melusina_diorama_beauty.png", "diorama"),
    ("generated/assets/character/melusina_water_splash_001.png", "water_dynamic"),
    ("generated/assets/landscape-loops/WP_SakuraDream_terrain.png", "world_sakura"),
    ("generated/assets/landscape-loops/WP_SpaceCathedral_terrain.png", "world_space"),
    ("generated/assets/material-loops/MI_Cosmic_AuroraVeil.png", "material_aurora"),
    ("generated/assets/material-loops/MI_SDF_RosyQuartz.png", "material_quartz"),
]

def build_postcards():
    print("\n" + "=" * 60)
    print("📮 BUILDING: Postcards")
    print("=" * 60)

    fronts_dir = ensure_dir(os.path.join(PRODUCTS, "postcards", "fronts"))
    backs_dir = ensure_dir(os.path.join(PRODUCTS, "postcards", "backs"))
    count = 0

    # Build fronts
    for src_rel, name in POSTCARD_FRONTS:
        src_path = os.path.join(ROOT, src_rel)
        if not os.path.exists(src_path):
            print(f"  ⚠️  SKIP: {src_rel} not found")
            continue

        img = Image.open(src_path).convert("RGB")
        target_ratio = POSTCARD_SIZE[0] / POSTCARD_SIZE[1]
        img = smart_crop_to_ratio(img, target_ratio)
        img = img.resize(POSTCARD_SIZE, Image.LANCZOS)

        # Add thin gold border
        draw = ImageDraw.Draw(img)
        draw.rectangle([(12, 12), (POSTCARD_SIZE[0] - 12, POSTCARD_SIZE[1] - 12)],
                        outline=BRAND_GOLD, width=4)

        # Add subtle "Melodia" text bottom-right
        try:
            font = ImageFont.truetype(os.path.join(ROOT, "BS_GodFile", "NotoMusic-Regular.ttf"), 18)
        except (OSError, IOError):
            font = ImageFont.load_default()
        draw.text((POSTCARD_SIZE[0] - 120, POSTCARD_SIZE[1] - 40), "Melodia",
                   fill=BRAND_GOLD, font=font)

        img.save(os.path.join(fronts_dir, f"{name}_front.png"), "PNG", dpi=(POSTCARD_DPI, POSTCARD_DPI))
        count += 1
        print(f"  ✅ {name}_front.png (300dpi)")

    # Build back template
    back = Image.new("RGB", POSTCARD_SIZE, BRAND_PARCHMENT)
    draw = ImageDraw.Draw(back)

    # Parchment texture overlay (subtle grain)
    grain = load_ui_texture("T_Melodia_Grain.png")
    if grain:
        grain_rgb = grain.resize(POSTCARD_SIZE, Image.LANCZOS).convert("RGB")
        # Blend grain at low opacity
        back = Image.blend(back, grain_rgb, 0.1)
        draw = ImageDraw.Draw(back)

    # Dividing line (center vertical)
    center_x = POSTCARD_SIZE[0] // 2
    draw.line([(center_x, 80), (center_x, POSTCARD_SIZE[1] - 80)], fill=(*BRAND_GOLD, 128), width=2)

    # Address lines (right half)
    try:
        font = ImageFont.truetype(os.path.join(ROOT, "BS_GodFile", "NotoMusic-Regular.ttf"), 16)
    except (OSError, IOError):
        font = ImageFont.load_default()

    for i in range(5):
        y = 300 + i * 80
        draw.line([(center_x + 60, y), (POSTCARD_SIZE[0] - 100, y)], fill=(180, 170, 155), width=1)

    # Stamp area (top-right)
    stamp_margin = 40
    stamp_size = 120
    draw.rectangle([
        (POSTCARD_SIZE[0] - stamp_size - stamp_margin, stamp_margin),
        (POSTCARD_SIZE[0] - stamp_margin, stamp_margin + stamp_size)
    ], outline=(180, 170, 155), width=2)

    # Seal stamp
    seal = load_ui_texture("T_Melodia_SoftMG_SealSP.png")
    if seal:
        seal = seal.resize((80, 80), Image.LANCZOS)
        back.paste(seal.convert("RGB"),
                   (POSTCARD_SIZE[0] - stamp_size - stamp_margin + 20, stamp_margin + 20))

    # URL at bottom
    draw.text((center_x + 60, POSTCARD_SIZE[1] - 60),
               "fromage3900.github.io/my-site", fill=BRAND_GOLD, font=font)

    # "MELODIA" header on left side
    try:
        font_large = ImageFont.truetype(os.path.join(ROOT, "BS_GodFile", "NotoMusic-Regular.ttf"), 28)
    except (OSError, IOError):
        font_large = ImageFont.load_default()
    draw.text((80, 100), "MELODIA", fill=BRAND_GOLD, font=font_large)

    # Message area label
    draw.text((80, 160), "Write your message here...", fill=(180, 170, 155), font=font)

    back.save(os.path.join(backs_dir, "postcard_back.png"), "PNG", dpi=(POSTCARD_DPI, POSTCARD_DPI))
    print(f"  ✅ postcard_back.png (300dpi template)")

    # Preview grid
    preview_imgs = []
    for src_rel, name in POSTCARD_FRONTS:
        path = os.path.join(fronts_dir, f"{name}_front.png")
        if os.path.exists(path):
            preview_imgs.append(Image.open(path))
    if preview_imgs:
        grid = generate_preview_grid(preview_imgs, cols=4, cell_size=400)
        grid.save(os.path.join(PRODUCTS, "postcards", "preview_grid.png"), "PNG")
        print(f"  ✅ preview_grid.png ({len(preview_imgs)} designs)")

    # README
    readme = f"""# Melodia Postcards

**{count} front designs** + 1 back template at 300dpi, print-ready.

## Front Designs

| # | Name | Vibe |
|---|------|------|
| 1 | classic_beauty | Classic Melusina beauty render |
| 2 | nikki_dream | Iridescent Nikki-style |
| 3 | void_celestial | Dark celestial gothic |
| 4 | court_formal | Jeweled court formal |
| 5 | soft_glam | Soft EEVEE glam |
| 6 | alt_glam | Alt glam variant |
| 7 | diorama | Diorama scene |
| 8 | water_dynamic | Dynamic water splash |
| 9 | world_sakura | Sakura Dream world |
| 10 | world_space | Space Cathedral world |
| 11 | material_aurora | Aurora Veil material |
| 12 | material_quartz | Rosy Quartz material |

## Print Specs
- Size: 6×4" (standard postcard)
- Bleed: 0.25" on all sides (included in 1875×1275 at 300dpi)
- Resolution: 300dpi
- Color: RGB (convert to CMYK for professional printing)

## Recommended Print Services
- **Vistaprint** — ~$25-40 for 600 cards (50 each design)
- **Moo** — ~$40-60 premium quality
- **Local print shop** — ~$15-30, fastest turnaround

## Mailing Strategy
- Send to recruiters at target studios
- Include handwritten note referencing specific role
- Pair with hiring dossier / recruiter one-sheet
- Add QR code linking to portfolio

## Credits
Art from Melodia — a stylized rhythm-action game project.
Portfolio: https://fromage3900.github.io/my-site/
"""
    with open(os.path.join(PRODUCTS, "postcards", "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    # Print spec
    spec = f"""# Postcard Print Specification

## Dimensions
- Final size: 6 × 4 inches (152.4 × 101.6 mm)
- Bleed: 0.125" on all sides
- Total with bleed: 6.25 × 4.25 inches
- File size: 1875 × 1275 pixels at 300dpi

## Color
- Source: sRGB
- Print: Convert to CMYK before sending to printer
- Gold accent: #C9A86A (Pantone 7555 C approximate)
- Dark background: #141A30

## File Format
- Fronts: PNG with bleed, 300dpi
- Back: PNG with bleed, 300dpi
- Alternative: Export as PDF/X-1a for professional printing

## Safe Zones
- Keep all text 0.25" from trim edge
- Keep important elements 0.375" from trim edge
"""
    with open(os.path.join(PRODUCTS, "postcards", "print_spec.md"), "w", encoding="utf-8") as f:
        f.write(spec)

    print(f"\n🎉 Postcards complete: {count} fronts + back template in {PRODUCTS}/postcards/")
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("🎵 Melodia Asset Product Builder")
    print("=" * 60)
    print(f"Root: {ROOT}")
    print(f"Output: {PRODUCTS}")
    print()

    # Check dependencies
    try:
        from PIL import Image
        print("✅ Pillow detected")
    except ImportError:
        print("❌ Pillow not found. Install with: pip install Pillow")
        sys.exit(1)

    # Check source dirs
    for d in [GAME_UI, CHAR_DIR, LAND_DIR, MAT_DIR]:
        if os.path.exists(d):
            print(f"✅ {os.path.basename(d)}/ found")
        else:
            print(f"⚠️  {os.path.basename(d)}/ not found — some products may be incomplete")

    ensure_dir(PRODUCTS)

    # Build all products
    results = {}
    results["twitch_emotes"] = build_twitch_emotes()
    results["obs_overlays"] = build_obs_overlays()
    results["wallpapers"] = build_wallpaper_packs()
    results["postcards"] = build_postcards()

    # Summary
    print("\n" + "=" * 60)
    print("📦 PRODUCTION SUMMARY")
    print("=" * 60)
    total_files = sum(results.values())
    for product, count in results.items():
        print(f"  {product}: {count} files")
    print(f"\n  TOTAL: {total_files} files generated")
    print(f"  Output: {PRODUCTS}/")
    print()
    print("Next steps:")
    print("  1. Review generated files in each product folder")
    print("  2. Check README.md in each folder for distribution instructions")
    print("  3. Zip each product folder for Gumroad upload")
    print("  4. Post previews on social media")
    print()

    # Write summary JSON
    summary = {
        "generated": str(PRODUCTS),
        "products": results,
        "total_files": total_files,
    }
    with open(os.path.join(PRODUCTS, "build_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return 0

if __name__ == "__main__":
    sys.exit(main())