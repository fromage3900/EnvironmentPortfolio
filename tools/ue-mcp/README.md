# UE MCP in VS Code

The project already ships MCP servers **inside** the Unreal Editor via the
enabled plugins `UnrealMCP`, `UEBlueprintMCP`, `ModelContextProtocol`, and
`MCPClientToolset`. No new server is needed — VS Code agents (Copilot /
Claude-class tools) connect to them through `.vscode/mcp.json` at the repo root,
which launches `stdio_proxy.py` to bridge stdio JSON-RPC to the editor's local
TCP endpoint.

## Setup

1. Check the port your UE MCP plugin listens on (see
   `BS_GodFile/Plugins/UnrealMCP` / `UEBlueprintMCP` docs; commonly 55557).
2. Open the repo in VS Code → the MCP server `unreal-mcp` starts on demand.
3. Launch the editor first (`UE: Launch Editor (PIE-ready)` task) — the proxy
   fails fast if the editor isn't running.

## Safety rules (mirror the Embody/Envoy AGENTS.md conventions)

- Always `127.0.0.1` binding, never `0.0.0.0`.
- Prefer querying live state over assuming paths; agents must call
  query/discovery tools before mutating.
- Batch repetitive MCP operations; check errors after each group of edits.
- Never let agents run destructive editor operations unattended (save/overwrite
  confirmations off in `-unattended` runs).
