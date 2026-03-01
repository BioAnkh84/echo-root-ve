# Legacy Ledger Archive

This folder contains pre-Patch v1.0.3 ledger artifacts that are **not** cryptographically verifiable as a continuous chain.

Findings:
- Original `ve_ledger.jsonl` contained malformed JSONL (multiple JSON objects on one line).
- After repair to valid JSONL, `hash_prev` continuity failed at line 2.
- `hash_self` values could not be reproduced under canonical UTF-8 stable JSON hashing or legacy ASCII-escaped fallback.

Action:
- Legacy files are preserved as archival notes only.
- Canonical tamper-evident ledger restarted under Patch v1.0.3 tooling alignment.
