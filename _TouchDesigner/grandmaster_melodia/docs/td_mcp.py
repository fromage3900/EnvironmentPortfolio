#!/usr/bin/env python3
import json, sys, urllib.request, re

ENDPOINT = "http://127.0.0.1:9870/mcp"

def call(tool, args):
    payload = {
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": tool, "arguments": args}
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read().decode()
    # parse SSE: data: {...}
    data = None
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("data:"):
            data = json.loads(line[5:].strip())
    if data is None:
        return {"raw": raw}
    if "error" in data:
        return {"error": data["error"]}
    content = data.get("result", {}).get("content", [])
    texts = []
    for c in content:
        if c.get("type") == "text":
            t = c.get("text")
            # unwrap if the text is itself a JSON string
            try:
                texts.append(json.loads(t))
            except Exception:
                texts.append(t)
    return texts[0] if len(texts) == 1 else texts

if __name__ == "__main__":
    tool = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    print(json.dumps(call(tool, args)))
