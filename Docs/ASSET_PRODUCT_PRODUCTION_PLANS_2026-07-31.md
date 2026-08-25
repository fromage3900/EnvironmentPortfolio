# Asset Product Production Plans — Ready-to-Ship Packages

**Date:** 2026-07-31
**Purpose:** Concrete production plans for 4 zero-new-asset products using existing renders/textures
**Rule:** No new 3D renders, no gameplay changes. Polish + package what exists.

---

## 📊 Twitch Emote Pack (#55)

### What You Have
**Source files in `generated/assets/melodia-game-ui/`:**
- `T_Melodia_FiligreeGradeHalo_Perfect.png` → **"PERFECT" hype emote**
- `T_Melodia_FiligreeGradeHalo_Great.png` → **"GREAT" approval emote**
- `T_Melodia_FiligreeGradeHalo_Good.png` → **"GOOD" chill emote**
- `T_Melodia_FiligreeGradeHalo_Miss.png` → **"MISS" fail emote**
- `T_Melodia_GradePerfect.png` / `_A.png` → alt variants
- `T_Melodia_GradeGreat.png` / `_A.png` → alt variants
- `T_Melodia_GradeGood.png` / `_A.png` → alt variants
- `T_Melodia_GradeMiss.png` / `_A.png` → alt variants
- `T_Melodia_ComboBurst.png` → **"COMBO" hype emote**
- `T_Melodia_SkillRing.png` → **"SKILL" emote**
- `T_Melodia_ElementWheel.png` → **"SPIN" emote**
- `T_Melodia_FiligreeCrest_Finale.png` → **"FINALE" emote**
- `T_Melodia_FiligreeMedallionRosette.png` → **"ROSETTE" emote**
- `T_Melodia_SoftMG_SealSP.png` → **"SEAL" emote**
- `T_Melodia_SoftMG_PillowChip.png` → **"PILLOW" cute emote**

**Total: 15+ emote-ready textures**

### Production Steps

#### Step 1: Resize to Twitch Specs
Twitch emotes need 3 sizes: **112x112** (large), **56x56** (medium), **28x28** (small)

```python
# tools/build_twitch_emotes.py
from PIL import Image
import os

SOURCE_DIR = "generated/assets/melodia-game-ui"
OUTPUT_DIR = "generated/products/twitch-emotes"
SIZES = [(112, 112), (56, 56), (28, 28)]

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

os.makedirs(OUTPUT_DIR, exist_ok=True)

for src_file, emote_name in EMOTE_MAP.items():
    img = Image.open(os.path.join(SOURCE_DIR, src_file)).convert("RGBA")
    
    # Center-crop to square (take center 80% to avoid edge artifacts)
    w, h = img.size
    crop_size = min(w, h)
    left = (w - crop_size) // 2
    top = (h - crop_size) // 2
    img = img.crop((left, top, left + crop_size, top + crop_size))
    
    for size_idx, (tw, th) in enumerate(SIZES):
        resized = img.resize((tw, th), Image.LANCZOS)
        size_label = ["1x", "2x", "3x"][size_idx]
        out_path = os.path.join(OUTPUT_DIR, f"{emote_name}_{size_label}.png")
        resized.save(out_path, "PNG")
        print(f"  ✅ {emote_name}_{size_label}.png ({tw}x{th})")

print(f"\n🎉 {len(EMOTE_MAP) * 3} emotes generated in {OUTPUT_DIR}/")
```

