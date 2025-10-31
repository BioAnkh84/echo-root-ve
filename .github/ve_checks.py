import json, hashlib, os, sys, re, glob

FAIL = 1

def sha256(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

logs = sorted(glob.glob("QUICKCHECK_LOGS/*.jsonl"))
if not logs:
    print("FAIL: no QUICKCHECK_LOGS/*.jsonl found"); sys.exit(FAIL)

for p in logs:
    if os.path.getsize(p) == 0:
        print(f"FAIL: empty log: {p}"); sys.exit(FAIL)
    if os.path.getsize(p) > 5 * 1024 * 1024:
        print(f"FAIL: log too large (>5MB): {p}"); sys.exit(FAIL)
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except Exception as e:
                print(f"FAIL: non-JSON line in {p} at {i}: {e}")
                sys.exit(FAIL)

man = "SHA256_MANIFEST.txt"
if not os.path.exists(man):
    print("FAIL: missing manifest"); sys.exit(FAIL)

manifest = {}
for line in open(man, "r", encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"): continue
    parts = line.split()
    if len(parts) == 2:
        manifest[parts[0]] = parts[1]

for p in logs:
    rel = p.replace("\\","/")
    h = sha256(p)
    want = manifest.get(rel)
    if not want:
        print(f"FAIL: {rel} not in manifest"); sys.exit(FAIL)
    if h.lower() != want.lower():
        print(f"FAIL: hash mismatch for {rel}\n got={h}\n want={want}")
        sys.exit(FAIL)

bad_ps = re.compile(r"\bGet-Random\b", re.I)
if os.path.exists("ve_kernel.ps1"):
    s = open("ve_kernel.ps1","r",encoding="utf-8",errors="ignore").read()
    if bad_ps.search(s):
        print("FAIL: RNG usage in safety path: ve_kernel.ps1"); sys.exit(FAIL)

ok = False
for fname in ["ve_kernel.ps1","ve_kernel.py","ve_kernel.sh"]:
    if os.path.exists(fname):
        text = open(fname,"r",encoding="utf-8",errors="ignore").read().lower()
        if "policy_hash" in text or "policy-hash" in text:
            ok = True
if not ok:
    print("FAIL: policy_hash() not present"); sys.exit(FAIL)

print("PASS: PR policy checks")
