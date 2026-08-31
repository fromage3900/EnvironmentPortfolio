import json, urllib.request, sys
out = open(r"C:\EnvironmentPortfolio\logs\overnight\smoke_result.txt", "w", encoding="utf-8")
for m in ["qwen3-coder:30b", "qwen2.5:14b", "qwen3:8b"]:
    body = json.dumps({"model": m, "messages": [{"role": "user", "content": "Reply with exactly OK"}], "stream": False}).encode()
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=body, headers={"Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=900)
        out.write(f"{m} => {json.loads(r.read())['message']['content'][:40]}\n")
    except urllib.error.HTTPError as e:
        out.write(f"{m} => HTTP {e.code} {e.read().decode()[:150]}\n")
    except Exception as e:
        out.write(f"{m} => ERR {str(e)[:150]}\n")
    out.flush()
out.write("SMOKE_DONE\n")
out.close()