#### Step 2: Background Options
Twitch emotes need to read at small sizes. Generate 3 variants per emote:
- **Transparent** (default, for dark-mode streamers)
- **Dark bg** (#141A30 surface-base, for light-mode streams)
- **Gold bg** (#C9A86A at 20% opacity, branded feel)

#### Step 3: Package
```
generated/products/twitch-emotes/
├── README.md (emote names, preview grid, install instructions)
├── preview_grid.png (all emotes at 112x112 in a grid)
├── dark/
│   ├── melodia_perfect_1x.png ... _3x.png
│   └── ...
├── transparent/
│   ├── melodia_perfect_1x.png ... _3x.png
│   └── ...
└── gold/
    ├── melodia_perfect_1x.png ... _3x.png
    └── ...
```

#### Step 4: Distribution
- **Free:** Upload as a zip on Gumroad (name-your-price, $0 minimum)
- **Portfolio:** Add preview grid to `wix/social-kit.html`
- **Twitch:** Submit via Twitch dashboard (requires affiliate or use as channel emotes)
- **Marketing:** Post preview grid on Twitter with #TwitchEmotes #GameDev

### Polish Checklist
- [ ] Run resize script
- [ ] Check each emote at 28x28 (must be readable)
- [ ] Add 2px padding around each emote for breathing room
- [ ] Generate preview grid image
- [ ] Write README with emote names + meanings
- [ ] Zip and upload to Gumroad
- [ ] Post preview on social media

---

## 🖥️ OBS Overlay Pack (#54)

### What You Have
**Source files in `generated/assets/melodia-game-ui/`:**

**Frame Elements (for webcam borders, alert boxes):**
- `T_Melodia_FiligreeCorner.png` → corner ornament
- `T_Melodia_FiligreeCornerBaroque.png` → baroque corner
- `T_Melodia_FiligreeBraceVolute.png` → scroll brace
- `T_Melodia_FiligreeBatchO_Baroque.png` → baroque batch
- `T_Melodia_GothicFrameCorner.png` → gothic corner
- `T_Melodia_GothicFrameRail.png` → gothic rail (horizontal/vertical)

**Divider Elements (for section separators, lower thirds):**
- `T_Melodia_FiligreeDivider.png` → straight divider
- `T_Melodia_FiligreeDividerScroll.png` → scroll divider
- `T_Melodia_FiligreeCrest_Finale.png` → center crest
- `T_Melodia_FiligreeCrestBaroque.png` → baroque crest

**Background Elements (for panels, text boxes):**
- `T_Melodia_SoftMG_Parchment.png` → parchment background
- `T_Melodia_SheetParchment.png` → sheet parchment
- `T_Melodia_Grain.png` → grain texture overlay

**Accent Elements:**
- `T_Melodia_FiligreeMedallionRosette.png` → medallion
- `T_Melodia_SoftMG_SealSP.png` → seal
- `T_Melodia_SoftMG_ScrollEdge.png` → scroll edge
- `T_Melodia_SkillChipBG.png` → chip background
- `T_Melodia_SkillRing.png` → ring accent

**Total: 20+ overlay-ready textures**

### Production Steps

#### Step 1: Define Overlay Templates
Create 6 overlay layouts using the filigree elements:

| Overlay | Description | Elements Used |
|---------|-------------|---------------|
| **Gothic Frame** | Full webcam border with gothic corners + rails | GothicFrameCorner ×4 + GothicFrameRail ×4 |
| **Baroque Frame** | Ornate webcam border with baroque corners | FiligreeCornerBaroque ×4 + FiligreeBraceVolute ×4 |
| **Lower Third** | Name/title bar with scroll divider + crest | FiligreeDividerScroll + FiligreeCrestBaroque + Parchment bg |
| **Alert Box** | Popup frame for follows/subs/raids | FiligreeCorner ×4 + SoftMG_Parchment bg + SealSP |
| **Scene Transition** | Full-screen wipe with filigree batch | FiligreeBatchO_Baroque + Grain overlay |
| **Starting Soon** | Title card with medallion + parchment | SoftMG_Parchment + MedallionRosette + ScrollEdge |

#### Step 2: Create OBS-Ready PNGs
Each overlay needs to be a **1920x1080 PNG with transparency** (32-bit).

```python
# tools/build_obs_overlays.py
from PIL import Image, ImageDraw
import os

SOURCE_DIR = "generated/assets/melodia-game-ui"
OUTPUT_DIR = "generated/products/obs-overlays"
CANVAS = (1920, 1080)

# Example: Gothic Frame overlay
def build_gothic_frame():
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    
    corner = Image.open(f"{SOURCE_DIR}/T_Melodia_GothicFrameCorner.png").convert("RGBA")
    rail_h = Image.open(f"{SOURCE_DIR}/T_Melodia_GothicFrameRail.png").convert("RGBA")
    
    # Scale corner to ~15% of canvas width
    corner_size = int(CANVAS[0] * 0.15)
    corner = corner.resize((corner_size, corner_size), Image.LANCZOS)
    
    # Place 4 corners
    canvas.paste(corner, (0, 0), corner)  # top-left
    canvas.paste(corner.transpose(Image.FLIP_LEFT_RIGHT), (CANVAS[0] - corner_size, 0), corner)  # top-right
    canvas.paste(corner.transpose(Image.FLIP_TOP_BOTTOM), (0, CANVAS[1] - corner_size), corner)  # bottom-left
    canvas.paste(corner.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM), 
                 (CANVAS[0] - corner_size, CANVAS[1] - corner_size), corner)  # bottom-right
    
    # Stretch rails between corners
    rail_width = CANVAS[0] - 2 * corner_size
    rail_h_scaled = rail_h.resize((rail_width, int(rail_h.size[1] * corner_size / rail_h.size[0])), Image.LANCZOS)
    canvas.paste(rail_h_scaled, (corner_size, 0), rail_h_scaled)  # top
    canvas.paste(rail_h_scaled, (corner_size, CANVAS[1] - rail_h_scaled.size[1]), rail_h_scaled)  # bottom
    
    return canvas

# Run for each overlay type
overlays = {
    "gothic_frame": build_gothic_frame,
    # ... other overlay builders
}

os.makedirs(OUTPUT_DIR, exist_ok=True)
for name, builder in overlays.items():
    result = builder()
    result.save(f"{OUTPUT_DIR}/{name}.png", "PNG")
    print(f"  ✅ {name}.png (1920x1080)")
```

#### Step 3: Create OBS Scene Collection
Export an OBS scene collection JSON that pre-arranges the overlays:
- Scene: "Just Chatting" → Gothic Frame + Lower Third
- Scene: "Gameplay" → Minimal corner accents
- Scene: "Starting Soon" → Starting Soon card
- Scene: "BRB" → Alert box template

#### Step 4: Package
```
generated/products/obs-overlays/
├── README.md (overlay names, preview, OBS import instructions)
├── preview_grid.png (all overlays as thumbnails)
├── overlays/
│   ├── gothic_frame.png
│   ├── baroque_frame.png
│   ├── lower_third.png
│   ├── alert_box.png
│   ├── scene_transition.png
│   └── starting_soon.png
├── obs-scene-collection.json (importable OBS config)
└── individual_elements/
    ├── corners/ (all corner variants)
    ├── dividers/ (all divider variants)
    ├── backgrounds/ (parchment, grain)
    └── accents/ (medallions, seals, rings)
```

#### Step 5: Distribution
- **Free/Paid:** Gumroad zip (free basic pack, paid full pack with individual elements)
- **Portfolio:** Preview on website
- **Marketing:** Post overlay examples on Twitter with #OBS #StreamOverlay #GameDev

### Polish Checklist
- [ ] Build all 6 overlay templates as 1920x1080 PNGs
- [ ] Test each overlay in OBS at actual stream resolution
- [ ] Verify transparency compositing looks correct
- [ ] Create OBS scene collection JSON
- [ ] Generate preview grid
- [ ] Write README with import instructions
- [ ] Package individual elements for modularity
- [ ] Zip and upload to Gumroad

---

## 📱 Wallpaper Packs (#52)

### What You Have
**Source renders in `generated/assets/`:**

**Character (phone-ready portraits):**
- `character/melusina_portrait_face.png`
- `character/melusina_eevee_portrait.png`
- `character/melusina_eevee_front.png`
- `character/melusina_eevee_three_quarter.png`
- `character/melusina_beauty_34.png`
- `character/melusina_beauty_nikki_001.png`
- `character/melusina_beauty_void_iri.png`
- `character/melusina_beauty_jewelry_001.png`
- `character/melusina_verify_beauty.png`
- `character/melusina_diorama_beauty.png`

**Landscape (phone backgrounds):**
- `landscape-loops/WP_SakuraDream_terrain.png`
- `landscape-loops/WP_SpaceCathedral_terrain.png`
- `landscape-loops/WP_CosmicOrrery_terrain.png`
- `landscape-loops/WP_BaroqueGrotto_terrain.png`

**Material (abstract backgrounds):**
- `material-loops/MI_Cosmic_AuroraVeil.png`
- `material-loops/MI_Cosmic_BlueNebulaA.png`
- `material-loops/MI_Cosmic_EclipseHalo.png`
- `material-loops/MI_Cosmic_PurpleNebulaA.png`
- `material-loops/MI_Cosmic_StarfieldA.png`
- `material-loops/MI_Cosmic_VoidDeep.png`
- `material-loops/MI_SDF_Aurora_Band.png`
- `material-loops/MI_SDF_CelestialVinyl.png`
- `material-loops/MI_SDF_IvoryScrollwork.png`
- `material-loops/MI_SDF_Nebula_Veil.png`
- `material-loops/MI_SDF_RosyQuartz.png`
- `material-loops/MI_SDF_VoidStarlight.png`

**Total: 26+ wallpaper-ready images**

### Production Steps

#### Step 1: Crop to Phone Specs
Standard phone wallpaper sizes:
- **iPhone:** 1170x2532 (or 1290x2796 for Pro Max)
- **Android:** 1080x2400 (common)
- **Universal:** 1080x1920 (safe minimum)

Generate 3 sizes per image.

```python
# tools/build_wallpaper_packs.py
from PIL import Image
import os

OUTPUT_DIR = "generated/products/wallpaper-packs"
SIZES = {
    "iphone": (1290, 2796),
    "android": (1080, 2400),
    "universal": (1080, 1920),
}

# Categorize sources into packs
PACKS = {
    "01_character_portraits": [
        "generated/assets/character/melusina_portrait_face.png",
        "generated/assets/character/melusina_eevee_portrait.png",
        "generated/assets/character/melusina_eevee_front.png",
        "generated/assets/character/melusina_eevee_three_quarter.png",
        "generated/assets/character/melusina_beauty_34.png",
        "generated/assets/character/melusina_verify_beauty.png",
    ],
    "02_beauty_plates": [
        "generated/assets/character/melusina_beauty_nikki_001.png",
        "generated/assets/character/melusina_beauty_void_iri.png",
        "generated/assets/character/melusina_beauty_jewelry_001.png",
        "generated/assets/character/melusina_diorama_beauty.png",
    ],
    "03_worlds": [
        "generated/assets/landscape-loops/WP_SakuraDream_terrain.png",
        "generated/assets/landscape-loops/WP_SpaceCathedral_terrain.png",
        "generated/assets/landscape-loops/WP_CosmicOrrery_terrain.png",
        "generated/assets/landscape-loops/WP_BaroqueGrotto_terrain.png",
    ],
    "04_materials_cosmic": [
        "generated/assets/material-loops/MI_Cosmic_AuroraVeil.png",
        "generated/assets/material-loops/MI_Cosmic_BlueNebulaA.png",
        "generated/assets/material-loops/MI_Cosmic_EclipseHalo.png",
        "generated/assets/material-loops/MI_Cosmic_PurpleNebulaA.png",
        "generated/assets/material-loops/MI_Cosmic_StarfieldA.png",
        "generated/assets/material-loops/MI_Cosmic_VoidDeep.png",
    ],
    "05_materials_sdf": [
        "generated/assets/material-loops/MI_SDF_Aurora_Band.png",
        "generated/assets/material-loops/MI_SDF_CelestialVinyl.png",
        "generated/assets/material-loops/MI_SDF_IvoryScrollwork.png",
        "generated/assets/material-loops/MI_SDF_Nebula_Veil.png",
        "generated/assets/material-loops/MI_SDF_RosyQuartz.png",
        "generated/assets/material-loops/MI_SDF_VoidStarlight.png",
    ],
}

for pack_name, sources in PACKS.items():
    for size_name, (tw, th) in SIZES.items():
        pack_dir = os.path.join(OUTPUT_DIR, pack_name, size_name)
        os.makedirs(pack_dir, exist_ok=True)
        
        for src_path in sources:
            img = Image.open(src_path).convert("RGB")
            
            # Smart crop: center-crop to target aspect ratio, then resize
            target_ratio = tw / th
            img_ratio = img.size[0] / img.size[1]
            
            if img_ratio > target_ratio:
                # Image is wider — crop sides
                new_w = int(img.size[1] * target_ratio)
                left = (img.size[0] - new_w) // 2
                img = img.crop((left, 0, left + new_w, img.size[1]))
            else:
                # Image is taller — crop top/bottom
                new_h = int(img.size[0] / target_ratio)
                top = (img.size[1] - new_h) // 2
                img = img.crop((0, top, img.size[0], top + new_h))
            
            img = img.resize((tw, th), Image.LANCZOS)
            
            filename = os.path.basename(src_path)
            img.save(os.path.join(pack_dir, filename), "PNG", quality=95)
    
    print(f"  ✅ Pack '{pack_name}': {len(sources)} wallpapers × {len(SIZES)} sizes")

print(f"\n🎉 All wallpaper packs generated in {OUTPUT_DIR}/")
```

#### Step 2: Add Branding (Subtle)
Add a tiny Melodia watermark in the bottom-right corner of each wallpaper:
- 20px from edge
- Gold (#C9A86A) at 30% opacity
- Small "Melodia" text or seal icon

#### Step 3: Create Preview Images
For each pack, generate a preview showing all wallpapers as phone mockups.

#### Step 4: Package
```
generated/products/wallpaper-packs/
├── README.md (pack descriptions, preview, install instructions)
├── preview_all.png (grid of all packs)
├── 01_character_portraits/
│   ├── iphone/ (6 wallpapers at 1290x2796)
│   ├── android/ (6 wallpapers at 1080x2400)
│   └── universal/ (6 wallpapers at 1080x1920)
├── 02_beauty_plates/
│   ├── iphone/ ...
│   ├── android/ ...
│   └── universal/ ...
├── 03_worlds/ ...
├── 04_materials_cosmic/ ...
└── 05_materials_sdf/ ...
```

#### Step 5: Distribution
- **Free pack:** Characters only (teaser)
- **Paid pack:** All 5 packs ($3-5 on Gumroad)
- **Email signup incentive:** Free pack in exchange for email
- **Social:** Post phone mockups on Instagram/Twitter

### Polish Checklist
- [ ] Run crop/resize script for all 26 sources × 3 sizes
- [ ] Check each wallpaper on actual phone (transfer test)
- [ ] Add subtle watermark
- [ ] Generate phone mockup previews
- [ ] Write README with pack descriptions
- [ ] Create Gumroad listings (free + paid)
- [ ] Set up email signup landing page

---

## 📮 Postcards (#68)

### What You Have
Same source renders as wallpaper packs, plus:
- `T_Melodia_SoftMG_Parchment.png` → postcard back texture
- `T_Melodia_SoftMG_SealSP.png` → wax seal stamp
- Material palette data (from Color Story Generator, once built)

### Production Steps

#### Step 1: Design Postcard Layout
Standard postcard: **6x4 inches** (1800x1200px at 300dpi)

**Front:**
- Full-bleed render (bleed area: 1875x1275px at 300dpi)
- Optional: thin gold border (2px, #C9A86A)
- Optional: "Melodia" wordmark bottom-right

**Back:**
- Left half: message area (parchment texture background)
- Right half: address area with lines
- Top-right corner: seal stamp (`T_Melodia_SoftMG_SealSP.png`)
- Bottom: small "fromage3900.github.io/my-site" URL

#### Step 2: Generate Front Designs
One postcard per hero render. Recommended 12 designs:

| # | Front Image | Vibe |
|---|-------------|------|
| 1 | melusina_beauty_34 | Classic beauty |
| 2 | melusina_beauty_nikki_001 | Iridescent dream |
| 3 | melusina_beauty_void_iri | Dark celestial |
| 4 | melusina_beauty_jewelry_001 | Court formal |
| 5 | melusina_eevee_glam_20260715c_01 | Soft glam |
| 6 | melusina_eevee_glam_20260715c_05 | Alt glam |
| 7 | melusina_diorama_beauty | Diorama scene |
| 8 | melusina_water_splash_001 | Dynamic water |
| 9 | WP_SakuraDream_terrain | World: Sakura |
| 10 | WP_SpaceCathedral_terrain | World: Space |
| 11 | MI_Cosmic_AuroraVeil | Material: Aurora |
| 12 | MI_SDF_RosyQuartz | Material: Quartz |

#### Step 3: Print-Ready Output
```python
# tools/build_postcards.py
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = "generated/products/postcards"
DPI = 300
FRONT_SIZE = (1875, 1275)  # 6.25x4.25" with bleed
BACK_SIZE = (1875, 1275)

# Front designs
FRONTS = [
    ("generated/assets/character/melusina_beauty_34.png", "classic_beauty"),
    ("generated/assets/character/melusina_beauty_nikki_001.png", "nikki_dream"),
    # ... 10 more
]

os.makedirs(f"{OUTPUT_DIR}/fronts", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/backs", exist_ok=True)

for src_path, name in FRONTS:
    img = Image.open(src_path).convert("RGB")
    # Smart crop to 6:4 aspect ratio
    # ... (same crop logic as wallpaper)
    img = img.resize(FRONT_SIZE, Image.LANCZOS)
    
    # Optional: add thin gold border
    draw = ImageDraw.Draw(img)
    draw.rectangle([(10, 10), (FRONT_SIZE[0]-10, FRONT_SIZE[1]-10)], outline="#C9A86A", width=3)
    
    img.save(f"{OUTPUT_DIR}/fronts/{name}_front.png", "PNG", dpi=(DPI, DPI))
    print(f"  ✅ {name}_front.png")

# Back design (one template, reuse for all)
back = Image.new("RGB", BACK_SIZE, "#F5F0E8")  # parchment base
# Add parchment texture overlay
# Add address lines
# Add seal stamp
# Add URL
back.save(f"{OUTPUT_DIR}/backs/postcard_back.png", "PNG", dpi=(DPI, DPI))
print(f"  ✅ postcard_back.png (template)")
```

#### Step 4: Print Options

| Service | Cost (12 designs × 50 each) | Quality | Turnaround |
|---------|---------------------------|---------|------------|
| **Vistaprint** | ~$25-40 | Good | 3-5 days |
| **Moo** | ~$40-60 | Premium | 5-7 days |
| **Local print shop** | ~$15-30 | Varies | 1-2 days |
| **Blurb** | ~$30-50 | Good | 5-7 days |

**Recommendation:** Start with Vistaprint standard postcards, 50 of each design (600 total). Cost: ~$30.

#### Step 5: Package for Distribution
```
generated/products/postcards/
├── README.md (design descriptions, print instructions)
├── preview_grid.png (all 12 fronts as thumbnails)
├── fronts/ (12 print-ready PNGs at 300dpi)
├── backs/ (1 back template at 300dpi)
├── print_spec.md (bleed, DPI, color profile notes)
└── mailing_list.md (recruiter addresses to mail to)
```

#### Step 6: Mailing Strategy
**Who to send to:**
- Recruiters at target studios (Digital Extreme, Infold, etc.)
- Include a handwritten note referencing the specific role
- Pair with the hiring dossier / recruiter one-sheet

**What to include:**
- 3-5 postcards (variety pack)
- Handwritten note
- QR code linking to portfolio
- Optional: small sticker or patch (if you have them)

### Polish Checklist
- [ ] Design front layouts for all 12 renders
- [ ] Design back template (parchment + lines + seal + URL)
- [ ] Export all at 300dpi with bleed
- [ ] Soft-proof colors (RGB → CMYK conversion check)
- [ ] Order test print (5 copies) before full run
- [ ] Write personalized notes for each recipient
- [ ] Mail to recruiter list
- [ ] Post photos of physical postcards on social media

---

## 📦 MASTER PRODUCTION TIMELINE

### Week 1: Digital Products (Zero Cost)
| Day | Task | Product |
|-----|------|---------|
| Mon | Run Twitch emote resize script | Emote Pack |
| Mon | Generate preview grid | Emote Pack |
| Tue | Upload to Gumroad + test purchase flow | Emote Pack |
| Tue | Run wallpaper crop script | Wallpaper Packs |
| Wed | Generate phone mockup previews | Wallpaper Packs |
| Wed | Upload free pack to Gumroad | Wallpaper Packs |
| Thu | Build OBS overlay templates | OBS Pack |
| Thu | Test in OBS at stream resolution | OBS Pack |
| Fri | Package OBS overlays + scene collection | OBS Pack |
| Fri | Upload all 3 digital products to Gumroad | All |

### Week 2: Physical Products (Small Investment)
| Day | Task | Product |
|-----|------|---------|
| Mon | Design postcard fronts (12 designs) | Postcards |
| Tue | Design postcard back template | Postcards |
| Tue | Export print-ready files at 300dpi | Postcards |
| Wed | Order test print (Vistaprint, 5 copies) | Postcards |
| Wed | Post digital product launch on social | All |
| Thu | Receive test prints, check quality | Postcards |
| Thu | Order full run (600 postcards, ~$30) | Postcards |
| Fri | Write recruiter mailing list | Postcards |
| Fri | Prepare handwritten notes | Postcards |

### Week 3: Distribution
| Day | Task | Product |
|-----|------|---------|
| Mon | Receive postcards, assemble mailers | Postcards |
| Mon | Mail to first batch of recruiters | Postcards |
| Tue | Post product previews on Twitter/ArtStation | All |
| Tue | Share Gumroad links in game dev communities | All |
| Wed | Mail second batch of recruiters | Postcards |
| Wed | Monitor Gumroad analytics, adjust pricing | All |
| Thu | Post "making of" thread for each product | All |
| Fri | Review: what sold, what got traction, iterate | All |

---

## 💰 REVENUE PROJECTIONS (Conservative)

| Product | Price | Monthly Sales | Monthly Revenue |
|---------|-------|---------------|-----------------|
| Twitch Emote Pack | $0+ (name your price) | 20 downloads × $2 avg | $40 |
| OBS Overlay Pack | $5 | 10 sales | $50 |
| Wallpaper Pack (full) | $3 | 15 sales | $45 |
| Wallpaper Pack (free) | $0 | 50 downloads | $0 (email list) |
| Postcards (physical) | N/A (marketing) | 20 mailers | Career ROI |
| **Total** | | | **~$135/mo** |

Not life-changing money, but: **the real value is portfolio presence + recruiter touchpoints + community building.**

---

**End of Production Plans**