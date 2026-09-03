"""Standalone smoke test for the recommended local model fleet.

Tests the 2026-09-01 recommended fleet (granite4.2:3b, granite4.2:8b, muse-glimmer:30b)
with a bounded timeout so a large offloaded model cannot hang the runner.
"""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

OUT = Path(r"C:\EnvironmentPortfolio\logs\overnight\smoke_result.txt")
OUT.parent.mkdir(parents=True, exist_ok=True)

OLLAMA_CHAT_URL = os.environ.get("OLLAMA_CHAT_URL", "http://127.0.0.1:11434/api/chat")
# Models ordered from fastest/smallest to reasoner; timeout is per-model.
MODELS = ["granite4.2:3b", "granite4.2:8b", "muse-glimmer:30b"]
PER_MODEL_TIMEOUT = int(os.environ.get("SMOKE_TIMEOUT", "45"))

with OUT.open("w", encoding="utf-8") as out:
    for m in MODELS:
        body = json.dumps({
            "model": m,
            "messages": [{"role": "user", "content": "Reply with exactly OK"}],
            "stream": False,
        }).encode()
        req = urllib.request.Request(OLLAMA_CHAT_URL, data=body, headers={"Content-Type": "application/json"})
        try:
            r = urllib.request.urlopen(req, timeout=PER_MODEL_TIMEOUT)
            content = json.loads(r.read())
            msg = content.get("message", {}).get("content", "")[:40]
            out.write(f"{m} => {msg}\n")
        except urllib.error.HTTPError as e:
            out.write(f"{m} => HTTP {e.code} {e.read().decode()[:150]}\n")
        except Exception as e:
            out.write(f"{m} => ERR {str(e)[:150]}\n")
        out.flush()
    out.write("SMOKE_DONE\n")

