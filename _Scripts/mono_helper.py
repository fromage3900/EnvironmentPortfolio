import json, urllib.request

URL = "http://localhost:9316/mcp"

def mono(tool, args):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
               "params": {"name": tool, "arguments": args}}
    req = urllib.request.Request(URL, json.dumps(payload).encode(),
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    content = resp.get("result", {}).get("content", [])
    texts = [c.get("text", "") for c in content if c.get("type") == "text"]
    raw = "\n".join(texts)
    try:
        return json.loads(raw)
    except Exception:
        return raw

if __name__ == "__main__":
    import sys
    tool = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    print(json.dumps(mono(tool, args), indent=1)[:6000])
