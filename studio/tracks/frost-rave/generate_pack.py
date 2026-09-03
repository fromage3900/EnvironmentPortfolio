# Generate Tidecall rave track pack: MIDI (vocal guide / chords / bass) + Melusina USTX
# Song: "UNDERTOW (Until Dawn)" — 128 BPM, A minor. BPM matches Tidecall's Descent engine.
import json, struct, os

TPQ = 480  # ticks per quarter
BAR = 1920
OUT = r'C:\EnvironmentPortfolio\studio\tracks\frost-rave'

def vlq(n):
    out = bytearray([n & 0x7F]); n >>= 7
    while n:
        out.insert(0, 0x80 | (n & 0x7F)); n >>= 7
    return bytes(out)

def track_chunk(events):
    data = b''.join(events)
    return b'MTrk' + struct.pack('>I', len(data)) + data

def write_midi(path, tracks, tempo_bpm=128):
    # tracks: list of list of (abs_ticks, bytes) merged with tempo on track 0
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

# --- Chords: Am F C G, offbeat 8th stabs, 4-bar loop x2 ---
CH = {0: [57, 60, 64], 1: [53, 57, 60], 2: [55, 60, 64], 3: [55, 59, 62]}  # Am F C G
chord_notes = []
for cycle in range(2):
    for bar, root in enumerate([0, 1, 2, 3]):
        base = (cycle * 4 + bar) * BAR
        for off in (240, 720, 1200, 1680):
            for tone in CH[root]:
                chord_notes.append((base + off, 170, tone, 88))

# --- Bass: rolling offbeat 8ths + 16th turn ---
BASS = [45, 41, 48, 43]  # A2 F2 C3 G2
bass_notes = []
for cycle in range(2):
    for bar, root in enumerate(BASS):
        base = (cycle * 4 + bar) * BAR
        for off in (240, 720, 1200, 1680):
            bass_notes.append((base + off, 200, root, 104))
        if bar == 3:  # turnaround run: G A Bb B
            for k, tone in enumerate([43, 45, 46, 47]):
                bass_notes.append((base + 1760 + k * 40, 40, tone, 96))

# --- Vocal: 8-bar phrase (JA romaji), sung loop ---
VOCAL_PHRASE = [
    # (lyric, tone, dur) sequenced bar by bar
    ('u', 69, 240), ('chi', 72, 240), ('na', 76, 360), ('ru', 74, 120),          # Am
    ('shi', 72, 240), ('o', 69, 240), ('yo', 67, 480),                           # F
    ('o', 67, 240), ('do', 72, 240), ('re', 76, 240), ('ka', 74, 240),           # C
    ('i', 71, 240), ('yo', 67, 240), ('u', 69, 720),                             # G
    ('yo', 69, 240), ('ru', 72, 240), ('ga', 76, 360), ('a', 74, 120),           # Am
    ('ke', 72, 240), ('ru', 69, 240), ('ma', 67, 480),                           # F
    ('de', 67, 240), ('mo', 72, 240), ('hi', 76, 240), ('ka', 74, 240),          # C
    ('ru', 71, 240), ('de', 67, 240), ('', 69, 720),                             # G
]
vocal_notes, t = [], 0
for lyric, tone, dur in VOCAL_PHRASE:
    if dur: vocal_notes.append((t, dur, tone, 100))
    t += dur
vocal_notes_loop = vocal_notes + [(s + 8 * BAR, d, n, v) for (s, d, n, v) in vocal_notes]

write_midi(os.path.join(OUT, 'UNDERTOW_vocal_guide.mid'), [[], note_events(vocal_notes_loop)])
write_midi(os.path.join(OUT, 'UNDERTOW_chords.mid'), [[], note_events(chord_notes, prog=48)])   # 48 = strings-ish
write_midi(os.path.join(OUT, 'UNDERTOW_bass.mid'), [[], note_events(bass_notes, prog=38)])      # 38 = synth bass

# --- USTX: Melusina sings the phrase (one loop; user duplicates in OpenUtau) ---
ustx = {
    'ustx_version': 0.6,
    'name': 'Melusina_UNDERTOW_hook',
    'comment': 'UNDERTOW (Until Dawn) — 128 BPM A minor rave. Assign singer: Melusina JA VCV, render, export WAV.',
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
            'name': 'hook_loop',
            'notes': [
                {'position': pos, 'duration': dur, 'tone': tone, 'lyric': lyric if lyric else 'a'}
                for (pos, dur, tone, _v), (lyric, _t, _d) in zip(vocal_notes, VOCAL_PHRASE)
            ],
        }],
    }],
}
with open(os.path.join(OUT, 'Melusina_UNDERTOW_hook.ustx'), 'w', encoding='utf-8') as f:
    json.dump(ustx, f, indent=2, ensure_ascii=False)

print('vocal notes:', len(vocal_notes), '| chord notes:', len(chord_notes), '| bass notes:', len(bass_notes))
print('written:', os.listdir(OUT))
