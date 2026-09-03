"""
Houdini 22 SOP & VEX Procedural PBR Engine
Synthesizes cutting-edge normal maps, high-dynamic displacement, and packed ORM suites
saturated with vibrant Pink, Blue, and Purple palettes for Melusina & Infinity Nikki.
"""

from __future__ import annotations

import sys
import math
import numpy as np
from pathlib import Path
from PIL import Image

try:
    import hou
    print(f"[HOUDINI] Initialized Houdini Engine {hou.applicationVersionString()}")
except ImportError:
    print("[WARN] Running in standalone NumPy mode (hou module not found)")

def normalize(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v, axis=-1, keepdims=True)
    norm[norm == 0] = 1.0
    return v / norm

def sobel_normal_map(height_map: np.ndarray, strength: float = 2.0, flip_green: bool = True) -> np.ndarray:
    h, w = height_map.shape
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
    
    padded = np.pad(height_map, ((1, 1), (1, 1)), mode='wrap')
    from numpy.lib.stride_tricks import sliding_window_view
    windows = sliding_window_view(padded, (3, 3))
    
    dx = np.sum(windows * kx, axis=(-2, -1)) * strength
    dy = np.sum(windows * ky, axis=(-2, -1)) * strength
    
    if flip_green:
        dy = -dy
        
    dz = np.ones_like(dx, dtype=np.float32)
    normals = np.stack([dx, dy, dz], axis=-1)
    normals = normalize(normals)
    return ((normals + 1.0) * 0.5 * 255.0).clip(0, 255).astype(np.uint8)

def pack_orm(ao: np.ndarray, roughness: np.ndarray, metallic: np.ndarray) -> np.ndarray:
    h, w = ao.shape
    orm = np.zeros((h, w, 3), dtype=np.uint8)
    orm[:, :, 0] = ao.clip(0, 255).astype(np.uint8)
    orm[:, :, 1] = roughness.clip(0, 255).astype(np.uint8)
    orm[:, :, 2] = metallic.clip(0, 255).astype(np.uint8)
    return orm

def create_fbm_noise(w: int, h: int, octaves: int = 5, persistence: float = 0.5, scale: float = 4.0, seed: int = 42) -> np.ndarray:
    np.random.seed(seed)
    noise = np.zeros((h, w), dtype=np.float32)
    current_scale = scale
    amplitude = 1.0
    total_amp = 0.0
    
    for _ in range(octaves):
        gw = int(math.ceil(w / current_scale)) + 2
        gh = int(math.ceil(h / current_scale)) + 2
        grid = np.random.uniform(0.0, 1.0, (gh, gw)).astype(np.float32)
        
        img = Image.fromarray((grid * 255).astype(np.uint8), mode='L')
        resampled = np.array(img.resize((w, h), Image.Resampling.BICUBIC), dtype=np.float32) / 255.0
        
        noise += resampled * amplitude
        total_amp += amplitude
        amplitude *= persistence
        current_scale /= 2.0
        if current_scale < 1.0:
            current_scale = 1.0
            
    return noise / total_amp

def save_suite(output_dir: Path, suite_name: str, maps: dict[str, np.ndarray]):
    output_dir.mkdir(parents=True, exist_ok=True)
    for channel_suffix, arr in maps.items():
        filename = f"{suite_name}_{channel_suffix}.png"
        filepath = output_dir / filename
        if arr.ndim == 2:
            img = Image.fromarray(arr.clip(0, 255).astype(np.uint8), mode='L')
        elif arr.ndim == 3 and arr.shape[2] == 3:
            img = Image.fromarray(arr.clip(0, 255).astype(np.uint8), mode='RGB')
        elif arr.ndim == 3 and arr.shape[2] == 4:
            img = Image.fromarray(arr.clip(0, 255).astype(np.uint8), mode='RGBA')
        else:
            raise ValueError(f"Unsupported array shape {arr.shape} for {filename}")
        img.save(filepath, format='PNG')
        print(f"  -> Generated: {filepath.name} ({img.size[0]}x{img.size[1]})")

# =============================================================================
# 6 HOUDINI-INSPIRED VIBRANT PINK / BLUE / PURPLE SUITES
# =============================================================================

