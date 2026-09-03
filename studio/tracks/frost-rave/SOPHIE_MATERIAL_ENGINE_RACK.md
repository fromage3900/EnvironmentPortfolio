# Phase Plant / Serum II — Sophie Material Engine Macro Rack

## Concept
**One MIDI sequence → 4 Material Lanes** sharing a single sequencer lane.
Each lane = one Sophie "material" (Brass/Strings/Perc/Vocal) with **universal pitch envelope (latex trick)** + per-material macro controls.

**BPM**: 128 | **Key**: A minor | **Progression**: Am-F-C-G

---

## GLOBAL MACROS (Master — controls all 4 lanes)

| Macro | Range | Default | Mapping |
|-------|-------|---------|---------|
| **MATERIAL MORPH** | 0–100% | 0% | Crossfade between lanes (0=Brass, 25=Strings, 50=Perc, 75=Vocal, 100=Brass) |
| **LATEX AMOUNT** | 0–100% | 60% | Global pitch envelope depth multiplier |
| **LATEX SPEED** | 0–100% | 50% | Global pitch envelope decay time multiplier |
| **BRIGHTNESS** | 0–100% | 50% | Global filter cutoff offset (all lanes) |
| **GRIT** | 0–100% | 30% | Global saturation/distortion amount |
| **SPACE** | 0–100% | 40% | Global reverb send / width |
| **SUB WEIGHT** | 0–100% | 70% | GND-SIN sub-bass level (separate lane) |

---

## LANE 1: BRASS — "Molten Chrome" (FM + Comb Filter)

### Core Synthesis
- **Engine**: FM (Phase Plant) / Serum II FM from B wavetable
- **Carrier:Modulator Ratio**: 1:7 (primary), 1:13 (secondary) — Sophie Monomachine brass ratios
- **Mod Index**: Macro-controlled (0–100)
- **Feedback**: 15–25% on modulator for clang

### Comb Filter (Brass Resonance)
- **Type**: Comb+ (feedforward) or Allpass comb
- **Delay Time**: 2.5–5 ms (tuned to fundamental — keytrack 100%)
- **Feedback**: 85–95% (high Q = metallic resonance)
- **Dampening**: LPF in feedback path (macro: BRIGHTNESS)

### Latex Pitch Envelope (Brass)
- **Attack**: 0 ms (instant)
- **Initial Pitch**: +12 to +24 semitones (macro: LATEX AMOUNT)
- **Decay**: 8 ms exponential (macro: LATEX SPEED × 8ms)
- **Curve**: Exponential fall
- **Amplitude**: Linked to pitch decay (louder at peak pitch)

### Macros (Brass Lane)
| Macro | Range | Default | Mapping |
|-------|-------|---------|---------|
| **FM INDEX** | 0–100% | 70% | Modulator level / mod index |
| **COMB Q** | 0–100% | 90% | Comb filter feedback |
| **COMB TUNE** | -50–+50 | 0 | Comb delay fine-tune (detune for thickness) |
| **NOISE BLEND** | 0–100% | 10% | White noise → comb input (breath texture) |

### Serum II Wavetables to Use
- `Basic Shapes` → `FM from B` (carrier) + `FM from A` (mod)
- Custom: `Sophie_Brass_FM` (single-cycle FM brass waveform)
- Noise: `White Noise` → comb filter input

---

## LANE 2: STRINGS — "Stretched Latex" (Physical Modeling / Karplus-Strong)

### Core Synthesis
- **Engine**: Physical Modeling (Phase Plant: String/Resonator) / Serum II: `Karplus Strong` wavetable + `Comb` filter
- **Exciter**: Impulse + filtered noise (bow noise)
- **String Model**: Delay line + LPF in feedback (damping = brightness)

### Karplus-Strong Parameters
- **Delay Time**: 1/f0 (keytracked 100%) — fundamental period
- **Feedback**: 97–99.5% (high = long sustain)
- **Damping Filter**: LPF cutoff = macro BRIGHTNESS × 8kHz
- **Pick Position**: Macro (0=bridge, 100=center) — comb filter feedforward

