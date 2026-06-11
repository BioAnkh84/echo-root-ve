#!/usr/bin/env python3
import sys
import io
import json
import os
import subprocess
import re
import ast
from datetime import datetime
from typing import List
from contextlib import redirect_stdout

EXIT_OK = 0
EXIT_FAIL = 1

MAX_PAYLOAD_LEN = 512
ALLOWED_ROUTE_HINTS = {"normal", "safe_only", "blocked"}

ALLOWED_AST_NODES = (
    ast.Expression,
    ast.Constant,
    ast.Tuple,
    ast.List,
    ast.Dict,
    ast.Set,
    ast.UnaryOp,
    ast.BinOp,
    ast.BoolOp,
    ast.Compare,
    ast.IfExp,
    ast.JoinedStr,
    ast.FormattedValue,
    ast.Load,
    ast.UAdd,
    ast.USub,
    ast.Not,
    ast.Invert,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.And,
    ast.Or,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
)

HELP = """Vulpine Echo (Python core)
Usage:
  ve_kernel.py status
  ve_kernel.py exec '<payload>'
  ve_kernel.py audit
  ve_kernel.py audit-verbose
  ve_kernel.py quickcheck
"""

# ------------------------------------------------
# CONFIG
# ------------------------------------------------
GATE_BRIDGE = os.environ.get(
    "VE_GATE_BRIDGE",
    r"E:\Echo_Nexus_Data\habitat\cipher_local\echo_gate_bridge.py"
)
LEDGER_FILE = "ve_ledger.jsonl"

# ------------------------------------------------
# BASIC FUNCTIONS
# ------------------------------------------------
def print_ready():
    print("READY")
    return EXIT_OK

def run_audit(verbose: bool):
    if verbose:
        print("one=one")
        print("two=two")
    return EXIT_OK

# ------------------------------------------------
# GOVERNANCE BRIDGE
# ------------------------------------------------
def run_gate(payload: str):
    try:
        result = subprocess.run(
            ["python", GATE_BRIDGE, payload],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)

        required = ["decision", "rho", "gamma", "delta"]
        if not all(k in data for k in required):
            raise ValueError("Malformed gate response")

        data.setdefault("route_hint", "blocked")
        data.setdefault("trace_id", "missing_trace")
        data.setdefault("ts", datetime.utcnow().isoformat() + "Z")

        return data

    except Exception as e:
        print(f"[GATE ERROR] {e}", file=sys.stderr)
        return {
            "decision": "ABORT",
            "route_hint": "blocked",
            "rho": 0.0,
            "gamma": 0.0,
            "delta": 1.0,
            "trace_id": "gate_error",
            "ts": datetime.utcnow().isoformat() + "Z"
        }

# ------------------------------------------------
# INPUT SANITIZATION
# ------------------------------------------------
def sanitize_payload(payload: str) -> str:
    if not payload:
        return ""

    payload = payload.strip()

    if len(payload) > MAX_PAYLOAD_LEN:
        payload = payload[:MAX_PAYLOAD_LEN]

    payload = re.sub(r"[^\x20-\x7E]", "", payload)
    return payload

# ------------------------------------------------
# POLICY NORMALIZATION
# ------------------------------------------------
def normalize_policy(decision: str, route_hint: str):
    decision = (decision or "ABORT").upper()
    route_hint = (route_hint or "blocked").lower()

    if route_hint not in ALLOWED_ROUTE_HINTS:
        return "ABORT", "blocked", f"unknown_route_hint:{route_hint}"

    if decision not in {"PROCEED", "PAUSE", "ABORT"}:
        return "ABORT", "blocked", f"unknown_decision:{decision}"

    if decision == "ABORT":
        return "ABORT", "blocked", "decision_abort"

    if route_hint == "blocked":
        return "ABORT", "blocked", "route_hint_blocked"

    if decision == "PAUSE":
        return "PAUSE", "safe_mode", "decision_pause"

    if decision == "PROCEED" and route_hint == "safe_only":
        return "PAUSE", "safe_mode", "route_hint_safe_only"

    if decision == "PROCEED" and route_hint == "normal":
        return "PROCEED", "proceed", "decision_proceed"

    return "ABORT", "blocked", "fallback_fail_closed"

