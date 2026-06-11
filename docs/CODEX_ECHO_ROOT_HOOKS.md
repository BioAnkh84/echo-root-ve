# Codex Echo Root Hooks

Echo Root can help Codex most at the repo boundary: orientation before work,
posture checks around tool use, and receipts after meaningful actions.

This repo includes a conservative Codex hook bridge:

- `.codex/hooks.json`
- `.codex/hooks/codex_echo_root_hook.py`

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

Tune scores from evidence:

- Raise `rho` after passing tests, verified receipts, hash checks, replay, or
  explicit human confirmation.
- Raise `delta` after escalation, destructive intent, stale context, dirty
  worktree, fallback, branch mismatch, or unclear scope.
- Lower future confidence when human review finds an explanation mismatch.
- Let repeated clean replay earn trust slowly.
