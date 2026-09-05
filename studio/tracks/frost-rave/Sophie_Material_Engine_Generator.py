#!/usr/bin/env python3
"""
Sophie Material Engine — Full Track Pack Generator
Generates: MIDI test sequence + Melusina USTX + FL Studio MCP build commands
for the 4-lane material engine (Brass/Strings/Perc/Vocal) + GND-SIN sub-bass.

One MIDI sequence → 4 materials. Velocity = material intensity. Sophie's trick.
"""

import json, struct, os

TPQ = 480
BAR = 1920
OUT = r'C:\EnvironmentPortfolio\studio\tracks\frost-rave'

# ──────────────────────────────────────────────────────────────────────────────
# MIDI writers (stdlib only)
# ──────────────────────────────────────────────────────────────────────────────

def vlq(n):
    out = bytearray([n & 0x7F]); n >>= 7
    while n:
        out.insert(0, 0x80 | (n & 0x7F)); n >>= 7
    return bytes(out)

def track_chunk(events):
    data = b''.join(events)
    return b'MTrk' + struct.pack('>I', len(data)) + data

def write_midi(path, tracks, tempo_bpm=128):
    header = b'MThd' + struct.pack('>IHHH', 6, 1, len(tracks), TPQ)
    micros = int(60_000_000 / tempo_bpm)
    with open(path, 'wb') as f:
        f.write(header)
        for i, events in enumerate(tracks):
            merged = []
            if i == 0:
                merged.append((0, 0, b'\xFF\x51\x03' + struct.pack('>I', micros)[1:]))
                merged.append((0, 0, b'\xFF\x58\x04\x04\x02\x18\x08'))  # 4/4
            for tick, order, payload in events:
                merged.append((tick, order, payload))
            merged.sort()
            last = 0
            evs = []
            for tick, _order, payload in merged:
                evs.append(vlq(tick - last) + payload)
                last = tick
            evs.append(vlq(0) + b'\xFF\x2F\x00')
            f.write(track_chunk(evs))

def note_events(notes, channel=0, prog=None):
    out = []
    if prog is not None:
        out.append((0, 0, bytes([0xC0 | channel, prog])))
    for start, dur, tone, vel in notes:
        out.append((start, 1, bytes([0x90 | channel, tone, vel])))
        out.append((start + dur, 0, bytes([0x80 | channel, tone, 0])))
    return out

def cc_events(cc_data, channel=0):
    """cc_data: list of (tick, cc_num, value)"""
    out = []
    for tick, cc_num, value in cc_data:
        out.append((tick, 1, bytes([0xB0 | channel, cc_num, value])))
    return out

# ──────────────────────────────────────────────────────────────────────────────
# SOPHIE MATERIAL ENGINE — SEQUENCER PATTERN (8 bars, 16th notes)
# ──────────────────────────────────────────────────────────────────────────────

# Progression: Am - F - C - G (2 bars each = 8 bars total)
# Root notes (MIDI): A3=57, F3=53, C4=60, G3=55
ROOTS = [57, 53, 60, 55]  # A3, F3, C4, G3
OCTAVES = [0, 12]        # Root + octave

seq_notes = []
vel_curve = []  # velocity ramp 40→127 over 8 bars
cc74_bright = []  # CC74 = brightness filter cutoff
cc1_latex = []    # CC1 = mod wheel = LATEX AMOUNT

