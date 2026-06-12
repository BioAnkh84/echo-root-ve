## Summary

Adds a Codex-facing Echo Root integration layer with receipt-backed hooks, MCP configuration, and an MCP-independent CLI proof adapter.

This branch makes Echo Root usable by Codex even when live external stdio MCP tools are not exposed by the active Codex surface.

## Key Changes

- Adds repo-local Codex lifecycle hooks for orientation, pre-tool posture, permission requests, post-tool receipts, and closeout receipts.
- Adds an explicit Codex score baseline with `rho`, `delta`, difference makers, calibration reasons, and confidence-stability lessons.
- Adds Echo Root MCP server config and tools for repo map, gate action, append receipt, verify chain, self-test, and live probe.
- Documents current MCP transport finding: Echo Root and a minimal hello-world stdio MCP server both pass direct framed tests but are not live-exposed in this Codex Desktop/CLI surface.
- Adds `echo_root_cli.py`, an MCP-independent fallback adapter for repo map, gate, receipts, verify, replay, self-test, live probe, and one-command proof.
- Adds tests for hook behavior, MCP request handling, score baseline lessons, and CLI proof behavior.

## Proof Command

```powershell
py -3.11 .\echo_root_cli.py prove --reset
```

Expected proof:

- repo orientation receipt with `map_hash`
- gate decisions in order: `PROCEED`, `PAUSE`, `ABORT`
- hash-chained receipts written under ignored `ve_data`
- receipt chain verification: `ok: true`
- replay matches every decision
- MCP is optional for this proof path

## Test Plan

```powershell
py -3.11 .\echo_root_cli.py prove --reset
py -3.11 -m unittest discover -s Tests
py -3.11 .github\ve_checks.py
```

Current local result:

- CLI proof: `ok: true`
- Unit tests: `58 tests OK`
- VE checks: all OK

## Claim Boundary

This does not claim live MCP exposure works in every Codex surface.

Current evidence shows:

- `echo_root_ve` is registered and direct server calls work.
- live Codex currently exposes only bundled `mcp__node_repl`.
- a minimal external stdio MCP server also failed to become live-callable.

Therefore the fallback proof path is:

```text
MCP when available. CLI receipts always.
```
