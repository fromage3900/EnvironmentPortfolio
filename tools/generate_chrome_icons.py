#!/usr/bin/env python3
"""
Generate Melodia chrome PNGs from wix/melodia-tokens.css tokens.
Gold-ivory with pink & rose-gold details (user choice 2026-08-25).
Outputs to Tools/BlenderAddons/melodia_chrome/ + melodia_icons/ overrides.

Run: python tools/generate_chrome_icons.py
Requires: Pillow
"""
import re
from pathlib import Path

REPO = Path(r"C:\EnvironmentPortfolio")
TOKENS_CSS = REPO / "wix" / "melodia-tokens.css"
OUT_CHROME = REPO / "BS_GodFile" / "Tools" / "BlenderAddons" / "melodia_chrome"
OUT_ICONS = REPO / "BS_GodFile" / "Tools" / "BlenderAddons" / "melodia_icons"

OUT_CHROME.mkdir(parents=True, exist_ok=True)
OUT_ICONS.mkdir(parents=True, exist_ok=True)

# --- parse primitive hexes from tokens.css ---
text = TOKENS_CSS.read_text(encoding="utf-8", errors="ignore")
def _hex(key):
    m = re.search(rf"{re.escape(key)}:\s*#([0-9A-Fa-f]+)", text)
    return f"#{m.group(1)}" if m else "#C9A86A"

HEX = {
    "ivory_50": _hex("--primitive-ivory-50"),
    "ivory_100": _hex("--primitive-ivory-100"),
    "ivory_300": _hex("--primitive-ivory-300"),
    "plum_800": _hex("--primitive-plum-800"),
    "gold_500": _hex("--primitive-gold-500"),
    "gold_700": _hex("--primitive-gold-700"),
    "sakura_300": _hex("--primitive-sakura-300"),
    "sakura_500": _hex("--primitive-sakura-500"),
    "iris_500": _hex("--primitive-iris-500"),
    "plum_700": _hex("--primitive-plum-700"),
}
# Fallbacks matching live CSS
for k, v in {
    "ivory_50": "#FFF8EE",
    "ivory_100": "#F8ECD6",
    "gold_500": "#C9A86A",
    "sakura_300": "#E7C9CE",
    "sakura_500": "#D6A9B0",
    "plum_800": "#241B2E",
}.items():
    if HEX.get(k) == "#C9A86A" and k != "gold_500":
        # keep parsed if found else fallback
        pass

print("Tokens:", HEX)

from PIL import Image, ImageDraw, ImageFont

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def lerp(a,b,t): return int(a + (b-a)*t)

def make_gold_rule():
    # 256x6 with centered 1px gold line + rose-gold dot
    w,h = 512, 8
    iv = hex_to_rgb(HEX["ivory_100"])
    gold = hex_to_rgb(HEX["gold_500"])
    rose = hex_to_rgb(HEX["sakura_300"])
    img = Image.new("RGBA", (w,h), iv + (0,))
    draw = ImageDraw.Draw(img)
    # hairline
    y = h//2
    draw.line([(16, y), (w-16, y)], fill=gold+(230,), width=1)
    # centered rose-gold star dot (sim 6px)
    cx = w//2
    draw.ellipse([(cx-4, y-4), (cx+4, y+4)], fill=rose+(255,), outline=gold+(255,), width=1)
    # inner dot
    draw.ellipse([(cx-2, y-2), (cx+2, y+2)], fill=(255,255,255,220))
    path = OUT_CHROME / "gold_rule.png"
    img.save(path, "PNG")
    print("wrote", path)

