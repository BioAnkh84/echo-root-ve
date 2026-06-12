# Codex Echo Root Hooks

Echo Root can help Codex most at the repo boundary: orientation before work,
posture checks around tool use, and receipts after meaningful actions.

This repo includes a conservative Codex hook bridge:

- `.codex/hooks.json`
- `.codex/hooks/codex_echo_root_hook.py`

For the shortest AI startup sequence, see:

```text
docs/CODEX_AI_OPERATOR_PACKET.md
```

The bridge writes local runtime receipts under:

```text
ve_data/codex_hooks/
```

Those files are ignored by git. They are local evidence, not public release
artifacts.

The hook score baseline lives at:

```text
.codex/echo_root_score_baseline.json
```

That file defines the starting `rho`, `delta`, confidence, and action lane for
each Codex hook event.

## What The Hooks Do

`SessionStart`

- Builds a deterministic repo-map snapshot.
- Writes an Echo Root receipt.
- Records the boundary: repo map is orientation, not proof.

`PreToolUse`

- Records a pre-action posture receipt for shell and file-edit tools.
- Uses Echo Root gate language to classify the posture.

`PermissionRequest`

- Records the approval posture when Codex asks for elevated authority.

`PostToolUse`

- Appends a post-action receipt after shell or file-edit tools run.

`Stop`

- Appends a closeout receipt at the end of a Codex turn.

## Self-Test

Run the local self-test to see whether Echo Root changes the Codex workflow in
practice:

```text
py -3.11 .codex/hooks/codex_echo_root_selftest.py
```

The self-test simulates session start, pre-tool checks, permission request,
alternate Codex payload shapes, destructive command posture, post-tool
receipt, and closeout. It should show that permission requests become `PAUSE`,
destructive command posture becomes `ABORT`, calibration reasons are attached,
and lifecycle events become hash-chained receipts.

## Live Activation Probe

The self-test proves the hook bridge logic. A live activation probe checks
whether Codex is actually running the repo-local hooks in the current session:

```text
py -3.11 .codex/hooks/codex_hook_live_probe.py
```

Note `receipt_count`, run one harmless Codex tool action in a fresh trusted
session, then run:

```text
py -3.11 .codex/hooks/codex_hook_live_probe.py --before-count <count>
```

If `live_hook_append_detected` is `true`, the repo hooks are active. If not,
review hook trust/activation before relying on lifecycle receipts.

## What The Hooks Do Not Do

- They do not silently approve commands.
- They do not replace Codex sandboxing or user approval.
- They do not claim a file is healthy because it exists.
- They do not convert capability into authority.

## Trust And Activation

Codex requires project-local hooks to be trusted before they run. Review the
hook definitions in `.codex/hooks.json` and the script in
`.codex/hooks/codex_echo_root_hook.py` before enabling them.

In Codex CLI, use:

```text
/hooks
```

Then review and trust the project hooks.

## Doctrine Boundary

Hooked in does not mean trusted.

Receipts improve reviewability, but they are not permission. If a receipt says
`PAUSE`, the operator should inspect the reason before continuing. If a receipt
says `ABORT` or `SAFE_MODE`, the operator should treat the workflow as needing
human review.

## Score Baseline

The first baseline is intentionally conservative:

- `SessionStart` starts as orientation, not proof.
- `PreToolUse` starts in a PAUSE-prone inspection posture.
- `PermissionRequest` starts with higher drift because authority changed.
- `PostToolUse` can score stronger when receipts and command results exist.
- `Stop` can score strongest when tests and receipts stayed clean.

Each hook receipt also records optional `calibration_reason` so old receipts
can explain why their `rho` and `delta` started where they did. That field is
optional, so the public v0.1 required receipt schema stays stable.

Tune scores from evidence:

- Raise `rho` after passing tests, verified receipts, hash checks, replay, or
  explicit human confirmation.
- Raise `delta` after escalation, destructive intent, stale context, dirty
  worktree, fallback, branch mismatch, unclear scope, or confidence instability
  across recent decisions.
- Lower future confidence when human review finds an explanation mismatch.
- Let repeated clean replay earn trust slowly.
- Keep normal confidence stable while preserving edge-case readiness; score
  movement can itself become evidence when it spikes without matching proof.

## Difference Makers

The score baseline names the signals that should actually change Codex's
posture:

- Evidence makers raise `rho`: repo-map snapshot, verified hash chain,
  post-action checks, and explicit human confirmation.
- Risk makers raise `delta`: permission requests, dirty worktree, destructive
  command text, missing scope, provider or route fallback, and confidence
  instability.
- Feedback makers tune future runs: unexpected action, weak receipts, and
  repeated clean replay.

The self-test reports `difference_makers_caught` so we can tell whether Echo
Root improved the workflow or merely added ceremony.
