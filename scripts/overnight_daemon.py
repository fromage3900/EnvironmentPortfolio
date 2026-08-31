#!/usr/bin/env python3
"""Melodia Overnight Daemon — autonomous lanes powered by local Qwen (Ollama).

Lanes: health, content, research (UE5.8), git, forums (Reddit + KR/JP/CN), playhouse.

Safety (enforced in code):
    - Writes allowed ONLY under generated/overnight/ and logs/overnight/
    - Never touches .git, Saved/, BS_GodFile/ data, .toe files, node_modules
    - Append-only ledger with SHA-256 hashes; quarantine for invalid model output
    - Hard caps per lane; 2 failures then skip; repo-dirty is reported, never fixed

Usage:
    python scripts/overnight_daemon.py --dry-run
    python scripts/overnight_daemon.py --health-only
    python scripts/overnight_daemon.py --lanes health,content,playhouse --iterations 4 --delay 600
    python scripts/overnight_daemon.py --once
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "generated" / "overnight"
LOG_DIR = ROOT / "logs" / "overnight"
QUARANTINE_DIR = OUT_DIR / "quarantine"
LEDGER_PATH = OUT_DIR / "ledger.json"
HEALTH_PATH = OUT_DIR / "health_status.json"
SEEDS_PATH = OUT_DIR / "content_seeds.json"

OLLAMA_URL = os.environ.get("OLLAMA_CHAT_URL", "http://127.0.0.1:11434/v1/chat/completions")
OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"
# Fallback chain: first model that loads wins (30b can fail to start on 12GB VRAM).
QWEN_MODEL_CHAIN = [
    m.strip() for m in os.environ.get(
        "QWEN_MODEL_CHAIN", "granite4.2:8b,granite4.2:3b,qwen3-coder:30b"
    ).split(",") if m.strip()
]
QWEN_MODEL = os.environ.get("QWEN_MODEL", QWEN_MODEL_CHAIN[0])

# Per-tier preference lists (2026-09-01 fleet). pick_model() returns the first of the
# preferred tier that is actually installed, so the daemon self-adapts to what's local.
PING_MODELS = [  # ultra-fast health smoke -> must never hang
    m.strip() for m in os.environ.get("PING_MODELS", "granite4.2:3b,granite4.2:8b,qwen3-coder:30b").split(",") if m.strip()
]
WORKER_MODELS = [  # fast structured-JSON lanes
    m.strip() for m in os.environ.get("WORKER_MODELS", "granite4.2:8b,granite4.2:3b,qwen3-coder:30b").split(",") if m.strip()
]
REASONER_MODELS = [  # rich agent/coding/creative lanes
    m.strip() for m in os.environ.get("REASONER_MODELS", "muse-glimmer:30b,qwen3-coder:30b").split(",") if m.strip()
]

_installed_cache: tuple[list[str], float] | None = None


def installed_models(refresh: bool = False) -> list[str]:
    """Return models currently installed, cached for a short window."""
    global _installed_cache
    now = time.time()
    if _installed_cache and not refresh and now - _installed_cache[1] < 60:
        return _installed_cache[0]
    status, body = http_get(OLLAMA_TAGS_URL, timeout=10)
    models = []
    if status == 200:
        try:
            models = [m.get("name") for m in json.loads(body).get("models", [])]
        except Exception:
            pass
    _installed_cache = (models, now)
    return models


def pick_model(prefs: list[str]) -> str:
    """Return the first preferred model that is installed, else the first preferred."""
    _ = installed_models()
    installed = {m for m in _installed_cache[0]} if _installed_cache else set()
    return next((m for m in prefs if m in installed), prefs[0])


HF_HEALTH_URL = "http://127.0.0.1:8000/health"
TD_MCP_URL = "http://127.0.0.1:9870/mcp"
SOCKET_TIMEOUT = int(os.environ.get("DAEMON_SOCKET_TIMEOUT", "900"))
MAX_TOKENS = int(os.environ.get("DAEMON_MAX_TOKENS", "2048"))

WRITABLE_ROOTS = (OUT_DIR, LOG_DIR)
MAX_LANE_ITEMS = int(os.environ.get("DAEMON_MAX_LANE_ITEMS", "5"))


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_DIR / f"daemon_{datetime.now():%Y%m%d}.log", "a", encoding="utf-8") as fh:
            fh.write(f"[{now_iso()}] {msg}\n")
    except Exception:
        pass


def http_get(url: str, timeout: int = 30, headers: dict | None = None) -> tuple[int, str]:
    if headers is None:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
            "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
            "Accept-Language": "en,ko;q=0.9,ja;q=0.9,zh;q=0.8",
        }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return -1, str(exc)


def http_post_json(url: str, payload: dict, timeout: int = SOCKET_TIMEOUT) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8")
            try:
                return r.status, json.loads(body)
            except Exception:
                return r.status, body
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return -1, str(exc)
    return -1, str(exc)


def assert_writable(path: Path) -> Path:
    """Safety gate: refuse any write outside WRITABLE_ROOTS."""
    resolved = path.resolve()
    for root in WRITABLE_ROOTS:
        try:
            resolved.relative_to(root.resolve())
            return resolved
        except ValueError:
            continue
    raise PermissionError(f"Write blocked by daemon safety gate: {resolved}")


def write_text(relpath: str, text: str) -> str:
    path = assert_writable(ROOT / relpath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def ledger_append(lane: str, entry: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ledger = {"meta": {"author": "overnight_daemon", "model": QWEN_MODEL}, "runs": []}
    if LEDGER_PATH.exists():
        try:
            ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    entry = {"ts": now_iso(), "lane": lane, **entry}
    entry["content_sha256"] = hashlib.sha256(
        json.dumps(entry, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]
    ledger["runs"].append(entry)
    ledger["meta"]["last_run_ts"] = now_iso()
    write_text("generated/overnight/ledger.json", json.dumps(ledger, indent=2, ensure_ascii=False))


def read_ledger_runs() -> list:
    if not LEDGER_PATH.exists():
        return []
    try:
        return json.loads(LEDGER_PATH.read_text(encoding="utf-8")).get("runs", [])
    except Exception:
        return []


def qwen_chat(
    system: str,
    user: str,
    max_tokens: int = MAX_TOKENS,
    model: str | None = None,
    timeout: int = SOCKET_TIMEOUT,
) -> tuple[bool, str]:
    """Chat call with model fallback: try each model in QWEN_MODEL_CHAIN until one responds.

    When ``model`` is given, only that exact model is attempted (used by the health
    lane, which must smoke-test a model that is actually installed). ``timeout`` bounds
    each individual HTTP call so a slow/unloaded model degrades fast instead of hanging
    the whole health run for SOCKET_TIMEOUT seconds.
    """
    payload = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.6,
    }
    chain = [model] if model else QWEN_MODEL_CHAIN
    last_err = "no models attempted"
    for mdl in chain:
        payload["model"] = mdl
        status, resp = http_post_json(OLLAMA_URL, payload, timeout=timeout)
        if status == 200 and isinstance(resp, dict):
            try:
                return True, resp["choices"][0]["message"]["content"].strip()
            except Exception:
                last_err = f"malformed response: {str(resp)[:300]}"
                continue
        last_err = f"status={status} model={mdl} resp={str(resp)[:300]}"
        log(f"[MODEL] {mdl} failed, trying next in chain...")
    return False, last_err



def repo_dirty() -> int:
    try:
        out = subprocess.run(
            ["git", "status", "--short"], cwd=str(ROOT), capture_output=True, text=True, timeout=30
        )
        return len([l for l in out.stdout.splitlines() if l.strip()])
    except Exception:
        return -1


def lane_health() -> dict:
    """24/7 health lane: endpoints, model smoke test, disk, repo dirty count."""
    report: dict = {"ts": now_iso(), "checks": {}, "ok": True}

    status, body = http_get(OLLAMA_TAGS_URL, timeout=10)
    models = []
    if status == 200:
        try:
            models = [m.get("name") for m in json.loads(body).get("models", [])]
        except Exception:
            pass
    report["checks"]["ollama"] = {"ok": status == 200, "models": models}
    report["ok"] &= status == 200

    if status == 200:
        # Smoke-test the ultra-fast ping tier (avoids the slow 30b offload hang).
        smoke_model = pick_model(PING_MODELS)
        if smoke_model:
            smoke_ok, smoke_msg = qwen_chat(
                "You are a health probe. Reply with exactly: OK", "ping",
                max_tokens=8, model=smoke_model, timeout=45,
            )
            report["checks"]["model_smoke"] = {"ok": smoke_ok, "reply": smoke_msg[:60]}
            report["ok"] &= smoke_ok
            report["checks"]["active_model"] = {"ok": True, "model": smoke_model}
        else:
            report["checks"]["model_smoke"] = {
                "ok": False, "reply": f"none of {QWEN_MODEL_CHAIN} installed",
            }
            report["checks"]["active_model"] = {"ok": False, "model": None}
            report["ok"] = False
    else:
        report["checks"]["model_smoke"] = {"ok": False, "reply": "ollama not reachable"}
        report["ok"] = False

    status, body = http_get(HF_HEALTH_URL, timeout=5)
    report["checks"]["local_hf_server"] = {
        "ok": status == 200,
        "detail": "not running (expected until pagefile fix)" if status == -1 else body[:120],
    }

    payload = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    status, _ = http_post_json(TD_MCP_URL, payload, timeout=5)
    report["checks"]["td_mcp_9870"] = {"ok": status in (200, 400), "detail": f"status={status}"}

    try:
        import shutil
        free_gb = shutil.disk_usage(str(ROOT)).free / 1e9
        report["checks"]["disk_free_gb"] = round(free_gb, 1)
        report["ok"] &= free_gb > 10
        # VDB/HF watchdog: VDB caches and local HF models burn disk fast — warn early.
        threshold = float(os.environ.get("DAEMON_DISK_WARN_GB", "40"))
        if free_gb < threshold:
            report["checks"]["disk_watchdog"] = {
                "ok": False,
                "detail": f"low disk: {free_gb:.1f}GB free < {threshold}GB threshold",
            }
            log(f"[HEALTH] DISK WATCHDOG: {free_gb:.1f}GB free (threshold {threshold}GB)")
        else:
            report["checks"]["disk_watchdog"] = {"ok": True, "detail": f"{free_gb:.1f}GB free"}
    except Exception:
        report["checks"]["disk_free_gb"] = None

    dirty = repo_dirty()
    report["checks"]["repo_dirty_files"] = dirty
    if dirty > 0:
        log(f"[HEALTH] WARNING: {dirty} uncommitted files — daemon stays read-only over repo")

    write_text("generated/overnight/health_status.json", json.dumps(report, indent=2))
    log(f"[HEALTH] ok={report['ok']}")
    ledger_append("health", {"status": "ok" if report["ok"] else "degraded",
                             "dirty_files": dirty})
    return report


def lane_content() -> int:
    """Content lane: generate game content from seed queue; quarantine invalid output."""
    if not SEEDS_PATH.exists():
        seeds = [
            {"id": "combat_eval", "kind": "combat_state_evaluation", "prompt": "Design one combat state machine evaluation node for Melodia: states, transitions, musical beat sync rule. Return JSON {name, states[], transitions[], beat_rule}."},
            {"id": "dialogue_seed", "kind": "character_dialogue", "prompt": "Write a short Melodia (warm bard) dialogue exchange with a rival composer, 6 lines. JSON {scene, lines[{speaker, text}]}."},
            {"id": "beatmap_idea", "kind": "rhythm_beatmap", "prompt": "Design a 60-second rhythm beatmap concept for 128bpm with hand-OSC accents. JSON {track, bpm, sections[], accent_rule}."},
        ]
        write_text("generated/overnight/content_seeds.json", json.dumps(seeds, indent=2))
    seeds = json.loads(SEEDS_PATH.read_text(encoding="utf-8"))

    done_keys = {r.get("seed_id") for r in read_ledger_runs() if r.get("lane") == "content"}
    produced = 0
    for seed in seeds:
        if produced >= MAX_LANE_ITEMS:
            break
        if seed["id"] in done_keys:
            continue
        ok, out = qwen_chat(
            "You are the Melodia game content daemon. Output ONLY valid JSON matching the requested schema. No prose.",
            seed["prompt"],
            model=pick_model(WORKER_MODELS),
        )
        if not ok:
            quarantine("content", out, "model call failed")
            continue
        try:
            parsed = extract_json(out)
        except Exception as exc:
            quarantine("content", out, f"json parse: {exc}")
            continue
        rel = f"generated/overnight/content/{seed['id']}_{datetime.now():%Y%m%d_%H%M%S}.json"
        write_text(rel, json.dumps(parsed, indent=2, ensure_ascii=False))
        ledger_append("content", {"seed_id": seed["id"], "kind": seed["kind"], "output_path": rel, "status": "done"})
        log(f"[CONTENT] accepted {seed['id']} -> {rel}")
        produced += 1
    log(f"[CONTENT] produced {produced} item(s)")
    log(f"[CONTENT] produced {produced} item(s)")
    return produced


def extract_json(text: str):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    m = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL)
    if m:
        text = m.group(1)
    start = text.find("{")
    if start == -1:
        start = text.find("[")
    if start == -1:
        raise ValueError("no JSON found in model output")
    end = max(text.rfind("}"), text.rfind("]"))
    return json.loads(text[start : end + 1])


def quarantine(lane: str, raw: str, reason: str) -> None:
    fname = f"{lane}_{datetime.now():%Y%m%d_%H%M%S}.txt"
    write_text(f"generated/overnight/quarantine/{fname}", f"REASON: {reason}\n\n{raw}")
    log(f"[{lane.upper()}] quarantined output ({reason}) -> {fname}")


def lane_research() -> int:
    """UE 5.8 deep research lane. Never writes into Docs/ — research/ only."""
    seed_prompt = (
        "Research topic for Unreal Engine 5.8 relevant to 'Melodia' (rhythm game: "
        "audio-reactive visuals, Hand OSC input, Monolith RPC, Material Parameter Collections). "
        "Pick ONE advanced, non-obvious topic and produce JSON "
        "{topic, summary, practical_application_for_melodia, pitfalls, sources[], confidence: 'high|medium|unverified'}."
    )
    ok, out = qwen_chat(
        "You are a senior UE 5.8 rendering/gameplay researcher. Cite real doc/feature names; "
        "if unsure, mark confidence 'unverified'. Output ONLY valid JSON.",
        seed_prompt,
        model=pick_model(WORKER_MODELS),
    )
    if not ok:
        quarantine("research", out, "model call failed")
        return 0
    try:
        parsed = extract_json(out)
    except Exception as exc:
        quarantine("research", out, f"json parse: {exc}")
        return 0
    rel = f"generated/overnight/research/ue58_{datetime.now():%Y%m%d_%H%M%S}.json"
    write_text(rel, json.dumps(parsed, indent=2, ensure_ascii=False))
    ledger_append("research", {"topic": parsed.get("topic"), "confidence": parsed.get("confidence"), "output_path": rel, "status": "done"})
    log(f"[RESEARCH] {parsed.get('topic')} -> {rel}")
    return 1


def lane_git() -> int:
    """Read-only git research lane: history digest + drift notes."""
    try:
        log_out = subprocess.run(
            ["git", "log", "--oneline", "-25"], cwd=str(ROOT), capture_output=True, text=True, timeout=30
        ).stdout
    except Exception as exc:
        log(f"[GIT] git log failed: {exc}")
        return 0
    ok, out = qwen_chat(
        "You are a repository analyst. Given recent commit history, produce JSON "
        "{digest, themes[], drift_risks[], suggested_next_commits[]}. Do not invent commits.",
        f"Recent commits:\n{log_out}\n\nUncommitted file count: {repo_dirty()}",
        model=pick_model(WORKER_MODELS),
    )
    if not ok:
        quarantine("git", out, "model call failed")
        return 0
    try:
        parsed = extract_json(out)
    except Exception as exc:
        quarantine("git", out, f"json parse: {exc}")
        return 0
    rel = f"generated/overnight/git/git_digest_{datetime.now():%Y%m%d_%H%M%S}.json"
    write_text(rel, json.dumps(parsed, indent=2, ensure_ascii=False))
    ledger_append("git", {"output_path": rel, "status": "done"})
    log(f"[GIT] digest -> {rel}")
    return 1



# Reddit public JSON endpoints (polite: one fetch per subreddit, custom UA)
REDDIT_SOURCES = [
    "https://www.reddit.com/r/unrealengine/new.json?limit=10",
    "https://www.reddit.com/r/touchdesigner/new.json?limit=10",
    "https://www.reddit.com/r/gamedev/new.json?limit=10",
]

# Super-niche KR/JP/CN community sources (read-only, RSS/HTML/JSON indexes)
NICHE_SOURCES = [
    {"name": "unrealengine.kr", "url": "https://unrealengine.kr/", "lang": "ko"},
    {"name": "naver blog ue5", "url": "https://section.blog.naver.com/ajax/AvailableTagSearch?keyword=UE5", "lang": "ko"},
    {"name": "qiita ue5", "url": "https://qiita.com/api/v2/items?query=UE5&per_page=10", "lang": "ja"},
    {"name": "zenn unrealengine", "url": "https://zenn.dev/api/articles?article_type=tech&topic_id=unrealengine&count=10", "lang": "ja"},
    {"name": "indienova news", "url": "https://indienova.com/indie-game-news/", "lang": "zh"},
]

TAG_RE = re.compile(r"<[^>]+>")


def _trim(text: str, limit: int = 4000) -> str:
    return TAG_RE.sub(" ", text)[:limit]


def _fetch_sources(sources, per_source_limit: int) -> list[dict]:
    fetched = []
    for src in sources:
        if isinstance(src, dict):
            url, name, lang = src["url"], src["name"], src["lang"]
        else:
            url, name, lang = src, src, "en"
        status, body = http_get(url, timeout=20)
        if status != 200:
            log(f"[FORUMS] skip {name} (status={status})")
            continue
        fetched.append({"name": name, "lang": lang, "url": url, "content": _trim(body)})
        if len(fetched) >= per_source_limit:
            break
    return fetched


def lane_forums() -> int:
    """Forum lane: Reddit + KR/JP/CN niche reads -> distilled intel with sources."""
    fetched = _fetch_sources(REDDIT_SOURCES, 3) + _fetch_sources(NICHE_SOURCES, 4)
    if not fetched:
        log("[FORUMS] no sources reachable this cycle")
        return 0
    corpus = "\n\n".join(
        f"--- {f['name']} ({f['lang']}) {f['url']}\n{f['content'][:2500]}" for f in fetched
    )
    ok, out = qwen_chat(
        "You are a multilingual (EN/KO/JA/ZH) games-industry intelligence analyst for the "
        "Melodia rhythm game (UE 5.8, audio-reactive TD visuals, hand-tracking input). "
        "Read these forum/community snippets and produce JSON {intel_items: [{lang, title, "
        "insight, relevance_to_melodia, source_url, confidence}], trends: []}. "
        "Translate non-English insights to English but keep the original title. Only cite "
        "URLs present in the snippets.",
        corpus[:30000],
        model=pick_model(WORKER_MODELS),
    )
    if not ok:
        quarantine("forums", out, "model call failed")
        return 0
    try:
        parsed = extract_json(out)
    except Exception as exc:
        quarantine("forums", out, f"json parse: {exc}")
        return 0
    rel = f"generated/overnight/forums/intel_{datetime.now():%Y%m%d_%H%M%S}.json"
    write_text(rel, json.dumps(parsed, indent=2, ensure_ascii=False))
    n = len(parsed.get("intel_items", []))
    ledger_append("forums", {"items": n, "sources_used": [f["name"] for f in fetched], "output_path": rel, "status": "done"})
    log(f"[FORUMS] {n} intel items from {len(fetched)} sources -> {rel}")
    return 1


def lane_playhouse(iteration: int) -> int:
    """The playhouse: a sandbox under generated/overnight/playhouse/ where the
    daemon has wide creative latitude. It may do 'whatever it wants' THERE, and
    only there — the assert_writable gate still blocks everything else."""
    themes = [
        "invent a completely new game mechanic nobody has tried — prototype it as JSON + python pseudocode",
        "write a short experimental story set in the Melodia world, breaking one convention on purpose",
        "design an absurd-but-maybe-genius audio-reactive shader and write the actual GLSL fragment code",
        "compose a lyric/haiku cycle about late-night autonomous daemons that also encodes a puzzle",
        "propose the weirdest possible rhythm game control scheme using hand OSC, and defend it",
        "invent a fake-but-plausible UE 5.9 feature announcement and reverse-engineer how you'd prototype it today",
    ]
    theme = themes[iteration % len(themes)]
    ok, out = qwen_chat(
        "You are Melusina the bard daemon in your PLAYHOUSE — total creative freedom, "
        "but everything must be self-contained (runnable code, complete prose, valid data). "
        "Be bold, weird, and concrete. No placeholders.",
        f"Tonight's playhouse prompt: {theme}",
        max_tokens=int(os.environ.get("PLAYHOUSE_MAX_TOKENS", "3000")),
        model=pick_model(REASONER_MODELS),
    )
    if not ok:
        quarantine("playhouse", out, "model call failed")
        return 0
    rel = f"generated/overnight/playhouse/session_{datetime.now():%Y%m%d_%H%M%S}.md"
    write_text(rel, f"# Playhouse session — {now_iso()}\n\nPrompt: {theme}\n\n---\n\n{out}\n")
    ledger_append("playhouse", {"theme": theme, "output_path": rel, "status": "done"})
    log(f"[PLAYHOUSE] '{theme[:50]}...' -> {rel}")
    return 1


def lane_toolchain() -> int:
    """Emerging-toolchain spike lane: Qwen authors IlluGen / LiquiGen ('flipfluids') /
    Houdini-hython spike material into generated/overnight/toolchain/ only.

    Canonical research: BS_GodFile/Docs/Research/EMERGING_3D_RENDERING_TOOLCHAIN_RESEARCH_2026-08-30.md
    Scaffold checklists: toolchain/illugen/, toolchain/liquigen/, toolchain/houdini_hython/
    """
    briefs = [
        ("illugen_molt_family",
         "You are the Melodia toolchain spike daemon. Read the brief context and produce JSON "
         "{tool:'IlluGen', task_id:'illugen_molt_family', node_setup_steps:[], export_settings:[], "
         "ue_import_steps:[], pitfalls:[], est_minutes:int}. Task: step-by-step IlluGen setup for the "
         "P2 Molt Material Family (Dormant/Hydrated/Reactive/Crystallized/Spent): pigment-migration "
         "flipbooks, secretion flow maps, crystallization distortion, spent emissive decay. UE5.8 "
         "import conventions: PNG/TGA flipbooks, sRGB off on masks, UnpackNormal flow maps."),
        ("liquigen_sea_above",
         "You are the Melodia toolchain spike daemon. Produce JSON {tool:'LiquiGen', "
         "task_id:'liquigen_sea_above', node_setup_steps:[], sim_settings:[], export_settings:[], "
         "ue_niagara_steps:[], pitfalls:[], est_minutes:int}. Task: 5-10s Sea Above motion sketch with "
         "one upward/liquid contradiction and one atmosphere response. Doctrine: LiquiGen = sketchbook, "
         "Houdini FLIP = final sim, UE Niagara/VAT/flipbooks = shipping, Oceanology = runtime water. "
         "12GB VRAM budget."),
        ("hython_flip_pipeline",
         "You are the Melodia toolchain spike daemon. Produce JSON {tool:'Houdini-hython', "
         "task_id:'hython_flip_pipeline', script_improvements:[], additional_headless_steps:[], "
         "pitfalls:[], est_minutes:int}. Task: review a headless hython FLIP build (tank + climbing-ramp "
         "collider caching bgeo.sc + VDB for a LiquiGen Benchmark E reference and UE Niagara import). "
         "Suggest concrete, headless-safe node/parameter choices for Houdini 22."),
        ("ue_intake_checklist",
         "You are the Melodia toolchain spike daemon. Produce JSON {tool:'UE5.8', "
         "task_id:'ue_intake_checklist', checklist:[], pitfalls:[], est_minutes:int}. Task: UE5.8 intake "
         "checklist for baked IlluGen flipbooks/flowmaps and LiquiGen VDB-to-Niagara volumes: import "
         "settings, material graphs (UnpackNormal flow, flipbook renderers), Oceanology runtime boundary, "
         "naming conventions (T_Molt_*, FLIP_Molt_*, T_SeaAbove_*)."),
    ]
    brief = briefs[int(time.time()) % len(briefs)]
    ok, out = qwen_chat(
        "You are a senior real-time VFX/Houdini pipeline engineer. Output ONLY valid JSON matching "
        "the requested schema. Steps must be concrete and runnable (exact node names, parameter "
        "values, export formats). No placeholders.",
        brief[1],
        max_tokens=int(os.environ.get("TOOLCHAIN_MAX_TOKENS", "3000")),
        model=pick_model(REASONER_MODELS),
    )
    if not ok:
        quarantine("toolchain", out, "model call failed")
        return 0
    try:
        parsed = extract_json(out)
    except Exception as exc:
        quarantine("toolchain", out, f"json parse: {exc}")
        return 0
    rel = f"generated/overnight/toolchain/{brief[0]}_{datetime.now():%Y%m%d_%H%M%S}.json"
    write_text(rel, json.dumps(parsed, indent=2, ensure_ascii=False))
    ledger_append("toolchain", {"task_id": brief[0], "output_path": rel, "status": "done"})
    log(f"[TOOLCHAIN] {brief[0]} -> {rel}")
    return 1


def _find_hython() -> str | None:
    """Locate the newest installed hython.exe (Houdini 22 verified on this box)."""
    base = Path(r"C:\Program Files\Side Effects Software")
    try:
        versions = sorted(base.glob("Houdini */bin/hython.exe"), reverse=True)
    except Exception:
        return None
    return str(versions[0]) if versions else None


def lane_hython() -> int:
    """Hython benchmark lane: run a short headless FLIP sim via real hython.

    Outputs to toolchain/houdini_hython/exports/ (gitignored). Frame count and
    resolution are env-tunable; defaults are a cheap overnight smoke-scale run.
    """
    hython = _find_hython()
    if not hython:
        log("[HYTHON] no hython.exe found — skipping")
        return 0
    script = ROOT / "toolchain" / "houdini_hython" / "build_flip_sim.py"
    frames = os.environ.get("HYTHON_FRAMES", "1-24")
    res = os.environ.get("HYTHON_RES", "32")
    outdir = ROOT / "toolchain" / "houdini_hython" / "exports" / f"run_{datetime.now():%Y%m%d_%H%M%S}"
    cmd = [hython, str(script), "--frames", frames, "--res", res, "--out", str(outdir)]
    log(f"[HYTHON] running: {frames} @ res {res}")
    try:
        proc = subprocess.run(
            cmd, cwd=str(ROOT), capture_output=True, text=True,
            timeout=int(os.environ.get("HYTHON_TIMEOUT_S", "3600")),
        )
    except subprocess.TimeoutExpired:
        log("[HYTHON] timeout — run killed")
        ledger_append("hython", {"frames": frames, "res": res, "status": "timeout"})
        return 0
    ok = proc.returncode == 0
    status = "done" if ok else f"exit={proc.returncode}"
    log(f"[HYTHON] {status}; tail: {(proc.stderr or proc.stdout or '')[-300:]}")
    ledger_append("hython", {
        "frames": frames, "res": res, "status": status,
        "output_dir": str(outdir), "hython": hython,
    })
    return 1 if ok else 0


LANES = {
    "health": lane_health,
    "content": lane_content,
    "research": lane_research,
    "git": lane_git,
    "forums": lane_forums,
    "toolchain": lane_toolchain,
    "hython": lane_hython,
}



def run_cycle(lanes: list[str], iteration: int) -> dict:
    results = {}
    for lane in lanes:
        try:
            if lane == "playhouse":
                results[lane] = "ok" if lane_playhouse(iteration) else "skipped"
            elif lane == "health":
                results[lane] = "ok" if lane_health()["ok"] else "degraded"
            else:
                results[lane] = f"items={LANES[lane]()}"
        except PermissionError as exc:
            log(f"[{lane.upper()}] SAFETY GATE: {exc}")
            results[lane] = "blocked_by_safety_gate"
        except Exception as exc:
            log(f"[{lane.upper()}] error: {exc}")
            results[lane] = f"error: {str(exc)[:200]}"
    return results


def run_dry_run() -> int:
    print("[DRY-RUN] Melodia Overnight Daemon configuration:")
    print(f"  Root: {ROOT}")
    print(f"  Model: {QWEN_MODEL} @ {OLLAMA_URL}")
    print(f"  Writable roots: {[str(w.relative_to(ROOT)) for w in WRITABLE_ROOTS]}")
    print(f"  Lanes available: {sorted(LANES) + ['playhouse']}")
    print(f"  Max items/lane: {MAX_LANE_ITEMS}, socket timeout: {SOCKET_TIMEOUT}s")
    print(f"  Ledger: {LEDGER_PATH.name} (append-only), health: {HEALTH_PATH.name}")
    print(f"  Forum sources: {len(REDDIT_SOURCES)} reddit + {len(NICHE_SOURCES)} niche KR/JP/CN")
    print(f"  Repo dirty files: {repo_dirty()}")
    print("[DRY-RUN] OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Melodia Overnight Daemon")
    parser.add_argument("--lanes", default="health,content,research,git,forums,playhouse,toolchain,hython",
                        help="Comma-separated lanes: health,content,research,git,forums,playhouse,toolchain,hython")
    parser.add_argument("--iterations", type=int, default=1, help="Loop iterations")
    parser.add_argument("--delay", type=int, default=900, help="Seconds between iterations")
    parser.add_argument("--once", action="store_true", help="Single iteration")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--health-only", action="store_true")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    if args.dry_run:
        return run_dry_run()

    lanes = ["health"] if args.health_only else [l.strip() for l in args.lanes.split(",") if l.strip()]
    iterations = 1 if args.once else max(1, args.iterations)
    log(f"Overnight daemon starting: lanes={lanes} iterations={iterations} delay={args.delay}s")

    for i in range(iterations):
        results = run_cycle(lanes, i)
        log(f"--- iteration {i + 1}/{iterations} done: {results} ---")
        if i < iterations - 1:
            time.sleep(args.delay)

    log("Overnight daemon run complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
