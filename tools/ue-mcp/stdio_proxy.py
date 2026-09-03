#!/usr/bin/env python3
"""Stdio <-> TCP proxy for UE MCP servers (UnrealMCP / UEBlueprintMCP).

VS Code's mcp.json launches this as a stdio MCP server; it forwards JSON-RPC
lines to the MCP server already running inside the Unreal Editor over a local
TCP socket (default 127.0.0.1:55557). Adjust the port to match your plugin's
configured endpoint.

Usage: stdio_proxy.py [host] [port]
"""
import json
import socket
import sys
import threading


def pump_socket_to_stdout(sock: socket.socket) -> None:
    buf = b""
    while True:
        try:
            chunk = sock.recv(65536)
        except OSError:
            break
        if not chunk:
            break
        buf += chunk
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            sys.stdout.write(line.decode("utf-8", "replace") + "\n")
            sys.stdout.flush()


def main() -> None:
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 55557
    sock = socket.create_connection((host, port))
    threading.Thread(target=pump_socket_to_stdout, args=(sock,), daemon=True).start()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)  # validate it's JSON-RPC-shaped before forwarding
        except json.JSONDecodeError:
            err = {"jsonrpc": "2.0", "id": None,
                   "error": {"code": -32700, "message": "Parse error"}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()
            continue
        sock.sendall((line + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
