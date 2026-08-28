# Grandmaster Melodia — Audio-Reactive Environment

The real-time visual identity of **Melodia Melusina**, built in TouchDesigner.
Music IS the visual. The hand IS the instrument.

Warm-violet toon language, celestial/gothic kitbash, ornamented like the game it
sings for. Blender is the scene engine (via Spout); TouchDesigner is the live
composite/performer surface.

## The four rooms (and what each owns)

| Room | Responsibility | Live? |
|------|----------------|-------|
| `SCENE`   | Blender Eevee content in via Spout (`syphonspoutinTOP`) | present |
| `AUDIO`   | FFT + 5-band RMS + chord/pitch analysis; the music engine | live |
| `PERFORM` | Hand OSC (`hand_osc`, port 7000) → gesture drives audio+visuals | live |
| `COMPOSITE`| Starfield, particles, postfx (bloom/vignette/LUT) → `spoutout1` | live |

Canonical project: `project/grandmaster_melodia.toe`.

## What is LIVE right now

- **Hand → starfield** binding, verified end-to-end: wrist X → tx, wrist Y → ty,
  openness → scale, index → rotate. Expression recipe:
  `op('/project1/hand_osc')['hand/0/wrist1']*4`. Exact-match proof this session:
  `0.042 × 4 = 0.169`.
- **Hand → audio** live: wrist X → cutoff (4,570 Hz), wrist Y → pan (−0.018),
  openness → volume (0.010), all `ParMode.EXPRESSION`.
- **Audio engine** (36 ops): Audio Device In → 5-band bandpass/RMS/analyze →
  chord detector + pitch analyzer + spectral analyzer. This is the engine the
  effects react to.
- **Postfx chain**: bloom, vignette, and an Infinity Nikki-style LUT (`nikki_lut`).
- **Spout out** (`spoutout1`) → OBS / Resolume.
- **Particles**: burst-on-onset + motes (audio-reactive emitter grid).

## What is NOT done yet (honest)

- **FL → TD audio link**: the Voicemeeter + loopMIDI install completes the pipe.
  Right now audio is whatever feeds `Audio Device In` directly.
- **AAA effect layer** (resonance rings, toon glow) — in progress.
- **Properties panel + Drivers table** (the "Blender for a TD user" surface).
- Brand palette is defined (`assets/palette.json`) but not yet consumed by every
  effect chain as the single source.

## Ports & tooling

- TD MCP (Envoy): `http://127.0.0.1:9870/mcp`
- Hand OSC in: UDP port 7000
- Spout send: `TDSyphonSpoutOut`
- Blender addon: `maybites/TextureSharing` v9.0.3 + SpoutGL 0.1.1

*Owner voice: this is a live environment, not a finished product. What's true is
marked live; everything else is named as not-done rather than hyped.*
