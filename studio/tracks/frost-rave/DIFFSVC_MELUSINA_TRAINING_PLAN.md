# Diff-SVC Melusina Voice Model — Training Plan

## Goal
Train a custom Diff-SVC model to convert **Frost Children vocal stems → Melusina voice** (UTAU timbre), preserving phrasing/expression while changing singer identity.

---

## 1. Dataset Preparation (CRITICAL)

### Source Material: Melusina UTAU Renders
- **Voicebank**: `Melusina JA VCV` + `RangeHigh` / `RangeLow` / `Microintonation` subbanks
- **Location**: `Documents/OpenUtau/Singers/Melusina JA VCV/`
- **Target**: 20–30 minutes of clean, diverse vocal audio

### Rendering Strategy (OpenUtau)
| Pass | Subbank | Pitch Range | Style | Duration |
|------|---------|-------------|-------|----------|
| 1 | JA VCV (base) | C3–C5 | Sustained vowels, legato | 5 min |
| 2 | RangeHigh | C5–C6 | Bright, airy, head voice | 5 min |
| 3 | RangeLow | C2–C3 | Warm, chest, fry | 5 min |
| 4 | Microintonation | C3–C5 | Microtonal slides, vibrato variants | 5 min |
| 5 | JA VCV | C3–C5 | Consonant-heavy (k, t, s, n, m) — articulation clarity | 5 min |
| 6 | Mixed | Full range | Frost-style phrasing (staccato, glitchy, breathy) | 5 min |

**Total**: ~30 min → comfortable for single-speaker Diff-SVC

### Phoneme Coverage Checklist (Japanese VCV)
- [ ] All 5 vowels (a, i, u, e, o) in all pitch ranges
- [ ] All consonant+vowel combos (k, s, t, n, h, m, y, r, w, g, z, d, b, p)
- [ ] Nasal codas (n, m, ng)
- [ ] Gemination (small tsu) — critical for Frost glitch aesthetic
- [ ] Long vowels (aa, ii, uu, ee, oo)
- [ ] Devoiced vowels (isu → isɯ̥)

### Output Format
```
data/raw/melusina/
├── melusina_001.wav  (48kHz or 24kHz, mono, 16-bit)
├── melusina_002.wav
...
└── melusina_XXX.wav
```

**Naming**: Sequential, no spaces. Diff-SVC expects `data/raw/<speaker>/`.

---

## 2. Preprocessing Pipeline (Diff-SVC Binarizer)

### Config Adjustments for Melusina (from `training/config.yaml`)
```yaml
# Speaker identity
speaker_id: melusina
num_spk: 1
work_dir: checkpoints/melusina

# Data paths
raw_data_dir: data/raw/melusina
binary_data_dir: data/binary/melusina

# Audio — match UTAU render sample rate
audio_sample_rate: 24000  # or 48000 if we render at 48k
hop_size: 256             # 24000/256 = 93.75 fps (good for singing)
win_size: 1024
fft_size: 1024
audio_num_mel_bins: 80

# Pitch — singing range
f0_min: 65.0    # C2
f0_max: 1100.0  # ~C6
f0_bin: 256
pitch_extractor: parselmouth  # robust for singing

# HuBERT — content encoder
hubert_path: checkpoints/hubert/hubert_soft.pt
hubert_gpu: true

# Alignment — Japanese VCV needs MFA
pre_align_args:
  forced_align: mfa
  txt_processor: ja_g2p  # Need Japanese G2P (OpenUtau has this)
  use_tone: false

# Diffusion — singing needs more steps
timesteps: 1000
K_step: 1000
pndm_speedup: 10
max_beta: 0.02

# Vocoder — HiFi-GAN (pre-trained on singing)
vocoder: network.vocoders.hifigan.HifiGAN
vocoder_ckpt: checkpoints/0109_hifigan_bigpopcs_hop128  # verify exists

# Training
max_epochs: 3000
lr: 0.0004
batch_size: 8  # adjust for VRAM (24GB → 16–32)
ds_workers: 4
```

### Required Checkpoints (Download First)
```bash
# HuBERT Soft (content encoder)
wget -P checkpoints/hubert/ https://github.com/bshall/hubert/releases/download/v0.1/hubert_soft.pt

# HiFi-GAN vocoder (singing-trained)
# From Diff-SVC releases or train own on singing data
```

---

## 3. Training Commands

### Step 1: Preprocess / Binarize
```bash
cd C:/EnvironmentPortfolio/diff-svc
python -m training.train_pipeline \
  --config training/config_melusina.yaml \
  --stage binarize
```
Outputs to `data/binary/melusina/`