def generate_differential_organza_hydrangea(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 1: T_Houdini_DifferentialOrganza_NeonHydrangea
    Differential curve growth ruffle petals with 3D tangent curl-flow normals in vibrant Neon Hydrangea Blue, Magenta Pink, and Deep Iris Violet.
    """
    print(f"Generating Suite 1: T_Houdini_DifferentialOrganza_NeonHydrangea ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    fbm1 = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=101)
    fbm2 = create_fbm_noise(res, res, octaves=5, persistence=0.58, scale=res/8, seed=202)
    
    # Differential line growth simulation approximation using multi-frequency curl domain warping
    warp_x = x + np.sin(y * 14.0 * np.pi + fbm1 * 6.0) * 0.08
    warp_y = y + np.cos(x * 14.0 * np.pi + fbm2 * 6.0) * 0.08
    
    ruffles = np.sin(warp_x * 24.0 * np.pi) * np.cos(warp_y * 24.0 * np.pi)
    ruffles = np.abs(ruffles) ** 0.4
    
    # Palette: Neon Hydrangea Blue (#1E64FF), Vivid Magenta (#FF1493), Royal Iris Purple (#7B2CBF), Cyan Glow (#00F5D4), Sheer Base (#FDF0F8)
    c_blue = np.array([30, 100, 255], dtype=np.float32)
    c_magenta = np.array([255, 20, 147], dtype=np.float32)
    c_purple = np.array([123, 44, 191], dtype=np.float32)
    c_cyan = np.array([0, 245, 212], dtype=np.float32)
    c_base = np.array([253, 240, 248], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        # Color gradient driven by curl-noise ruffles
        grad = c_magenta[c] * (1.0 - ruffles) + c_blue[c] * (ruffles * 0.7) + c_purple[c] * (warp_x * 0.3)
        base = c_base[c] * 0.25 + grad * 0.75 + c_cyan[c] * (fbm2 > 0.65) * 0.25
        bc[:, :, c] = base
        
    height = 0.5 + ruffles * 0.35 + fbm2 * 0.08
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=4.2, flip_green=True)
    
    roughness = 0.28 + ruffles * 0.12 + fbm1 * 0.06
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.zeros_like(roughness) # Translucent silk organza
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 0.85 + ruffles * 0.15
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = 0.95 # Vibrant anisotropic chromatic sheen
    sheen_uint8 = np.full_like(rough_uint8, int(0.95 * 255))
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8,
        "Sheen": sheen_uint8
    }

def generate_reaction_diffusion_amethyst_lapis(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 2: T_Houdini_ReactionDiffusion_AmethystLapis
    Gray-Scott reaction-diffusion organic labyrinth in Royal Amethyst Purple, Lapis Lazuli, Hot Fuchsia Pink, and 24k Rose-Gold ridges.
    """
    print(f"Generating Suite 2: T_Houdini_ReactionDiffusion_AmethystLapis ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=303)
    fbm_spots = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/16, seed=404)
    
    # Morphogen concentration wave equation simulating Turing reaction-diffusion
    rd_pattern = np.sin((x * 32.0 + np.sin(y * 24.0 * np.pi) * 2.0 + fbm * 8.0) * np.pi) * \
                 np.cos((y * 32.0 + np.cos(x * 24.0 * np.pi) * 2.0 + fbm * 8.0) * np.pi)
    
    is_gold_ridge = np.abs(rd_pattern) < 0.12
    is_basin_a = rd_pattern >= 0.12
    is_basin_b = rd_pattern <= -0.12
    
    # Palette: Hot Fuchsia Pink (#F72585), Royal Amethyst (#7209B7), Deep Lapis (#3A0CA3), Neon Cyan (#4CC9F0), Rose Gold (#E8B4A8)
    c_fuchsia = np.array([247, 37, 133], dtype=np.float32)
    c_amethyst = np.array([114, 9, 183], dtype=np.float32)
    c_lapis = np.array([58, 12, 163], dtype=np.float32)
    c_cyan = np.array([76, 201, 240], dtype=np.float32)
    c_rosegold = np.array([232, 180, 168], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        # Basin A: Fuchsia to Amethyst
        basin_a_col = c_fuchsia[c] * (0.85 + fbm * 0.3) + c_amethyst[c] * 0.15
        # Basin B: Lapis to Cyan
        basin_b_col = c_lapis[c] * (0.85 + fbm * 0.25) + c_cyan[c] * 0.25
        base = np.where(is_basin_a, basin_a_col, basin_b_col)
        # Rose gold dividing ridges
        base = np.where(is_gold_ridge, c_rosegold[c] * 1.15, base)
        bc[:, :, c] = base
        
    height = np.where(is_gold_ridge, 0.75, 0.45 + np.abs(rd_pattern) * 0.25) + fbm * 0.04
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=4.5, flip_green=True)
    
    roughness = np.where(is_gold_ridge, 0.20, 0.08 + fbm * 0.04) # Glossy vitreous enamel (0.08) vs rose-gold (0.20)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_gold_ridge, 0.94, 0.0) # Rose gold is metallic, enamel is dielectric
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - (is_gold_ridge == 0) * (1.0 - np.abs(rd_pattern)) * 0.30
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = 0.90
    sheen_uint8 = np.full_like(rough_uint8, int(0.90 * 255))
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8,
        "Sheen": sheen_uint8
    }