### Latex Pitch Envelope (Strings)
- **Attack**: 0 ms
- **Initial Pitch**: +12 to +24 semitones
- **Decay**: 22 ms exponential (slower = more "stretch")
- **Curve**: Exponential with slight knee at 50% (latex snap-back feel)

### Macros (Strings Lane)
| Macro | Range | Default | Mapping |
|-------|-------|---------|---------|
| **DAMPING** | 0–100% | 40% | String decay LPF cutoff |
| **PICK POS** | 0–100% | 30% | Exciter comb feedforward (timbre shift) |
| **BOW NOISE** | 0–100% | 15% | Filtered noise → exciter |
| **DETUNE** | -50–+50 | 5 | Chorus-like unison spread |

### Serum II Wavetables
- `Karplus Strong` (factory) — exciter impulse response
- `Bowed String` (factory) — sustained texture layer
- Custom: `Latex_String_Impulse` (short click + noise burst)

---

## LANE 3: PERCUSSION — "Clang / Squeak / Thwack" (FM Drums + Corpus)

### Core Synthesis: Three Parallel Voices (key-split or velocity-layered)

#### Voice A: CLANG (Kick/Tom) — FM Drum
- **Ratio**: 1:2.5 (kick), 1:4 (tom)
- **Mod Envelope**: Sharp decay (5–20 ms), high mod index → pitch drop
- **Carrier**: Sine → wavefolder (Serum: `Wavefolder` FX) for harmonic richness
- **Latex Envelope**: +24 semitones, 5 ms decay (hardest hit)

#### Voice B: SQUEAK (Snare/Rim) — FM + Noise
- **FM**: 1:7 ratio, very short mod envelope (2 ms) → high-pitched chirp
- **Noise Bandpass**: 2–6 kHz (snare wire band)
- **Comb Filter**: Short delay (1–2 ms), high feedback → metallic ring
- **Latex Envelope**: +12 semitones, 5 ms

#### Voice C: THWACK (Perc/Hit) — Corpus/Physical
- **Engine**: Corpus (Phase Plant) / Serum: `Comb` + `Noise`
- **Body**: Low-passed noise burst (50–200 Hz) → comb filter (body resonance)
- **Latex Envelope**: +6 semitones, 8 ms (heavier = slower)

### Macros (Perc Lane)
| Macro | Range | Default | Mapping |
|-------|-------|---------|---------|
| **CLANG DECAY** | 0–100% | 50% | FM mod envelope decay (kick/tom) |
| **SQUEAK TUNE** | -24–+24 | +12 | FM ratio fine-tune (snare pitch) |
| **WIRE TENSION** | 0–100% | 70% | Comb feedback on snare voice |
| **BODY SIZE** | 0–100% | 60% | Corpus/Comb delay time (thwack resonance) |
| **TRANSIENT** | 0–100% | 80% | Click/impulse level on all voices |

### Serum II Wavetables
- `FM Drum` (factory) — kick/tom base
- `Noise` → bandpass → snare wires
- Custom: `Sophie_Clang`, `Sophie_Squeak`, `Sophie_Thwack` (rendered one-shots)

---

## LANE 4: VOCAL — "Processed Alloy" (Granular + Formant + Spectral Morph)

### Core Synthesis
- **Engine**: Granular (Phase Plant) / Serum II: `Granular` oscillator + `Formant` filter
- **Source**: Melusina UTAU renders (pre-loaded) OR live input via MCP
- **Formant Filter**: 3–5 parallel bandpass filters at vowel formants (F1, F2, F3)

### Granular Parameters
- **Grain Size**: 20–100 ms (macro: GRANULAR SIZE)
- **Density**: 10–100 Hz (overlap)
- **Pitch Spread**: ±12 semitones (random per grain)
- **Position Jitter**: 0–100% (scrub through source)

### Formant Shifting (Sophie Choir Trick)
- **Method**: Pitch-shift grains → formant filter tracks new pitch → **decouples pitch from timbre**
- **Macro**: FORMANT SHIFT (-12 to +12 semitones) — changes "vowel size" without pitch change

