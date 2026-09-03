"""
High-to-Low PBR Texture Baker for Haute-Couture Geometry.
Bakes 2048x2048 POT 16-bit Height, DirectX Normal (Green=-Y), Curvature,
Horizon-Based Ambient Occlusion, and Linear Packed ORM maps.
"""

import os
from typing import Any, Dict, Optional, Tuple, Union
import numpy as np
from PIL import Image


class HighToLowBaker:
    """
    Vectorized High-to-Low Baker for converting procedural 3D heightfields
    and micro-geometry into production-ready PBR texture maps.
    """

    def __init__(self, resolution: int = 2048):
        self.res = int(resolution)

    def bake_height_16bit(
        self, z_depth: np.ndarray, output_path: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Normalizes float32 depth to [0.0, 1.0] and converts to 16-bit unsigned
        grayscale PNG (uint16, 0..65535, Pillow mode 'I;16').

        Returns: (height_norm_float32, height_uint16)
        """
        z_float = z_depth.astype(np.float32)
        z_min = float(np.min(z_float))
        z_max = float(np.max(z_float))

        if abs(z_max - z_min) < 1e-7:
            h_norm = np.zeros_like(z_float, dtype=np.float32)
        else:
            h_norm = (z_float - z_min) / (z_max - z_min)

        h_norm = np.clip(h_norm, 0.0, 1.0).astype(np.float32)
        h_uint16 = np.clip(np.round(h_norm * 65535.0), 0, 65535).astype(np.uint16)

        if output_path is not None:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            img = Image.fromarray(h_uint16)
            img.save(output_path)

        return h_norm, h_uint16

    def compute_directx_normals(
        self, height_norm: np.ndarray, bump_scale: float = 25.0
    ) -> np.ndarray:
        """
        Computes DirectX Tangent Space Normal Map from normalized height map.
        Green Channel = -Y (DirectX standard), ||N|| = 1.0.

        Returns: uint8 RGB array [H, W, 3].
        """
        h = height_norm.astype(np.float32) * float(bump_scale)

        # Central differences with periodic wrapping
        dx = (np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)) * 0.5
        dy = (np.roll(h, -1, axis=0) - np.roll(h, 1, axis=0)) * 0.5

        # Tangent space normal vector: (-dx, -dy, 1.0)
        nx = -dx
        ny = -dy
        nz = np.ones_like(h, dtype=np.float32)

        # Normalization to exact unit vector length (||N|| = 1.0)
        length = np.sqrt(nx * nx + ny * ny + nz * nz)
        length = np.maximum(length, 1e-8)
        nx /= length
        ny /= length
        nz /= length

        # DirectX Tangent Normal Encoding:
        # Red = (nx * 0.5 + 0.5) * 255  (Nx = -dh/dx)
        # Green = (ny * 0.5 + 0.5) * 255  (Ny = -dh/dy, DirectX Green = -Y)
        # Blue = (nz * 0.5 + 0.5) * 255  (Nz = 1.0 / length)
        r = np.clip(np.round((nx * 0.5 + 0.5) * 255.0), 0, 255).astype(np.uint8)
        g = np.clip(np.round((ny * 0.5 + 0.5) * 255.0), 0, 255).astype(np.uint8)
        b = np.clip(np.round((nz * 0.5 + 0.5) * 255.0), 0, 255).astype(np.uint8)

        normal_rgb = np.stack([r, g, b], axis=-1)
        return normal_rgb

    def compute_curvature(self, height_norm: np.ndarray) -> np.ndarray:
        """
        Computes mean surface curvature (Convex ridges & concave crevices)
        via 2D discrete Laplacian.
        Neutral curvature baseline is 128 (0.5).

        Returns: uint8 grayscale array [H, W].
        """
        h = height_norm.astype(np.float32)
        laplacian = (
            np.roll(h, -1, axis=0)
            + np.roll(h, 1, axis=0)
            + np.roll(h, -1, axis=1)
            + np.roll(h, 1, axis=1)
            - 4.0 * h
        )
        curv = np.clip(np.round(128.0 - laplacian * 512.0), 0, 255).astype(np.uint8)
        return curv

    def compute_ambient_occlusion(
        self,
        height_norm: np.ndarray,
        num_directions: int = 8,
        max_radius: int = 16,
    ) -> np.ndarray:
        """
        Computes Horizon-Based Ambient Occlusion from heightfield.

        Returns: uint8 grayscale array [H, W].
        """
        h = height_norm.astype(np.float32)
        ao_accum = np.zeros_like(h)

        angles = np.linspace(0, 2 * np.pi, num_directions, endpoint=False)
        for theta in angles:
            dx = int(round(np.cos(theta)))
            dy = int(round(np.sin(theta)))
            max_slope = np.zeros_like(h)
            for r in range(1, max_radius + 1):
                h_sample = np.roll(np.roll(h, -dy * r, axis=0), -dx * r, axis=1)
                slope = (h_sample - h) / float(r)
                max_slope = np.maximum(max_slope, slope)
            ao_accum += np.clip(max_slope * 2.5, 0.0, 1.0)

        ao = np.clip(1.0 - (ao_accum / float(num_directions)), 0.0, 1.0)
        ao_uint8 = np.clip(np.round(ao * 255.0), 0, 255).astype(np.uint8)
        return ao_uint8

    def pack_orm(
        self,
        ao: np.ndarray,
        roughness: np.ndarray,
        metallic: np.ndarray,
    ) -> np.ndarray:
        """
        Packs discrete maps into Linear ORM texture:
        - Red: Ambient Occlusion
        - Green: Roughness
        - Blue: Metallic

        Returns: uint8 RGB array [H, W, 3].
        """
        ao_u8 = ao if ao.dtype == np.uint8 else (np.clip(ao, 0.0, 1.0) * 255.0).astype(np.uint8)
        r_u8 = roughness if roughness.dtype == np.uint8 else (np.clip(roughness, 0.0, 1.0) * 255.0).astype(np.uint8)
        m_u8 = metallic if metallic.dtype == np.uint8 else (np.clip(metallic, 0.0, 1.0) * 255.0).astype(np.uint8)

        return np.stack([ao_u8, r_u8, m_u8], axis=-1)

    def bake_all_channels(
        self,
        maps: Dict[str, np.ndarray],
        out_dir: str,
        prefix: str,
    ) -> Dict[str, str]:
        """
        Bakes and exports all 9 production PBR maps matching the project contract:
        - T_HauteCouture_<Archetype>_BC.png (sRGB 8-bit RGB)
        - T_HauteCouture_<Archetype>_N.png (DirectX Green=-Y, Unit Normalized)
        - T_HauteCouture_<Archetype>_ORM.png (Linear 8-bit RGB: R=AO, G=Roughness, B=Metallic)
        - T_HauteCouture_<Archetype>_H.png (Linear 16-bit Grayscale uint16)
        - T_HauteCouture_<Archetype>_AO.png (Linear 8-bit Grayscale)
        - T_HauteCouture_<Archetype>_R.png (Linear 8-bit Grayscale)
        - T_HauteCouture_<Archetype>_M.png (Linear 8-bit Grayscale)
        - T_HauteCouture_<Archetype>_Sheen.png (Linear 8-bit Grayscale)
        - T_HauteCouture_<Archetype>_Alpha.png (Linear 8-bit Grayscale)
        """
        os.makedirs(out_dir, exist_ok=True)
        results: Dict[str, str] = {}

        # 1. Height & 16-bit export
        h_raw = maps.get("Height", maps.get("height", np.zeros((self.res, self.res), dtype=np.float32)))
        h_path = os.path.join(out_dir, f"{prefix}_H.png")
        h_norm, h_uint16 = self.bake_height_16bit(h_raw, h_path)
        results["Height"] = h_path

        # 2. Normal (DirectX Tangent Space)
        if "Normal" in maps:
            normal_rgb = maps["Normal"]
        else:
            bump = maps.get("bump_scale", 25.0)
            normal_rgb = self.compute_directx_normals(h_norm, bump_scale=bump)
        n_path = os.path.join(out_dir, f"{prefix}_N.png")
        Image.fromarray(normal_rgb, mode="RGB").save(n_path)
        results["Normal"] = n_path

        # 3. AO
        if "AO" in maps:
            ao_u8 = maps["AO"]
        else:
            ao_u8 = self.compute_ambient_occlusion(h_norm)
        ao_path = os.path.join(out_dir, f"{prefix}_AO.png")
        Image.fromarray(ao_u8, mode="L").save(ao_path)
        results["AO"] = ao_path

        # 4. Roughness
        r_u8 = maps.get("Roughness", maps.get("roughness", np.full((self.res, self.res), 128, dtype=np.uint8)))
        if r_u8.dtype != np.uint8:
            r_u8 = np.clip(np.round(r_u8 * 255.0), 0, 255).astype(np.uint8)
        r_path = os.path.join(out_dir, f"{prefix}_R.png")
        Image.fromarray(r_u8, mode="L").save(r_path)
        results["Roughness"] = r_path

        # 5. Metallic
        m_u8 = maps.get("Metallic", maps.get("metallic", np.zeros((self.res, self.res), dtype=np.uint8)))
        if m_u8.dtype != np.uint8:
            m_u8 = np.clip(np.round(m_u8 * 255.0), 0, 255).astype(np.uint8)
        m_path = os.path.join(out_dir, f"{prefix}_M.png")
        Image.fromarray(m_u8, mode="L").save(m_path)
        results["Metallic"] = m_path

        # 6. Packed ORM
        orm_rgb = self.pack_orm(ao_u8, r_u8, m_u8)
        orm_path = os.path.join(out_dir, f"{prefix}_ORM.png")
        Image.fromarray(orm_rgb, mode="RGB").save(orm_path)
        results["ORM"] = orm_path

        # 7. BaseColor (sRGB)
        bc_rgb = maps.get("BaseColor", maps.get("basecolor", np.full((self.res, self.res, 3), 200, dtype=np.uint8)))
        bc_path = os.path.join(out_dir, f"{prefix}_BC.png")
        Image.fromarray(bc_rgb, mode="RGB").save(bc_path)
        results["BaseColor"] = bc_path

        # 8. Sheen
        sheen_u8 = maps.get("Sheen", maps.get("sheen", np.zeros((self.res, self.res), dtype=np.uint8)))
        if sheen_u8.dtype != np.uint8:
            sheen_u8 = np.clip(np.round(sheen_u8 * 255.0), 0, 255).astype(np.uint8)
        sheen_path = os.path.join(out_dir, f"{prefix}_Sheen.png")
        Image.fromarray(sheen_u8, mode="L").save(sheen_path)
        results["Sheen"] = sheen_path

        # 9. Alpha
        alpha_u8 = maps.get("Alpha", maps.get("alpha", np.full((self.res, self.res), 255, dtype=np.uint8)))
        if alpha_u8.dtype != np.uint8:
            alpha_u8 = np.clip(np.round(alpha_u8 * 255.0), 0, 255).astype(np.uint8)
        alpha_path = os.path.join(out_dir, f"{prefix}_Alpha.png")
        Image.fromarray(alpha_u8, mode="L").save(alpha_path)
        results["Alpha"] = alpha_path

        return results