# ------------------------------------------------
# SAFE MODE TIERING (fallback keyword logic)
# ------------------------------------------------
def detect_safe_mode_level(text: str) -> str:
    text = (text or "").lower()

    elevated_patterns = [
        r"\bmodify\b", r"\bchange\b", r"\baccess\b",
        r"\bdelete\b", r"\bsystem\b", r"\bdata\b", r"\bfile\b"
    ]

    execution_patterns = [
        r"\bexec\(", r"\bopen\(", r"__import__"
    ]

    mild_patterns = [
        r"\bmaybe\b", r"\bsomething\b", r"\banalyze\b",
        r"\bunknown\b", r"\bunclear\b", r"\brisky\b", r"\bdangerous\b"
    ]

    if any(re.search(p, text) for p in elevated_patterns):
        return "STRICT"

    if any(re.search(p, text) for p in execution_patterns):
        return "STRICT"

    if any(re.search(p, text) for p in mild_patterns):
        return "LIGHT"

    return "LIGHT"

# ------------------------------------------------
# SAFE PYTHON EXPRESSION EVALUATION
# ------------------------------------------------
def safe_eval_expr(expr: str):
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED_AST_NODES):
            raise ValueError(f"unsafe expression node: {node.__class__.__name__}")
        if isinstance(node, ast.Constant) and not isinstance(
            node.value,
            (str, int, float, bool, type(None)),
        ):
            raise ValueError("unsupported literal type")

    code = compile(tree, "<ve-safe-expr>", "eval")
    return eval(code, {"__builtins__": {}}, {})

# ------------------------------------------------
# EXECUTION CORE
# ------------------------------------------------
def do_exec(payload: str) -> int:
    s = sanitize_payload(payload)

    if not s:
        print("Error: empty payload", file=sys.stderr)
        return EXIT_FAIL

    if s.lower().startswith("echo:"):
        print(s[5:].lstrip())
        return EXIT_OK

    if s.lower().startswith("py:"):
        expr = s[3:].lstrip()
        expr = expr.split("#")[0].strip()

        try:
            print(safe_eval_expr(expr))
            return EXIT_OK
        except Exception as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            return EXIT_FAIL

    print(s)
    return EXIT_OK

# ------------------------------------------------
# SAFE MODE EXECUTION
# ------------------------------------------------
def safe_mode_exec(payload: str, level: str) -> int:
    s = sanitize_payload(payload)

    print(f"[SAFE MODE {level}]")

    if s.lower().startswith("echo:"):
        print(s[5:].lstrip())
        return EXIT_OK

    if s.lower().startswith("py:"):
        expr = s[3:].lstrip().split("#")[0].strip()

        if level == "STRICT":
            if not re.fullmatch(r"[0-9+\-*/(). ]+", expr):
                print("[SAFE MODE BLOCK]")
                return EXIT_FAIL

        try:
            print(safe_eval_expr(expr))
            return EXIT_OK
        except:
            print("[SAFE MODE BLOCK]")
            return EXIT_FAIL

    print(f"[SAFE OUTPUT] {s[:120]}")
    return EXIT_OK

# ------------------------------------------------
# LEDGER WRITE
# ------------------------------------------------
def write_ledger(entry: dict):
    try:
        with open(LEDGER_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[LEDGER ERROR] {e}", file=sys.stderr)

# ------------------------------------------------
# GOVERNED EXECUTION (Δ-DRIVEN)
# ------------------------------------------------
def governed_exec(payload: str) -> int:
    payload = sanitize_payload(payload)
    gate = run_gate(payload)

    decision, route, reason = normalize_policy(
        gate.get("decision"),
        gate.get("route_hint")
    )

    delta = gate.get("delta", 0.0)

    print(f"[VE] decision={decision} delta={delta:.2f}")

    entry = {
        "trace_id": gate.get("trace_id"),
        "delta": delta,
        "payload": payload
    }

    try:
        if decision == "ABORT":
            print("[BLOCKED]")
            return EXIT_FAIL

        if decision == "PAUSE":
            # 🔥 Δ-based tiering
            if delta > 0.45:
                level = "STRICT"
            else:
                level = "LIGHT"

            rc = safe_mode_exec(payload, level)

            print(f"[DELTA] -> SAFE_{level}")

            return rc

        return do_exec(payload)

    finally:
        write_ledger(entry)

# ------------------------------------------------
# MAIN
# ------------------------------------------------
def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print(HELP)
        return EXIT_FAIL

    if argv[1] == "status":
        return print_ready()

    if argv[1] == "exec":
        return governed_exec(" ".join(argv[2:]))

    if argv[1] == "quickcheck":
        checks = [
            ("echo: hello", EXIT_OK),
            ("handle it", EXIT_OK),
            ("delete everything", EXIT_FAIL),
        ]
        for payload, expected in checks:
            rc = governed_exec(payload)
            if rc != expected:
                print(f"[QUICKCHECK FAIL] {payload} rc={rc} expected={expected}")
                return EXIT_FAIL
        print("[QUICKCHECK OK]")
        return EXIT_OK

    return EXIT_FAIL

if __name__ == "__main__":
    sys.exit(main(sys.argv))
