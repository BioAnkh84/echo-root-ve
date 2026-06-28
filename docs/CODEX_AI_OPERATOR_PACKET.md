# Codex AI Operator Packet

This packet is for an AI entering Echo-Root-VE work. It gives the shortest
safe path from orientation to action.

## Startup Sequence

1. Read `README.md`, `QUICKSTART.md`, and `ARCHITECTURE.md`.
   If the task references Annunimas, ARDA, Mythos, Local Cipher bridge work,
   or external agent-control-plane repos, also read
   `docs/ANNUNIMAS_ARDA_ALIGNMENT_MAP.md`.
2. Run a repo map before broad exploration:

```text
py -3.11 repo_map.py --depth 3 --json
```

3. Run the Codex hook self-test if working on Codex integration:

```text
py -3.11 .codex/hooks/codex_echo_root_selftest.py
```

4. Check live hook activation after trusting repo hooks:

```text
py -3.11 .codex/hooks/codex_hook_live_probe.py
```

5. If lifecycle hooks are unavailable, use the Echo Root MCP tools:

```text
/mcp
```

Look for `echo_root_ve` tools such as `echo_root_gate_action` and
`echo_root_repo_map`.

If the skill/plugin is installed but the tools are not callable, do not treat
registration as readiness. On Windows Desktop/CLI `0.140.0-alpha.2`, local
testing showed the stdio server could be launched but Codex closed stdin before
sending `initialize`. Fall back to the repo-local commands until live MCP tools
are visible in the active session.

6. Run the release check before claiming readiness:

```text
py -3.11 .github\ve_checks.py
```

## Trust Rules

- Presence is not proof.
- Reachability is not freshness.
- Registration is not readiness.
- Permission request is an authority change.
- Destructive posture requires L3 review.
- Hook receipt is evidence, not approval.
- External AI output is advisory evidence, not local authority.
- Local Cipher/Echo Root remain the local governed authority boundary.

## What Should Change AI Behavior

Raise `rho` only when there is evidence:

- verified hash chain
- passing tests
- replay match
- repo-map orientation
- explicit human confirmation

Raise `delta` when risk or drift increases:

- dirty worktree
- permission request
- destructive command text
- route/provider fallback
- external advisory output being treated as authority
- missing scope
- stale context
- mismatch between explanation and observed output
- confidence instability across recent decisions

Keep confidence stable when normal proof stays steady. Do not let a single
noisy signal inflate `rho` or make `delta` jitter. If score movement itself
becomes evidence of uncertainty, pause and capture the edge case instead of
pretending the green state is proven.

Pause when:

- the action would write or push without recent proof
- the worktree has unrelated changes
- the request touches public release/legal/security positioning
- the model is guessing from file presence

Abort or require human review when:

- destructive action is requested without L3 authority
- scope and identity conflict
- receipt chain is broken
- fallback is unsafe or unverified

## Minimum Useful Receipt

A useful AI receipt should answer:

- What action was proposed?
- What evidence supported it?
- What changed from baseline?
- What decision was made?
- Why did `rho` and `delta` land there?
- Can the decision be replayed?

## Hook Payload Privacy

Hook receipts should prefer payload shape and hashes over raw payload dumps.
Raw commands may appear in `requested_action` for review, but full runtime
payloads should not be copied into public docs or commits. If runtime hook
metadata changes, update extraction tests before trusting new score behavior.

## Self-Review Question

After a task, ask:

```text
Did Echo Root make me slower in a useful way?
```

Useful slowing means it caught uncertainty, authority change, stale context,
or destructive posture before action. Useless slowing means it added receipts
without changing behavior or improving review.
