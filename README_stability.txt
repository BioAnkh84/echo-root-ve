VE Stability Pack v0.3
=======================
Harden your Vulpine Echo suite with atomic writes, a mutexed ledger append, schema checks, and environment diagnostics.

Files
-----
- ve_atomic_io.ps1 — atomic JSONL writes, SHA256, safe last-line read
- ve_ledger_append_atomic.ps1 — mutex-protected, atomic ledger append with metadata (actor, type, consent)
- ve_schema_check.py — schema + hash-chain + ψ floor verification
- ve_diag.ps1 — environment diagnostics (execution policy, Python, OneDrive/space hints)
- ve_stable_run.ps1 — hardened one-shot runner (file-based handshake → atomic append → schema check)

Suggested Use
-------------
1) Copy these files into your VE suite folder:
   C:\Users\User\OneDrive\Documents\Ciphers stuff\VE_Test_Suite_v0.1a

2) From that folder:
   powershell -ExecutionPolicy Bypass -File .\ve_diag.ps1
   powershell -ExecutionPolicy Bypass -File .\ve_stable_run.ps1

3) Inspect outputs:
   - ledger.jsonl grows by one line per run (with hash_prev/hash_self)
   - ve_schema_check.py prints [OK] or details
   - Use ve_ledger_append_atomic.ps1 directly if you want to append with custom metadata

Created: 2025-10-28 09:24 