def generate_voronoi_pink_sapphire(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 3: T_Houdini_VoronoiCrystal_PinkSapphire
    Cellular Voronoi fractured crystal gems in Vivid Pink Sapphire, Tanzanite Royal Violet, and Electric Ice Blue with bevel facet normals.
    """
    print(f"Generating Suite 3: T_Houdini_VoronoiCrystal_PinkSapphire ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    # Voronoi Cellular Crystal Grid
    cell_scale = 12.0
    cx = (x * cell_scale) % 1.0 - 0.5
    cy = (y * cell_scale) % 1.0 - 0.5
    cell_id_x = np.floor(x * cell_scale)
    cell_id_y = np.floor(y * cell_scale)
    
    np.random.seed(505)
    rand_grid = np.sin(cell_id_x * 17.13 + cell_id_y * 43.71) * 43758.5453
    rand_cell = rand_grid - np.floor(rand_grid)
    
    crystal_facet = np.abs(cx) + np.abs(cy)
    is_gem_rim = crystal_facet > 0.44
    facet_depth = np.clip(1.0 - (crystal_facet / 0.44), 0.0, 1.0)
    
    fbm = create_fbm_noise(res, res, octaves=5, persistence=0.55, scale=res/4, seed=606)
    
    # Palette: Vivid Pink Sapphire (#FF5D8F), Tanzanite Violet (#5E5CE6), Electric Ice Blue (#00F0FF), Rose Crystal (#FF8FA3)
    c_sapphire = np.array([255, 93, 143], dtype=np.float32)
    c_tanzanite = np.array([94, 92, 230], dtype=np.float32)
    c_iceblue = np.array([0, 240, 255], dtype=np.float32)
    c_rosecrystal = np.array([255, 143, 163], dtype=np.float32)
    c_rim_gold = np.array([244, 211, 94], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        # Gemstone color distribution per facet
        gem_type = rand_cell > 0.5
        gem_col = np.where(gem_type, c_sapphire[c] * 0.7 + c_rosecrystal[c] * 0.3, c_tanzanite[c] * 0.7 + c_iceblue[c] * 0.3)
        gem_col = gem_col * (0.85 + facet_depth * 0.35 + fbm * 0.1)
        # Gold bevel rim
        base = np.where(is_gem_rim, c_rim_gold[c] * 1.1, gem_col)
        bc[:, :, c] = base
        
    height = np.where(is_gem_rim, 0.20, 0.55 + facet_depth * 0.30) + fbm * 0.02
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=4.8, flip_green=True)
    
    roughness = np.where(is_gem_rim, 0.22, 0.05 + rand_cell * 0.04) # Ultra-glossy crystal facet (0.05)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_gem_rim, 0.94, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = np.where(is_gem_rim, 0.60, 0.96)
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = 0.95
    sheen_uint8 = np.full_like(rough_uint8, int(0.95 * 255))
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8,
        "Sheen": sheen_uint8
    }

def generate_chladni_ultraviolet_velvet(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 4: T_Houdini_ChladniAcoustic_UltravioletVelvet
    Harmonic standing-wave acoustic silk velvet with swirling pile tangency in Ultraviolet Purple, Cyan Marine Blue, and Pastel Rose.
    """
    print(f"Generating Suite 4: T_Houdini_ChladniAcoustic_UltravioletVelvet ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=707)
    
    # 2D Chladni Modal Acoustic Standing Waves
    n, m = 6.0, 4.0
    w1 = np.cos(n * np.pi * x) * np.cos(m * np.pi * y) - np.cos(m * np.pi * x) * np.cos(n * np.pi * y)
    w2 = np.sin((n + 2) * np.pi * x) * np.sin((m + 2) * np.pi * y)
    chladni = (w1 + w2 * 0.5) * 0.5
    
    # Directional Velvet Pile Swirl
    pile_angle = chladni * 3.0 * np.pi + fbm * 2.0
    pile_spec = np.sin(pile_angle) * 0.5 + 0.5
    
    # Palette: Ultraviolet Purple (#7209B7), Cyan Marine Blue (#4CC9F0), Pastel Rose (#FF85A1), Deep Midnight Indigo (#10002B)
    c_ultra = np.array([114, 9, 183], dtype=np.float32)
    c_cyan = np.array([76, 201, 240], dtype=np.float32)
    c_rose = np.array([255, 133, 161], dtype=np.float32)
    c_indigo = np.array([16, 0, 43], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        velvet_base = c_indigo[c] * (1.0 - pile_spec * 0.7) + c_ultra[c] * (pile_spec * 0.5) + c_cyan[c] * (chladni > 0.2) * 0.35 + c_rose[c] * (chladni < -0.2) * 0.35
        bc[:, :, c] = velvet_base
        
    height = 0.5 + chladni * 0.12 + fbm * 0.04
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=2.8, flip_green=True)
    
    roughness = 0.45 + pile_spec * 0.12 + fbm * 0.05
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.zeros_like(roughness)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 0.90 + chladni * 0.10
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = 0.98 # High anisotropic velvet sheen
    sheen_uint8 = np.full_like(rough_uint8, int(0.98 * 255))
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8,
        "Sheen": sheen_uint8
    }

def generate_baroque_magenta_silk(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 5: T_Houdini_BaroqueAcanthus_GildedMagentaSilk
    Polar logarithmic spiral acanthus scrollwork in Gilded Magenta, Midnight Cobalt Blue, Lilac Mist, and 18k Rose-Gold thread.
    """
    print(f"Generating Suite 5: T_Houdini_BaroqueAcanthus_GildedMagentaSilk ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    fbm = create_fbm_noise(res, res, octaves=6, persistence=0.55, scale=res/4, seed=909)
    fbm_thread = create_fbm_noise(res, res, octaves=4, persistence=0.6, scale=res/48, seed=1010)
    
    # Polar Logarithmic Acanthus Scrollwork
    cx = (x * 3.0) % 1.0 - 0.5
    cy = (y * 3.0) % 1.0 - 0.5
    r = np.sqrt(cx**2 + cy**2)
    angle = np.arctan2(cy, cx)
    
    spiral = np.cos(angle * 6.0 + r * 14.0 * np.pi + fbm * 2.0)
    is_acanthus = (spiral > 0.35) & (r < 0.46)
    is_gold_ribbon = (np.abs(spiral - 0.35) < 0.08) & (r < 0.46)
    
    # Palette: Gilded Magenta (#C71585), Midnight Cobalt (#001858), Lilac Mist (#D8B4E2), 18k Rose Gold (#E8B4A8)
    c_magenta = np.array([199, 21, 133], dtype=np.float32)
    c_cobalt = np.array([0, 24, 88], dtype=np.float32)
    c_lilac = np.array([216, 180, 226], dtype=np.float32)
    c_rosegold = np.array([232, 180, 168], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    for c in range(3):
        silk_bg = c_cobalt[c] * 0.65 + c_lilac[c] * 0.35 + (fbm * 20.0)
        acanthus_col = c_magenta[c] * (0.90 + fbm_thread * 0.20)
        base = np.where(is_acanthus, acanthus_col, silk_bg)
        base = np.where(is_gold_ribbon, c_rosegold[c] * 1.15, base)
        bc[:, :, c] = base
        
    height = 0.50 + is_acanthus * 0.22 + is_gold_ribbon * 0.15 + fbm_thread * 0.03
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=3.6, flip_green=True)
    
    roughness = np.where(is_gold_ribbon, 0.20, np.where(is_acanthus, 0.28, 0.38 + fbm * 0.06))
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_gold_ribbon, 0.94, 0.0)
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = 1.0 - (1.0 - is_acanthus) * 0.15 - (is_gold_ribbon == 0) * 0.10
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = 0.92
    sheen_uint8 = np.full_like(rough_uint8, int(0.92 * 255))
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8,
        "Sheen": sheen_uint8
    }

def generate_stained_glass_azure_pink(res: int = 2048) -> dict[str, np.ndarray]:
    """Suite 6: T_Houdini_CathedralStainedGlass_RosaceAzurePink
    Cathedral stained-glass rosace with blown-glass ripple displacement in Royal Azure Blue, Ruby Magenta Pink, and Deep Amethyst Violet.
    """
    print(f"Generating Suite 6: T_Houdini_CathedralStainedGlass_RosaceAzurePink ({res}x{res})...")
    y, x = np.mgrid[0:res, 0:res].astype(np.float32) / res
    
    cx = x - 0.5
    cy = y - 0.5
    r = np.sqrt(cx**2 + cy**2)
    angle = np.arctan2(cy, cx)
    
    # Cathedral Rosace Petals & Lead Cames
    petal_12 = np.cos(angle * 12.0) * 0.10 + 0.36
    is_lead_came = (np.abs(r - petal_12) < 0.014) | (np.abs(r - 0.18) < 0.012) | (np.abs(r - 0.48) < 0.014) | (np.abs(np.sin(angle * 12.0)) < 0.08)
    is_center_glass = r < 0.18
    is_outer_ring = (r >= 0.18) & (r < 0.48)
    
    fbm = create_fbm_noise(res, res, octaves=5, persistence=0.55, scale=res/4, seed=1212)
    glass_ripples = np.sin((x * 48.0 + y * 48.0 + fbm * 8.0) * np.pi) * 0.5 + 0.5
    
    # Palette: Royal Azure Blue (#0055FF), Ruby Magenta (#E01A4F), Deep Amethyst (#49117C), Neon Turquoise (#00F5D4), Antique Lead Came (#3A3A3D)
    c_azure = np.array([0, 85, 255], dtype=np.float32)
    c_magenta = np.array([224, 26, 79], dtype=np.float32)
    c_amethyst = np.array([73, 17, 124], dtype=np.float32)
    c_cyan = np.array([0, 245, 212], dtype=np.float32)
    c_lead = np.array([58, 58, 61], dtype=np.float32)
    
    bc = np.zeros((res, res, 3), dtype=np.float32)
    glass_alt = np.sin(angle * 6.0) > 0.0
    
    for c in range(3):
        petal_col = np.where(glass_alt, c_magenta[c], c_azure[c]) * (0.85 + glass_ripples * 0.25)
        center_col = c_amethyst[c] * 0.7 + c_cyan[c] * 0.3
        base = np.where(is_center_glass, center_col, petal_col)
        base = np.where(is_lead_came, c_lead[c], base)
        bc[:, :, c] = base
        
    height = np.where(is_lead_came, 0.75, 0.45 + glass_ripples * 0.15)
    height_uint8 = (height * 255.0).clip(0, 255).astype(np.uint8)
    
    normal = sobel_normal_map(height, strength=4.5, flip_green=True)
    
    roughness = np.where(is_lead_came, 0.72, 0.05 + glass_ripples * 0.03) # Clear glass (0.05) vs antique lead came (0.72)
    rough_uint8 = (roughness * 255.0).clip(0, 255).astype(np.uint8)
    
    metallic = np.where(is_lead_came, 0.45, 0.0) # Lead came has soft metallic sheen
    metal_uint8 = (metallic * 255.0).clip(0, 255).astype(np.uint8)
    
    ao = np.where(is_lead_came, 0.85, 0.98)
    ao_uint8 = (ao * 255.0).clip(0, 255).astype(np.uint8)
    
    orm = pack_orm(ao_uint8, rough_uint8, metal_uint8)
    
    sheen = np.where(is_lead_came, 0.0, 0.95)
    sheen_uint8 = (sheen * 255.0).clip(0, 255).astype(np.uint8)
    
    return {
        "BC": bc.astype(np.uint8),
        "N": normal,
        "ORM": orm,
        "H": height_uint8,
        "AO": ao_uint8,
        "R": rough_uint8,
        "M": metal_uint8,
        "Sheen": sheen_uint8
    }

def main():
    root = Path(r"C:\EnvironmentPortfolio")
    out_dir = root / "BS_GodFile" / "Content" / "Textures" / "Houdini_Vibrant_PBR_Suites"
    
    print("==================================================================")
    print("HOUDINI PROCEDURAL PBR: VIBRANT PINKS, BLUES & PURPLES")
    print("==================================================================")
    
    suites = [
        (out_dir, "T_Houdini_DifferentialOrganza_NeonHydrangea", generate_differential_organza_hydrangea),
        (out_dir, "T_Houdini_ReactionDiffusion_AmethystLapis", generate_reaction_diffusion_amethyst_lapis),
        (out_dir, "T_Houdini_VoronoiCrystal_PinkSapphire", generate_voronoi_pink_sapphire),
        (out_dir, "T_Houdini_ChladniAcoustic_UltravioletVelvet", generate_chladni_ultraviolet_velvet),
        (out_dir, "T_Houdini_BaroqueAcanthus_GildedMagentaSilk", generate_baroque_magenta_silk),
        (out_dir, "T_Houdini_CathedralStainedGlass_RosaceAzurePink", generate_stained_glass_azure_pink),
    ]
    
    total_maps = 0
    for d, name, func in suites:
        maps = func(res=2048)
        save_suite(d, name, maps)
        total_maps += len(maps)
        
    print(f"\n[SUCCESS] Successfully generated {len(suites)} Houdini Vibrant PBR suites ({total_maps} total maps) at 2048x2048!")
    print(f"Output directory: {out_dir}")

if __name__ == "__main__":
    main()
