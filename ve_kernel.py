#!/usr/bin/env python3
import sys, re, ast

EXIT_OK=0; EXIT_LIT_A=10; EXIT_LIT_B=11; EXIT_ERR=99

def resolve(cmd: str):
    s = cmd.strip()
    # strip common echo-style prefixes
    m = re.match(r'^\s*(?:Write-Output|Write-Host|Echo)\s+(.+)$', s, re.I)
    if m:
        s = m.group(1).strip()

    # fully-quoted string?
    if (len(s) >= 2) and ((s[0]==s[-1]) and s[0] in ('"', "'")):
        return s[1:-1]

    # try Python literal first (e.g., "hello", 123, ["a","b"])
    try:
        lit = ast.literal_eval(s)
        return str(lit)
    except Exception:
        pass

    # last resort: safe-ish eval of simple expressions (no builtins)
    try:
        val = eval(s, {"__builtins__": None}, {})
        return "" if val is None else str(val)
    except Exception as e:
        raise RuntimeError(str(e))

def cmd_status():
    print("READY")
    return EXIT_OK

def cmd_exec(argv):
    if not argv:
        print('usage: ve_kernel.py exec "<command>"', file=sys.stderr)
        return 2
    cmd = " ".join(argv)
    try:
        out = resolve(cmd)
        if out:
            print(out)
        return EXIT_OK
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1

def cmd_audit():
    try:
        if resolve('"one"') != 'one': return EXIT_LIT_A
        if resolve('"two"') != 'two': return EXIT_LIT_B
        return EXIT_OK
    except Exception:
        return EXIT_ERR

def cmd_audit_verbose():
    a = b = "__ERR__"
    try: a = resolve('"one"')
    except: pass
    try: b = resolve('"two"')
    except: pass
    print(f"one={a}")
    print(f"two={b}")
    return EXIT_OK

def main():
    if len(sys.argv) < 2:
        print("usage: ve_kernel.py [status|exec|audit|audit-verbose]")
        return 2
    sub = sys.argv[1].lower()
    rest = sys.argv[2:]
    if   sub == "status":          return cmd_status()
    elif sub == "exec":            return cmd_exec(rest)
    elif sub == "audit":           return cmd_audit()
    elif sub in ("audit-verbose","auditv"):
        return cmd_audit_verbose()
    else:
        print("usage: ve_kernel.py [status|exec|audit|audit-verbose]")
        return 2

if __name__ == "__main__":
    sys.exit(main())