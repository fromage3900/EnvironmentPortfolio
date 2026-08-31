# Best / Lightest / Fastest Local Models for the Melodia Pipeline — 2026-09-01

Researched 2026-09-01 from Ollama's current catalog, model pages (Meta, NVIDIA, IBM,
Z.ai, Google/Qwen), and Artificial Analysis. All figures are the vendors'/Ollama's
published specs.

## 0. Hardware anchor (confirmed)
- **GPU:** NVIDIA GeForce RTX 4070 SUPER — **12,282 MiB** VRAM
- **Ollama:** v0.33.1 | **Model store:** `F:\OllamaModels`
- Currently installed: **`qwen3-coder:30b` (18 GB, dense)**

### The key constraint
On a 12 GB card, **dense 30B models do not fit** — they spill to CPU/system RAM. That is
exactly the failure we fixed; health hung for 15 min and the GPU pegged at 100% while the
30B offloaded. Any "fast + always-on" plan must prefer models that (a) fit fully in VRAM,
or (b) are **MoE with few active parameters** so per-token compute stays small even when
weights are partially offloaded.

---

## 1. The candidates that matter (as of Sept 1)

| Model | Size (GGUF) | Active params | Architect | Ctx | Tools | Thinking | Notes |
|---|---|---|---|---|---|---|---|
| **granite4.2:8b** | 5.3 GB | 8B (dense) | Dense | 128K | ✅ | ✅ | **Structured JSON output** is a headline feature |
| **granite4.2:3b** | 2.2 GB | 3B (dense) | Dense | 128K | ✅ | ✅ | Ultra-light; cheapest latency per AA |
| **gemma4:12b** | 7.6 GB | 12B (dense) | Dense | 256K | ✅ | ✅ | Fits fully in VRAM; reasoning/agentic/coding |
| **gemma4:e4b** | 9.6 GB | 4.5B eff | MoE | 128K | ✅ | ✅ | Small-active, on-device optimized |
| **nemotron-3.5-lightning** | 25 GB | **3B active** | MoE (30B tot.) | 1M | ✅ | ✅ | Built for **always-on agents**; 4× throughput |
| **muse-glimmer:30b** | 18 GB | 30B (dense) | Dense | 128K | ✅ | ✅ | **Tool use, long tasks, failure recovery**; Apache 2.0 |
| **qwen3.8:27b** | 18 GB | 27B (dense) | Dense | 256K | ✅ | ✅ | Successor to current qwen3-coder; +vision |
| qwen3.8-flash-next | 105 GB | 6B active | MoE (125B) | 256K | ✅ | ✅ | Too big for 12 GB — skip |
| glm-5.3-flash | cloud | 18B active | MoE (321B) | 1M | ✅ | ✅ | **Cloud-only tag** now; not a local 12 GB fit |

---

## 2. What this project actually needs (drives the pick)

The overnight daemon is **always-on**, does **repeated structured output**, and must not
jam the GPU (the exact bug we hit). Lanes produce **JSON** (content/research/toolchain),
call **tools**, and need **failure recovery** (quarantine → retry). Secondary: blueprint /
hython / shader **coding**, and research prose.

So the required capabilities in priority order:
1. **Fast tokens/sec + low latency** (daemon runs every 15 min / every night)
2. **Reliable structured JSON output**
3. **Reliable tool / function calling**
4. **Failure recovery** (retry on tool errors)
5. Good coding for the hython/blueprint scaffolding
---

## 3. Recommendation: a 2–3 tier "worker + reasoner" model fleet

No single model wins all five goals on 12 GB; the right answer is a **layered fleet**
mapped to lane type. All are Apache-2.0 or permissive (no commercial restriction).

### Tier A — Fast worker (structured JSON output). *Fully fits in VRAM → fast.*
- **`granite4.2:8b` (5.3 GB)** — the daemon's day-to-day **worker**. Structured JSON output
  and tool use are its literal design goals; 128K ctx; thinking is toggleable. Fits the 12 GB
  card entirely → no offload stall, high tokens/sec. Use for: content, research summaries,
  toolchain briefs, and the **health smoke test** (this is the model that stops the 15-min hang).
