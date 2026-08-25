# Breadcrumb grep patterns + term→replacement map

Used by the `de-ai-framing` skill to inventory and verify a clean pass.

## Inventory sweep (run from the site/repo root)

```bash
# Front-facing copy only (the stuff a visitor reads)
grep -rin -E "fleet|agent lane|agent swarm|orchestrator|swarm|agent harness|Agent Harness" \
  --include=*.md --include=*.html . | grep -v node_modules

# Softer "AI infra" phrasing that still leaks
grep -rin -E "model lanes|SWE Light orchestrator|live agent MCP|first agent ping|Hermes harness" \
  --include=*.md --include=*.html . | grep -v node_modules
```

## Link-graph check (before deleting/renaming a page)

```bash
# How many pages point AT the target? If >0, relabel, do not delete.
grep -rln "melusina-agent-harness.html" . --include=*.html --include=*.md | grep -v node_modules
```

## Term → replacement map (verified on a real portfolio)

| Found | Becomes | Notes |
|---|---|---|
| `fleet`, `fleet:qwen`, `fleet:muse`, `fleet:p0` (npm keys) | `models`, `models:qwen`, `models:muse`, `models:p0` | rename the KEY only; keep `run_model_fleet.py` filename |
| `Agent Harness` / `agent harness` (titles, labels) | `Model Tooling` | page renamed `melusina-agent-harness.html` → `melusina-model-tooling.html` via `git mv` |
| `Hermes harness, Qwen/Muse lanes, SWE Light orchestrator` | `local model tooling (Qwen/Muse)` | subtitle/scorecard phrasing |
| `live agent MCP` | `live bridge` | port-map / onboarding copy |
| `first agent ping` | `first bridge connection` | onboarding copy |
| `genome/agent control` (port map) | `bridge control` | |
| `agent lanes` (prose) | `local model lanes` | keep "AI tooling is a tool" framing verbatim |
| `og:title` "... Agent Harness Evidence" | "... Model Tooling Evidence" | meta tag — easy to miss, breaks social share |
| `og:url` pointing at old filename | new filename | else 404 on share |

## User-facing vs GENERATED split (do NOT hand-edit the generated side)

- EDIT: `README.md`, `wix/*.html`, `public/*.html`, `content/site-copy.json` (hand-authored copy).
- LEAVE (fix generator in Phase 2): `public/melodia/status/*.json` — contains `swarm`,
  `orchestrator_swe_light`, `hermes_harness` strings emitted by `Tools/health.py` /
  `run_math_eval.py`. They regenerate on deploy, so manual edits revert.

## Clean-pass acceptance

Step-2 grep returns ZERO hits in `wix/`, `public/`, `README.md`. `public/melodia/status/*.json`
hits are acceptable pending the generator fix. `grep -rln "old-name.html"` is empty (no broken links).