### Step 2: Train
```bash
python -m training.train_pipeline \
  --config training/config_melusina.yaml \
  --stage train
```
- Monitor: `tensorboard --logdir checkpoints/melusina/logs`
- Checkpoint every `val_check_interval: 2000` steps
- Target: ~200k–400k steps for convergence (single speaker)

### Step 3: Export ONNX (Optional, for faster inference)
```bash
python onnx_export.py --config training/config_melusina.yaml --ckpt checkpoints/melusina/model_ckpt_steps_XXX.ckpt
```

---

## 4. Inference: Frost Stem → Melusina

### Input: Frost Vocal Stems
- Place in `raw/frost_stems/` (WAV, 24kHz mono)
- One file per stem (lead, harmony, ad-lib, etc.)

### Inference Script (adapt from `infer.py`)
```python
from infer_tools.infer_tool import Svc

model = Svc(
    project_name="melusina",
    config_path="training/config_melusina.yaml",
    hubert_gpu=True,
    model_path="checkpoints/melusina/model_ckpt_steps_XXXXXX.ckpt"
)

# For each Frost stem
run_clip(
    model,
    key=0,              # pitch shift (semitones) — match Frost key to Melusina range
    acc=10,             # acceleration (higher = faster, lower quality)
    use_crepe=True,     # CREPE F0 extraction (more accurate for singing)
    thre=0.05,          # voicing threshold
    use_pe=True,        # pitch embed
    use_gt_mel=False,   # don't use ground truth mel
    add_noise_step=500, # diffusion denoising steps
    file_path="raw/frost_stems/lead_vocal.wav",
    out_path="results/melusina_lead_vocal.flac",
    format="flac"
)
```

### Key Parameters for Frost → Melusina
| Param | Frost Context | Recommended |
|-------|---------------|-------------|
| `key` | Frost songs often high/pitched | -5 to -12 (drop to Melusina comfortable range) |
| `acc` | Quality vs speed | 10–20 (20 = 20x realtime, decent) |
| `use_crepe` | Frost has breathy/glitchy sections | **True** (CREPE handles noise better) |
| `thre` | Voicing threshold | 0.05 (default) — lower if breathy parts drop out |

---

## 5. Integration with FL Studio MCP

### Post-Conversion Workflow
1. **Diff-SVC output** → `results/melusina_*.flac`
2. **FL Studio MCP** → Import to playlist, time-align to grid
3. **MCP Mix Doctor** → Diagnose converted vocals in context
4. **MCP Chain Suggestion** → "Vintage vocal chain from my Serum library" → applies EQ/comp/sat
5. **MCP Reference Match** → Match tonal balance to Sophie "Hard" vocal texture

---

## 6. Hardware / VRAM Estimates

| Component | VRAM (24GB RTX 3090/4090) |
|-----------|---------------------------|
| HuBERT (base) | ~2 GB |
| Diff-SVC model (256ch, 20 layers) | ~4 GB |
| Training batch (8×42k frames) | ~6 GB |
| **Total** | **~12–14 GB** — comfortable with headroom |

**If OOM**: Reduce `max_frames`, `max_tokens`, `batch_size` in config.

---

## 7. Timeline

| Phase | Duration |
|-------|----------|
| Dataset render (OpenUtau) | 2–3 hrs |
| Preprocessing / binarize | 30 min |
| Training (200k steps) | 12–24 hrs (single GPU) |
| Inference on Frost stems | 10–30 min per stem |
| FL integration + mix | 2–4 hrs |

---

## 8. Alternative: Pre-trained Diff-SVC + Fine-tune

If training from scratch is too heavy:
1. Download pre-trained checkpoint (e.g., `atri` or `yilanqiu` from Diff-SVC releases)
2. Fine-tune on Melusina dataset (lower LR: 1e-5, fewer epochs: 50–100)
3. Faster convergence, but may retain source speaker artifacts

---

## 9. Next Immediate Actions

1. [ ] **Render Melusina dataset** in OpenUtau (30 min diverse material)
2. [ ] **Create `config_melusina.yaml`** from template above
3. [ ] **Download HuBERT + HiFi-GAN checkpoints** to `checkpoints/`
4. [ ] **Run binarization** → verify `data/binary/melusina/` populates
5. [ ] **Start training** (overnight daemon)

---

*Sir Melodious watches the loss curve — the latex orchestra needs its voice.*