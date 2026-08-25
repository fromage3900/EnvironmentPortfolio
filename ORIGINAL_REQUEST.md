# Original User Request

## Initial Request — 2026-08-25T18:07:43Z

<USER_REQUEST>
# Teamwork Project Prompt — Draft

> Status: **Launched (Revised for Token Efficiency)**
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: [none — full team; standard project build path]

Generate a focused, structured content pack for **Melodia Melusina** (UE 5.8 JRPG).
To conserve token usage and maintain strict focus, **limit this generation exclusively to Chapters (Movements) 1, 2, and 3**. Do not generate content for Movement 4 or any Post-Game/Endgame layers. Keep all descriptions concise and token-efficient.

Working directory: `C:\EnvironmentPortfolio\generated\melodia_content_pack`
Integrity mode: development

---

## Game Reference Material

### Core Design Authorities
- **QuillScript syntax** (`.qsc`) — the scripting format used for all in-game dialogue and quest logic.
- **The Chapters (Movements) in scope:**
  - Movement 1 — *Petal Cantata* (Sakura Terrace, waltz register, opening arc)
  - Movement 2 — *Fugue Grotto* (collapsed gully network, deeper dream register)
  - Movement 3 — *Cadence Cathedral* (crystal ridge, farthest register, grief peak)
- **The loop** — `RunSeed + DoorwayID + DissonanceTier` backs seeded expeditions that replay deterministically.
- **The party in scope** — Melusina (bard) + Sir Melodious (companion anchor) + 3 recruits (Recruit A, B, C).

### Emotional Guardrails (hard limits)
- No animal harm, no corpse reveal, no guilt framing, no on-screen diagnosis, no punishment loop.
- No grief meter with teeth — grief and warmth coexist.
- The absent duet-partner stays fragmentary and absent.
- Sir Melodious is alive, benignly absent when not summoned.
- Keep descriptions brief to save tokens.

---

## Requirements

### R1. Content Scaffold (Chapters 1-3 only)

Produce a concise content design document (`content_manifest.md`) mapping out content for Movements 1, 2, and 3.
1. **Main Route** — Expand movements 1, 2, and 3 with additional expedition room pools, seam scenes, and hub state changes.
2. **Side Content** — Optional party arcs for Recruits A, B, and C, plus a few optional world quests for zones 1-3.

### R2. QuillScript Content Files

Produce at minimum **25 QuillScript (.qsc) files** (concise scripts):
- **Main route seams**: ~4 per movement (12 files total).
- **Recruit story arcs**: ~3 scenes per Recruit A, B, C (9 files total).
- **World quest beats**: ~4 optional world quests (4+ files total).
- Placeholder names: `Recruit_A`, `Recruit_B`, `Recruit_C`.

### R3. Encounter and Expedition Data Pack

Produce a structured JSON data pack (`encounter_pack.json`) containing:
- **~45 named enemy definitions**, each with: `id`, `display_name`, `movement_zone` (1-3 only), `dissonance_tier` (1-4), `hp`, `mp`, `attack`, `defense`, `skills` (1-2 abilities), `lore_hook` (short sentence).
- **12 boss encounters** (4 per movement), each with: `id`, `display_name`, `movement_zone`, `phase_count` (2), `phases`, `defeat_dialogue_flag`, `reward_id`.
- **~60 expedition room definitions** (`expedition_rooms.json`), each with: `id`, `room_name`, `movement_zone`, `dissonance_tier`, `enemy_pool`, `puzzle_type` (`music_key`, `timed_path`, `resonance_match`, `none`), `reward_on_clear`, `flavour_text` (very brief).

---

## Acceptance Criteria

### Content Manifest
- [ ] `content_manifest.md` exists and covers only Movements 1, 2, and 3.
- [ ] Explicitly omits Movement 4 and Post-game content to save tokens.

### QuillScript Files
- [ ] At least 25 `.qsc` files are produced.
- [ ] Every `.qsc` file parses correctly with `@ Start` / `$ End`.
- [ ] Emotional guardrails are respected.

### Encounter and Expedition Data Pack
- [ ] `encounter_pack.json` contains ~45 enemies and 12 bosses.
- [ ] `expedition_rooms.json` contains ~60 room definitions for zones 1-3.
- [ ] All `enemy_pool` arrays reference valid `id` values.
</USER_REQUEST>
