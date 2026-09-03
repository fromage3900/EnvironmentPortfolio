"""
Hyperbolic PBR Generators: Non-Euclidean Poincaré Disk & Upper Half-Plane Escher Suites
========================================================================================
Implements:
1. Suite 1: Poincaré Disk {7, 3} Heptagonal Triangular Coxeter Group Reflection Lattice
2. Suite 2: Hyperbolic Upper Half-Plane {5, 4} Escher Limiting Conformal Lattice

Target Resolution: 2048x2048 Power-of-Two (POT)
Pure NumPy + Pillow (Zero SciPy dependency)
"""

import os
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, Tuple, Optional, Union

import numpy as np

# Ensure parent directory is in path for package imports
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from generators.pbr_engine import PBREngine
except ImportError:
    from pbr_engine import PBREngine


class HyperbolicGenerator:
    """
    Procedural generator for Poincaré Disk and Upper Half-Plane Escher hyperbolic
    tiling PBR texture suites.
    """

    def __init__(self, resolution: int = 2048, pbr_engine: Optional[PBREngine] = None):
        self.resolution = resolution
        self.res = resolution
        self.pbr_engine = pbr_engine or PBREngine(resolution=resolution)

    def generate_poincare_triangular(
        self,
        p: int = 7,
        q: int = 3,
        iterations: int = 32,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Synthesizes the Poincaré Disk {p, q} Triangular Coxeter Group Reflection Lattice."""
        return generate_poincare_triangular(
            resolution=self.resolution,
            p=p,
            q=q,
            iterations=iterations,
        )

    def generate_halfplane_escher(
        self,
        p: int = 5,
        q: int = 4,
        iterations: int = 24,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Synthesizes the Hyperbolic Upper Half-Plane {p, q} Escher Limiting Conformal Lattice."""
        return generate_halfplane_escher(
            resolution=self.resolution,
            p=p,
            q=q,
            iterations=iterations,
        )

    def generate_poincare_triangular_suite(
        self,
        output_dir: Union[str, Path],
        palette: str = "lapis_gold",
        palette_name: Optional[str] = None,
        bump_strength: float = 4.5,
        p: int = 7,
        q: int = 3,
        iterations: int = 32,
    ) -> Dict[str, str]:
        """Synthesizes all 7 PBR maps for Suite 1 (T_Hyperbolic_PoincareTriangular)."""
        suite_name = "T_Hyperbolic_PoincareTriangular"
        selected_palette = palette_name or palette
        h, feat = generate_poincare_triangular(
            resolution=self.resolution,
            p=p,
            q=q,
            iterations=iterations,
        )
        return self.pbr_engine.export_suite(
            output_dir=output_dir,
            suite_name=suite_name,
            height_normalized=h,
            feature_field=feat,
            palette_name=selected_palette,
            bump_strength=bump_strength,
        )

    def generate_halfplane_escher_suite(
        self,
        output_dir: Union[str, Path],
        palette: str = "amethyst_quartz",
        palette_name: Optional[str] = None,
        bump_strength: float = 6.5,
        p: int = 5,
        q: int = 4,
        iterations: int = 24,
    ) -> Dict[str, str]:
        """Synthesizes all 7 PBR maps for Suite 2 (T_Hyperbolic_HalfPlaneEscher)."""
        suite_name = "T_Hyperbolic_HalfPlaneEscher"
        selected_palette = palette_name or palette
        h, feat = generate_halfplane_escher(
            resolution=self.resolution,
            p=p,
            q=q,
            iterations=iterations,
        )
        return self.pbr_engine.export_suite(
            output_dir=output_dir,
            suite_name=suite_name,
            height_normalized=h,
            feature_field=feat,
            palette_name=selected_palette,
            bump_strength=bump_strength,
        )

    def bake_all(
        self,
        output_root: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Dict[str, str]]:
        """Bakes all 14 maps for both Hyperbolic Domain Suites (Suite 1 & Suite 2)."""
        out_root = Path(output_root) if output_root is not None else PROJECT_ROOT / "textures"
        suite1_dir = out_root / "T_Hyperbolic_PoincareTriangular"
        suite2_dir = out_root / "T_Hyperbolic_HalfPlaneEscher"
        return {
            "T_Hyperbolic_PoincareTriangular": self.generate_poincare_triangular_suite(
                output_dir=suite1_dir,
                palette="lapis_gold",
                bump_strength=4.5,
            ),
            "T_Hyperbolic_HalfPlaneEscher": self.generate_halfplane_escher_suite(
                output_dir=suite2_dir,
                palette="amethyst_quartz",
                bump_strength=6.5,
            ),
        }


def generate_all_hyperbolic_suites(
    resolution: int = 2048,
    output_root: Optional[str] = None,
) -> Dict[str, Dict[str, str]]:
    """
    Generates and exports all 14 PBR maps across both Hyperbolic suites:
    1. T_Hyperbolic_PoincareTriangular (lapis_gold palette)
    2. T_Hyperbolic_HalfPlaneEscher (amethyst_quartz palette)
    """
    generator = HyperbolicGenerator(resolution=resolution)
    return generator.bake_all(output_root=output_root)


def main():
    parser = argparse.ArgumentParser(description="Generate Hyperbolic PBR Texture Suites")
    parser.add_argument("--res", type=int, default=2048, help="Target resolution (default: 2048)")
    parser.add_argument("--out", type=str, default=None, help="Output textures directory")
    args = parser.parse_args()

    generate_all_hyperbolic_suites(resolution=args.res, output_root=args.out)


if __name__ == "__main__":
    main()


def generate_poincare_triangular(
    resolution: int = 2048,
    p: int = 7,
    q: int = 3,
    iterations: int = 32,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Synthesizes the Poincaré Disk {p, q} Triangular Coxeter Group Reflection Lattice.
    For {7, 3}: Fundamental triangle Delta(7, 3, 2) with angles pi/7, pi/3, pi/2.

    Returns:
        Tuple[np.ndarray, np.ndarray]: (height_normalized float32 [0, 1], feature_field float32 [0, 1])
    """
    alpha = np.pi / p
    beta = np.pi / q
    cosh_a = np.cos(beta) / np.sin(alpha)
    a = np.arccosh(cosh_a)
    ra = np.tanh(a / 2.0)
    cx = (1.0 + ra**2) / (2.0 * ra)
    Rcirc = np.sqrt(cx**2 - 1.0)

    # Complex coordinate grid spanning [-1.06, 1.06]
    span = 1.06
    y, x = np.mgrid[-span:span:resolution * 1j, -span:span:resolution * 1j]
    z = x.astype(np.float64) + 1j * y.astype(np.float64)
    r_orig = np.abs(z)

    z_folded = z.copy()
    n_iter = np.zeros((resolution, resolution), dtype=np.int32)
    mask = r_orig < 0.999

    sector_angle = 2.0 * np.pi / p
    half_angle = np.pi / p
    rot_neg = np.exp(-1j * half_angle)

    for _ in range(iterations):
        # 1. Angular sector folding into [0, pi/p]
        angle = np.angle(z_folded) % sector_angle
        re_fold = np.where(angle > half_angle, sector_angle - angle, angle)
        z_folded = np.abs(z_folded) * np.exp(1j * re_fold)

        # 2. Circular mirror inversion across M3 orthogonal circle
        dist = np.abs(z_folded - cx)
        inv_mask = mask & (dist < Rcirc)
        if not np.any(inv_mask):
            break
        z_folded[inv_mask] = cx + (Rcirc**2) * (z_folded[inv_mask] - cx) / (dist[inv_mask] ** 2)
        n_iter[inv_mask] += 1

    # Distance to three geodesic boundary edges of fundamental triangle
    d1 = np.abs(np.imag(z_folded))
    d2 = np.abs(np.imag(z_folded * rot_neg))
    d3 = np.abs(np.abs(z_folded - cx) - Rcirc)
    d_min = np.minimum(np.minimum(d1, d2), d3)

    # Multi-component heightfield
    geodesic_ridges = 0.50 * np.exp(-45.0 * d_min)
    cell_domes = 0.35 * np.maximum(0.0, 1.0 - (np.abs(z_folded) / ra) ** 2)
    parity_modulation = 0.15 * (n_iter % 2)
    h_interior = geodesic_ridges + cell_domes + parity_modulation

    # Disk boundary fade and ornate carved bezel
    fade = np.clip((1.0 - r_orig) / 0.02, 0.0, 1.0)
    bezel = np.clip(1.0 - np.abs(r_orig - 1.0) / 0.03, 0.0, 1.0) * 0.45
    h = h_interior * fade + bezel * (1.0 - fade)

    # Global normalization to [0.0, 1.0]
    h_norm = (h - h.min()) / (h.max() - h.min() + 1e-8)
    feature_field = (d_min - d_min.min()) / (d_min.max() - d_min.min() + 1e-8)

    return h_norm.astype(np.float32), feature_field.astype(np.float32)


def generate_halfplane_escher(
    resolution: int = 2048,
    p: int = 5,
    q: int = 4,
    iterations: int = 24,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Synthesizes the Hyperbolic Upper Half-Plane {p, q} Escher Limiting Conformal Lattice.
    For {5, 4}: Logarithmic asymptotic scaling towards the real axis limit line with
    multi-scale conformal harmonic wave superposition.

    Returns:
        Tuple[np.ndarray, np.ndarray]: (height_normalized float32 [0, 1], feature_field float32 [0, 1])
    """
    y_grid, x_grid = np.mgrid[0:1:resolution * 1j, 0:1:resolution * 1j]

    # Map UV coordinates to Upper Half-Plane:
    # u in [-2.0, 2.0], v in [0.035, 2.8] with exponential density towards bottom horizon
    u = (x_grid.astype(np.float64) - 0.5) * 4.0
    v = 0.035 + 2.5 * (1.0 - y_grid.astype(np.float64)) ** 1.6

    w = u + 1j * v
    w_folded = w.copy()
    n_inv = np.zeros((resolution, resolution), dtype=np.int32)

    L = 1.0  # Horizontal period
    R0 = 0.45  # Inversion radius

    for _ in range(iterations):
        # 1. Periodic horizontal shift
        u_curr = np.real(w_folded)
        v_curr = np.imag(w_folded)
        u_mod = ((u_curr + L / 2.0) % L) - L / 2.0
        w_folded = u_mod + 1j * v_curr

        # 2. Inversion across semi-circular geodesics on real axis
        dist = np.abs(w_folded)
        inv_mask = (dist < R0) & (v_curr > 0.001)
        if not np.any(inv_mask):
            break
        w_folded[inv_mask] = (R0**2) * w_folded[inv_mask] / (dist[inv_mask] ** 2)
        n_inv[inv_mask] += 1

    u_f = np.real(w_folded)
    v_f = np.maximum(1e-5, np.imag(w_folded))

    # Geodesic edge boundaries
    d_semi = np.abs(np.abs(w_folded) - R0)
    d_vert = np.abs(u_f)
    d_min = np.minimum(d_semi, d_vert)

    # Conformal standing waves with logarithmic vertical scaling and high-frequency harmonics
    log_v = np.log(v_f + 0.04)
    w1 = np.sin(5.0 * np.pi * u_f + 4.0 * log_v)
    w2 = np.cos(4.0 * np.pi * u_f) * np.cos(5.0 * log_v)
    w3 = np.sin(10.0 * np.pi * u_f) * np.cos(8.0 * log_v)
    w4 = np.cos(16.0 * np.pi * (u_f + 0.1 * log_v)) * np.cos(12.0 * log_v)
    w5 = np.sin(24.0 * np.pi * u_f) * np.sin(18.0 * log_v)

    h = (
        0.35 * np.exp(-32.0 * d_min)
        + 0.20 * (0.5 + 0.5 * w1)
        + 0.15 * (0.5 + 0.5 * w2)
        + 0.12 * (0.5 + 0.5 * w3)
        + 0.10 * (0.5 + 0.5 * w4)
        + 0.05 * (0.5 + 0.5 * w5)
        + 0.03 * ((n_inv % 3) / 2.0)
    )

    # Global normalization to [0.0, 1.0]
    h_norm = (h - h.min()) / (h.max() - h.min() + 1e-8)
    feature_field = (d_min - d_min.min()) / (d_min.max() - d_min.min() + 1e-8)

    return h_norm.astype(np.float32), feature_field.astype(np.float32)
