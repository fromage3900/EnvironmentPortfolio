# Melodia Melusina

**A single-person AAA-tier rhythm-JRPG built in Unreal Engine 5.8.**

OMORI's shape. Zelda's music-as-key. Infinity Nikki's visual and wardrobe bar.

> **Authority:** [`PROJECT.md`](PROJECT.md) is the project's authority statement. If any document
> here disagrees with it about what this project is, `PROJECT.md` wins.

---

## 🎮 The game

**QuillScript** owns narrative. **The TurnBased JRPG template** owns party, turns, targeting,
damage, results, inventory and saves. These two are absolute — never rebuilt, never wrapped,
never competed with.

The **musical layer** is not a second game. Rhythm input rides *on top of* the JRPG command
scaffolding — the same Attack/Skill/Item/Flee decisions, timed. Music enhances combat, and in the
world it acts as a key: puzzles respond to played phrases.

The **wardrobe** is a core pillar. Outfits are Infinity Nikki-grade presentation on a Substrate
Toon spine, and they carry gameplay meaning.

### The loop

```text
sanctuary conversation
  -> authored departure
  -> dream traversal (music opens the way)
  -> JRPG encounter, rhythm-timed
  -> typed terminal result
  -> narrative consequence
  -> stable checkpoint/save
```

### Playable route

`L_MelusinaMorning` → `L_KaleidoNave` (Dreamstate content is merged into KaleidoNave)

Real paths:
- `/Game/Melodia/Levels/Opening/L_MelusinaMorning`
- `/Game/EnvSandbox/Environments/L_KaleidoNave`

### Systems

| System | Role | Layer |
|--------|------|-------|
| **QuillScript dialogue** | Narrative authority; NPC interaction + typed terminal results | **Absolute authority** |
| **Stock JRPG combat** | Turn/target/damage/result authority (TurnBasedJRPGTemplate) | **Absolute authority** |
| **Rhythm combat** | Timing layer on JRPG command input; `UMelodiaRhythmCombatSubsystem` + Harmonix music clock | Pillar |
| **Wardrobe** | Outfit presentation + gameplay meaning; `MelodiaWardrobe` plugin | Pillar |
| **UI** | One writer per surface | Pillar |
| **World puzzle** | Music as key — **not yet built** | Pillar |
| **Canonical save/load** | `BP_JRPGSaveGame` slot across process restart | Shipping gate |
| **Travel authority** | `UMelodiaTravelSubsystem` — single travel path with allowlist validation | Support |
| **Input authority** | `UMelodiaInputContextSubsystem` — push/pop context stack | Support |
| **Melody Token economy** | `UMelodiaTokenWalletSubsystem` — pickups + HUD | Support |
| **Co-op skills** | Petal Cadence, Skybound Refrain, Resonance (stock authority) | Support |

### Current state

The systems are **not incomplete — they were built twice, in parallel, and never joined.**
Rhythm exists in three places, wardrobe in five, and the battle HUD has two writers by design.
World puzzle has none.

The active work is **convergence**, not construction.

> **Checkpoint (2026-08-13):** The active Unreal checkout is `BS_GodFile` on `main`,
> synchronized with `MelodiaMelusinaV2/main` at `840b7650`. PRs **#4** and **#6** are merged.
>
> **Owner-locked WORKED in PIE:** rhythm highway and QuillScript (2026-08-12); real-keyboard
> `runtime` gate (2026-08-13). These are ground truth and are never re-proved.
>
> **Open:** the stock battle path, `save_load`, `repeat_consume`, `package_launch`, and the six
> orchestra convergence gates.

### Niche — cozy → demented psych-horror, light gacha, Western Steam
Pastel fairytale that curdles. Wardrobe-as-dread + rhythm-as-ritual + music-as-key. Deep niche report: [`BS_GodFile/research/melodia_niche_cozy-horror_ue_workflows.md`](BS_GodFile/research/melodia_niche_cozy-horror_ue_workflows.md) — UE 5.8 Substrate/Quartz/MCP/VRM 0.1% workflows + OSS toolkit (`rhythm-game-utilities`, `VRM4U`).

### Where to start reading

1. [`PROJECT.md`](PROJECT.md) — the authority statement
2. [`BS_GodFile/Docs/ORCHESTRA_CONVERGENCE_2026-08-20.md`](BS_GodFile/Docs/ORCHESTRA_CONVERGENCE_2026-08-20.md) — which implementation owns which pillar
3. [`BS_GodFile/Docs/ORCHESTRA_CONTRACT_2026-08-20.md`](BS_GodFile/Docs/ORCHESTRA_CONTRACT_2026-08-20.md) — how the pillars meet the authority layers
4. [`BS_GodFile/_AGENT_WORKING_AGREEMENT.md`](BS_GodFile/_AGENT_WORKING_AGREEMENT.md) — how work gets done here

