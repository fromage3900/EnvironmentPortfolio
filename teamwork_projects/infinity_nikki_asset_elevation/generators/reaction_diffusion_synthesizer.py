"""
Reaction-Diffusion Cloisons / Micro-Filigree Procedural Synthesizer (Archetype 4).
Implements Gray-Scott 9-point discrete Laplacian PDE simulation, morphogenetic
filigree ridge boundary isolation, and Young-Laplace vitreous enamel meniscus pooling.
"""

import math
from typing import Any, Dict, List, Tuple
import numpy as np
from PIL import Image

from .base_synthesizer import BaseSynthesizer


class ReactionDiffusionSynthesizer(BaseSynthesizer):
    """
    Procedural Haute-Couture Reaction-Diffusion Cloisonné & Vitreous Enamel Micro-Filigree.
    """

    def __init__(self, resolution: int = 2048, seed: int = 42):
        super().__init__(resolution=resolution, seed=seed)

    # -------------------------------------------------------------------------
    # Gray-Scott 9-Point Discrete Laplacian PDE Simulator
    # -------------------------------------------------------------------------
    def simulate_gray_scott(
        self,
        sim_res: int = 512,
        num_steps: int = 240,
        Du: float = 0.16,
        Dv: float = 0.08,
        F: float = 0.034,
        k: float = 0.065,
        dt: float = 1.0,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Solves the Gray-Scott Reaction-Diffusion PDE on a 2D periodic grid.
        Returns: (U_field, V_field) of shape [sim_res, sim_res].
        """
        # 1. Initialize nutrient U = 1.0 and activator V = 0.0
        U = np.ones((sim_res, sim_res), dtype=np.float32)
        V = np.zeros((sim_res, sim_res), dtype=np.float32)

        # 2. Seed symmetric haute-couture rosette clusters
        seed_centers = [
            (sim_res // 2, sim_res // 2, 24),            # Center rosette
            (sim_res // 4, sim_res // 4, 16),            # Quadrant seeds
            (3 * sim_res // 4, sim_res // 4, 16),
            (sim_res // 4, 3 * sim_res // 4, 16),
            (3 * sim_res // 4, 3 * sim_res // 4, 16),
            (0, 0, 14),                                  # Periodic corners
            (sim_res - 1, 0, 14),
            (0, sim_res - 1, 14),
            (sim_res - 1, sim_res - 1, 14),
        ]

        for cx, cy, rad in seed_centers:
            y_min = max(0, cy - rad)
            y_max = min(sim_res, cy + rad + 1)
            x_min = max(0, cx - rad)
            x_max = min(sim_res, cx + rad + 1)

            yy, xx = np.ogrid[y_min:y_max, x_min:x_max]
            dist_sq = (xx - cx) ** 2 + (yy - cy) ** 2
            mask = dist_sq <= (rad * rad)

            U[y_min:y_max, x_min:x_max][mask] = 0.50
            V[y_min:y_max, x_min:x_max][mask] = 0.25 + self.rng.uniform(0.0, 0.1, size=np.count_nonzero(mask))

        # 3. 9-Point Isotropic Discrete Laplacian Stencil Weights
        # Stencil:
        # [0.25, 0.50, 0.25]
        # [0.50, -3.0, 0.50]
        # [0.25, 0.50, 0.25]

        for _ in range(num_steps):
            # Fast periodic 9-point discrete Laplacian using np.pad
            u_pad = np.pad(U, ((1, 1), (1, 1)), mode="wrap")
            v_pad = np.pad(V, ((1, 1), (1, 1)), mode="wrap")

            lap_u = (
                0.25 * (u_pad[:-2, :-2] + u_pad[:-2, 2:] + u_pad[2:, :-2] + u_pad[2:, 2:])
                + 0.50 * (u_pad[:-2, 1:-1] + u_pad[2:, 1:-1] + u_pad[1:-1, :-2] + u_pad[1:-1, 2:])
                - 3.00 * U
            )
            lap_v = (
                0.25 * (v_pad[:-2, :-2] + v_pad[:-2, 2:] + v_pad[2:, :-2] + v_pad[2:, 2:])
                + 0.50 * (v_pad[:-2, 1:-1] + v_pad[2:, 1:-1] + v_pad[1:-1, :-2] + v_pad[1:-1, 2:])
                - 3.00 * V
            )

            uvv = U * V * V
            du = (Du * lap_u - uvv + F * (1.0 - U)) * dt
            dv = (Dv * lap_v + uvv - (F + k) * V) * dt

            U += du
            V += dv

            np.clip(U, 0.0, 1.0, out=U)
            np.clip(V, 0.0, 1.0, out=V)

        return U, V

    # -------------------------------------------------------------------------
    # 3D Geometry Generation
    # -------------------------------------------------------------------------
    def generate_geometry(self) -> Dict[str, Any]:
        """
        Constructs high-poly 3D mesh representing cloisonné gold filigree ridges
        and concave vitreous enamel cells.
        """
        mesh_res = 128  # High-poly 3D export resolution
        _, V_sim = self.simulate_gray_scott(sim_res=mesh_res, num_steps=180)

        # Compute filigree ridges and enamel meniscus
        v_iso = 0.26
        sigma = 0.05
        ridge_mask = np.exp(-((V_sim - v_iso) ** 2) / (2.0 * sigma * sigma))
        meniscus = np.abs(V_sim - v_iso) ** 0.6 * 0.008

        # Physical 3D Z-elevation
        wall_height = 0.015
        enamel_depth = 0.008
        z_grid = ridge_mask * wall_height + (1.0 - ridge_mask) * (enamel_depth - meniscus)

        # Generate vertex grid
        y_coords, x_coords = np.mgrid[0:mesh_res, 0:mesh_res] / float(mesh_res - 1)
        verts = np.stack([x_coords, y_coords, z_grid], axis=-1).reshape(-1, 3).astype(np.float32)

        # Generate UVs
        uvs = np.stack([x_coords, y_coords], axis=-1).reshape(-1, 2).astype(np.float32)

        # Vectorized Face Generation
        idx_grid = np.arange(mesh_res * mesh_res, dtype=np.int32).reshape(mesh_res, mesh_res)
        v0 = idx_grid[:-1, :-1].ravel()
        v1 = idx_grid[:-1, 1:].ravel()
        v2 = idx_grid[1:, 1:].ravel()
        v3 = idx_grid[1:, :-1].ravel()

        faces_t1 = np.stack([v0, v1, v2], axis=-1)
        faces_t2 = np.stack([v0, v2, v3], axis=-1)
        faces = np.vstack([faces_t1, faces_t2]).astype(np.int32)

        # Vectorized Face Normal Computation
        v_a = verts[faces[:, 0]]
        v_b = verts[faces[:, 1]]
        v_c = verts[faces[:, 2]]
        face_normals = np.cross(v_b - v_a, v_c - v_a)

        normals = np.zeros_like(verts)
        np.add.at(normals, faces[:, 0], face_normals)
        np.add.at(normals, faces[:, 1], face_normals)
        np.add.at(normals, faces[:, 2], face_normals)

        n_len = np.linalg.norm(normals, axis=1, keepdims=True)
        normals /= np.maximum(n_len, 1e-8)

        return {
            "vertices": verts,
            "faces": faces,
            "normals": normals,
            "uvs": uvs,
            "metadata": {
                "archetype": "ReactionDiffusion_Cloisonne",
                "grid_res": mesh_res,
            },
        }

    # -------------------------------------------------------------------------
    # 2D Heightfield & PBR Map Synthesis
    # -------------------------------------------------------------------------
    def generate_heightfield(self) -> np.ndarray:
        """
        Generates 2D float32 heightfield array representing 24k gold filigree walls
        and pooled vitreous enamel cells.
        """
        # Run Gray-Scott simulation at 256 resolution and upsample to target resolution
        sim_res = min(256, self.res)
        _, V_sim = self.simulate_gray_scott(sim_res=sim_res, num_steps=140)

        # Upsample V_sim to target resolution via bicubic PIL
        v_img = Image.fromarray((np.clip(V_sim, 0.0, 1.0) * 255.0).astype(np.uint8), mode="L")
        v_img_high = v_img.resize((self.res, self.res), Image.Resampling.BICUBIC)
        V_high = np.array(v_img_high, dtype=np.float32) / 255.0

        # Extract filigree ridge mask along iso-contour V = 0.28
        v_iso = 0.28
        sigma = 0.04
        ridge_mask = np.exp(-((V_high - v_iso) ** 2) / (2.0 * sigma * sigma))

        # Young-Laplace concave meniscus pooling in cell basins
        meniscus = (np.abs(V_high - v_iso) ** 0.55) * 0.45

        # Combined physical heightfield
        grid = ridge_mask * 0.95 + (1.0 - ridge_mask) * (0.65 - meniscus)

        # Base micro-texture relief
        y_grid, x_grid = np.mgrid[0 : self.res, 0 : self.res] / float(self.res)
        micro_relief = 0.03 * np.sin(x_grid * 40.0 * np.pi) * np.sin(y_grid * 40.0 * np.pi)
        grid = np.clip(grid + micro_relief, 0.0, 1.0)

        # Normalize to [0.0, 1.0]
        z_min = float(grid.min())
        z_max = float(grid.max())
        if z_max > z_min:
            grid = (grid - z_min) / (z_max - z_min)

        return grid.astype(np.float32)

    def synthesize_maps(self) -> Dict[str, np.ndarray]:
        """
        Synthesizes the complete suite of PBR maps for Reaction-Diffusion Cloisons.
        """
        H_map = self.generate_heightfield()

        # 1. Masks based on height & filigree ridges
        mask_grout = H_map < 0.20
        mask_enamel_deep = (H_map >= 0.20) & (H_map < 0.50)
        mask_enamel_crest = (H_map >= 0.50) & (H_map < 0.78)
        mask_gold_filigree = H_map >= 0.78

        # 2. BaseColor (sRGB)
        # Palette: Amethyst Purple (#6A0572), Opaline Turquoise (#40E0D0), Cobalt Royal Blue (#1E3F66), 24k Gold Wire (#FFD700)
        y_grid, x_grid = np.mgrid[0 : self.res, 0 : self.res] / float(self.res)
        polish_grain = 12.0 * np.sin(x_grid * 239.0 * np.pi + y_grid * 191.0 * np.pi) + 6.0 * np.cos(x_grid * 97.0 * np.pi - y_grid * 131.0 * np.pi)
        swirl = 18.0 * np.sin(x_grid * 13.7 * np.pi + y_grid * 17.3 * np.pi)
        h_grad = 30.0 * H_map

        bc_float = np.zeros((self.res, self.res, 3), dtype=np.float32)

        # Deep enamel cell basin: Cobalt Royal Blue with subtle depth gradient
        bc_float[mask_enamel_deep, 0] = 30.0 + swirl[mask_enamel_deep] * 0.4 + h_grad[mask_enamel_deep] * 0.3
        bc_float[mask_enamel_deep, 1] = 63.0 + polish_grain[mask_enamel_deep] * 0.8 + h_grad[mask_enamel_deep] * 0.4
        bc_float[mask_enamel_deep, 2] = 102.0 + swirl[mask_enamel_deep] + h_grad[mask_enamel_deep] * 0.5

        # Mid enamel layer: Amethyst Purple to Opaline Turquoise swirl
        t_enamel = np.clip((H_map[mask_enamel_crest] - 0.50) / 0.28, 0.0, 1.0)
        c_amethyst = np.array([106.0, 5.0, 114.0], dtype=np.float32)
        c_turquoise = np.array([64.0, 224.0, 208.0], dtype=np.float32)
        c_blend = c_amethyst[None, :] * (1.0 - t_enamel[:, None]) + c_turquoise[None, :] * t_enamel[:, None]
        bc_float[mask_enamel_crest] = c_blend + polish_grain[mask_enamel_crest, None] * 0.8 + h_grad[mask_enamel_crest, None] * 0.3

        # Recessed foundation grout: Dark oxidized bronze
        bc_float[mask_grout, 0] = 20.0 + h_grad[mask_grout] * 0.2
        bc_float[mask_grout, 1] = 24.0 + polish_grain[mask_grout] * 0.5 + h_grad[mask_grout] * 0.2
        bc_float[mask_grout, 2] = 38.0 + h_grad[mask_grout] * 0.3

        # 24k Gold filigree wire cladding
        bc_float[mask_gold_filigree, 0] = 255.0
        bc_float[mask_gold_filigree, 1] = 215.0 + polish_grain[mask_gold_filigree] * 0.5 + h_grad[mask_gold_filigree] * 0.2
        bc_float[mask_gold_filigree, 2] = np.clip(10.0 + polish_grain[mask_gold_filigree] * 0.3, 0.0, 255.0)

        basecolor = np.clip(np.round(bc_float), 0, 255).astype(np.uint8)

        # 3. Roughness
        roughness = np.zeros((self.res, self.res), dtype=np.uint8)
        roughness[mask_grout] = 195         # Recessed grout: 0.76
        roughness[mask_enamel_deep] = 18    # Ultra-glossy vitreous enamel glass: 0.07
        roughness[mask_enamel_crest] = 22   # Enamel glass: 0.08
        roughness[mask_gold_filigree] = 52  # Polished 24k gold wire: 0.20

        # 4. Metallic
        metallic = np.zeros((self.res, self.res), dtype=np.uint8)
        metallic[mask_gold_filigree] = 255  # 100% Metallic gold filigree wire
        metallic[mask_grout] = 40           # Slight oxidized metallic tint

        # 5. Sheen
        sheen = np.zeros((self.res, self.res), dtype=np.uint8)
        sheen[mask_enamel_deep] = 100       # Enamel glass clearcoat reflection: 0.39
        sheen[mask_enamel_crest] = 100

        # 6. Alpha
        # Vitreous enamel depth translucency (0.70) to opaque 24k gold filigree walls (1.0)
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
