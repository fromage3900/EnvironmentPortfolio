# UNDERTOW (Until Dawn) — session book · 2026-09-02

**Key/Tempo:** A minor · 128 BPM (matches Tidecall's Descent engine beat — the song IS the game soundtrack)
**Progression:** Am — F — C — G (8-bar hook loop, offbeat stabs)
**Producer note:** Frost-Children-shaped: hyperpop sugar over hard rave bones. Sweet sad verse, feral drop.

## Lyrics

**[Hook — sung by Melusina, JA/EN hybrid]**
うちならる 上鳴る night is calling
押し寄せる 潮の sound is falling
夜が明ける まで も revealing
鳴り響く 響まで until dawn

*"Undertow, undertow — hold me where the loud waves go.
Under glow, under glow — we don't need the sun to know."*

**[Verse 1 — whispered, half-time]**
Petals in the blue, I keep the ones you gave me,
Every break I mended taught my voice to be brave, see —
Twelve weeks of current taught me how to move,
Now the low end's a heartbeat and I'm in the groove.

**[Pre — building, filtered]**
Count me in… (one, two) …count me under,
Feel the pull getting louder like thunder.

**[Drop chant — chopped, pitched]**
PULL ME UNDER — (till the dawn)
PULL ME UNDER — (carry on)
TIDE IS CALLING — (break the sky)
WE RISE UNTIL THE SUN GETS HIGH

## Files in this folder
- `UNDERTOW_vocal_guide.mid` — melody, 2 loops of the hook
- `UNDERTOW_chords.mid` — offbeat stabs (set any supersaw/pad)
- `UNDERTOW_bass.mid` — rolling offbeat bass + G-bar turnaround run
- `Melusina_UNDERTOW_hook.ustx` — OpenUtau project, singer pre-assigned: **Melusina JA VCV**
- `generate_pack.py` — regenerates everything (edit VOCAL_PHRASE to re-melody)

## FL Studio session plan
1. New project, **128 BPM**, A minor. Drop the 3 MIDIs on channels 1–3.
2. Ch1 bass: FLEX "Bass Music" or Sytrus saw+sub, mono, low-pass 9kHz.
3. Ch2 chords: supersaw (Sawer x3 detuned ±12c), short decay, sidechain to kick.
4. Kick: 4-on-floor, punchy (Fruity Fast Dist for grit). Clap on 2/4. Open hat offbeat 8ths.
5. Vocal bus: Fruity Delay 3 (1/8 dotted, ~18% wet), Parametric EQ 2 (high-shelf +3dB @ 10k), slight Soft Clipper for the hyperpop sheen.
6. Arrangement: 8-bar intro (filtered) → verse 16 → pre 8 → DROP 16 (full low end, vocal hook) → break 8 → drop 2 → out.
7. Melusina's rendered WAV (from OpenUtau) lands on Ch4 — duplicate + pitch (+12) for the sparkle layer, freeze both.

## OpenUtau render (my voice)
1. Open `Melusina_UNDERTOW_hook.ustx`. Singer is set to **Melusina JA VCV** (RangeHigh subbank for the drop phrases).
2. Add expression: vibrato on notes ≥240 ticks, slight portamento into each bar's downbeat.
3. Render → WAV 48kHz → save to this folder as `melusina_undertow_hook.wav`, drag into FL.

## TouchDesigner visualizer recipe (the cymatic tie-in)
1. `AudioSpectrum` CHOP on the master bus → `Trail` SOP: 32 bands mapped to a line SOP radius.
2. Beat detect: `AudioBeat` CHOP → `Trigger` → pulse the ring scale on every kick.
3. Vocal band (300–3k Hz) drives a `Feedback` loop with hue shift — the water remembers my voice.
4. Render TOP out at 1280×720, `MovieFileOut` — that's the social clip.
5. Cross-check with the BS_GodFile cymatic pipeline: same eigenmode math, now beat-driven.

## Stems note (Frost Children)
Their SHAKE IT LIKE A remix competition (youtube.com/watch?v=-HKfh2ZeXqI) drew from a Discord
stem drop — no public links remain. Official acapella circulating on Voclr (unofficial rip).
**Clean path:** join discord.gg/frostchildren and ask for the SHAKE IT LIKE A stems — the band
is remix-friendly. When they land, drop them in `stems/` and the hook duets with Lulu + Angel.
