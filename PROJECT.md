# Melodia Melusina 100+ Hour Content Pack — Project Specification

## 1. Architecture & Overview
- **Project**: Melodia Melusina Content Pack Expansion (UE 5.8 JRPG)
- **Output Directory**: `C:\EnvironmentPortfolio\generated\melodia_content_pack\`
- **Core Systems**:
  1. **Narrative & Dialogue Engine (QuillScript)**: Modular dialogue scripts (`.qsc`) driving movement seams, recruit bonds, world quests, and post-game revelations.
  2. **Turn-Based Rhythm JRPG Core**: 85+ enemies and 25 multi-phase bosses with BPM synchronization, HP phase gates, and musical mechanics.
  3. **Expedition & Hub Loop**: 110+ procedural/authored expedition rooms with 4 puzzle archetypes (`music_key`, `timed_path`, `resonance_match`, `none`), tiered dissonance (Tiers 1–5), and hub progression anchors.

## 2. Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | Content Manifest Scaffold | Detailed 100+ hour time-budget, 4 movements + post-game, hub state matrix, recruit dossiers, quest logs | M1 | Survey / Request |
| F2 | Main Seams QuillScript Pack | 20 `.qsc` files (5 per movement) for opening, pre-brief, post-debrief, mid-climax, reunion | M2 | Request §R2 |
| F3 | Recruit Arcs QuillScript Pack | 20 `.qsc` files (5 per Recruit A–D) for intro, observation, revelation, duet, bond master | M2 | Request §R2 |
| F4 | World Quests QuillScript Pack | 18 `.qsc` files (3 per Quest 1–6) for quest hook, investigation/climax, resolution | M2 | Request §R2 |
| F5 | Post-Game QuillScript Pack | 5 `.qsc` files for Return Echo opening, 5th doorway, dissonance trial, NG+ anchor | M2 | Request §R2 |
| F6 | Encounter Pack JSON | 85 enemies (Tiers 1–5) + 25 multi-phase bosses (2–3 phases, HP triggers, defeat flags, reward IDs) | M3 | Request §R3 |
| F7 | Expedition Rooms JSON | 110 rooms across 5 zones with puzzle types, valid enemy pools, clear rewards, flavour text | M3 | Request §R3 |
| F8 | Test Runner & Static Validator | Python validation script checking JSON schema, AST parsing of all `.qsc` files, and foreign keys | M4 | Quality Plan |
| F9 | Independent Review & Forensic Audit | Objective review, challenger stress testing, and forensic integrity audit | M5 | Audit Plan |

## 3. Milestones & Status
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Content Manifest | `content_manifest.md` | Survey Complete | IN_PROGRESS |
| M2 | QuillScript Content Pack | 63 `.qsc` files across 4 directories | M1 contracts | PLANNED |
| M3 | Encounter & Expedition Pack | `encounter_pack.json`, `expedition_rooms.json` | M1 contracts | PLANNED |
| M4 | Test Suite & Validator | `validate_content_pack.py` + execution | M2, M3 | PLANNED |
| M5 | Review, Challenge & Audit | Reviewers, Challengers, Forensic Auditor | M4 | PLANNED |

## 4. Interface & Naming Contracts
- **QuillScript Syntax**:
  - Entry: `@ Start`
  - Exit: `$ End`
  - Choices: `* Choice text. | cond | -> TargetLabel`
  - Conditionals: `? if: {melodia_flag_name} == on`
  - Jump: `-> TargetLabel`
  - Label: `<@> TargetLabel`
  - Flag Assignment: `$ melodia_flag_name = on`
  - Notifications: `$ Notify melodia:[domain]:[event_id]` where domain in `['battle', 'quest', 'reward', 'stat', 'flag', 'travel', 'item']`
- **Flag Format**: `melodia_[scope]_[descriptor]` (e.g. `melodia_boss_fugue_overture_defeated`, `melodia_recruit_a_bond_unlocked`)
- **Reward ID Format**: `reward.[zone].[descriptor]` (e.g. `reward.sakura.melody_core`)
- **Emotional Guardrails**: No animal harm, no corpse reveal, no guilt framing, no on-screen diagnosis, no punishment loop, Sir Melodious is retrievable/benignly absent, absent duet-partner stays fragmentary.

## 5. Code & File Layout
```
generated/melodia_content_pack/
├── content_manifest.md
├── quill_scripts/
│   ├── main_seams/     (20 .qsc files)
│   ├── recruit_arcs/   (20 .qsc files)
│   ├── world_quests/   (18 .qsc files)
│   └── post_game/      (5 .qsc files)
├── data/
│   ├── encounter_pack.json
│   └── expedition_rooms.json
└── tests/
    └── validate_content_pack.py
```
