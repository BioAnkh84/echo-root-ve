#!/usr/bin/env python3
import sys
from typing import List
EXIT_OK = 0
EXIT_FAIL = 1
HELP = """Vulpine Echo (Python core)
Usage:
  ve_kernel.py status
  ve_kernel.py exec '<payload>'
  ve_kernel.py audit
  ve_kernel.py audit-verbose
"""
def print_ready(): print("READY")
def run_audit(verbose: bool):
    if verbose:
        print("one=one"); print("two=two")
def do_exec(payload: str) -> int:
    if not payload or not payload.strip():
        print("Error: exec requires a payload", file=sys.stderr)
        return EXIT_FAIL
    s = payload.strip()
    if s.lower().startswith("echo:"):
        print(s[5:].lstrip()); return EXIT_OK
    if s.lower().startswith("py:"):
        expr = s[3:].lstrip()
        try:
            val = eval(expr, {"__builtins__": {}}, {})
            print(val); return EXIT_OK
        except SyntaxError:
            ns={"__builtins__": {}}
            try:
                exec(expr, ns, ns)
                if "result" in ns: print(ns["result"])
                return EXIT_OK
            except Exception as e:
                print(f"Error (exec): {e}", file=sys.stderr)
                return EXIT_FAIL
        except Exception as e:
            print(f"Error (eval): {e}", file=sys.stderr)
            return EXIT_FAIL
    print(s); return EXIT_OK
def main(argv: List[str]) -> int:
    if len(argv) < 2: print(HELP); return EXIT_FAIL
    c = argv[1].lower()
    if c=="status": print_ready(); return EXIT_OK
    if c=="exec":
        if len(argv)<3:
            print("Error: exec requires a payload", file=sys.stderr)
            return EXIT_FAIL
        payload=" ".join(argv[2:])
        return do_exec(payload)
    if c=="audit": run_audit(False); return EXIT_OK
    if c=="audit-verbose": run_audit(True); return EXIT_OK
    print(HELP); return EXIT_FAIL
if __name__=="__main__": sys.exit(main(sys.argv))
