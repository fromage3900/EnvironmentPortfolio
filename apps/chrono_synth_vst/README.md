# SOPHIE-X — Physical Modeling & Hyperpop Latex Sound Engine

**SOPHIE-X** is a standalone, physical modeling synthesizer and hyperpop sound design workstation inspired by the sonic textures of **SOPHIE** (*BIPP*, *Faceshopping*, *Lemonade*, *Immaterial*, *Ponyboy*, *MSMSMSM*, *HARD*).

---

## 💖 Sound Design Architecture & Physical Modeling

1. **Liquid Bubble Pop Engine (*BIPP*)**:
   - High-$Q$ resonant formant filters paired with rapid exponential pitch drops ($3600\text{ Hz} \to 260\text{ Hz}$) that synthesize water drops, carbonated bubbles, and elastic rubber pops.

2. **Abrasive Tanh Sub-Bass (*Faceshopping*)**:
   - Monomachine-inspired sub-bass driven through asymmetric hyperbolic tangent clipping and metallic resonance for tactile, tearing physical sub-frequencies.

3. **Inharmonic FM Sheet Metal Clangs (*Lemonade* / *HARD*)**:
   - Carrier waveforms modulated by non-integer inharmonic ratios ($1:\sqrt{2}, 1:\sqrt{3}$) with high-speed exponential damping that model real sheet metal strikes, aluminum cans, and anvil clangs.

4. **Elastic Latex Whip (*Ponyboy*)**:
   - Extreme micro-timing pitch snaps on resonant sawtooth waves simulating stretched latex membranes and rubber snapping.

5. **Euphoric Hyperpop Shimmer (*Immaterial*)**:
   - Sparkle square-wave arpeggio leads with vocal vowel formant filters (`/A/`, `/I/`, `/U/`, `/O/`) and celestial reverb.

6. **Liquid Membrane Phosphor CRT Vector Scope**:
   - Real-time animated deforming pink latex fluid membrane and cyan laser beam trace.

7. **Direct Broadcast 32-Bit WAV Exporter**:
   - Click `● RECORD WAV` to capture performances or sound design experiments directly to disk for use in Ableton, FL Studio, Logic Pro, Bitwig, or Reaper.

---

## 🚀 How to Launch

- **Standalone GUI Synth**: Double-click [`launch_chrono_synth.bat`](file:///c:/EnvironmentPortfolio/apps/chrono_synth_vst/launch_chrono_synth.bat) or open [`index.html`](file:///c:/EnvironmentPortfolio/apps/chrono_synth_vst/index.html).
- **Python DSP Stem Renderer**: Run [`render_preset_wavs.bat`](file:///c:/EnvironmentPortfolio/apps/chrono_synth_vst/render_preset_wavs.bat) to synthesize high-fidelity physical modeling WAV stems into `renders/`.

---

## 🎹 Keyboard Controls

| Key Range | Function |
|:---:|:---|
| **A – L** | White Keys (C4 to D5) |
| **W, E, T, Y, U, O, P, ]** | Black Keys (C#4 to F#5) |
| **Spacebar** | Start / Stop 135 BPM Hyperpop Sequencer |
| **● RECORD WAV** | Start / Stop 32-bit Float Stereo WAV recording |