for bar in range(8):
    root = ROOTS[bar // 2]
    base = bar * BAR
    
    # 16th notes per bar = 16 notes (120 ticks each)
    for step in range(16):
        tick = base + step * 120
        
        # Alternate root / octave for movement
        tone = root + (OCTAVES[step % 2] if step % 4 < 2 else 0)
        
        # Velocity ramp: 40 → 127 over 128 steps
        vel = int(40 + (87 * (bar * 16 + step) / 127))
        
        seq_notes.append((tick, 100, tone, vel))  # dur=100 (short gate)
        
        # CC74 brightness: slow sweep 30→100 over 8 bars
        cc_val = int(30 + 70 * (bar * 16 + step) / 127)
        cc74_bright.append((tick, 74, cc_val))
        
        # CC1 latex amount: 60→100→60 triangle wave per 2 bars
        phase = (bar * 16 + step) % 32
        if phase < 16:
            latex_val = int(60 + 40 * phase / 15)
        else:
            latex_val = int(100 - 40 * (phase - 16) / 15)
        cc1_latex.append((tick, 1, latex_val))

# ──────────────────────────────────────────────────────────────────────────────
# MELUSINA VOCAL — USTX (extends the hook into full 8-bar phrase)
# ──────────────────────────────────────────────────────────────────────────────

VOCAL_PHRASE_FULL = [
    # Bar 1-2: Am
    ('u', 69, 240), ('chi', 72, 240), ('na', 76, 360), ('ru', 74, 120),
    ('shi', 72, 240), ('o', 69, 240), ('yo', 67, 480), ('', 69, 240),
    # Bar 3-4: F
    ('u', 69, 240), ('chi', 72, 240), ('na', 76, 360), ('ru', 74, 120),
    ('shi', 72, 240), ('o', 69, 240), ('yo', 67, 480), ('', 69, 240),
    # Bar 5-6: C
    ('o', 67, 240), ('do', 72, 240), ('re', 76, 240), ('ka', 74, 240),
    ('i', 71, 240), ('yo', 67, 240), ('u', 69, 720), ('', 69, 240),
    # Bar 7-8: G
    ('yo', 69, 240), ('ru', 72, 240), ('ga', 76, 360), ('a', 74, 120),
    ('ke', 72, 240), ('ru', 69, 240), ('ma', 67, 480), ('', 69, 240),
]

vocal_notes, t = [], 0
for lyric, tone, dur in VOCAL_PHRASE_FULL:
    if dur:
        vocal_notes.append((t, dur, tone, 100))
    t += dur

# ──────────────────────────────────────────────────────────────────────────────
# BASS — GND-SIN root following (keytracked to progression)
# ──────────────────────────────────────────────────────────────────────────────

BASS_ROOTS = [45, 41, 48, 43]  # A2, F2, C3, G2
bass_notes = []
for bar in range(8):
    root = BASS_ROOTS[bar // 2]
    base = bar * BAR
    # Quarter notes on downbeats
    for beat in range(4):
        tick = base + beat * 480
        bass_notes.append((tick, 400, root, 110))
    # Turnaround on bar 4 and 8 (G→A run)
    if bar in (3, 7):
        for k, tone in enumerate([43, 45, 46, 47]):  # G A Bb B
            bass_notes.append((base + 1760 + k * 40, 40, tone, 96))

# ──────────────────────────────────────────────────────────────────────────────
# CHORDS — Offbeat stabs for reference layer
# ──────────────────────────────────────────────────────────────────────────────

CH = {0: [57, 60, 64], 1: [53, 57, 60], 2: [55, 60, 64], 3: [55, 59, 62]}  # Am F C G
chord_notes = []
for bar in range(8):
    root = bar // 2
    base = bar * BAR
    for off in (240, 720, 1200, 1680):
        for tone in CH[root]:
            chord_notes.append((base + off, 170, tone, 88))

# ──────────────────────────────────────────────────────────────────────────────
# WRITE MIDI FILES
# ──────────────────────────────────────────────────────────────────────────────

# Main test MIDI: Track 0=tempo, Track 1=Sequencer, Track 2=CC74, Track 3=CC1
write_midi(
    os.path.join(OUT, 'Sophie_Material_Engine_Test.mid'),
    [
        [],  # tempo track
        note_events(seq_notes, channel=0),
        cc_events(cc74_bright, channel=0),
        cc_events(cc1_latex, channel=0),
    ]
)

# Vocal guide MIDI (for reference)
write_midi(
    os.path.join(OUT, 'Sophie_Material_Vocal_Guide.mid'),
    [[], note_events(vocal_notes, channel=0)]
)

# Bass MIDI (for sub-bass lane)
write_midi(
    os.path.join(OUT, 'Sophie_Material_Bass.mid'),
    [[], note_events(bass_notes, channel=0, prog=38)]
)

# Chords MIDI (for reference)
write_midi(
    os.path.join(OUT, 'Sophie_Material_Chords.mid'),
    [[], note_events(chord_notes, channel=0, prog=48)]
)

# ──────────────────────────────────────────────────────────────────────────────
# USTX — MELUSINA SINGS THE FULL 8-BAR PHRASE
# ──────────────────────────────────────────────────────────────────────────────

ustx = {
    'ustx_version': 0.6,
    'name': 'Melusina_Sophie_Material_Engine',
    'comment': 'Sophie Material Engine — Melusina vocal lane. 128 BPM A minor. Assign singer: Melusina JA VCV. RangeHigh_ subbank for bright sections, RangeLow_ for sub-bass doubling.',
    'author': 'Melusina',
    'tempo': 128.0,
    'beat_per_bar': 4,
    'beat_unit': 4,
    'tracks': [{
        'track_no': 1,
        'singer': 'Melusina JA VCV',
        'name': 'Melusina',
        'parts': [{
            'position': 0,
            'duration': 8 * BAR,
            'name': 'material_vocal_full',
            'notes': [
                {'position': pos, 'duration': dur, 'tone': tone, 'lyric': lyric if lyric else 'a'}
                for (pos, dur, tone, _v), (lyric, _t, _d) in zip(vocal_notes, VOCAL_PHRASE_FULL)
            ],
        }],
    }],
}

with open(os.path.join(OUT, 'Melusina_Sophie_Material_Engine.ustx'), 'w', encoding='utf-8') as f:
    json.dump(ustx, f, indent=2, ensure_ascii=False)

# ──────────────────────────────────────────────────────────────────────────────
# FL STUDIO MCP BUILD COMMANDS (rosasynthesiz/flstudio-mcp)
# ──────────────────────────────────────────────────────────────────────────────

mcp_commands = '''# ──────────────────────────────────────────────────────────────────────────────
# FL STUDIO MCP — SOPHIE MATERIAL ENGINE BUILD
# Run via rosasynthesiz/flstudio-mcp daemon (requires FL Studio 2025+, loopMIDI)
# ──────────────────────────────────────────────────────────────────────────────

# 1. CREATE 5 SERUM 2 INSTANCES (one per lane + sub)
fl_create_plugin(track=1, plugin="Serum 2", preset="Sophie_Brass_Latex")
fl_create_plugin(track=2, plugin="Serum 2", preset="Sophie_Strings_Latex")
fl_create_plugin(track=3, plugin="Serum 2", preset="Sophie_Perc_Latex")
fl_create_plugin(track=4, plugin="Serum 2", preset="Sophie_Vocal_Latex")
fl_create_plugin(track=5, plugin="Serum 2", preset="Sophie_GND_SIN")

# 2. ROUTE ALL TO MASTER, SET UP SENDS
fl_create_send(source=1, dest="Reverb", amount=40)
fl_create_send(source=2, dest="Reverb", amount=40)
fl_create_send(source=3, dest="Reverb", amount=30)
fl_create_send(source=4, dest="Reverb", amount=50)
fl_create_send(source=1, dest="Delay", amount=20)
fl_create_send(source=4, dest="Delay", amount=30)

# 3. LINK GLOBAL MACROS → ALL INSTANCES (rosasynthesiz macro mapper)
fl_link_macro(global="MATERIAL MORPH", targets=[1,2,3,4], params=["Level"])
fl_link_macro(global="LATEX AMOUNT", targets=[1,2,3,4], params=["Env 3 Amount"])
fl_link_macro(global="LATEX SPEED", targets=[1,2,3,4], params=["Env 3 Decay"])
fl_link_macro(global="BRIGHTNESS", targets=[1,2,3,4], params=["Filter Cutoff"])
fl_link_macro(global="GRIT", targets=[1,2,3,4], params=["Waveshaper Drive"])
fl_link_macro(global="SPACE", targets=[1,2,3,4], params=["Reverb Send"])
fl_link_macro(global="SUB WEIGHT", targets=[5], params=["Level"])

# 4. IMPORT TEST MIDI TO ALL LANES
fl_import_midi("Sophie_Material_Engine_Test.mid", track=1)
fl_copy_midi(source_track=1, dest_tracks=[2,3,4,5])

# 5. IMPORT MELUSINA VOCAL RENDERS TO VOCAL LANE (Track 4)
# After rendering USTX in OpenUtau → export WAVs → drag to Serum Granular Osc A
# fl_load_samples(track=4, plugin="Serum 2", oscillator="A", folder="Melusina_Sophie_Renders/")

# 6. LOAD FROST VOCAL STEMS TO VOCAL LANE OSC B (for spectral morph)
# fl_load_samples(track=4, plugin="Serum 2", oscillator="B", folder="Frost_Vocal_Stems_Granular/")

# 7. RUN MIX DOCTOR (calibrated processing intent → your actual plugin chain)
fl_mix_doctor()

# 8. EXPORT STEMS + MASTER
fl_export_stems(output_folder="Sophie_Material_Engine_Stems/", format="wav", bit_depth=24)
fl_export_master(output_file="Sophie_Material_Engine_Master.wav", format="wav", bit_depth=24)
'''

with open(os.path.join(OUT, 'Sophie_Material_Engine_MCP_Build.txt'), 'w') as f:
    f.write(mcp_commands)

# ──────────────────────────────────────────────────────────────────────────────
# TOUCHDESIGNER CYMATIC VISUALIZER — PROJECT FILE REFERENCE
# ──────────────────────────────────────────────────────────────────────────────

td_notes = '''# ──────────────────────────────────────────────────────────────────────────────
# TOUCHDESIGNER — SOPHIE MATERIAL ENGINE CYMATIC VISUALIZER
# ──────────────────────────────────────────────────────────────────────────────

# NETWORK STRUCTURE:
# /project1
#   /audio_in          ← Audio Device In (FL Studio ASIO out) OR MovieFileIn (rendered WAV)
#   /chladni           ← melodia-cymatic-eigenmode solver (CHOP→SOP)
#   /material_lanes    ← 4x Container COMPs (Brass/Strings/Perc/Vocal)
#   /composite         ← Overlay + Bloom + Color Grade
#   /movie_out         ← MovieFileOut (4K60 ProRes)

# CHLADNI SOLVER (melodia-cymatic-eigenmode):
#   Input: AudioSpectrum CHOP (64 bands, log scale)
#   Mode: Circular plate (Sophie latex = radial modes)
#   Frequencies: Map 64 bands → eigenmode (m,n) pairs
#   Displacement: Amplitude × 0.1 scale → SOP vertex offset
#   Material: Subsurface + Iridescence (Sophie oil-slick look)

# MATERIAL LANES (4 containers, driven by same MIDI via OSC from FL):
#   Brass:   High freq bands (4-16kHz) → high (m,n) modes → sharp cusps
#   Strings: Mid freq bands (500-4kHz) → low (m,n) modes → smooth waves
#   Perc:    Transient detection → impulse burst → expanding ring modes
#   Vocal:   Formant bands (F1/F2/F3) → vowel-shaped modes (elliptical plate)

# OSC FROM FL STUDIO MCP:
#   /midi/note      → trigger lane emphasis
#   /midi/cc/74     → BRIGHTNESS → global mode frequency scale
#   /midi/cc/1      → LATEX AMOUNT → displacement amplitude
#   /macro/morph    → MATERIAL MORPH → crossfade lane opacity

# RENDER SETTINGS:
#   Resolution: 3840×2160 @ 60fps
#   Codec: Apple ProRes 422 HQ
#   Audio: Embed FL Studio master out (48kHz 24-bit)
'''

with open(os.path.join(OUT, 'Sophie_Material_Engine_TouchDesigner.md'), 'w') as f:
    f.write(td_notes)

# ──────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────────────────────────────────────

print("=" * 70)
print("SOPHIE MATERIAL ENGINE — TRACK PACK GENERATED")
print("=" * 70)
print(f"Output dir: {OUT}")
print()
print("MIDI FILES:")
print("  • Sophie_Material_Engine_Test.mid      — Main sequencer (16th notes + CC74/CC1)")
print("  • Sophie_Material_Vocal_Guide.mid      — Melusina vocal reference")
print("  • Sophie_Material_Bass.mid             — GND-SIN sub-bass (keytracked)")
print("  • Sophie_Material_Chords.mid           — Harmonic reference (Am-F-C-G)")
print()
print("USTX:")
print("  • Melusina_Sophie_Material_Engine.ustx — Full 8-bar vocal phrase")
print("    Assign: Melusina JA VCV (RangeHigh_ for bright, RangeLow_ for sub)")
print()
print("FL STUDIO MCP:")
print("  • Sophie_Material_Engine_MCP_Build.txt — 5 Serum instances + macros + MIDI")
print()
print("TOUCHDESIGNER:")
print("  • Sophie_Material_Engine_TouchDesigner.md — Cymatic visualizer spec")
print()
print("NEXT:")
print("  1. Open .ustx in OpenUtau → render WAVs (48kHz)")
print("  2. Drag WAVs to Serum Granular Osc A (Track 4)")
print("  3. Run MCP build commands in FL Studio")
print("  4. Route FL audio to TouchDesigner → render visualizer")
print("=" * 70)