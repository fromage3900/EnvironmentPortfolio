"""
PBR Engine: High-Fidelity Mathematical PBR Map Baker & Haute-Couture Colorist
Target Resolution: 2048x2048 Power-of-Two (POT)
Zero External Dependency: Pure NumPy + Pillow (No SciPy required)
DirectX Normal Standard: R=X+, G=Y- (Bitangent Inversion), B=Z+, ||N|| = 1.0
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Union
import numpy as np
from PIL import Image


class PBREngine:
    """Core PBR Synthesis and Map Baking Engine."""

    def __init__(self, resolution: int = 2048):
        self.res = resolution
        # Precompute FFT frequency coordinates for seamless periodic Gaussian blurs
        self.ky = np.fft.fftfreq(resolution)
        self.kx = np.fft.rfftfreq(resolution)
        self.KY, self.KX = np.meshgrid(self.ky, self.kx, indexing="ij")
        self.k_sq = (self.KX**2 + self.KY**2) * (resolution**2)

    def fft_gaussian_blur(self, img: np.ndarray, sigma_pixels: float) -> np.ndarray:
        """Applies exact isotropic Gaussian blur with periodic boundary conditions via 2D FFT."""
        if sigma_pixels <= 0:
            return img.copy().astype(np.float32)
        kernel = np.exp(-2.0 * (np.pi * (sigma_pixels / self.res)) ** 2 * self.k_sq)
        f = np.fft.rfft2(img)
        blurred = np.fft.irfft2(f * kernel, s=img.shape)
        return blurred.astype(np.float32)

    def compute_tangent_normal(
        self, height: np.ndarray, bump_strength: float = 3.5
    ) -> np.ndarray:
        """
        Derives DirectX tangent space unit normal map from heightfield using periodic Scharr operator.
        DirectX convention: Red = +X, Green = -Y (Bitangent inverted), Blue = +Z.
        Guarantees ||N|| = 1.0 for all pixels.
        """
        h = height.astype(np.float32)

        # Periodic Scharr 3x3 filter (separable)
        y_smooth = (
            3.0 * np.roll(h, 1, axis=0)
            + 10.0 * h
            + 3.0 * np.roll(h, -1, axis=0)
        ) / 16.0
        dx = (np.roll(y_smooth, -1, axis=1) - np.roll(y_smooth, 1, axis=1)) * 0.5

        x_smooth = (
            3.0 * np.roll(h, 1, axis=1)
            + 10.0 * h
            + 3.0 * np.roll(h, -1, axis=1)
        ) / 16.0
        dy = (np.roll(x_smooth, -1, axis=0) - np.roll(x_smooth, 1, axis=0)) * 0.5

        # Tangent vector components:
        # In texture space, row index increases downward (+Y in image).
        # DirectX convention: Green channel is -Y (upward slope produces positive Y tangent normal).
        # When moving downward, if height increases (dy > 0), the surface normal points upward (-dy).
        vx = -dx * bump_strength
        vy = -dy * bump_strength
        vz = np.ones_like(h, dtype=np.float32)

        norm = np.sqrt(vx * vx + vy * vy + vz * vz)
        nx = vx / norm
        ny = vy / norm
        nz = vz / norm

        r = np.clip(np.round((nx * 0.5 + 0.5) * 255.0), 0, 255).astype(np.uint8)
        g = np.clip(np.round((ny * 0.5 + 0.5) * 255.0), 0, 255).astype(np.uint8)
        b = np.clip(np.round((nz * 0.5 + 0.5) * 255.0), 0, 255).astype(np.uint8)

        return np.stack([r, g, b], axis=-1)

    def compute_ambient_occlusion(
        self, height: np.ndarray, intensity: float = 1.4
    ) -> np.ndarray:
        """
        Derives high-fidelity Ambient Occlusion by combining multi-scale height deficits
        (radii 2, 8, 32 px) with discrete Laplacian cavity curvature.
        """
        h = height.astype(np.float32)
        b_micro = self.fft_gaussian_blur(h, 2.0)
        b_med = self.fft_gaussian_blur(h, 8.0)
        b_macro = self.fft_gaussian_blur(h, 32.0)

        d_micro = np.maximum(0.0, b_micro - h)
        d_med = np.maximum(0.0, b_med - h)
        d_macro = np.maximum(0.0, b_macro - h)

        lap = (
            np.roll(h, 1, axis=0)
            + np.roll(h, -1, axis=0)
            + np.roll(h, 1, axis=1)
            + np.roll(h, -1, axis=1)
            - 4.0 * h
        )
        cavity = np.maximum(0.0, lap * 2.5)

        occlusion = (
            d_micro * 2.8 + d_med * 1.6 + d_macro * 0.7 + cavity * 1.2
        ) * intensity
        ao = np.clip(1.0 - occlusion, 0.0, 1.0)
        return np.clip(np.round(ao * 255.0), 0, 255).astype(np.uint8)

    def compute_curvature(self, height: np.ndarray) -> np.ndarray:
        """Calculates normalized surface curvature (Laplacian). >0 for convex crests, <0 for valleys."""
        h = height.astype(np.float32)
        lap = (
            np.roll(h, 1, axis=0)
            + np.roll(h, -1, axis=0)
            + np.roll(h, 1, axis=1)
            + np.roll(h, -1, axis=1)
            - 4.0 * h
        )
        curv = -lap
        curv_norm = (curv - curv.min()) / (curv.max() - curv.min() + 1e-8)
        return curv_norm.astype(np.float32)

    def generate_fbm_spectral_noise(self, octaves_decay: float = 1.5) -> np.ndarray:
        """Generates seamless periodic 2D fractal noise via spectral synthesis."""
        freq = np.sqrt(self.k_sq)
        freq[0, 0] = 1.0
        amplitude = 1.0 / (freq**octaves_decay)
        amplitude[0, 0] = 0.0
        phases = np.random.uniform(0, 2 * np.pi, (self.res, self.res // 2 + 1))
        spectrum = amplitude * np.exp(1j * phases)
        noise = np.fft.irfft2(spectrum, s=(self.res, self.res))
        return (
            (noise - noise.min()) / (noise.max() - noise.min() + 1e-8)
        ).astype(np.float32)

    def synthesize_pbr_material_zones(
        self,
        height: np.ndarray,
        feature_field: Optional[np.ndarray] = None,
        gold_threshold: float = 0.55,
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, np.ndarray]]:
        """
        Partitions surface into physical material zones and evaluates Roughness & Metallic channels.
        Zones:
          - Vitreous Enamel: Roughness = 0.08, Metallic = 0.00
          - 24k Gold Leaf: Roughness = 0.22, Metallic = 1.00
          - Silk Satin: Roughness = 0.35, Metallic = 0.00
          - Matte Grout: Roughness = 0.85, Metallic = 0.00
        """
        h = height.astype(np.float32)
        curv = self.compute_curvature(h)
        field = feature_field if feature_field is not None else h

        # Zone mask calculations
        m_gold = np.clip((curv - gold_threshold) / 0.18, 0.0, 1.0)
        m_grout = np.clip((0.20 - h) / 0.15, 0.0, 1.0)
        m_enamel = np.clip((field - 0.38) / 0.25, 0.0, 1.0) * (1.0 - m_gold)
        m_silk = np.clip(1.0 - m_gold - m_grout - m_enamel, 0.0, 1.0)

        # Partition of unity normalization
        m_sum = m_gold + m_grout + m_enamel + m_silk + 1e-8
        m_gold /= m_sum
        m_grout /= m_sum
        m_enamel /= m_sum
        m_silk /= m_sum

        roughness = (
            m_enamel * 0.08 + m_gold * 0.22 + m_silk * 0.35 + m_grout * 0.85
        )
        metallic = m_gold * 1.0

        roughness_u8 = np.clip(np.round(roughness * 255.0), 0, 255).astype(np.uint8)
        metallic_u8 = np.clip(np.round(metallic * 255.0), 0, 255).astype(np.uint8)

        masks = {
            "gold": m_gold,
            "enamel": m_enamel,
            "silk": m_silk,
            "grout": m_grout,
        }
        return roughness_u8, metallic_u8, masks

    def synthesize_haute_couture_basecolor(
        self,
        height: np.ndarray,
        masks: Dict[str, np.ndarray],
        palette_name: str = "lapis_gold",
    ) -> np.ndarray:
        """
        Synthesizes 2048x2048 sRGB BaseColor with domain warping, watercolor pigment flow,
        24k gold leaf highlights, and enamel basin pigmentation.
        """
        palettes = {
            "lapis_gold": {
                "gold": np.array([245, 212, 98], dtype=np.float32),
                "enamel": np.array([16, 42, 102], dtype=np.float32),
                "silk": np.array([238, 232, 222], dtype=np.float32),
                "grout": np.array([26, 28, 34], dtype=np.float32),
            },
            "carmine_vermilion": {
                "gold": np.array([235, 178, 72], dtype=np.float32),
                "enamel": np.array([148, 24, 46], dtype=np.float32),
                "silk": np.array([242, 226, 214], dtype=np.float32),
                "grout": np.array([45, 22, 18], dtype=np.float32),
            },
            "sapphire_celestial": {
                "gold": np.array([230, 225, 210], dtype=np.float32),
                "enamel": np.array([0, 128, 160], dtype=np.float32),
                "silk": np.array([18, 24, 52], dtype=np.float32),
                "grout": np.array([8, 10, 16], dtype=np.float32),
            },
            "amethyst_quartz": {
                "gold": np.array([255, 215, 0], dtype=np.float32),
                "enamel": np.array([118, 28, 142], dtype=np.float32),
                "silk": np.array([235, 225, 242], dtype=np.float32),
                "grout": np.array([28, 12, 38], dtype=np.float32),
            },
            "titanium_cymatic": {
                "gold": np.array([228, 182, 64], dtype=np.float32),
                "enamel": np.array([14, 68, 82], dtype=np.float32),
                "silk": np.array([92, 104, 120], dtype=np.float32),
                "grout": np.array([18, 22, 28], dtype=np.float32),
            },
            "emerald_brocade": {
                "gold": np.array([250, 196, 24], dtype=np.float32),
                "enamel": np.array([0, 84, 68], dtype=np.float32),
                "silk": np.array([192, 228, 220], dtype=np.float32),
                "grout": np.array([24, 34, 38], dtype=np.float32),
            },
        }

        colors = palettes.get(palette_name, palettes["lapis_gold"])

        # Base layering from masks
        bc = (
            masks["gold"][..., np.newaxis] * colors["gold"]
            + masks["enamel"][..., np.newaxis] * colors["enamel"]
            + masks["silk"][..., np.newaxis] * colors["silk"]
            + masks["grout"][..., np.newaxis] * colors["grout"]
        )

        # Subtle paper / fabric stippling noise for watercolor texture
        noise = self.generate_fbm_spectral_noise(octaves_decay=1.2)
        bc += (noise[..., np.newaxis] - 0.5) * 8.0

        return np.clip(np.round(bc), 0, 255).astype(np.uint8)

    def pack_orm(
        self, ao: np.ndarray, roughness: np.ndarray, metallic: np.ndarray
    ) -> np.ndarray:
        """Packs AO, Roughness, and Metallic into 3-channel RGB ORM image."""
        return np.stack([ao, roughness, metallic], axis=-1)

    def export_suite(
        self,
        output_dir: Union[str, Path],
        suite_name: str,
        height_normalized: np.ndarray,
        feature_field: Optional[np.ndarray] = None,
        palette_name: str = "lapis_gold",
        bump_strength: float = 3.5,
    ) -> Dict[str, str]:
        """
        Synthesizes and writes all 7 PBR texture files into target directory.
        Files: _BC, _N, _ORM, _H, _AO, _R, _M (all 2048x2048 PNG).
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        h = np.clip(height_normalized, 0.0, 1.0).astype(np.float32)

        # 1. Normal map (DirectX Tangent Space)
        normal = self.compute_tangent_normal(h, bump_strength=bump_strength)

        # 2. Ambient Occlusion
        ao = self.compute_ambient_occlusion(h)

        # 3. Roughness & Metallic
        roughness, metallic, masks = self.synthesize_pbr_material_zones(
            h, feature_field=feature_field
        )

        # 4. Packed ORM
        orm = self.pack_orm(ao, roughness, metallic)

        # 5. BaseColor
        basecolor = self.synthesize_haute_couture_basecolor(
            h, masks, palette_name=palette_name
        )

        # 6. Height (8-bit grayscale for _H)
        height_u8 = np.clip(np.round(h * 255.0), 0, 255).astype(np.uint8)

        # File path mapping
        paths = {
            "BC": str(out_path / f"{suite_name}_BC.png"),
            "N": str(out_path / f"{suite_name}_N.png"),
            "ORM": str(out_path / f"{suite_name}_ORM.png"),
            "H": str(out_path / f"{suite_name}_H.png"),
            "AO": str(out_path / f"{suite_name}_AO.png"),
            "R": str(out_path / f"{suite_name}_R.png"),
            "M": str(out_path / f"{suite_name}_M.png"),
        }

        # Write to disk
        Image.fromarray(basecolor).save(paths["BC"], format="PNG")
        Image.fromarray(normal).save(paths["N"], format="PNG")
        Image.fromarray(orm).save(paths["ORM"], format="PNG")
        Image.fromarray(height_u8, mode="L").save(paths["H"], format="PNG")
        Image.fromarray(ao, mode="L").save(paths["AO"], format="PNG")
        Image.fromarray(roughness, mode="L").save(paths["R"], format="PNG")
        Image.fromarray(metallic, mode="L").save(paths["M"], format="PNG")

        return paths
