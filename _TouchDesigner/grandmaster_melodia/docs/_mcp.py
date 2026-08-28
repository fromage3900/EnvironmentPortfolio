#!/usr/bin/env python3
"""Helper: call a TD MCP tool and print the unwrapped result text."""
import sys, json, re, urllib.request

EP = "http://127.0.0.1:9870/mcp"

def call(name, arguments):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                          "params": {"name": name, "arguments": arguments}}).encode()
    req = urllib.request.Request(EP, data=payload,
                                 headers={"Content-Type": "application/json",
                                          "Accept": "application/json, text/event-stream"})
    raw = urllib.request.urlopen(req).read().decode()
    # strip event: lines and data: prefix per line
    text = raw
    text = re.sub(r'(?m)^event:.*$', '', text)
    text = re.sub(r'(?m)^data: ', '', text)
    text = re.sub(r'(?m)^: ping.*$', '', text)
    text = text.strip()
    d = json.loads(text)
    res = d.get("result", {})
    if isinstance(res, dict) and "content" in res:
        print(res["content"][0]["text"])
    else:
        print(json.dumps(res))
    sys.exit(0 if not d.get("error") else 1)

def query(name):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                          "params": {"name": name, "arguments": {}}}).encode()
    req = urllib.request.Request(EP, data=payload,
                                 headers={"Content-Type": "application/json",
                                          "Accept": "application/json, text/event-stream"})
    raw = urllib.request.urlopen(req).read().decode()
    text = re.sub(r'(?m)^event:.*$', '', raw)
    text = re.sub(r'(?m)^data: ', '', text)
    text = re.sub(r'(?m)^: ping.*$', '', text).strip()
    print(json.loads(text)["result"]["content"][0]["text"])

if __name__ == "__main__":
    name = sys.argv[1]
    args = {}
    if len(sys.argv) >= 3:
        args = json.loads(sys.argv[2])
    call(name, args)