Then: [`BS_GodFile/_VERTICAL_SLICE_SCOPE.md`](BS_GodFile/_VERTICAL_SLICE_SCOPE.md) (scope) ·
[`BS_GodFile/_TASK_QUEUE.md`](BS_GodFile/_TASK_QUEUE.md) (live tasks) ·
[`BS_GodFile/_DECISION_LOG.md`](BS_GodFile/_DECISION_LOG.md) (settled questions).

---

## 🏗️ The world-building toolchain

The environment-art platform is **the toolchain that feeds the game** — not a second product.
UE 5.8 + Blender 5.2: a real-time Blender↔Unreal level design bridge, procedural geometry
generation, automatic material crosswalk, and a capture/publish pipeline.

### Onboarding paths

| Path | Time | What You'll Do |
|------|------|----------------|
| **Viewer** | 5 min | Open & explore levels |
| **Geometry** | 10 min | Build & send assets to UE |
| **Materials** | 15 min | Create & preview materials |
| **Full Collaborator** | 30 min | Complete live workflow |

Full guide: [`BS_GodFile/QUICKSTART.md`](BS_GodFile/QUICKSTART.md) and
[`BS_GodFile/COLLABORATOR_SETUP.md`](BS_GodFile/COLLABORATOR_SETUP.md)

### Port map

| Port | Service | Direction |
|------|---------|-----------|
| `9876` | LiveLink — FBX/texture/animation stream | Blender → UE |
| `9316` | UE Monolith MCP — Python execution | Any → UE |
| `9317` | Blender MCP — bridge control | Any → Blender |
| `50021` | VOICEVOX — TTS (7 characters) | Any → VOICEVOX |
| `50022` | Melusina Voice — custom SBV2 | Any → Melusina |

---

## 🤖 AI tooling

**The AI tooling is a tool.** Local models, MCP surfaces and local model lanes exist to produce game
artifacts. None of them is the product, and none may set project direction.

Production model lanes route real game work — wardrobe catalog rows, rhythm beat maps,
QuillScript dialogue drafts, asset QA, animation binding checks — to local models running on
Ollama and koboldcpp. A lane's output counts only when an Echo gate accepts the artifact.

- Router: `python BS_GodFile/Tools/model_router.py classes`
- Gate ledger: `python BS_GodFile/Tools/echo_run.py list`
- Policy (default-deny): `BS_GodFile/Tools/mcp_policy.py`
- Surfaces and the one-writer rule: [`BS_GodFile/Docs/AGENT_MCP_SURFACES.md`](BS_GodFile/Docs/AGENT_MCP_SURFACES.md)

---

## 📚 Documentation

- **Full index:** [`BS_GodFile/DOC_INDEX.md`](BS_GodFile/DOC_INDEX.md)
- **Community governance:** [`LICENSE`](LICENSE) (MIT) · [`CONTRIBUTING.md`](CONTRIBUTING.md) · [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) · [`SECURITY.md`](SECURITY.md)

Marketing, funding and hiring material lives under `BS_GodFile/Docs/Career/` and
`BS_GodFile/Docs/Portfolio/`. It is **downstream of the game** and carries no project authority.

---

## 🧭 Repo status

- `BS_GodFile/.git` is the active Unreal repository; `main` and `v2/main` are synchronized at `840b7650`.
- `my-site-clean/.git` is the website repository; local tip `3cfa5f0` is not synchronized with its
  configured remote because the histories are unrelated. Do not force-push or merge unrelated
  histories without an owner decision.
- A previous workflow used `G:\EnvironmentPortfolio` as a cross-PC mirror. That drive is not part
  of the active environment contract.
- Use `MELODIA_PROJECT_ROOT`, `MELODIA_WEBSITE_ROOT`, and `Config/paths.json` to select local
  checkouts. The active Unreal setup is documented in
  `BS_GodFile/Docs/ENVIRONMENT_RUNBOOK_2026-08-11.md`; never infer authority from a drive letter
  or a legacy root `.git`.
- GitHub synchronization is attempted only after local commits and remains subject to network access.
- Do not assume website commits are live on GitHub Pages until the website remote history is
  reconciled and the publication push is verified.
