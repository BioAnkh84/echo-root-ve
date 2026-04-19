#!/usr/bin/env python3
import sys
import io
import json
import subprocess
from typing import List
from contextlib import redirect_stdout

EXIT_OK = 0
EXIT_FAIL = 1

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
GATE_BRIDGE = r"E:\Echo_Nexus_Data\habitat\cipher_local\echo_gate_bridge.py"
LEDGER_FILE = "ve_ledger.jsonl"

# ------------------------------------------------
# BASIC FUNCTIONS
# ------------------------------------------------
def print_ready():
    print("READY")

def run_audit(verbose: bool):
    if verbose:
        print("one=one")
        print("two=two")

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
        return json.loads(result.stdout)
    except Exception as e:
        print(f"[GATE ERROR] {e}", file=sys.stderr)
        return None

# ------------------------------------------------
# EXECUTION CORE
# ------------------------------------------------
def do_exec(payload: str) -> int:
    if not payload or not payload.strip():
        print("Error: exec requires a payload like 'echo: ...' or 'py: ...'", file=sys.stderr)
        return EXIT_FAIL

    s = payload.strip()

    if s.lower().startswith("echo:"):
        print(s[5:].lstrip())
        return EXIT_OK

    if s.lower().startswith("py:"):
        expr = s[3:].lstrip()
        try:
            value = eval(expr, {"__builtins__": {}}, {})
            print(value)
            return EXIT_OK
        except SyntaxError:
            ns = {"__builtins__": {}}
            try:
                exec(expr, ns, ns)
                if "result" in ns:
                    print(ns["result"])
                return EXIT_OK
            except Exception as e:
                print(f"Error (exec): {e.__class__.__name__}: {e}", file=sys.stderr)
                return EXIT_FAIL
        except Exception as e:
            print(f"Error (eval): {e.__class__.__name__}: {e}", file=sys.stderr)
            return EXIT_FAIL

    print(s)
    return EXIT_OK

# ------------------------------------------------
# LEDGER WRITE
# ------------------------------------------------
def write_ledger(entry: dict):
    try:
        with open(LEDGER_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[LEDGER ERROR] {e}", file=sys.stderr)

# ------------------------------------------------
# GOVERNED EXECUTION
# ------------------------------------------------
def governed_exec(payload: str) -> int:
    gate = run_gate(payload)

    if not gate:
        return EXIT_FAIL

    decision = gate.get("decision")
    route_hint = gate.get("route_hint")

    print(f"[VE] decision={decision} route_hint={route_hint}")

    if decision == "ABORT":
        print("[BLOCKED] Execution denied by governance layer")
        return EXIT_FAIL

    if decision == "PAUSE":
        print("[SAFE MODE] Execution deferred")
        return EXIT_OK

    # PROCEED
    rc = do_exec(payload)

    entry = {
        "trace_id": gate.get("trace_id"),
        "decision": decision,
        "route_hint": route_hint,
        "rho": gate.get("rho"),
        "gamma": gate.get("gamma"),
        "delta": gate.get("delta"),
        "payload": payload,
        "rc": rc
    }

    write_ledger(entry)

    return rc

# ------------------------------------------------
# INTERNAL TEST HELPERS
# ------------------------------------------------
def _capture(fn, *args, **kwargs):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = fn(*args, **kwargs)
    out = buf.getvalue().rstrip("\n")
    return rc, out

def cmd_quickcheck() -> int:
    tests = [
        ("status",           lambda: _capture(print_ready)),
        ("py: (10*2)+5",     lambda: _capture(do_exec, "py: (10*2)+5")),
        ('py: f"sum={1+2}"', lambda: _capture(do_exec, 'py: f"sum={1+2}"')),
        ("audit-verbose",    lambda: _capture(run_audit, True)),
    ]
    expect = {
        "status": "READY",
        "py: (10*2)+5": "25",
        'py: f"sum={1+2}"': "sum=3",
        "audit-verbose": "one=one\ntwo=two",
    }

    failed = 0
    print("VE Quickcheck\n---------------")
    for name, runner in tests:
        rc, out = runner()
        want = expect[name]
        ok = (rc in (None, EXIT_OK)) and (out.strip() == want)
        status = "PASS" if ok else "FAIL"
        print(f"{status:4} :: {name:16} :: got='{out}' :: want='{want}'")
        if not ok:
            failed += 1

    return EXIT_OK if failed == 0 else EXIT_FAIL

# ------------------------------------------------
# MAIN
# ------------------------------------------------
def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print(HELP)
        return EXIT_FAIL

    cmd = argv[1].lower()

    if cmd == "status":
        print_ready()
        return EXIT_OK

    if cmd == "exec":
        if len(argv) < 3:
            print("Error: exec requires a payload string", file=sys.stderr)
            return EXIT_FAIL
        payload = " ".join(argv[2:])
        return governed_exec(payload)

    if cmd == "audit":
        run_audit(verbose=False)
        return EXIT_OK

    if cmd == "audit-verbose":
        run_audit(verbose=True)
        return EXIT_OK

    if cmd == "quickcheck":
        return cmd_quickcheck()

    print(HELP)
    return EXIT_FAIL

if __name__ == "__main__":
    sys.exit(main(sys.argv))