- **`granite4.2:3b` (2.2 GB)** as the ultra-fast micro-tier for health pings / parsing.

### Tier B — Reasoner / full agent (tool use + failure recovery). *Swap-in for current 30b.*
- **`muse-glimmer:30b` (18 GB)** — **this is the model the project already points to**
  (`muse-glimmer-30b` in `Docs/LOCAL_HF_MODELS.md`). It is Meta's **always-on local agent**
  model: reliable tool use, multi-step reasoning, **failure recovery** (diagnoses + retries),
  multimodal. It outperforms Gemma4-31B and Qwen3.6-27B on agentic benchmarks (MCP-Atlas,
  DeepSearch QA, SWE-bench). **Same 18 GB footprint as the current `qwen3-coder:30b`** → direct
  drop-in upgrade for the complex/tool lanes.
  - **Bonus:** it's now a plain `ollama pull muse-glimmer` GGUF — the whole `G:\AI\Models`
    transformer-download + pagefile-fix path for Muse-Glimmer is **no longer needed.**

### Tier C — Speed king for the always-on loop (optional, if tokens/sec dominates).
- **`nemotron-3.5-lightning` (30B total / 3B active, 25 GB)** — NVIDIA's always-on-agent MoE.
  ~4× throughput, built for harnesses like this daemon. Larger footprint but tiny active
  compute → very fast on 12 GB. Best if the daemon loop must churn many short generations.

### Comparison vs. the current model
| Goal | `qwen3-coder:30b` (now) | `granite4.2:8b` | `muse-glimmer:30b` |
|---|---|---|---|
| Fits 12 GB (no offload) | ❌ (offloads, slow) | ✅ | ❌ (offloads, moderate) |
| Speed | slow | **fast** | moderate |
| Structured JSON | ok | **native / best** | ok |
| Tool calling | ✅ | ✅ | **best (failure recovery)** |
| Coding | ✅ | good | **good + agentic** |
| Config (disk) | 18 GB | 5.3 GB | 18 GB |

---

## 4. Concrete plan (if you approve)

```pwsh
# pull the fleet
ollama pull granite4.2:3b      # ultra-fast health/ping worker
ollama pull granite4.2:8b      # fast JSON worker (daemon worker tier)
ollama pull muse-glimmer:30b   # agent/reasoner tier (replaces qwen3-coder:30b)

# daemon: route lanes by tier
#   health smoke    -> granite4.2:3b  (instant, no hang)
#   content/research/toolchain JSON -> granite4.2:8b  (fast structured output)
#   hython/blueprint coding, complex tool lanes -> muse-glimmer:30b
```

Then update `scripts/overnight_daemon.py` `QWEN_MODEL_CHAIN` and per-lane model selection
to use the tiered fleet, and re-run the health lane to confirm it stays green with an instant
smoke test.

---

## 5. Also worth knowing
- **`qwen3.8:27b`** is the direct successor to the installed `qwen3-coder:30b` — same 18 GB
  footprint, better coding/research/agentic + vision + thinking control. A fine drop-in if
  you want to stay on Qwen rather than move to Granite/Muse.
- **`qwen3.8-flash-next` (125B/6B active)** is architecturally impressive but 105 GB GGUF —
  not a 12 GB local fit; watch for smaller quantizations later.
- **`glm-5.3-flash`** (18B active, ~Claude Opus 4.8 coding) is currently **cloud-only** on
  Ollama — not for this fully-local 12 GB setup.
- **HF transformer ecosystem:** with `muse-glimmer` and `qwen3.8` now available as local
  ollama GGUFs, the heavy HF/`:8000` server path (54 GB downloads + 100 GB pagefile) can be
  retired in favor of the much lighter ollama route.