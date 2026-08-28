import json, subprocess, sys, os

MCP = "http://127.0.0.1:9870/mcp"
_cmd = sys.argv[0]  # unused

def rpc(tool, args):
    payload = {"jsonrpc":"2.0","id":1,"method":"tools/call",
               "params":{"name":tool,"arguments":args}}
    p = subprocess.run(["curl","-s","-X","POST",MCP,
        "-H","Content-Type: application/json",
        "-H","Accept: application/json, text/event-stream",
        "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=30)
    out = p.stdout
    # strip SSE event lines and data: prefix
    txt = "\n".join(l[6:] for l in out.splitlines() if l.startswith("data: "))
    if not txt:
        txt = out
    try:
        obj = json.loads(txt)
    except Exception as e:
        return {"raw": out, "parse_error": str(e)}
    # unwrap result.content[0].text if present
    try:
        c = obj["result"]["content"]
        if isinstance(c, list) and c and isinstance(c[0].get("text"), str):
            inner = c[0]["text"]
            try:
                return json.loads(inner)
            except Exception:
                return {"_raw_text": inner}
    except Exception:
        pass
    return obj

if __name__ == "__main__":
    tool = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    res = rpc(tool, args)
    print(json.dumps(res, indent=2, default=str)[:6000])