### Spectral Morph (Cross-synthesis)
- **Source A**: Melusina vocal grains
- **Source B**: Frost Children vocal stem (granular)
- **Morph**: Spectral envelope of B applied to A (or vice versa) — **MATERIAL MORPH macro**

### Latex Pitch Envelope (Vocal)
- **Attack**: 0 ms
- **Initial Pitch**: +12 semitones
- **Decay**: 15 ms (between brass/strings)
- **Special**: Formant filter tracks pitch envelope → "vowel stretches with pitch"

### Macros (Vocal Lane)
| Macro | Range | Default | Mapping |
|-------|-------|---------|---------|
| **GRAIN SIZE** | 0–100% | 40% | Granular grain length |
| **DENSITY** | 0–100% | 60% | Grains per second |
| **FORMANT SHIFT** | -12–+12 | 0 | Formant filter offset (vowel morph) |
| **SPECTRAL MORPH** | 0–100% | 0% | Cross-synthesis with Frost stem |
| **BREATH** | 0–100% | 20% | Unvoiced noise layer |

### Serum II Setup
- **Osc A**: Granular → load Melusina render folder (drag WAVs onto oscillator)
- **Osc B**: Granular → load Frost vocal stems
- **FX**: `Formant Filter` (Serum 2 has this) → macro FORMANT SHIFT
- **FX**: `Compressor` (vintage) → macro GRIT
- **Mod**: `Envelope 3` → pitch (latex) + formant filter freq

---

## SUB-BASS LANE: GND-SIN (Separate, Always On)

### Pure Sine — Geological Sub
- **Oscillator**: Single sine wave (Serum: `Analog_BD_Sin` / Phase Plant: Analog → Sine)
- **Frequency**: 30–60 Hz (A1=55Hz, F1=43Hz, C1=32Hz, G1=49Hz) — **keytracked to root notes**
- **Envelope**: Instant attack, 200–500 ms decay, **zero sustain**, quick release
- **Processing**: 
  - **Saturation**: Soft clip (tube) — macro GRIT × 30%
  - **High-pass**: 20 Hz (remove DC)
  - **Sidechain**: Kick drum ducking (MCP can route)

### Macro
| Macro | Range | Default | Mapping |
|-------|-------|---------|---------|
| **SUB WEIGHT** | 0–100% | 70% | Global sub level (master macro) |

---

## SEQUENCER / ARPEGGIATOR (Shared)

### Single Sequencer Lane Drives All 4 Material Lanes
- **Pattern**: 16th notes (128 BPM = 32nd note grid for Sophie speed)
- **Notes**: Root notes of progression (A, F, C, G) + octaves
- **Velocity**: Per-step → maps to **LATEX AMOUNT** per hit (velocity = material intensity)
- **Gate**: 50–100% (short gates = more percussive)

### Sophie "Full Frequency Morphing" Trick
- **Same MIDI** → all lanes
- **Each lane** interprets velocity differently:
  - Brass: Velocity → FM Index + Comb Q
  - Strings: Velocity → Damping + Pick Position
  - Perc: Velocity → Transient + Clang Decay
  - Vocal: Velocity → Grain Density + Formant Shift

---

## EFFECTS CHAIN (Post-Lane Mixer)

### Insert FX (Per Lane → Master)
```
Lane Out → [Saturation: Decapitator/Serum Waveshaper] → [EQ: Pro-Q 3] → [Compressor: MJUC/Serum] → Master Bus
```

### Send FX (Shared)
| Send | Effect | Macro |
|------|--------|-------|
| **REVERB** | Valhalla VintageVerb / Serum Reverb | SPACE |
| **DELAY** | 1/8 note ping-pong, filtered | SPACE × 0.5 |
| **DISTORTION** | Parallel heavy clip (Decapitator) | GRIT × 1.5 |

