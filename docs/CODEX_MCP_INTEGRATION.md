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

If only built-in Codex project tools appear, the project MCP config has not
loaded yet. Check:

1. The session is on branch `codex/echo-root-hooks`.
2. `.codex/config.toml` exists in the repo.
3. The project config has been reviewed/trusted.
4. A fresh project session was opened after the config file was added.
5. The app can run `py -3.11 .codex/mcp/echo_root_mcp.py` from the repo root.

## Current Windows Desktop Finding

On 2026-06-11, Codex Desktop/CLI `0.140.0-alpha.2` could see the
`echo_root_ve` MCP configuration through `codex mcp get echo_root_ve`, and the
server passed direct framed initialize tests. However, a live Codex session did
not expose the `echo_root_*` tools.

Temporary startup tracing showed:

```text
serve_start
read_wait
read_eof
serve_stop
```

That means Codex launched the configured process in the correct repo, then
closed stdin before sending the MCP `initialize` request. Treat this as a live
transport activation gap, not proof that the Echo Root server tools are invalid.

On 2026-06-12, a minimal temporary stdio MCP server with one hello-world tool
also passed direct framed initialize testing and was visible through
`codex mcp list`, but did not appear as a callable tool in a live Codex session.
Codex reported handshake timeouts for both the minimal server and Echo Root.
That lowers the probability of an Echo Root implementation bug and raises the
probability of an active-surface external stdio MCP limitation or transport
issue.

Until this is resolved in the active Codex surface, use the repo-local commands
as the fallback proof path:

```text
py -3.11 repo_map.py --depth 3 --json
py -3.11 .codex/hooks/codex_echo_root_selftest.py
py -3.11 .codex/hooks/codex_hook_live_probe.py
py -3.11 .github\ve_checks.py
```

## Personal Plugin Wrapper

If project/global MCP config is visible on disk but not exposed in the live
Codex tool registry, use the personal plugin wrapper:

```text
C:\Users\Richard\plugins\echo-root-ve
```

The plugin bundles:

- a skill entry point
- `.mcp.json` pointing at this repo's Echo Root MCP server
- marketplace metadata under `C:\Users\Richard\.agents\plugins\marketplace.json`

After changing the plugin, refresh Codex by restarting the app and installing
or reopening **Echo Root VE** from the personal plugin marketplace.

## Boundary

MCP tools make Echo Root callable. They do not grant authority.

Use `echo_root_gate_action` before risky work, `echo_root_append_receipt` for
reviewable decisions, and `echo_root_verify_chain` before trusting receipt
history.
