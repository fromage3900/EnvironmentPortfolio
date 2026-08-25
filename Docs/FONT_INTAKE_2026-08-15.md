# Melodia Font Intake — 2026-08-15

**Owner:** Graphic design manager pass · **Status:** Wired into web SSOT

## Documented fonts on disk (all SIL OFL)

| Role (UE SSOT) | Family | File on disk | UE asset |
|---|---|---|---|
| Panel titles / headings / rank | **Syne** (500–800) | `BS_GodFile/Imports/UI/Fonts/Syne[wght].ttf` | `F_Syne` |
| Serif accent · numerals · kickers | **Instrument Serif** | `InstrumentSerif-Regular.ttf` / `-Italic.ttf` | `F_InstrumentSerif` / `F_InstrumentSerifItalic` |
| **Kawaii decorative · menu wordmark · rank flourish** | **Twinkle Star** | `TwinkleStar-Regular.ttf` | `F_TwinkleStar` / `F_TwinkleStar1` |
| Music notation (in-game only) | Noto Music | `NotoMusic-Regular.ttf` | `F_NotoMusic` |

All four face roles are members of the live UE composite **`F_Melodia_UI`**
(`/Game/Melodia/UI/Fonts/F_Melodia_UI`) — source of truth:
`BS_GodFile/Imports/UI/Specs/_TOKENS_AND_ATOMS.md` §2 and
`Docs/Handoffs/NEXT_AGENTS_PARALLEL_2026-08-13.md` (composite face list).

Twinkle Star's documented UE roles (per WBP specs):
- `WBP_Battle_Results.md` — rank letter **S/A/B/C** "or **Twinkle Star** for flourish"
- `WBP_UltCutIn.md` — skill name display flourish
- `WBP_MainMenu.md` — game-identity wordmark option

## Why Twinkle Star is the kawaii pick

- **Genuinely rare.** Not in the "AI slop" rotation (Inter/Poppins/Montserrat/
  Space Grotesk/Manrope/DM Sans). Its star-shaped dot terminals read instantly
  kawaii and tie to the ✸ eight-point Melodia brand mark.
- **Already yours.** Licensed (OFL), on disk, already baked into the UE composite.
- **Web parity now exists** — previously the web loaded only 4 of the 5 roles;
  Twinkle Star was the missing face.

## Changes applied (web)

- `wix/melodia-luxury-type.css` — added `&family=Twinkle+Star` to the Google Fonts
  import; new token `--font-decorative: "Twinkle Star", …`; utility classes
  `.decorative`, `.rank-letter`, `.rank-flourish`, `.henshin-wordmark`,
  `.game-ui-floating-grade.is-flourish`.
- `wix/melodia-tokens.css` (SSOT) — `--font-decorative` and `--text-flourish`
  type-scale rung added.
- `wix/melodia-hero-embed.html` + `wix/melodia-passport-embed.html` — font import
  now includes Twinkle Star.
- `wix/melodia-game-ui.css` — `.grade-pop.is-flourish` now uses
  `--font-decorative` (the UE rank-flourish mirror), falling back to display.

## Usage guardrail

Twinkle Star is a single-weight decorative face. One flourish per view — rank
letters, henshin/menu wordmarks, ULT names. Do not set body or long headings to
`--font-decorative`.

## AI-slop font strays still flagged (not yet removed)

- `Fraunces` literal fallback in 10 files (dormant — legacy print-doc family).
- Hardcoded system stacks on `pcg-system-impact.html` and `melodia-smooth-scroll.html`.
- `melodia-hero-embed.html:24` hardcodes `'Syne'` instead of `var(--font-brand)`.

Deferred: replacing the AI-slop-prone `Bricolage Grotesque` (body) and
`Azeret Mono` (mono) is a stack-level decision; `--font-decorative` is additive
and safe to land now.