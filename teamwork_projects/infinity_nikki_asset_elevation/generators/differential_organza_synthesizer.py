"""
Differential Line Growth Organza Procedural Synthesizer (Archetype 2).
Implements iterative 4-step morphogenetic curve relaxation, 3D out-of-plane
ruffle petal meshes, continuous 3D tangent flow vectors, and gossamer sheer PBR maps.
"""

import math
from typing import Any, Dict, List, Tuple
import numpy as np

from .base_synthesizer import BaseSynthesizer


class DifferentialOrganzaSynthesizer(BaseSynthesizer):
    """
    Procedural Differential Line Growth Organza with Translucent Ruffles and Anisotropic Tangent Flow.
    """

    def __init__(self, resolution: int = 2048, seed: int = 42):
        super().__init__(resolution=resolution, seed=seed)

    # -------------------------------------------------------------------------
    # Morphogenetic Differential Line Growth Solver
    # -------------------------------------------------------------------------
    def simulate_differential_growth(
        self,
        num_seeds: int = 48,
        num_iterations: int = 60,
        d_split: float = 0.015,
        repulsion_radius: float = 0.05,
        k_rep: float = 0.025,
        k_spring: float = 0.35,
        buckle_amp: float = 0.06,
    ) -> List[np.ndarray]:
        """
        Executes morphogenetic differential curve growth relaxation.
        Returns a list of 3D polyline curves for organza ruffle petal tiers.
        """
        curves = []

        # Multi-tiered petal concentric seeds
        seed_radii = [0.15, 0.28, 0.40]
        for tier_idx, base_radius in enumerate(seed_radii):
            angles = np.linspace(0, 2 * np.pi, num_seeds, endpoint=False)
            pts = []
            for a in angles:
                r = base_radius + self.rng.uniform(-0.01, 0.01)
                x = 0.5 + r * math.cos(a)
                y = 0.5 + r * math.sin(a)
                z = 0.02 * tier_idx + 0.005 * math.sin(a * 4.0)
                pts.append([x, y, z])
            pts = np.array(pts, dtype=np.float32)

            # Iterative relaxation loop
            for step in range(num_iterations):
                n_pts = len(pts)
                if n_pts > 450:  # Bound max curve complexity
                    break

                # 1. Edge Subdivision (Splitting long edges)
                diffs = np.roll(pts, -1, axis=0) - pts
                edge_lens = np.linalg.norm(diffs, axis=1)

                new_pts = []
                for i in range(n_pts):
                    new_pts.append(pts[i])
                    if edge_lens[i] > d_split:
                        mid = (pts[i] + pts[(i + 1) % n_pts]) * 0.5
                        # Add slight outward radial noise
                        center_vec = mid[:2] - np.array([0.5, 0.5])
                        c_dist = np.linalg.norm(center_vec)
                        if c_dist > 1e-6:
                            radial_dir = center_vec / c_dist
                            mid[:2] += radial_dir * self.rng.uniform(0.001, 0.003)
                        new_pts.append(mid)

                pts = np.array(new_pts, dtype=np.float32)
                n_pts = len(pts)

                # 2. Spatial Repulsion Force (Self-Avoidance)
                forces = np.zeros_like(pts)
                # Subsample pairwise distance check for performance
                for i in range(n_pts):
                    p_i = pts[i]
                    diff = p_i - pts
                    dists = np.linalg.norm(diff[:, :2], axis=1)
                    mask = (dists > 1e-5) & (dists < repulsion_radius)
                    if np.any(mask):
                        close_diff = diff[mask, :2]
                        close_dists = dists[mask, None]
                        factor = 1.0 - (close_dists / repulsion_radius)
                        rep_vec = np.sum((close_diff / close_dists) * (factor * factor), axis=0)
                        forces[i, :2] += rep_vec * k_rep

                # 3. Neighbor Spring & Laplacian Smoothing
                p_prev = np.roll(pts, 1, axis=0)
                p_next = np.roll(pts, -1, axis=0)
                laplacian = 0.5 * (p_prev + p_next) - pts
                forces += laplacian * k_spring

                # 4. Out-of-Plane Buckling (3D Ruffles)
                curvatures = np.linalg.norm(laplacian[:, :2], axis=1)
                buckle_dir = np.sin(pts[:, 0] * 24.0 + pts[:, 1] * 24.0 + float(tier_idx))
                forces[:, 2] += curvatures * buckle_amp * buckle_dir

                # Integrate displacement & clamp domain bounds
                pts += forces * 0.15
                pts[:, 0] = np.clip(pts[:, 0], 0.05, 0.95)
                pts[:, 1] = np.clip(pts[:, 1], 0.05, 0.95)
                pts[:, 2] = np.clip(pts[:, 2], 0.0, 0.15)

            curves.append(pts)

        return curves

    # -------------------------------------------------------------------------
    # 3D Geometry Generation
    # -------------------------------------------------------------------------
    def generate_geometry(self) -> Dict[str, Any]:
        """
        Constructs the high-poly 3D mesh for organza ruffles by sweeping
        undulating 3D ribbon strips along the morphogenetic curves.
        """
        curves = self.simulate_differential_growth()
        all_verts = []
        all_faces = []
        all_norms = []
        all_uvs = []
        vert_offset = 0

        for tier_idx, curve in enumerate(curves):
            num_pts = len(curve)
            if num_pts < 3:
                continue

            # Ribbon parameters
            ribbon_width = 0.045 + 0.015 * tier_idx
            num_cross = 6  # 6 cross-section segments across ribbon

            # Compute tangents along curve
            tangents = np.roll(curve, -1, axis=0) - np.roll(curve, 1, axis=0)
            t_len = np.linalg.norm(tangents, axis=1, keepdims=True)
            tangents /= np.maximum(t_len, 1e-8)

            up = np.array([0.0, 0.0, 1.0], dtype=np.float32)
            normals_curve = np.cross(tangents, up)
            n_len = np.linalg.norm(normals_curve, axis=1, keepdims=True)
            normals_curve /= np.maximum(n_len, 1e-8)

            tier_verts = []
            tier_norms = []
            tier_uvs = []

            for i in range(num_pts):
                c_pt = curve[i]
                norm_vec = normals_curve[i]
                u_coord = float(i) / float(num_pts)

                for k in range(num_cross):
                    v_coord = float(k) / float(num_cross - 1)
                    # Fluting sinusoidal displacement across width
                    flute = 0.008 * math.sin(u_coord * 32.0 * math.pi) * v_coord
                    disp_pos = c_pt + norm_vec * (v_coord * ribbon_width)
                    disp_pos[2] += flute + v_coord * 0.012

                    surf_norm = np.array([0.0, 0.0, 1.0], dtype=np.float32)

                    tier_verts.append(disp_pos)
                    tier_norms.append(surf_norm)
                    tier_uvs.append([u_coord, v_coord])

            tier_verts = np.array(tier_verts, dtype=np.float32)
            tier_norms = np.array(tier_norms, dtype=np.float32)
            tier_uvs = np.array(tier_uvs, dtype=np.float32)

            # Faces across quad mesh
            tier_faces = []
            for i in range(num_pts):
                i_next = (i + 1) % num_pts
                for k in range(num_cross - 1):
                    v0 = i * num_cross + k
                    v1 = i * num_cross + (k + 1)
                    v2 = i_next * num_cross + (k + 1)
                    v3 = i_next * num_cross + k

                    tier_faces.append([v0, v1, v2])
                    tier_faces.append([v0, v2, v3])

            tier_faces = np.array(tier_faces, dtype=np.int32)

            all_verts.append(tier_verts)
            all_faces.append(tier_faces + vert_offset)
            all_norms.append(tier_norms)
            all_uvs.append(tier_uvs)
            vert_offset += len(tier_verts)

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
                "archetype": "DifferentialOrganza_Petals",
                "num_tiers": len(curves),
            },
        }

    # -------------------------------------------------------------------------
    # 2D Heightfield & PBR Map Synthesis
    # -------------------------------------------------------------------------
    def generate_heightfield(self) -> np.ndarray:
        """
        Generates 2D float32 heightfield representing multi-scale organza ruffles.
        """
        curves = self.simulate_differential_growth()
        grid = np.zeros((self.res, self.res), dtype=np.float32)

        # Base background silk wave
        y_grid, x_grid = np.mgrid[0 : self.res, 0 : self.res] / float(self.res)
        base_silk = 0.08 * (
            np.sin(x_grid * 6.0 * np.pi + y_grid * 4.0 * np.pi) * 0.5 + 0.5
        )
        grid += base_silk

        # Rasterize each morphed organza curve tier with varying elevations and smooth profiles
        elevations = [0.45, 0.70, 0.92]
        widths = [
            max(8.0, self.res * (12.0 / 2048.0)),
            max(12.0, self.res * (18.0 / 2048.0)),
            max(16.0, self.res * (24.0 / 2048.0)),
        ]

        for i, curve in enumerate(curves):
            elev = elevations[min(i, len(elevations) - 1)]
            w = widths[min(i, len(widths) - 1)]
            self.rasterize_curves_onto_grid(
                grid, [curve], radius_px=w, elevation=elev, profile="smooth"
            )

        # Add high-frequency micro-fluting ruffles
        fluting = 0.06 * np.sin(x_grid * 40.0 * np.pi) * np.cos(y_grid * 40.0 * np.pi)
        grid = np.clip(grid + fluting * (grid > 0.15), 0.0, 1.0)

        # Normalize heightfield to [0.0, 1.0]
        z_min = float(grid.min())
        z_max = float(grid.max())
        if z_max > z_min:
            grid = (grid - z_min) / (z_max - z_min)

        return grid.astype(np.float32)

    def synthesize_maps(self) -> Dict[str, np.ndarray]:
        """
        Synthesizes the complete suite of PBR maps for Differential Organza Petals.
        """
        H_map = self.generate_heightfield()

        # 1. BaseColor (sRGB)
        # Palette: Deep Sapphire Blue (#3C5FB9), Hydrangea Blue (#7294D4), Wisteria Lilac (#B892FF), Gossamer Violet (#D0C4DF), Dewdrop White (#F8FAFF)
        y_grid, x_grid = np.mgrid[0 : self.res, 0 : self.res] / float(self.res)
        c_deep_blue = np.array([60, 95, 185], dtype=np.float32)        # Deep ruffle fold
        c_hydrangea_blue = np.array([114, 148, 212], dtype=np.float32) # Lower ruffle body
        c_wisteria_lilac = np.array([184, 146, 255], dtype=np.float32) # Mid petal crest
        c_gossamer_violet = np.array([208, 196, 223], dtype=np.float32)# Translucent edge
        c_dewdrop_white = np.array([248, 250, 255], dtype=np.float32)  # Highlights

        h_3d = H_map[..., None]
        bc_float = np.zeros((self.res, self.res, 3), dtype=np.float32)

        mask_deep = h_3d < 0.25
        t_deep = np.clip(h_3d / 0.25, 0.0, 1.0)
        bc_float += (c_deep_blue * (1.0 - t_deep) + c_hydrangea_blue * t_deep) * mask_deep

        mask_low = (h_3d >= 0.25) & (h_3d < 0.55)
        t_low = np.clip((h_3d - 0.25) / 0.30, 0.0, 1.0)
        bc_float += (c_hydrangea_blue * (1.0 - t_low) + c_wisteria_lilac * t_low) * mask_low

        mask_mid = (h_3d >= 0.55) & (h_3d < 0.85)
        t_mid = np.clip((h_3d - 0.55) / 0.30, 0.0, 1.0)
        bc_float += (c_wisteria_lilac * (1.0 - t_mid) + c_gossamer_violet * t_mid) * mask_mid

        mask_high = h_3d >= 0.85
        t_high = np.clip((h_3d - 0.85) / 0.15, 0.0, 1.0)
        bc_float += (c_gossamer_violet * (1.0 - t_high) + c_dewdrop_white * t_high) * mask_high

        # Add haute-couture gossamer micro-twill weave and crisp petal edge gradients
        twill = 12.0 * np.sin((x_grid + y_grid) * 384.0 * np.pi) + 8.0 * np.cos((x_grid - y_grid) * 384.0 * np.pi)
        petal_edge = np.abs(np.gradient(H_map, axis=0)) + np.abs(np.gradient(H_map, axis=1))
        edge_accent = np.clip(petal_edge * 600.0, 0.0, 35.0)
        bc_float += twill[:, :, None] * 0.5 + edge_accent[:, :, None]

        basecolor = np.clip(np.round(bc_float), 0, 255).astype(np.uint8)

        # 2. Roughness
        # Smooth translucent organza silk: ~0.30 in body, slightly rougher at sheer flutter hem (0.42)
        roughness_f = 0.26 + 0.16 * (1.0 - H_map)
        roughness = np.clip(np.round(roughness_f * 255.0), 0, 255).astype(np.uint8)

        # 3. Metallic
        # Translucent organza with delicate metallic lurex thread flecks on ruffle crests
        metallic_f = (H_map ** 3) * 60.0 + 15.0 * np.sin(x_grid * 60.0 * np.pi) * (H_map > 0.70)
        metallic = np.clip(np.round(metallic_f), 0, 255).astype(np.uint8)

        # 4. Sheen
        # High anisotropic iridescent gossamer sheen: 0.85 - 0.95
        sheen_f = 0.75 + 0.22 * H_map
        sheen = np.clip(np.round(sheen_f * 255.0), 0, 255).astype(np.uint8)

        # 5. Alpha
        # Translucent organza: 0.18 at sheer edges, 0.88 at dense gathered folds
        alpha_f = 0.22 + 0.72 * H_map
        alpha = np.clip(np.round(alpha_f * 255.0), 0, 255).astype(np.uint8)

        return {
            "BaseColor": basecolor,
            "Roughness": roughness,
            "Metallic": metallic,
            "Sheen": sheen,
            "Alpha": alpha,
            "Height": H_map,
        }
