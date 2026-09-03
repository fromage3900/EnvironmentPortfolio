"""
Chantilly Lace & Micro-Beading Procedural Synthesizer (Archetype 1).
Implements perturbed hexagonal Poisson reseau lattices, multi-harmonic Superformula
floral cordonnet curves, satin stitch fills, and Frenet-Serret oriented
pearl cabochon and bicone crystal seed bead scatter.
"""

import math
from typing import Any, Dict, List, Tuple
import numpy as np
from PIL import Image

from .base_synthesizer import BaseSynthesizer


class ChantillyLaceSynthesizer(BaseSynthesizer):
    """
    Procedural Haute-Couture Chantilly Lace with Micro-Bead Arrays.
    """

    def __init__(self, resolution: int = 2048, seed: int = 42):
        super().__init__(resolution=resolution, seed=seed)

    # -------------------------------------------------------------------------
    # Curve & Lattice Generators
    # -------------------------------------------------------------------------
    def generate_reseau_lattice(
        self, num_x: int = 24, jitter_scale: float = 0.12
    ) -> List[np.ndarray]:
        """
        Generates the perturbed hexagonal honeycomb thread segments (Fond de Chantilly).
        """
        dx = 1.0 / float(num_x)
        dy = (math.sqrt(3.0) / 2.0) * dx
        num_y = int(math.ceil(1.0 / dy)) + 2

        # 1. Create grid points with stochastic jitter
        grid_pts = {}
        for j in range(-1, num_y + 1):
            row_shift = (j % 2) * (dx * 0.5)
            for i in range(-1, num_x + 2):
                jx = (self.rng.uniform(-1, 1) * jitter_scale * dx)
                jy = (self.rng.uniform(-1, 1) * jitter_scale * dy)
                px = i * dx + row_shift + jx
                py = j * dy + jy
                pz = self.rng.uniform(0.001, 0.003)
                grid_pts[(i, j)] = np.array([px, py, pz], dtype=np.float32)

        # 2. Build hexagonal/triangular connecting thread curves
        curves = []
        for j in range(-1, num_y):
            for i in range(-1, num_x + 1):
                p0 = grid_pts.get((i, j))
                p_right = grid_pts.get((i + 1, j))
                p_up = grid_pts.get((i, j + 1))
                p_diag = grid_pts.get((i + 1 if (j % 2 == 0) else i - 1, j + 1))

                if p0 is not None and p_right is not None:
                    # Horizontal thread
                    c = np.linspace(p0, p_right, 6)
                    c[:, 2] += 0.001 * np.sin(np.linspace(0, np.pi, 6))
                    curves.append(c)

                if p0 is not None and p_up is not None:
                    # Vertical/diagonal tie
                    c = np.linspace(p0, p_up, 6)
                    c[:, 2] += 0.001 * np.sin(np.linspace(0, np.pi, 6))
                    curves.append(c)

                if p0 is not None and p_diag is not None:
                    c = np.linspace(p0, p_diag, 6)
                    curves.append(c)

        return curves

    def generate_cordonnet_rosettes(self) -> Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray]]:
        """
        Generates Superformula floral outlines, internal satin stitch hatching,
        and scalloped border curves.
        """
        outlines = []
        satin_stitches = []
        scallop_curves = []

        # Floral Rosette centers: Center and 4 periodic corners
        centers = [
            (0.5, 0.5, 0.22, 6),     # Center main rosette: radius 0.22, 6 petals
            (0.0, 0.0, 0.14, 5),     # Corner rosettes
            (1.0, 0.0, 0.14, 5),
            (0.0, 1.0, 0.14, 5),
            (1.0, 1.0, 0.14, 5),
            (0.5, 0.0, 0.11, 4),     # Border side rosettes
            (0.5, 1.0, 0.11, 4),
            (0.0, 0.5, 0.11, 4),
            (1.0, 0.5, 0.11, 4),
        ]

        for cx, cy, base_r, k_petals in centers:
            # 1. Superformula multi-harmonic floral envelope
            num_theta = 240
            theta = np.linspace(0, 2 * np.pi, num_theta, endpoint=True)
            r = base_r * (
                1.0
                + 0.38 * np.cos(k_petals * theta)
                + 0.14 * np.cos(2 * k_petals * theta)
                + 0.05 * np.sin(3 * k_petals * theta)
            )

            px = cx + r * np.cos(theta)
            py = cy + r * np.sin(theta)
            pz = 0.012 + 0.004 * np.cos(k_petals * theta)
            rosette_pts = np.stack([px, py, pz], axis=-1)
            outlines.append(rosette_pts)

            # Secondary inner ring
            r_inner = r * 0.55
            px_in = cx + r_inner * np.cos(theta)
            py_in = cy + r_inner * np.sin(theta)
            pz_in = 0.016 + 0.003 * np.cos(k_petals * theta)
            outlines.append(np.stack([px_in, py_in, pz_in], axis=-1))

            # 2. Satin stitch zigzag fill between inner and outer boundary
            num_stitches = 48
            for s in range(num_stitches):
                th = (float(s) / float(num_stitches)) * 2 * np.pi
                p_in = np.array([cx + (base_r * 0.25) * math.cos(th), cy + (base_r * 0.25) * math.sin(th), 0.008])
                p_out = np.array([
                    cx + (base_r * 0.95 * (1.0 + 0.35 * math.cos(k_petals * th))) * math.cos(th),
                    cy + (base_r * 0.95 * (1.0 + 0.35 * math.cos(k_petals * th))) * math.sin(th),
                    0.009
                ])
                # Zigzag path
                stitch_path = np.linspace(p_in, p_out, 8)
                stitch_path[:, 2] += 0.002 * np.sin(np.linspace(0, np.pi, 8))
                satin_stitches.append(stitch_path)

        # 3. Scalloped floral lace borders
        for border_y in [0.08, 0.92]:
            x_vals = np.linspace(0, 1, 200)
            y_scallop = border_y + 0.035 * np.abs(np.sin(8.0 * np.pi * x_vals)) ** 1.6
            z_scallop = np.full_like(x_vals, 0.010)
            scallop_curves.append(np.stack([x_vals, y_scallop, z_scallop], axis=-1))

        return outlines, satin_stitches, scallop_curves

    def generate_micro_beads(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Scatters pearl cabochons and faceted bicone crystal seed beads
        along cordonnet ridges.
        Returns: (pearl_centers, crystal_centers)
        """
        pearls = []
        crystals = []

        # Center rosette bead garland
        cx, cy = 0.5, 0.5
        # Inner pearl garland (circle at r=0.10)
        num_pearls = 20
        for i in range(num_pearls):
            th = (float(i) / float(num_pearls)) * 2 * np.pi
            px = cx + 0.10 * math.cos(th)
            py = cy + 0.10 * math.sin(th)
            pz = 0.024
            pearls.append([px, py, pz])

        # Outer crystal bicones at petal crests
        k_petals = 6
        base_r = 0.22
        num_crystals = 36
        for i in range(num_crystals):
            th = (float(i) / float(num_crystals)) * 2 * np.pi
            r = base_r * (1.0 + 0.38 * math.cos(k_petals * th) + 0.14 * math.cos(2 * k_petals * th))
            px = cx + (r * 0.92) * math.cos(th)
            py = cy + (r * 0.92) * math.sin(th)
            pz = 0.026
            crystals.append([px, py, pz])

        # Corner beads
        for ccx, ccy in [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)]:
            for i in range(8):
                th = (float(i) / 8.0) * 2 * np.pi
                px = ccx + 0.07 * math.cos(th)
                py = ccy + 0.07 * math.sin(th)
                if (px >= 0.0 or px <= 1.0) and (py >= 0.0 or py <= 1.0):
                    pearls.append([px % 1.0, py % 1.0, 0.020])

        pearl_arr = np.array(pearls, dtype=np.float32)
        cryst_arr = np.array(crystals, dtype=np.float32)
        return pearl_arr, cryst_arr

    # -------------------------------------------------------------------------
    # 3D Geometry Generation
    # -------------------------------------------------------------------------
    def generate_geometry(self) -> Dict[str, Any]:
        """
        Constructs the high-poly 3D mesh combining reseau tubes, cordonnet sweeps,
        pearl UV spheres, and faceted bicone crystals.
        """
        all_verts = []
        all_faces = []
        all_norms = []
        all_uvs = []
        vert_offset = 0

        # 1. Sweep Cordonnet outlines
        outlines, satin_stitches, scallops = self.generate_cordonnet_rosettes()
        for curve in outlines + scallops:
            v, f, n, uv = self.build_tube_mesh(curve, radius=0.004, sides=8, closed_loop=True)
            if len(v) > 0:
                all_verts.append(v)
                all_faces.append(f + vert_offset)
                all_norms.append(n)
                all_uvs.append(uv)
                vert_offset += len(v)

        # 2. Sweep Satin stitch threads
        for stitch in satin_stitches[::2]:  # Subsample for efficient poly count
            v, f, n, uv = self.build_tube_mesh(stitch, radius=0.0018, sides=6, closed_loop=False)
            if len(v) > 0:
                all_verts.append(v)
                all_faces.append(f + vert_offset)
                all_norms.append(n)
                all_uvs.append(uv)
                vert_offset += len(v)

        # 3. Micro-beads (Pearls & Crystals)
        pearls, crystals = self.generate_micro_beads()

        # Pearls: UV spheres
        for p in pearls:
            v, f, n = self.build_sphere_mesh(p, radius=0.007, lat_res=8, lon_res=10)
            uv = np.zeros((len(v), 2), dtype=np.float32)
            uv[:, 0] = p[0]
            uv[:, 1] = p[1]
            all_verts.append(v)
            all_faces.append(f + vert_offset)
            all_norms.append(n)
            all_uvs.append(uv)
            vert_offset += len(v)

        # Crystals: Faceted bicones
        for c in crystals:
            v, f, n = self.build_bicone_mesh(c, radius=0.006, height=0.012, facets=8)
            uv = np.zeros((len(v), 2), dtype=np.float32)
            uv[:, 0] = c[0]
            uv[:, 1] = c[1]
            all_verts.append(v)
            all_faces.append(f + vert_offset)
            all_norms.append(n)
            all_uvs.append(uv)
            vert_offset += len(v)

        vertices = np.vstack(all_verts).astype(np.float32)
        faces = np.vstack(all_faces).astype(np.int32)
        normals = np.vstack(all_norms).astype(np.float32)
        uvs = np.vstack(all_uvs).astype(np.float32)

        return {
            "vertices": vertices,
            "faces": faces,
            "normals": normals,
            "uvs": uvs,
            "metadata": {
                "archetype": "ChantillyLace_PearlBeading",
                "num_pearls": len(pearls),
                "num_crystals": len(crystals),
            },
        }

    # -------------------------------------------------------------------------
    # 2D Heightfield & PBR Map Synthesis
    # -------------------------------------------------------------------------
    def generate_heightfield(self) -> np.ndarray:
        """
        Generates 2D float32 heightfield array [H, W] normalized [0.0, 1.0].
        """
        grid = np.zeros((self.res, self.res), dtype=np.float32)

        # 1. Base tulle gossamer weave foundation relief
        y_grid, x_grid = np.mgrid[0 : self.res, 0 : self.res] / float(self.res)
        base_tulle = 0.04 * (np.sin(x_grid * 137.0 * np.pi + y_grid * 89.0 * np.pi) * 0.5 + 0.5)
        base_gradient = 0.03 * (np.sin(x_grid * 3.7 * np.pi) * np.cos(y_grid * 3.7 * np.pi) * 0.5 + 0.5)
        grid += base_tulle + base_gradient

        # 2. Rasterize reseau lattice
        reseau_curves = self.generate_reseau_lattice(num_x=28, jitter_scale=0.10)
        # Reseau thread radius ~ 2.0 px at 2048
        r_reseau = max(1.5, self.res * (1.5 / 2048.0))
        self.rasterize_curves_onto_grid(grid, reseau_curves, radius_px=r_reseau, elevation=0.22, profile="dome")

        # 3. Rasterize satin stitches
        outlines, satin_stitches, scallops = self.generate_cordonnet_rosettes()
        r_stitch = max(2.5, self.res * (2.8 / 2048.0))
        self.rasterize_curves_onto_grid(grid, satin_stitches, radius_px=r_stitch, elevation=0.42, profile="smooth")

        # 4. Rasterize cordonnet floral outlines & scallops
        r_cordonnet = max(4.5, self.res * (5.5 / 2048.0))
        self.rasterize_curves_onto_grid(grid, outlines + scallops, radius_px=r_cordonnet, elevation=0.68, profile="dome")

        # 5. Rasterize micro-beads
        pearls, crystals = self.generate_micro_beads()
        r_pearl = max(6.0, self.res * (10.0 / 2048.0))
        r_cryst = max(5.0, self.res * (8.5 / 2048.0))
        self.rasterize_points_onto_grid(grid, pearls, radius_px=r_pearl, height_val=0.95, shape="sphere")
        self.rasterize_points_onto_grid(grid, crystals, radius_px=r_cryst, height_val=0.90, shape="bicone")

        # Normalize heightfield to [0.0, 1.0]
        z_min = float(grid.min())
        z_max = float(grid.max())
        if z_max > z_min:
            grid = (grid - z_min) / (z_max - z_min)

        return grid.astype(np.float32)

    def synthesize_maps(self) -> Dict[str, np.ndarray]:
        """
        Synthesizes the complete suite of PBR maps for Chantilly Lace & Micro-Beading.
        """
        H_map = self.generate_heightfield()

        # 1. Masks based on height & geometric layers
        mask_void = H_map < 0.08
        mask_reseau = (H_map >= 0.08) & (H_map < 0.32)
        mask_satin = (H_map >= 0.32) & (H_map < 0.58)
        mask_cordonnet = (H_map >= 0.58) & (H_map < 0.85)
        mask_beads = H_map >= 0.85

        # 2. BaseColor (sRGB)
        # Palette: Pearl White (#FDFBF7), Blush Pink (#EE8EAF), Ice Blue (#B4DCFA), 24k Gold (#FFD71E), Sheer Tulle (#C3AFD7)
        y_grid, x_grid = np.mgrid[0 : self.res, 0 : self.res] / float(self.res)
        wash = 16.0 * np.sin(x_grid * 5.7 * np.pi + y_grid * 4.3 * np.pi)
        grain = 8.0 * np.sin(x_grid * 239.0 * np.pi + y_grid * 181.0 * np.pi)

        bc_float = np.zeros((self.res, self.res, 3), dtype=np.float32)

        # Background sheer tulle void: Soft lavender-rose watercolor glaze
        bc_float[mask_void, 0] = 195.0 + wash[mask_void]
        bc_float[mask_void, 1] = 175.0 + wash[mask_void] * 0.5
        bc_float[mask_void, 2] = 215.0 + wash[mask_void] * 0.8

        # Reseau lattice: Pearlescent ivory-white threads
        bc_float[mask_reseau, 0] = 235.0 + grain[mask_reseau]
        bc_float[mask_reseau, 1] = 230.0 + grain[mask_reseau]
        bc_float[mask_reseau, 2] = 242.0 + grain[mask_reseau]

        # Satin fill: Rich blush rose to coral watercolor glaze with soft gradient
        bc_satin_r = 238.0 + 10.0 * np.sin(y_grid[mask_satin] * 8.0 * np.pi) + grain[mask_satin]
        bc_satin_g = 142.0 + 15.0 * np.cos(x_grid[mask_satin] * 8.0 * np.pi)
        bc_satin_b = 175.0 + 12.0 * np.sin((x_grid[mask_satin] + y_grid[mask_satin]) * 6.0 * np.pi)
        bc_float[mask_satin, 0] = bc_satin_r
        bc_float[mask_satin, 1] = bc_satin_g
        bc_float[mask_satin, 2] = bc_satin_b

        # Cordonnet: Elevated silk floral outlines (Luminous pale blush to crystal white)
        bc_float[mask_cordonnet, 0] = 252.0
        bc_float[mask_cordonnet, 1] = 222.0 + grain[mask_cordonnet] * 0.5
        bc_float[mask_cordonnet, 2] = 235.0

        # Beads: Pearls (Lustrous Ivory) & Crystal Bicones (Ice Blue Shimmer)
        pearl_submask = mask_beads & (H_map < 0.95)
        bc_float[pearl_submask, 0] = 255.0
        bc_float[pearl_submask, 1] = 250.0
        bc_float[pearl_submask, 2] = 235.0

        # Crystal seed beads and 24k gold prongs
        cryst_submask = mask_beads & (H_map >= 0.95) & (H_map < 0.97)
        bc_float[cryst_submask, 0] = 180.0
        bc_float[cryst_submask, 1] = 220.0
        bc_float[cryst_submask, 2] = 250.0

        prong_submask = H_map >= 0.97
        bc_float[prong_submask, 0] = 255.0
        bc_float[prong_submask, 1] = 215.0
        bc_float[prong_submask, 2] = 30.0

        basecolor = np.clip(np.round(bc_float), 0, 255).astype(np.uint8)

        # 3. Roughness
        roughness = np.zeros((self.res, self.res), dtype=np.uint8)
        roughness[mask_void] = 220        # Void fabric: 0.86
        roughness[mask_reseau] = 165      # Reseau threads: 0.65
        roughness[mask_satin] = 115       # Satin stitch: 0.45
        roughness[mask_cordonnet] = 95    # Cordonnet silk: 0.37
        roughness[mask_beads] = 30        # Ultra-smooth pearls & crystal facets: 0.12

        # 4. Metallic
        metallic = np.zeros((self.res, self.res), dtype=np.uint8)
        # Gold prongs on top 3% of bead heights
        mask_gold_prongs = H_map >= 0.97
        metallic[mask_gold_prongs] = 255

        # 5. Sheen (High for silk cordonnet, satin, and pearls)
        sheen = np.zeros((self.res, self.res), dtype=np.uint8)
        sheen[mask_reseau] = 110          # 0.43
        sheen[mask_satin] = 190           # 0.75
        sheen[mask_cordonnet] = 220       # 0.86
        sheen[mask_beads] = 200           # 0.78

        # 6. Alpha (Sheer lace transparency)
        alpha = np.zeros((self.res, self.res), dtype=np.uint8)
        alpha[mask_void] = 35             # Sheer void: 0.14
        alpha[mask_reseau] = 160          # Reseau open lattice: 0.63
        alpha[mask_satin] = 230           # Dense satin: 0.90
        alpha[mask_cordonnet] = 255       # Solid cordonnet: 1.0
        alpha[mask_beads] = 255           # Solid beads: 1.0

        return {
            "BaseColor": basecolor,
            "Roughness": roughness,
            "Metallic": metallic,
            "Sheen": sheen,
            "Alpha": alpha,
            "Height": H_map,
        }
