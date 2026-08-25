#!/usr/bin/env python3
"""
SOPHIE-DSP — Physical Modeling & Hyperpop Latex Sound Generator
Generates high-fidelity 48kHz stereo WAV sound stems inspired by SOPHIE's
legendary sound design (BIPP bubble pops, Faceshopping distorted bass,
Lemonade metallic clangs, and Ponyboy latex whips).
"""

import os
import wave
import struct
import math
import numpy as np

SAMPLE_RATE = 48000

def write_stereo_wav(filepath, left_channel, right_channel):
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    n_samples = len(left_channel)
    
    # Normalize peak to -0.5 dB
    peak = max(np.max(np.abs(left_channel)), np.max(np.abs(right_channel)))
    if peak > 0:
        gain = 0.94 / peak
        left_channel = left_channel * gain
        right_channel = right_channel * gain

    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2) # 16-bit PCM
        wav_file.setframerate(SAMPLE_RATE)
        
        frames = bytearray()
        for i in range(n_samples):
            l_val = int(np.clip(left_channel[i] * 32767.0, -32768, 32767))
            r_val = int(np.clip(right_channel[i] * 32767.0, -32768, 32767))
            frames.extend(struct.pack('<hh', l_val, r_val))
            
        wav_file.writeframes(frames)
    print(f"[OK] Rendered: {filepath} ({n_samples / SAMPLE_RATE:.2f}s)")

def generate_bipp_bubble_pop(duration=2.5):
    """SOPHIE 'BIPP' signature liquid bubble pop with exponential frequency drop"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    
    # Rapid exponential frequency glide (3200Hz down to 260Hz in 40ms)
    freq_env = 260.0 + 3600.0 * np.exp(-t * 45.0)
    phase = 2.0 * np.pi * np.cumsum(freq_env) / SAMPLE_RATE
    
    # Pure sine bubble with resonant formant harmonic
    bubble = np.sin(phase) + 0.35 * np.sin(phase * 2.0)
    
    # Sharp exponential amp envelope
    amp_env = np.exp(-t * 12.0)
    sig = bubble * amp_env
    
    # Add subtle stereophonic slapback
    delay_samples = int(SAMPLE_RATE * 0.012)
    left = sig
    right = np.roll(sig, delay_samples)
    return left, right

def generate_faceshopping_bass(duration=4.0):
    """SOPHIE 'Faceshopping' Monomachine style abrasive tanh sub-bass"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    base_freq = 55.0 # A1 Note
    
    # Initial snap
    pitch_mod = 1.0 + 2.5 * np.exp(-t * 60.0)
    phase = 2.0 * np.pi * np.cumsum(base_freq * pitch_mod) / SAMPLE_RATE
    
    # Dual saw + square sub
    saw = 2.0 * ((phase / (2.0 * np.pi)) - np.floor((phase / (2.0 * np.pi)) + 0.5))
    sqr = np.sign(np.sin(phase))
    sub = np.sin(phase * 0.5)
    
    raw = saw * 0.4 + sqr * 0.3 + sub * 0.6
    
    # Extreme Tanh Saturation + Asymmetric Metallic Clip
    drive = 14.0
    dist = np.tanh(raw * drive) + 0.2 * np.sin(raw * math.pi * 3.0)
    
    # Amplitude envelope
    amp = np.exp(-t * 1.5)
    sig = dist * amp
    
    return sig, sig * (0.95 + 0.05 * np.sin(2 * np.pi * 4 * t))

def generate_lemonade_metallic_clang(duration=3.0):
    """SOPHIE 'Lemonade' / 'Hard' inharmonic FM sheet metal clang"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    carrier_freq = 440.0
    
    # Inharmonic modulators (non-integer ratios)
    mod1 = np.sin(2.0 * np.pi * carrier_freq * 2.414 * t) * np.exp(-t * 22.0)
    mod2 = np.sin(2.0 * np.pi * carrier_freq * 5.828 * t) * np.exp(-t * 35.0)
    
    # Carrier FM
    fm_index = 8.0
    phase = 2.0 * np.pi * carrier_freq * t + (mod1 * fm_index + mod2 * (fm_index * 0.6))
    clang = np.sin(phase) + 0.25 * np.sin(phase * 1.732)
    
    # Metallic decay
    amp = np.exp(-t * 3.5)
    sig = np.tanh(clang * 2.5) * amp
    
    # Stereo spatialization
    left = sig * (0.8 + 0.2 * np.cos(2 * np.pi * 1.5 * t))
    right = sig * (0.8 - 0.2 * np.cos(2 * np.pi * 1.5 * t))
    return left, right

def generate_ponyboy_latex_whip(duration=2.0):
    """SOPHIE 'Ponyboy' latex elastic snap & whip strike"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    
    # Instant pitch drop from 5000Hz down to 80Hz
    freq_snap = 80.0 + 4800.0 * np.exp(-t * 90.0)
    phase = 2.0 * np.pi * np.cumsum(freq_snap) / SAMPLE_RATE
    
    # Resonant saw strike
    saw = 2.0 * ((phase / (2.0 * np.pi)) - np.floor((phase / (2.0 * np.pi)) + 0.5))
    whip = np.tanh(saw * 8.0) * np.exp(-t * 18.0)
    
    return whip, np.roll(whip, int(SAMPLE_RATE * 0.008))

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, "renders")
    
    print("=== SOPHIE-DSP PHYSICAL MODELING RENDERER ===")
    
    l1, r1 = generate_bipp_bubble_pop(2.5)
    write_stereo_wav(os.path.join(out_dir, "Sophie_Bipp_Bubble_Pop.wav"), l1, r1)
    
    l2, r2 = generate_faceshopping_bass(4.0)
    write_stereo_wav(os.path.join(out_dir, "Sophie_Faceshopping_Distorted_Bass.wav"), l2, r2)
    
    l3, r3 = generate_lemonade_metallic_clang(3.0)
    write_stereo_wav(os.path.join(out_dir, "Sophie_Lemonade_Metallic_Clang.wav"), l3, r3)
    
    l4, r4 = generate_ponyboy_latex_whip(2.0)
    write_stereo_wav(os.path.join(out_dir, "Sophie_Ponyboy_Latex_Whip.wav"), l4, r4)
    
    print(f"\n[DONE] All 4 SOPHIE-inspired physical modeling stems rendered into: {out_dir}")

if __name__ == "__main__":
    main()
