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
4) Unit tests pass
5) v0.1 receipt demo can append, verify, and replay a temporary ledger
6) Repo map receipt and delta receipt can be generated for human/AI orientation
"""

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path


REQUIRED_FILES = [
    "ARCHITECTURE.md",
    "QUICKSTART.md",
    "RELEASE_EVIDENCE.md",
    "LICENSE_READINESS_CHECKLIST.md",
    "RELEASE_MANIFEST.md",
    "PUBLIC_RELEASE_SAFETY_SCAN.md",
    "docs/CODEX_ECHO_ROOT_HOOKS.md",
    "docs/CODEX_AI_OPERATOR_PACKET.md",
    "docs/REPO_MAP_RECEIPTS.md",
    ".codex/hooks.json",
    ".codex/echo_root_score_baseline.json",
    ".codex/hooks/codex_echo_root_hook.py",
    ".codex/hooks/codex_echo_root_selftest.py",
    ".codex/hooks/codex_hook_live_probe.py",
    ".codex/config.toml",
    ".codex/mcp/echo_root_mcp.py",
    "docs/CODEX_MCP_INTEGRATION.md",
    "schemas/echo_root_receipt.schema.json",
    "echo_root_receipt.py",
    "repo_map.py",
    "ve_quickcheck.py",
    "ve_kernel.ps1",
    "ve_kernel.py",
    "ve_kernel.sh",
    "ve_parse.sh",
    "README.md",
]


RUNTIME_SHOULD_NOT_BE_TRACKED = [
    "ve_ledger.jsonl",
    "ledger.jsonl",
    "receipts/demo_receipts.jsonl",
    "governance_ttl.json",
    "_tmp_ledger.jsonl",
    "_tmp_repo_map_snapshot.json",
]


def run(cmd: list[str], cwd: Path) -> int:
    p = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode != 0 and p.stdout:
        print(p.stdout.strip())
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
    rc = run([sys.executable, str(repo / "ve_quickcheck.py"), "--help"], cwd=repo)
    if rc != 0:
        print("[FAIL] ve_quickcheck.py --help failed with rc=", rc)
        return 20
    print("[OK] ve_quickcheck.py runnable.")

    # 3) Git sanity: runtime artifacts not tracked
    # If git isn't available (rare on GH runners), skip this check gracefully.
    try:
        tracked = subprocess.check_output(
            ["git", "ls-files"], cwd=str(repo), text=True, stderr=subprocess.DEVNULL
        ).splitlines()
        tracked_set = set(tracked)
        bad = [f for f in RUNTIME_SHOULD_NOT_BE_TRACKED if f in tracked_set]
        if bad:
            print("[FAIL] Runtime artifacts are tracked (should be ignored):", ", ".join(bad))
            return 20
        print("[OK] Runtime artifacts not tracked.")
    except Exception as e:
        print("[WARN] git check skipped:", e)

    # 4) Unit tests
    rc = run([sys.executable, "-m", "unittest", "discover", "-s", "Tests"], cwd=repo)
    if rc != 0:
        print("[FAIL] Unit tests failed with rc=", rc)
        return 20
    print("[OK] Unit tests passed.")

    # 5) Receipt demo on temp ledger
    temp_ledger = repo / "_tmp_receipt_demo.jsonl"
    try:
        if temp_ledger.exists():
            temp_ledger.unlink()
        for scenario in ("proceed", "pause", "abort"):
            rc = run(
                [
                    sys.executable,
                    str(repo / "echo_root_receipt.py"),
                    "--ledger",
                    str(temp_ledger),
                    "demo",
                    "--scenario",
                    scenario,
                ],
                cwd=repo,
            )
            if rc != 0:
                print(f"[FAIL] receipt demo scenario {scenario} failed with rc=", rc)
                return 20
        for command in ("verify", "replay"):
            rc = run(
                [
                    sys.executable,
                    str(repo / "echo_root_receipt.py"),
                    "--ledger",
                    str(temp_ledger),
                    command,
                ],
                cwd=repo,
            )
            if rc != 0:
                print(f"[FAIL] receipt demo {command} failed with rc=", rc)
                return 20
        print("[OK] v0.1 receipt demo verified and replayed.")
    finally:
        if temp_ledger.exists():
            temp_ledger.unlink()

    # 6) Repo map receipt and delta receipt
    temp_snapshot = repo / "_tmp_repo_map_snapshot.json"
    try:
        if temp_snapshot.exists():
            temp_snapshot.unlink()
        rc = run(
            [
                sys.executable,
                str(repo / "repo_map.py"),
                "--depth",
                "3",
                "--write-snapshot",
                str(temp_snapshot),
                "--json",
            ],
            cwd=repo,
        )
        if rc != 0:
            print("[FAIL] repo map receipt generation failed with rc=", rc)
            return 20
        rc = run(
            [sys.executable, str(repo / "repo_map.py"), "--depth", "3", "--delta-from", str(temp_snapshot)],
            cwd=repo,
        )
        if rc != 0:
            print("[FAIL] repo map delta generation failed with rc=", rc)
            return 20
        print("[OK] Repo map and delta receipts generated.")
    finally:
        if temp_snapshot.exists():
            temp_snapshot.unlink()

    print("[OK] VE PR checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
