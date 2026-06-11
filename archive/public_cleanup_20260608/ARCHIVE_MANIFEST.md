# Public Cleanup Archive - 2026-06-08

This archive keeps old public-repo clutter reachable without leaving it in the root path.

Authority: historical reference only. These files are not active runtime inputs, proof surfaces, or current demo evidence.

## Archive Root

```text
archive/public_cleanup_20260608/
```

## Why This Archive Exists

The public Echo Root root path had legacy backup files, old artifact report folders, and tiny scratch payload files mixed with active docs, code, tests, and proof packets.

Those files were moved here to:

- keep active public paths easier to review
- reduce accidental inclusion of stale or confusing data in public packaging
- preserve historical evidence instead of deleting it
- make cleanup decisions explicit and reversible through Git history

## Moved Buckets

| Bucket | Count | Archive path | Why archived |
| --- | ---: | --- | --- |
| Legacy artifact reports | 27 | `archive/public_cleanup_20260608/legacy_artifacts/` | Old October 2025 generated report outputs, not current proof packet evidence. |
| Legacy backups and logs | 43 | `archive/public_cleanup_20260608/legacy_backups/` | Timestamped `.bak*` and old run-log files superseded by active source files. |
| Scratch payloads | 10 | `archive/public_cleanup_20260608/scratch_payloads/` | Tiny hello/bench/payload files used for early smoke tests, not current demo fixtures. |

## Not Archived In This Pass

- Active source files and scripts.
- Current `ve_data` gate pipeline audit, replay report, mission memory, lessons, and twin state.
- `.venv`, `__pycache__`, and other generated local runtime folders. These should be ignored or regenerated, not preserved as public archive evidence.
- Scripts with hardcoded local paths. Those need portability fixes or a separate local-only launcher decision, not blind archiving.

## Clean-As-You-Go Rule

When archiving future files:

1. Move only clear stale/generated/superseded artifacts.
2. Preserve active code, tests, current evidence, and docs unless replacing them intentionally.
3. Put archived files under a dated archive folder.
4. Record path, reason, and whether the file was tracked or ignored.
5. Run tests or the relevant smoke check after the move.
