#!/usr/bin/env python3
"""
VE PR Check harness

This file exists because the GitHub Actions workflow expects it at:
  .github/ve_checks.py

Design goals:
- Deterministic
- Cross-platform (Linux runner)
- Meaningful but lightweight checks
- No dependency on PowerShell availability

Checks performed:
1) Required repo files exist (quickcheck + kernel scripts)
2) Python quickcheck CLI is runnable
3) Git sanity: ensure runtime artifacts are not tracked
"""

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path


REQUIRED_FILES = [
    "ve_quickcheck_stub.py",
    "ve_kernel.ps1",
    "ve_kernel.py",
    "ve_kernel.sh",
    "ve_parse.sh",
    "README.md",
]


RUNTIME_SHOULD_NOT_BE_TRACKED = [
    "ve_ledger.jsonl",
    "ledger.jsonl",
    "governance_ttl.json",
    "_tmp_ledger.jsonl",
]


def run(cmd: list[str], cwd: Path) -> int:
    p = subprocess.run(cmd, cwd=str(cwd), text=True)
    return p.returncode


def main() -> int:
    repo = Path(__file__).resolve().parent.parent

    # 1) Required files
    missing = [f for f in REQUIRED_FILES if not (repo / f).exists()]
    if missing:
        print("[FAIL] Missing required files:", ", ".join(missing))
        return 20
    print("[OK] Required files present.")

    # 2) quickcheck CLI runnable
    rc = run([sys.executable, str(repo / "ve_quickcheck_stub.py"), "--help"], cwd=repo)
    if rc != 0:
        print("[FAIL] ve_quickcheck_stub.py --help failed with rc=", rc)
        return 20
    print("[OK] ve_quickcheck_stub.py runnable.")

    # 3) Git sanity: runtime artifacts not tracked
    # If git isn't available (rare on GH runners), skip this check gracefully.
    try:
        tracked = subprocess.check_output(
            ["git", "ls-files"], cwd=str(repo), text=True
        ).splitlines()
        tracked_set = set(tracked)
        bad = [f for f in RUNTIME_SHOULD_NOT_BE_TRACKED if f in tracked_set]
        if bad:
            print("[FAIL] Runtime artifacts are tracked (should be ignored):", ", ".join(bad))
            return 20
        print("[OK] Runtime artifacts not tracked.")
    except Exception as e:
        print("[WARN] git check skipped:", e)

    print("[OK] VE PR checks passed.")
    return 0


# --- PATCH: tracked-only runtime artifact check (PS/CI hardened) ---
import subprocess

def _tracked(paths):
    out = subprocess.check_output(["git","ls-files","-z","--"] + list(paths))
    items = [p for p in out.decode("utf-8", errors="replace").split("\x00") if p]
    return set(items)

tracked = _tracked(["ve_ledger.jsonl","ledger.jsonl"])
if tracked:
    print("[FAIL] Runtime artifacts are tracked (should be ignored): " + ", ".join(sorted(tracked)))
    raise SystemExit(20)
# --- END PATCH ---
if __name__ == "__main__":
    raise SystemExit(main())

