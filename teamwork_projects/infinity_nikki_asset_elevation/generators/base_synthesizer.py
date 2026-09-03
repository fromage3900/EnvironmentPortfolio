"""
Base Synthesizer for Procedural Haute-Couture Geometry and PBR Texture Suites.
Provides common mathematical utilities, 3D Wavefront OBJ mesh export,
vectorized curve/point rasterization, and PBR color grading functions.
"""

from abc import ABC, abstractmethod
import math
import os
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class BaseSynthesizer(ABC):
    """
    Abstract base class for all Infinity Nikki procedural haute-couture generators.
    """

    def __init__(self, resolution: int = 2048, seed: int = 42):
        self.res = int(resolution)
        self.seed = int(seed)
        self.rng = np.random.default_rng(self.seed)

    # -------------------------------------------------------------------------
    # 3D Mesh Exporter (.obj)
    # -------------------------------------------------------------------------
    @staticmethod
    def export_obj(
        filepath: str,
        vertices: np.ndarray,
        faces: np.ndarray,
        normals: Optional[np.ndarray] = None,
        uvs: Optional[np.ndarray] = None,
        material_name: str = "M_HauteCouture_Material",
    ) -> str:
        """
        Exports geometry as a standard Wavefront OBJ file.

        Args:
            filepath: Destination .obj path.
            vertices: [N, 3] float array of vertex positions (x, y, z).
            faces: [M, 3] or [M, 4] int array of 0-based face vertex indices.
            normals: Optional [N, 3] or [M, 3] float array of normal vectors.
            uvs: Optional [N, 2] float array of (u, v) texture coordinates.
            material_name: Name of the OBJ material group.
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Infinity Nikki Procedural Haute-Couture 3D Mesh\n")
            f.write(f"# Vertices: {len(vertices)}, Faces: {len(faces)}\n")
            f.write(f"usemtl {material_name}\n\n")

            # 1. Vertices
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")

            # 2. UVs
            has_uvs = uvs is not None and len(uvs) == len(vertices)
            if has_uvs:
                for uv in uvs:
                    f.write(f"vt {uv[0]:.6f} {uv[1]:.6f}\n")

            # 3. Normals
            has_normals = normals is not None and len(normals) == len(vertices)
            if has_normals:
                for n in normals:
                    f.write(f"vn {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}\n")

            # 4. Faces (1-indexed in OBJ)
            for face in faces:
                idx = [i + 1 for i in face]
                if has_uvs and has_normals:
                    f_str = " ".join(f"{i}/{i}/{i}" for i in idx)
                elif has_uvs:
                    f_str = " ".join(f"{i}/{i}" for i in idx)
                elif has_normals:
                    f_str = " ".join(f"{i}//{i}" for i in idx)
                else:
                    f_str = " ".join(f"{i}" for i in idx)
                f.write(f"f {f_str}\n")

        return filepath

    # -------------------------------------------------------------------------
    # Curve & Tube Mesh Construction Helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def build_tube_mesh(
        curve_pts: np.ndarray,
        radius: float = 0.005,
        sides: int = 8,
        closed_loop: bool = False,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Sweeps an N-sided circular cross-section along a 3D space curve using
        the Frenet-Serret / Parallel Transport frame.

        Returns: (vertices, faces, normals, uvs)
        """
        num_pts = len(curve_pts)
        if num_pts < 2:
            return (
                np.zeros((0, 3), dtype=np.float32),
                np.zeros((0, 3), dtype=np.int32),
                np.zeros((0, 3), dtype=np.float32),
                np.zeros((0, 2), dtype=np.float32),
            )

        # 1. Tangents
        tangents = np.zeros_like(curve_pts)
        tangents[0] = curve_pts[1] - curve_pts[0]
        tangents[-1] = curve_pts[-1] - curve_pts[-2]
        if num_pts > 2:
            tangents[1:-1] = curve_pts[2:] - curve_pts[:-2]
        t_len = np.linalg.norm(tangents, axis=1, keepdims=True)
        t_len = np.maximum(t_len, 1e-8)
        tangents /= t_len

        # 2. Parallel Transport Frame
        frames_n = np.zeros_like(curve_pts)
        frames_b = np.zeros_like(curve_pts)

        # Initial normal
        t0 = tangents[0]
        up = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        if abs(np.dot(t0, up)) > 0.9:
            up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        n0 = np.cross(t0, up)
        n0 /= max(np.linalg.norm(n0), 1e-8)
        b0 = np.cross(t0, n0)
        frames_n[0] = n0
        frames_b[0] = b0

        # Propagate frame along curve
        for i in range(1, num_pts):
            t_prev = tangents[i - 1]
            t_curr = tangents[i]
            axis = np.cross(t_prev, t_curr)
            axis_len = np.linalg.norm(axis)
            if axis_len > 1e-6:
                axis /= axis_len
                angle = math.acos(np.clip(np.dot(t_prev, t_curr), -1.0, 1.0))
                # Rodrigues rotation
                n_prev = frames_n[i - 1]
                n_curr = (
                    n_prev * math.cos(angle)
                    + np.cross(axis, n_prev) * math.sin(angle)
                    + axis * np.dot(axis, n_prev) * (1.0 - math.cos(angle))
                )
                n_curr /= max(np.linalg.norm(n_curr), 1e-8)
            else:
                n_curr = frames_n[i - 1]

            frames_n[i] = n_curr
            frames_b[i] = np.cross(t_curr, n_curr)

        # 3. Generate ring vertices
        angles = np.linspace(0, 2 * np.pi, sides, endpoint=False)
        cos_a = np.cos(angles)[:, None]  # [sides, 1]
        sin_a = np.sin(angles)[:, None]  # [sides, 1]

        all_verts = []
        all_norms = []
        all_uvs = []

        for i in range(num_pts):
            center = curve_pts[i]
            N = frames_n[i]
            B = frames_b[i]
            u_coord = float(i) / float(max(num_pts - 1, 1))

            # Ring vertex positions
            ring_disp = cos_a * N + sin_a * B  # [sides, 3]
            ring_pos = center + radius * ring_disp
            ring_norm = ring_disp / max(np.linalg.norm(ring_disp, axis=1, keepdims=True).mean(), 1e-8)

            all_verts.append(ring_pos)
            all_norms.append(ring_norm)

            ring_uvs = np.zeros((sides, 2), dtype=np.float32)
            ring_uvs[:, 0] = u_coord
            ring_uvs[:, 1] = np.linspace(0, 1, sides, endpoint=False)
            all_uvs.append(ring_uvs)

        vertices = np.vstack(all_verts).astype(np.float32)
        normals = np.vstack(all_norms).astype(np.float32)
        uvs = np.vstack(all_uvs).astype(np.float32)

        # 4. Generate quad faces (as 2 triangles each)
        faces = []
        ring_segments = num_pts if closed_loop else num_pts - 1
        for i in range(ring_segments):
            r1 = i * sides
            r2 = ((i + 1) % num_pts) * sides
            for s in range(sides):
                s_next = (s + 1) % sides
                v0 = r1 + s
                v1 = r1 + s_next
                v2 = r2 + s_next
                v3 = r2 + s

                faces.append([v0, v1, v2])
                faces.append([v0, v2, v3])

        faces = np.array(faces, dtype=np.int32)
        return vertices, faces, normals, uvs

    # -------------------------------------------------------------------------
    # 3D Sphere & Bicone Primitive Helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def build_sphere_mesh(
        center: np.ndarray,
        radius: float = 0.01,
        lat_res: int = 12,
        lon_res: int = 16,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Creates a UV sphere mesh at specified center."""
        lats = np.linspace(-np.pi / 2, np.pi / 2, lat_res)
        lons = np.linspace(0, 2 * np.pi, lon_res, endpoint=False)

        verts = []
        norms = []
        for lat in lats:
            for lon in lons:
                x = math.cos(lat) * math.cos(lon)
                y = math.cos(lat) * math.sin(lon)
                z = math.sin(lat)
                norm = np.array([x, y, z], dtype=np.float32)
                pos = center + radius * norm
                verts.append(pos)
                norms.append(norm)

        verts = np.array(verts, dtype=np.float32)
        norms = np.array(norms, dtype=np.float32)

        faces = []
        for i in range(lat_res - 1):
            r1 = i * lon_res
            r2 = (i + 1) * lon_res
            for j in range(lon_res):
                j_next = (j + 1) % lon_res
                faces.append([r1 + j, r1 + j_next, r2 + j_next])
                faces.append([r1 + j, r2 + j_next, r2 + j])

        return verts, np.array(faces, dtype=np.int32), norms

    @staticmethod
    def build_bicone_mesh(
        center: np.ndarray,
        radius: float = 0.01,
        height: float = 0.016,
        facets: int = 8,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Creates a faceted dual-conical crystal seed bead mesh."""
        angles = np.linspace(0, 2 * np.pi, facets, endpoint=False)
        base_ring = np.zeros((facets, 3), dtype=np.float32)
        base_ring[:, 0] = center[0] + radius * np.cos(angles)
        base_ring[:, 1] = center[1] + radius * np.sin(angles)
        base_ring[:, 2] = center[2]

        top_apex = np.array([center[0], center[1], center[2] + height * 0.5], dtype=np.float32)
        bot_apex = np.array([center[0], center[1], center[2] - height * 0.5], dtype=np.float32)

        verts = [top_apex, bot_apex]
        for pt in base_ring:
            verts.append(pt)
        verts = np.array(verts, dtype=np.float32)

        faces = []
        for k in range(facets):
            k_next = (k + 1) % facets
            # Top cone triangle
            faces.append([0, 2 + k, 2 + k_next])
            # Bottom cone triangle
            faces.append([1, 2 + k_next, 2 + k])

        faces = np.array(faces, dtype=np.int32)
        # Compute face normals
        norms = np.zeros_like(verts)
        for f in faces:
            v0, v1, v2 = verts[f[0]], verts[f[1]], verts[f[2]]
            fn = np.cross(v1 - v0, v2 - v0)
            fn /= max(np.linalg.norm(fn), 1e-8)
            norms[f[0]] += fn
            norms[f[1]] += fn
            norms[f[2]] += fn
        n_len = np.linalg.norm(norms, axis=1, keepdims=True)
        norms /= np.maximum(n_len, 1e-8)

        return verts, faces, norms

    # -------------------------------------------------------------------------
    # Vectorized 2D Rasterization & Heightfield Painting (High Performance)
    # -------------------------------------------------------------------------
    def rasterize_curves_onto_grid(
        self,
        grid: np.ndarray,
        curves: List[np.ndarray],
        radius_px: float = 4.0,
        elevation: float = 0.5,
        profile: str = "dome",
    ) -> np.ndarray:
        """
        Vectorized polyline curve rasterizer onto 2D float heightfield grid [H, W]
        using native NumPy ufuncs.
        """
        H, W = grid.shape
        r = max(int(math.ceil(radius_px)), 1)
        r2 = radius_px * radius_px

        all_sample_pts = []
        for curve in curves:
            if len(curve) < 2:
                continue

            dists = np.linalg.norm(np.diff(curve[:, :2], axis=0), axis=1)
            total_len = float(np.sum(dists))
            if total_len < 1e-6:
                continue

            num_steps = max(int(total_len * max(H, W) * 1.5), len(curve) * 2)
            t_orig = np.concatenate([[0.0], np.cumsum(dists)])
            t_interp = np.linspace(0, total_len, num_steps)
            x_interp = np.interp(t_interp, t_orig, curve[:, 0]) * W
            y_interp = np.interp(t_interp, t_orig, curve[:, 1]) * H

            if curve.shape[1] >= 3:
                z_interp = np.interp(t_interp, t_orig, curve[:, 2])
            else:
                z_interp = np.full(num_steps, elevation, dtype=np.float32)

            pts_stacked = np.stack([x_interp, y_interp, z_interp], axis=-1)
            all_sample_pts.append(pts_stacked)

        if not all_sample_pts:
            return grid

        all_pts = np.vstack(all_sample_pts)
        x_base = np.round(all_pts[:, 0]).astype(np.int32)
        y_base = np.round(all_pts[:, 1]).astype(np.int32)
        z_base = all_pts[:, 2].astype(np.float32)

        # Iterate over kernel offsets (dx, dy) in [-r, r]
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                dist_sq = dx * dx + dy * dy
                if dist_sq > r2:
                    continue
                d_norm = math.sqrt(dist_sq) / max(radius_px, 1e-4)
                if profile == "dome":
                    factor = math.sqrt(max(0.0, 1.0 - d_norm**2))
                elif profile == "smooth":
                    factor = 0.5 + 0.5 * math.cos(math.pi * d_norm)
                elif profile == "ridge":
                    factor = 1.0 - d_norm
                else:
                    factor = 1.0

                elev = z_base * factor
                px = np.clip(x_base + dx, 0, W - 1)
                py = np.clip(y_base + dy, 0, H - 1)

                np.maximum.at(grid, (py, px), elev)

        return grid

    def rasterize_points_onto_grid(
        self,
        grid: np.ndarray,
        points: np.ndarray,
        radius_px: float = 8.0,
        height_val: float = 0.8,
        shape: str = "sphere",
    ) -> np.ndarray:
        """
        Vectorized 3D point primitive stamper onto 2D float heightfield grid [H, W].
        """
        if len(points) == 0:
            return grid

        H, W = grid.shape
        r = max(int(math.ceil(radius_px)), 1)
        r2 = radius_px * radius_px

        x_base = np.round(points[:, 0] * W).astype(np.int32)
        y_base = np.round(points[:, 1] * H).astype(np.int32)
        z_base = (
            points[:, 2].astype(np.float32)
            if points.shape[1] >= 3
            else np.full(len(points), height_val, dtype=np.float32)
        )

        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                dist_sq = dx * dx + dy * dy
                if dist_sq > r2:
                    continue
                d_norm = math.sqrt(dist_sq) / max(radius_px, 1e-4)
                if shape == "sphere":
                    factor = math.sqrt(max(0.0, 1.0 - d_norm**2))
                elif shape == "bicone":
                    factor = 1.0 - d_norm
                else:
                    factor = 0.5 + 0.5 * math.cos(math.pi * d_norm)

                elev = z_base * factor
                px = np.clip(x_base + dx, 0, W - 1)
                py = np.clip(y_base + dy, 0, H - 1)

                np.maximum.at(grid, (py, px), elev)

        return grid

    # -------------------------------------------------------------------------
    # PBR Map Synthesis Utilities
    # -------------------------------------------------------------------------
    @staticmethod
    def blend_colors(
        c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: np.ndarray
    ) -> np.ndarray:
        """Linear RGB interpolation between two colors driven by weight array t."""
        t_clamped = np.clip(t[..., None], 0.0, 1.0)
        c1_arr = np.array(c1, dtype=np.float32)
        c2_arr = np.array(c2, dtype=np.float32)
        return (c1_arr * (1.0 - t_clamped) + c2_arr * t_clamped).astype(np.uint8)

    # -------------------------------------------------------------------------
    # Abstract Interface
    # -------------------------------------------------------------------------
    @abstractmethod
    def generate_geometry(self) -> Dict[str, Any]:
        """
        Constructs the high-poly 3D mesh for the archetype.
        Returns:
            {
                "vertices": np.ndarray [N, 3],
                "faces": np.ndarray [M, 3 or 4],
                "normals": np.ndarray [N, 3],
                "uvs": np.ndarray [N, 2],
                "metadata": dict
            }
        """
        pass

    @abstractmethod
    def generate_heightfield(self) -> np.ndarray:
        """
        Generates 2D float32 depth / height field [H, W] normalized [0.0, 1.0].
        """
        pass

    @abstractmethod
    def synthesize_maps(self) -> Dict[str, np.ndarray]:
        """
        Generates all PBR map channels for the archetype.
        Returns dict with keys:
            - 'BaseColor': [H, W, 3] uint8
            - 'Roughness': [H, W] uint8
            - 'Metallic': [H, W] uint8
            - 'Sheen': [H, W] uint8
            - 'Alpha': [H, W] uint8
            - 'Height': [H, W] float32 [0.0, 1.0]
        """
        pass
