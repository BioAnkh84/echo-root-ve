# Contributing to Vulpine Echo (VE)

Thanks for helping! This repo aims to stay tiny, auditable, and PS 5.1–safe.

## Dev environment
- Windows 10/11, PowerShell 5.1 (stock)
- No external modules required
- Run: `.\ve_kernel.ps1 audit` (exit code 0 = pass)

## Workflow
1. Fork → branch: `feat/<topic>` or `fix/<topic>`
2. Keep PRs small; include **exact repro steps** and before/after output
3. Add/adjust tests where relevant (`Tests/*` or tiny smoke checks)
4. CI must pass

## Commit style
- Conventional-ish: `feat: ...`, `fix: ...`, `docs: ...`, `chore: ...`
- Present tense, imperative (“add…”, “fix…”)

## Versioning
- Tags like `v0.1a`, `v0.1b`, …; CHANGELOG in Releases page

## Security
- Don’t file public issues with exploit details; see SECURITY.md