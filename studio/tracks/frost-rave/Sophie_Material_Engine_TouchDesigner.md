# ──────────────────────────────────────────────────────────────────────────────
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
