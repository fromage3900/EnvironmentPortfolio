import os, sys, math, json
from pathlib import Path
import numpy as np
from PIL import Image

PROJECT_ROOT = Path(r'C:/EnvironmentPortfolio/teamwork_projects/surreal_mathematical_textures')
TEXTURES_DIR = PROJECT_ROOT / 'textures'

SUITE_NAMES = [
    'T_Hyperbolic_PoincareTriangular',
    'T_Hyperbolic_HalfPlaneEscher',
    'T_Hopf_ToroidalFibration',
    'T_Hypersphere_DimensionalInterference',
    'T_Chladni_ResonantModal',
    'T_Cymatic_HarmonicLattice',
]

MAP_SUFFIXES = ['_BC.png', '_N.png', '_ORM.png', '_H.png', '_AO.png', '_R.png', '_M.png']

def shannon_entropy(arr):
    if arr.ndim > 2:
        return float(np.mean([shannon_entropy(arr[..., c]) for c in range(arr.shape[2])]))
    flat = arr.ravel()
    if np.issubdtype(flat.dtype, np.floating):
        flat = np.clip(flat * 255.0, 0, 255).astype(np.uint8)
    hist, _ = np.histogram(flat, bins=256, range=(0, 256))
    total = hist.sum()
    if total == 0: return 0.0
    probs = hist / total
    nz = probs[probs > 0]
    return float(-np.sum(nz * np.log2(nz)))

def laplacian_variance(arr):
    if arr.ndim == 3:
        g = 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
    else:
        g = arr.astype(np.float64)
    lap = (
        g[0:-2, 1:-1] +
        g[2:, 1:-1] +
        g[1:-1, 0:-2] +
        g[1:-1, 2:] -
        4.0 * g[1:-1, 1:-1]
    )
    return float(np.var(lap))

def decode_normal(rgb):
    rgb_f = rgb[..., :3].astype(np.float64) / 255.0
    nx = rgb_f[..., 0] * 2.0 - 1.0
    ny = rgb_f[..., 1] * 2.0 - 1.0
    nz = rgb_f[..., 2] * 2.0 - 1.0
    norm = np.sqrt(nx * nx + ny * ny + nz * nz)
    return nx, ny, nz, norm

def check_boundary_seam(arr):
    if arr.ndim == 3:
        arr_f = arr.astype(np.float64)
    else:
        arr_f = arr[..., np.newaxis].astype(np.float64)
    h_diff = np.abs(arr_f[0, ...] - arr_f[-1, ...])
    v_diff = np.abs(arr_f[..., 0, :] - arr_f[..., -1, :])
    return {
        'mean_h_diff': float(np.mean(h_diff)),
        'max_h_diff': float(np.max(h_diff)),
        'mean_v_diff': float(np.mean(v_diff)),
        'max_v_diff': float(np.max(v_diff)),
    }

def run():
    results = {'normal': {}, 'orm': {}, 'entropy': {}, 'seam': {}}
    print('=' * 80)
    print('SURREAL MATHEMATICAL PBR TEXTURE SUITES - ADVERSARIAL STRESS TEST')
    print('=' * 80)

    # 1. Normal Maps
    print('\n1. NORMAL MAP EMPIRICAL UNIT VECTOR VALIDATION')
    for s in SUITE_NAMES:
        p = TEXTURES_DIR / s / f'{s}_N.png'
        arr = np.array(Image.open(p))
        nx, ny, nz, norm = decode_normal(arr)
        df_1 = np.abs(norm - 1.0)
        m = float(np.mean(norm))
        sd = float(np.std(norm))
        mx_dev = float(np.max(df_1))
        w01 = float(np.mean(df_1 <= 0.01)) * 100.0
        w02 = float(np.mean(df_1 <= 0.02)) * 100.0
        w05 = float(np.mean(df_1 <= 0.05)) * 100.0
        min_nz = float(np.min(nz))
        mean_nz = float(np.mean(nz))
        results['normal'][s] = {
            'mean': m, 'std': sd, 'max_diff': mx_dev,
            'pct_within_001': w01, 'pct_within_002': w02, 'pct_within_005': w05,
            'min_nz': min_nz, 'mean_nz': mean_nz
        }
        print(f'{s:<38}: Mean={m:.6f}, Std={sd:.6f}, MaxDiff={mx_dev:.6f}, Pct<=0.01={w01:.2f}%, Pct<=0.02={w02:.2f}%, MinNz={min_nz:.4f}')

    # 2. ORM vs Discrete
    print('\n2. PACKED ORM VS DISCRETE MAPS PIXEL DISCREPANCY')
    for s in SUITE_NAMES:
        o = np.array(Image.open(TEXTURES_DIR / s / f'{s}_ORM.png'))
        ao = np.array(Image.open(TEXTURES_DIR / s / f'{s}_AO.png'))
        r = np.array(Image.open(TEXTURES_DIR / s / f'{s}_R.png'))
        m = np.array(Image.open(TEXTURES_DIR / s / f'{s}_M.png'))
        if ao.ndim == 3: ao = ao[..., 0]
        if r.ndim == 3: r = r[..., 0]
        if m.ndim == 3: m = m[..., 0]

        d_ao = np.abs(o[..., 0].astype(np.int32) - ao.astype(np.int32))
        d_r = np.abs(o[..., 1].astype(np.int32) - r.astype(np.int32))
        d_m = np.abs(o[..., 2].astype(np.int32) - m.astype(np.int32))

        ao_exact = float(np.mean(d_ao == 0)) * 100.0
        r_exact = float(np.mean(d_r == 0)) * 100.0
        m_exact = float(np.mean(d_m == 0)) * 100.0

        results['orm'][s] = {
            'AO_MAE': float(np.mean(d_ao)), 'AO_MaxDiff': int(np.max(d_ao)), 'AO_ExactMatchPct': ao_exact,
            'R_MAE': float(np.mean(d_r)), 'R_MaxDiff': int(np.max(d_r)), 'R_ExactMatchPct': r_exact,
            'M_MAE': float(np.mean(d_m)), 'M_MaxDiff': int(np.max(d_m)), 'M_ExactMatchPct': m_exact,
        }
        print(f'{s:<38}: AO Exact={ao_exact:.2f}% (MaxDiff={int(np.max(d_ao))}), R Exact={r_exact:.2f}% (MaxDiff={int(np.max(d_r))}), M Exact={m_exact:.2f}% (MaxDiff={int(np.max(d_m))})')

    # 3. Shannon Entropy & Dynamic Range
    print('\n3. SHANNON ENTROPY & DYNAMIC RANGE')
    for s in SUITE_NAMES:
        for suffix in MAP_SUFFIXES:
            mapname = f'{s}{suffix}'
            p = TEXTURES_DIR / s / mapname
            arr = np.array(Image.open(p))
            ent = shannon_entropy(arr)
            lap = laplacian_variance(arr)
            seam = check_boundary_seam(arr)
            results['entropy'][mapname] = {
                'entropy': ent, 'laplacian_var': lap,
                'min': int(arr.min()), 'max': int(arr.max()), 'std': float(arr.std())
            }
            results['seam'][mapname] = seam
            if suffix in ['_BC.png', '_N.png', '_H.png']:
                mn = arr.min()
                mx = arr.max()
                std_v = arr.std()
                print(f'{mapname:<48}: Entropy={ent:.3f} bits, DynSpan=[{mn},{mx}], Std={std_v:.2f}, LapVar={lap:.2f}')

    out_file = PROJECT_ROOT / 'tests' / 'adversarial_stress_test_report.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f'\nWrote stress test report JSON to {out_file}')

if __name__ == '__main__':
    run()