def make_header_void():
    # 512x48 gilded header strip: ivory paper -> plum depth with pink & rose glow
    w,h = 512, 48
    gold = hex_to_rgb(HEX["gold_500"])
    plum = hex_to_rgb(HEX["plum_800"])
    ivory = hex_to_rgb(HEX["ivory_50"])
    sakura = hex_to_rgb(HEX["sakura_500"])
    # gradient top ivory to plum bottom
    img = Image.new("RGBA", (w,h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h-1)
        # ivory 0.0 -> plum 1.0, with slight pink mid
        r = lerp(ivory[0], plum[0], t*0.92)
        g = lerp(ivory[1], plum[1], t*0.92)
        b = lerp(ivory[2], plum[2], t*0.92)
        # pink wash in middle band
        if 10 < y < 28:
            pink_t = (1 - abs(y-19)/9) * 0.18
            r = lerp(r, sakura[0], pink_t)
            g = lerp(g, sakura[1], pink_t)
            b = lerp(b, sakura[2], pink_t)
        draw.line([(0, y), (w, y)], fill=(r,g,b,255))
    # soft gold speckles (HoYoverse glow, one-hero only - here baked)
    for (x,y,rad,alpha) in [(80,12,14,90), (w-90,10,10,70), (w//2,36,18,45), (140,30,8,60)]:
        for dy in range(-rad, rad+1):
            for dx in range(-rad, rad+1):
                if dx*dx+dy*dy > rad*rad: continue
                px, py = x+dx, y+dy
                if 0 <= px < w and 0 <= py < h:
                    # blend
                    orig = img.getpixel((px,py))
                    t = 1 - (dx*dx+dy*dy)**0.5 / rad
                    r = lerp(orig[0], gold[0], t*alpha/255*0.6)
                    g = lerp(orig[1], gold[1], t*alpha/255*0.6)
                    b = lerp(orig[2], gold[2], t*alpha/255*0.6)
                    img.putpixel((px,py), (r,g,b,255))
    # bottom hairline
    draw.line([(0, h-1), (w, h-1)], fill=gold+(180,), width=1)
    path = OUT_CHROME / "header_void.png"
    img.save(path, "PNG")
    print("wrote", path)
    # also small version for icons folder
    img_small = img.resize((256,24), Image.LANCZOS)
    img_small.save(OUT_ICONS / "header_void.png", "PNG")

def make_preset_cards():
    presets = [
        ("walkable_valley", "VALLEY", "Wide · Gentle"),
        ("walkable_highlands", "HIGHLANDS", "Tall · Dramatic"),
        ("walkable_plaza", "PLAZA", "Broad · Flat"),
        ("walkable_canyon", "CANYON", "Deep · Mesa"),
        ("walkable_spiral_arena", "SPIRAL", "Coil · Arena"),
        ("cathedral_wide", "CATHEDRAL", "Wide · Nave"),
    ]
    gold = hex_to_rgb(HEX["gold_500"])
    ivory = hex_to_rgb(HEX["ivory_50"])
    sakura = hex_to_rgb(HEX["sakura_300"])
    plum = hex_to_rgb(HEX["plum_800"])
    rose = hex_to_rgb("#E8A9A1")  # nikki rose
    for pid, label, sub in presets:
        w,h = 256, 160
        img = Image.new("RGBA", (w,h), ivory+(255,))
        draw = ImageDraw.Draw(img)
        # border
        draw.rectangle([(0,0),(w-1,h-1)], outline=gold+(200,), width=2)
        # inner rose-gold accent stripe top 4px
        draw.rectangle([(2,2),(w-3,6)], fill=sakura+(255,))
        # subtle parchment texture via noise dots
        import random
        rnd = random.Random(hash(pid) & 0xffffffff)
        for _ in range(120):
            x = rnd.randint(8, w-8); y = rnd.randint(16, h-20)
            draw.point((x,y), fill=(plum[0], plum[1], plum[2], 10))
        # label (use default font, centered)
        try:
            font_big = ImageFont.truetype("arial.ttf", 28)
            font_small = ImageFont.truetype("arial.ttf", 13)
            font_kicker = ImageFont.truetype("arial.ttf", 10)
        except Exception:
            font_big = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_kicker = ImageFont.load_default()
        # kicker
        kicker = "MELODIA  ·  " + ("WALKABLE" if "walkable" in pid else "VOXEL")
        draw.text((w//2, 26), kicker, fill=gold+(255,), font=font_kicker, anchor="mm")
        # main label
        draw.text((w//2, 58), label, fill=plum+(255,), font=font_big, anchor="mm")
        # sub
        draw.text((w//2, 82), sub, fill=(90,97,112,255), font=font_small, anchor="mm")
        # pink rose accent dot row bottom
        for i, c in enumerate([rose, sakura, gold]):
            x = w//2 - 16 + i*16
            y = h - 18
            draw.ellipse([(x-5,y-5),(x+5,y+5)], fill=c+(255,), outline=(255,255,255,200), width=1)
        # gold rule near bottom
        y = h - 32
        draw.line([(24,y),(w-24,y)], fill=gold+(120,), width=1)
        path = OUT_CHROME / f"preset_{pid}.png"
        img.save(path, "PNG")
        print("wrote", path)

def make_pillar_dots():
    # 16x16 dots per pillar
    cols = {
        "cathedral": hex_to_rgb("#66D9FF"), # cosmic
        "grotto": hex_to_rgb(HEX["gold_500"]),
        "zen": hex_to_rgb(HEX["sakura_500"]),
        "plaza": hex_to_rgb("#C2BAE0"), # lavender
    }
    for name, rgb in cols.items():
        img = Image.new("RGBA", (24,24), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        # outer glow
        for r, a in [(12,30),(9,50),(6,90)]:
            draw.ellipse([(12-r,12-r),(12+r,12+r)], fill=rgb+(a,))
        draw.ellipse([(12-5,12-5),(12+5,12+5)], fill=rgb+(255,), outline=(255,255,255,230), width=1)
        path = OUT_CHROME / f"pillar_{name}.png"
        img.save(path, "PNG")
        print("wrote", path)

def make_starlight_gold():
    # upgrade starlight.png with rose-gold glow baked
    w=h=64
    img = Image.new("RGBA", (w,h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    gold = hex_to_rgb(HEX["gold_500"])
    sakura = hex_to_rgb(HEX["sakura_300"])
    # glow behind
    for r, a in [(26,25),(20,45),(14,80)]:
        draw.ellipse([(32-r,32-r),(32+r,32+r)], fill=gold+(a,))
    # star shape (simple 4-point)
    cx,cy=32,32
    pts=[(cx,8),(cx+7,26),(cx+24,32),(cx+7,38),(cx,56),(cx-7,38),(cx-24,32),(cx-7,26)]
    draw.polygon(pts, fill=(255,248,238,255), outline=sakura+(255,), width=1)
    # center rose highlight
    draw.ellipse([(32-7,32-7),(32+7,32+7)], fill=sakura+(230,))
    draw.ellipse([(32-3,32-3),(32+3,32+3)], fill=(255,255,255,255))
    img.save(OUT_CHROME / "starlight_gold.png", "PNG")
    img.save(OUT_ICONS / "starlight.png", "PNG")
    print("wrote starlight")

if __name__ == "__main__":
    make_gold_rule()
    make_header_void()
    make_preset_cards()
    make_pillar_dots()
    make_starlight_gold()
    print("Done. Chrome:", list(OUT_CHROME.glob("*.png")))
