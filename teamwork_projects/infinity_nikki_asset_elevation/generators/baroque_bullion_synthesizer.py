"""
Baroque Bullion Embroidery Procedural Synthesizer (Archetype 3).
Implements polar logarithmic acanthus scrolls, multi-strand braided gold wire coils,
micro-purl helical windings, and transverse couching clamps over royal velvet ground.
"""

import math
from typing import Any, Dict, List, Tuple
import numpy as np

from .base_synthesizer import BaseSynthesizer


class BaroqueBullionSynthesizer(BaseSynthesizer):
    """
    Procedural Haute-Couture Baroque Bullion Goldwork & Acanthus Embroidery.
    """

    def __init__(self, resolution: int = 2048, seed: int = 42):
        super().__init__(resolution=resolution, seed=seed)

    # -------------------------------------------------------------------------
    # Polar Logarithmic Spirals & Braided Goldwork Generators
    # -------------------------------------------------------------------------
    def generate_acanthus_spines(self) -> List[np.ndarray]:
        """
        Generates polar logarithmic spiral acanthus spine curves with lobe modulation.
        """
        spines = []

        # Central Heraldic Acanthus Scrolls (S-scrolls & C-scrolls)
        scroll_configs = [
            # (cx, cy, a_scale, b_pitch, theta_max, rot_deg, flip_x)
            (0.50, 0.50, 0.035, 0.18, 3.8 * math.pi, 30.0, False),
            (0.50, 0.50, 0.035, 0.18, 3.8 * math.pi, -150.0, True),
            (0.22, 0.22, 0.025, 0.20, 3.2 * math.pi, 45.0, False),
            (0.78, 0.78, 0.025, 0.20, 3.2 * math.pi, 225.0, False),
            (0.22, 0.78, 0.025, 0.20, 3.2 * math.pi, 135.0, True),
            (0.78, 0.22, 0.025, 0.20, 3.2 * math.pi, -45.0, True),
        ]

        for cx, cy, a, b, theta_max, rot_deg, flip in scroll_configs:
            num_pts = 240
            theta = np.linspace(0.2, theta_max, num_pts)
            u = np.linspace(0.0, 1.0, num_pts)

            # Logarithmic spiral equation
            r = a * np.exp(b * theta)

            # Acanthus lobe envelope & serrations
            envelope = (u**0.7) * ((1.0 - u) ** 0.5) * 3.5
            serration = 0.025 * np.sin(theta * 12.0) * envelope

            x_local = (r + serration) * np.cos(theta)
            y_local = (r + serration) * np.sin(theta)
            if flip:
                x_local = -x_local

            # Rotation
            rot_rad = math.radians(rot_deg)
            cos_r = math.cos(rot_rad)
            sin_r = math.sin(rot_rad)
            x_rot = x_local * cos_r - y_local * sin_r + cx
            y_rot = x_local * sin_r + y_local * cos_r + cy

            # 3D relief elevation
            z = 0.020 * envelope * (1.0 + 0.35 * np.cos(theta * 6.0)) + 0.005

            spine = np.stack([x_rot, y_rot, z], axis=-1).astype(np.float32)
            spines.append(spine)

        return spines

    def generate_braided_strands(
        self, spine: np.ndarray, num_strands: int = 3
    ) -> List[np.ndarray]:
        """
        Synthesizes multi-strand braided gold wire coils around a spine curve.
        """
        num_pts = len(spine)
        if num_pts < 3:
            return []

        # Tangents
        tangents = np.roll(spine, -1, axis=0) - np.roll(spine, 1, axis=0)
        t_len = np.linalg.norm(tangents, axis=1, keepdims=True)
        tangents /= np.maximum(t_len, 1e-8)

        up = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        normals = np.cross(tangents, up)
        n_len = np.linalg.norm(normals, axis=1, keepdims=True)
        normals /= np.maximum(n_len, 1e-8)
        binormals = np.cross(tangents, normals)

        braid_radius = 0.008
        braid_freq = 40.0
        purl_radius = 0.002
        purl_freq = 280.0

        strands = []
        u_vals = np.linspace(0, 10.0, num_pts)

        for s in range(num_strands):
            phase = float(s) * (2.0 * math.pi / float(num_strands))
            braid_angle = u_vals * braid_freq + phase
            purl_angle = u_vals * purl_freq

            macro_offset = braid_radius * (
                np.cos(braid_angle)[:, None] * normals
                + np.sin(braid_angle)[:, None] * binormals
            )
            micro_offset = purl_radius * (
                np.cos(purl_angle)[:, None] * normals
                + np.sin(purl_angle)[:, None] * tangents
            )

            strand_pts = spine + macro_offset + micro_offset
            strands.append(strand_pts)

        return strands

    def generate_couching_clamps(self, spines: List[np.ndarray]) -> List[np.ndarray]:
        """
        Generates transverse couching clamp arches anchoring the coils.
        """
        clamps = []
        for spine in spines:
            num_pts = len(spine)
            # Place clamp every 25 points
            for i in range(15, num_pts - 15, 25):
                pt = spine[i]
                # Small transverse arch
                t = np.linspace(-0.012, 0.012, 6)
                arch_x = pt[0] + t
                arch_y = pt[1] + t * 0.5
                arch_z = pt[2] + 0.004 * np.cos(np.linspace(-np.pi / 2, np.pi / 2, 6))
                clamp = np.stack([arch_x, arch_y, arch_z], axis=-1)
                clamps.append(clamp)

        return clamps

    # -------------------------------------------------------------------------
    # 3D Geometry Generation
    # -------------------------------------------------------------------------
    def generate_geometry(self) -> Dict[str, Any]:
        """
        Constructs high-poly 3D mesh combining braided bullion gold wire tubes
        and couching clamps.
        """
        spines = self.generate_acanthus_spines()
        all_verts = []
        all_faces = []
        all_norms = []
        all_uvs = []
        vert_offset = 0

        # 1. Sweep braided gold strands
        for spine in spines:
            strands = self.generate_braided_strands(spine, num_strands=3)
            for strand in strands:
                v, f, n, uv = self.build_tube_mesh(
                    strand, radius=0.003, sides=8, closed_loop=False
                )
                if len(v) > 0:
                    all_verts.append(v)
                    all_faces.append(f + vert_offset)
                    all_norms.append(n)
                    all_uvs.append(uv)
                    vert_offset += len(v)

        # 2. Sweep couching clamps
        clamps = self.generate_couching_clamps(spines)
        for clamp in clamps:
            v, f, n, uv = self.build_tube_mesh(
                clamp, radius=0.0015, sides=6, closed_loop=False
            )
            if len(v) > 0:
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
                "archetype": "BaroqueBullion_Acanthus",
                "num_spines": len(spines),
                "num_clamps": len(clamps),
            },
        }

    # -------------------------------------------------------------------------
    # 2D Heightfield & PBR Map Synthesis
    # -------------------------------------------------------------------------
    def generate_heightfield(self) -> np.ndarray:
        """
        Generates 2D float32 heightfield array representing heavy bullion goldwork relief.
        """
        grid = np.zeros((self.res, self.res), dtype=np.float32)
        spines = self.generate_acanthus_spines()

        # 1. Base silk velvet foundation weave
        y_grid, x_grid = np.mgrid[0 : self.res, 0 : self.res] / float(self.res)
        velvet_weave = 0.04 * (
            np.sin(x_grid * 60.0 * np.pi) * np.sin(y_grid * 60.0 * np.pi) * 0.5 + 0.5
        )
        grid += velvet_weave

        # 2. Rasterize main acanthus spine bodies
        r_acanthus = max(8.0, self.res * (12.0 / 2048.0))
        self.rasterize_curves_onto_grid(
            grid, spines, radius_px=r_acanthus, elevation=0.60, profile="dome"
        )

        # 3. Rasterize individual braided gold wire strands
        for spine in spines:
            strands = self.generate_braided_strands(spine, num_strands=3)
            r_strand = max(3.5, self.res * (5.0 / 2048.0))
            self.rasterize_curves_onto_grid(
                grid, strands, radius_px=r_strand, elevation=0.88, profile="dome"
            )

        # 4. Rasterize couching clamps
        clamps = self.generate_couching_clamps(spines)
        r_clamp = max(2.5, self.res * (3.5 / 2048.0))
        self.rasterize_curves_onto_grid(
            grid, clamps, radius_px=r_clamp, elevation=0.96, profile="smooth"
        )

        # Normalize heightfield to [0.0, 1.0]
        z_min = float(grid.min())
        z_max = float(grid.max())
        if z_max > z_min:
            grid = (grid - z_min) / (z_max - z_min)

        return grid.astype(np.float32)

    def synthesize_maps(self) -> Dict[str, np.ndarray]:
        """
        Synthesizes the complete suite of PBR maps for Baroque Bullion Embroidery.
        """
        H_map = self.generate_heightfield()

        # 1. Masks based on heightfield elevation
        mask_velvet = H_map < 0.12
        mask_acanthus_bed = (H_map >= 0.12) & (H_map < 0.45)
        mask_gold_wire = (H_map >= 0.45) & (H_map < 0.90)
        mask_couching = H_map >= 0.90

        # 2. BaseColor (sRGB)
        # Palette: 24k Imperial Gold (#FFD700), Rose Gold (#B76E79), Royal Blue Velvet (#0F1123), Couching Gold (#D4AF37)
        y_grid, x_grid = np.mgrid[0 : self.res, 0 : self.res] / float(self.res)
        velvet_fuzz = 14.0 * np.sin(x_grid * 233.0 * np.pi + y_grid * 179.0 * np.pi) + 8.0 * np.cos(x_grid * 97.0 * np.pi - y_grid * 131.0 * np.pi)
        thread_facet = 16.0 * np.sin(x_grid * 487.0 * np.pi + y_grid * 373.0 * np.pi)
        h_grad = 25.0 * H_map

        bc_float = np.zeros((self.res, self.res, 3), dtype=np.float32)

        # Velvet ground: Deep midnight royal blue with subtle pile fuzz
        bc_float[mask_velvet, 0] = 15.0 + velvet_fuzz[mask_velvet] + h_grad[mask_velvet] * 0.3
        bc_float[mask_velvet, 1] = 17.0 + velvet_fuzz[mask_velvet] * 0.8 + h_grad[mask_velvet] * 0.4
        bc_float[mask_velvet, 2] = 35.0 + velvet_fuzz[mask_velvet] * 1.2 + h_grad[mask_velvet] * 0.8

        # Acanthus foundation: Dark rose gold / antique bronze
        bc_float[mask_acanthus_bed, 0] = 183.0 + thread_facet[mask_acanthus_bed] + h_grad[mask_acanthus_bed] * 0.5
        bc_float[mask_acanthus_bed, 1] = 110.0 + thread_facet[mask_acanthus_bed] * 0.6 + h_grad[mask_acanthus_bed] * 0.3
        bc_float[mask_acanthus_bed, 2] = 121.0 + h_grad[mask_acanthus_bed] * 0.2

        # Braided wire: Brilliant 24k Imperial Gold with helical micro-reflections
        bc_float[mask_gold_wire, 0] = 255.0
        bc_float[mask_gold_wire, 1] = 215.0 + thread_facet[mask_gold_wire] + h_grad[mask_gold_wire] * 0.2
        bc_float[mask_gold_wire, 2] = 20.0 + thread_facet[mask_gold_wire] * 0.5 + h_grad[mask_gold_wire] * 0.3

        # Couching stitches: Rich antique gold silk thread
        bc_float[mask_couching, 0] = 212.0 + thread_facet[mask_couching]
        bc_float[mask_couching, 1] = 175.0 + h_grad[mask_couching] * 0.2
        bc_float[mask_couching, 2] = 55.0 + thread_facet[mask_couching] * 0.4

        basecolor = np.clip(np.round(bc_float), 0, 255).astype(np.uint8)

        # 3. Roughness
        roughness = np.zeros((self.res, self.res), dtype=np.uint8)
        roughness[mask_velvet] = 210        # Velvet pile: 0.82
        roughness[mask_acanthus_bed] = 95   # Polished metal relief: 0.37
        roughness[mask_gold_wire] = 55      # Smooth 24k gold wire: 0.22
        roughness[mask_couching] = 115      # Silk couching thread: 0.45

        # 4. Metallic
        metallic = np.zeros((self.res, self.res), dtype=np.uint8)
        metallic[mask_velvet] = 0
        metallic[mask_acanthus_bed] = 255   # Metallic bronze
        metallic[mask_gold_wire] = 255      # 100% Metallic 24k gold
        metallic[mask_couching] = 0         # Silk stitch (dielectric)

        # 5. Sheen
        sheen = np.zeros((self.res, self.res), dtype=np.uint8)
        sheen[mask_velvet] = 205            # High velvet fuzz rim sheen (0.80)
        sheen[mask_acanthus_bed] = 30
        sheen[mask_gold_wire] = 0
        sheen[mask_couching] = 130          # Silk sheen (0.51)

        # 6. Alpha
        # Applique cutout trim opacity from velvet base (0.70) to heavy bullion embroidery (1.0)
        alpha_f = 0.70 + 0.30 * H_map
        alpha = np.clip(np.round(alpha_f * 255.0), 160, 255).astype(np.uint8)

        return {
            "BaseColor": basecolor,
            "Roughness": roughness,
            "Metallic": metallic,
            "Sheen": sheen,
            "Alpha": alpha,
            "Height": H_map,
        }
