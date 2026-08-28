#!/usr/bin/env python3
"""Minimal TD MCP client helper. Usage:
  python mcp_call.py <tool> '<json-args>' [--raw]
Prints the tool result text. Wraps tools/call correctly.
"""
import json, sys, urllib.request

ENDPOINT = "http://127.0.0.1:9870/mcp"

def call(tool, args):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": args},
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode()
    # strip SSE event/data framing
    text = None
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("data:"):
            text = line[5:].strip()
    if text is None:
        text = body
    return json.loads(text)

def main():
    tool = sys.argv[1]
    args = json.loads(sys.argv[2])
    raw = "--raw" in sys.argv
    resp = call(tool, args)
    try:
        content = resp["result"]["content"]
        # content is a list of {type:text, text:"<json string>"} -> unwrap
        for item in content:
            t = item.get("text", "")
            if raw:
                print(t)
            else:
                try:
                    obj = json.loads(t)
                    print(json.dumps(obj, indent=2))
                except Exception:
                    print(t)
    except KeyError:
        print(json.dumps(resp, indent=2))

if __name__ == "__main__":
    main()