### Master Bus
- **EQ**: Gentle high-shelf +2dB @ 10kHz (Sophie air)
- **Compression**: Glue (2:1, slow attack, auto release) — 1–2 dB GR
- **Limiter**: Ceiling -0.3 dB, true peak

---

## SERUM II PRESET STRUCTURE (If Using Serum Instead of Phase Plant)

### Four Instances (One per Lane) + One Sub Instance
| Instance | Preset Name | Key Wavetables |
|----------|-------------|----------------|
| 1 | `Sophie_Brass_Latex` | FM from B, FM from A, White Noise |
| 2 | `Sophie_Strings_Latex` | Karplus Strong, Bowed String |
| 3 | `Sophie_Perc_Latex` | FM Drum, Noise, Custom one-shots |
| 4 | `Sophie_Vocal_Latex` | Granular (Melusina), Granular (Frost) |
| 5 | `Sophie_GND_SIN` | Analog_BD_Sin |

### Macro Mapping (Serum Global Macros → All Instances via MCP)
- **Macro 1**: MATERIAL MORPH → Instance mixer levels
- **Macro 2**: LATEX AMOUNT → Env 3 Amount (pitch) on all
- **Macro 3**: LATEX SPEED → Env 3 Decay on all
- **Macro 4**: BRIGHTNESS → Filter Cutoff all
- **Macro 5**: GRIT → Waveshaper Drive all
- **Macro 6**: SPACE → Reverb Send all
- **Macro 7**: SUB WEIGHT → Instance 5 Level

---

## MIDI FILE FOR TESTING (8-Bar Loop)

### File: `Sophie_Material_Engine_Test.mid`
- **Track 1**: Sequencer pattern (16th notes, A-F-C-G roots, 2 bars each)
- **Track 2**: Velocity curve (ramping 40→127 over 8 bars)
- **Track 3**: CC74 (Brightness) — slow sweep 30→80
- **Track 4**: CC1 (Mod Wheel) — LATEX AMOUNT 60→100→60

**Import to FL Studio** → assign to all 5 Serum instances → play → **instant Sophie material engine**

---

## FL STUDIO MCP COMMANDS TO BUILD THIS

```python
# Via MCP (once daemon running):
# 1. Create 5 Serum instances on tracks 1-5
fl_create_plugin(track=1, plugin="Serum 2", preset="Sophie_Brass_Latex")
fl_create_plugin(track=2, plugin="Serum 2", preset="Sophie_Strings_Latex")
fl_create_plugin(track=3, plugin="Serum 2", preset="Sophie_Perc_Latex")
fl_create_plugin(track=4, plugin="Serum 2", preset="Sophie_Vocal_Latex")
fl_create_plugin(track=5, plugin="Serum 2", preset="Sophie_GND_SIN")

# 2. Route all to master, set up sends
fl_create_send(source=1, dest="Reverb", amount=40)
fl_create_send(source=2, dest="Reverb", amount=40)
# ... etc

# 3. Link macros via MCP macro mapper (rosasynthesiz supports this)
fl_link_macro(global="MATERIAL MORPH", targets=[1,2,3,4], params=["Level"])
fl_link_macro(global="LATEX AMOUNT", targets=[1,2,3,4], params=["Env 3 Amount"])
# ... etc

# 4. Import test MIDI
fl_import_midi("Sophie_Material_Engine_Test.mid", track=1)
fl_copy_midi(source_track=1, dest_tracks=[2,3,4,5])

# 5. Run Mix Doctor
fl_mix_doctor()
```

---

## CUSTOM VST INTEGRATION

Your custom VSTs can slot into any lane:
- **Brass lane**: Your FM synth VST → replace Phase Plant FM
- **Strings lane**: Your physical modeling VST → replace Karplus-Strong
- **Perc lane**: Your drum synth → replace FM Drum
- **Vocal lane**: Your granular/formant VST → replace Serum Granular
- **Master bus**: Your mastering chain → replace master FX

**MCP Chain Suggestion** will detect them: *"Vintage bass preset from my custom VST library"*

---

*Sir Melodious taps the macro knobs — one sequence, infinite materials.*