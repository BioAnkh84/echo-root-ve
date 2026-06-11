# Codex MCP Integration

Echo Root VE also exposes a repo-local MCP server so Codex can call Echo Root
directly as tools.

## Files

- `.codex/config.toml`
- `.codex/mcp/echo_root_mcp.py`

The config registers a stdio MCP server named `echo_root_ve`.

## Tools

- `echo_root_repo_map`
- `echo_root_gate_action`
- `echo_root_append_receipt`
- `echo_root_verify_chain`
- `echo_root_selftest`
- `echo_root_live_probe`

## Activation

Open a fresh Codex project session in this repo and review/trust project
configuration if prompted. Then ask Codex to list MCP tools or use:

```text
/mcp
```

If the server is active, Codex should see Echo Root tools without needing the
repo-local lifecycle hooks to fire.

## Boundary

MCP tools make Echo Root callable. They do not grant authority.

Use `echo_root_gate_action` before risky work, `echo_root_append_receipt` for
reviewable decisions, and `echo_root_verify_chain` before trusting receipt
history.
