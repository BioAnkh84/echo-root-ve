import argparse, json, hashlib, os, sys

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def build_manifest(root):
    root = os.path.abspath(root)
    out = []
    if not os.path.isdir(root):
        return out
    for base, _, files in os.walk(root):
        for name in files:
            full = os.path.join(base, name)
            rel = os.path.relpath(full, root).replace("\\", "/")
            out.append({
                "path": rel,
                "size": os.path.getsize(full),
                "sha256": sha256_file(full),
            })
    out.sort(key=lambda x: x["path"])
    return out

def normalize_manifest(m):
    """
    Return a list of {path,size,sha256} entries, accepting:
      - list of dicts/strings,
      - dict with "path"/"size"/"sha256" (single entry),
      - dict with "files": [...],
      - dict mapping path -> {size,sha256} or string,
      - anything else -> [].
    """
    if m is None:
        return []

    # list of dicts/strings
    if isinstance(m, list):
        out = []
        for e in m:
            if isinstance(e, dict):
                p = e.get("path")
                if isinstance(p, str):
                    out.append({"path": p, "size": e.get("size"), "sha256": e.get("sha256")})
            elif isinstance(e, str):
                out.append({"path": e, "size": None, "sha256": None})
        out.sort(key=lambda x: x["path"])
        return out

    # dict that already looks like a single entry
    if isinstance(m, dict) and ("path" in m or "sha256" in m or "size" in m):
        p = m.get("path")
        if isinstance(p, str):
            return [{"path": p, "size": m.get("size"), "sha256": m.get("sha256")}]

    # dict with "files" → recurse
    if isinstance(m, dict) and "files" in m:
        return normalize_manifest(m["files"])

    # dict mapping path -> details/hash
    if isinstance(m, dict):
        out = []
        for k, v in m.items():
            if not isinstance(k, str):
                continue
            if isinstance(v, dict):
                out.append({"path": k, "size": v.get("size"), "sha256": v.get("sha256")})
            elif isinstance(v, str):
                out.append({"path": k, "size": None, "sha256": v})
            else:
                out.append({"path": k, "size": None, "sha256": None})
        out.sort(key=lambda x: x["path"])
        return out

    # last resort: single dict-like with .get
    if hasattr(m, "get"):
        p = m.get("path")
        if isinstance(p, str):
            return [{"path": p, "size": m.get("size"), "sha256": m.get("sha256")}]

    return []    # already a list of dicts/strings
    if isinstance(m, list):
        out = []
        for e in m:
            if isinstance(e, dict):
                p = e.get("path")
                if not isinstance(p, str):
                    continue
                out.append({
                    "path": p,
                    "size": e.get("size"),
                    "sha256": e.get("sha256"),
                })
            elif isinstance(e, str):
                out.append({"path": e, "size": None, "sha256": None})
        out.sort(key=lambda x: x["path"])
        return out

    # dict with "files" → recurse
    if isinstance(m, dict) and "files" in m:
        return normalize_manifest(m["files"])

    # dict mapping path -> details/hash
    if isinstance(m, dict):
        out = []
        for k, v in m.items():
            if not isinstance(k, str):
                continue
            if isinstance(v, dict):
                out.append({"path": k, "size": v.get("size"), "sha256": v.get("sha256")})
            elif isinstance(v, str):
                out.append({"path": k, "size": None, "sha256": v})
            else:
                out.append({"path": k, "size": None, "sha256": None})
        out.sort(key=lambda x: x["path"])
        return out

    # single dict-like object?
    if hasattr(m, "get"):
        p = m.get("path")
        if isinstance(p, str):
            return [{"path": p, "size": m.get("size"), "sha256": m.get("sha256")}]

    return []

def main():
    ap = argparse.ArgumentParser(description="Verify that ve_data matches a snapshot manifest.")
    ap.add_argument("--snap-root", default=".ve_snapshots", help="Snapshots directory (default: .ve_snapshots)")
    ap.add_argument("--seq", type=int, required=True, help="Sequence number of snapshot to verify against")
    ap.add_argument("--data-root", default="ve_data", help="Live data directory (default: ve_data)")
    args = ap.parse_args()

    snap_dir = os.path.join(args.snap_root, f"seq-{args.seq:04d}")
    manifest_path = os.path.join(snap_dir, "manifest.json")
    if not os.path.isfile(manifest_path):
        print(f"ERR: manifest not found: {manifest_path}")
        sys.exit(2)

    try:
        snap_raw = json.load(open(manifest_path, "r", encoding="utf-8-sig"))
    except Exception as e:
        print(f"ERR: cannot read manifest: {e}")
        sys.exit(2)

    snap_manifest = normalize_manifest(snap_raw)
    live_manifest = build_manifest(args.data_root)

    snap_ix = {e["path"]: e for e in snap_manifest}
    live_ix = {e["path"]: e for e in live_manifest}

    missing = sorted(set(snap_ix.keys()) - set(live_ix.keys()))
    extra   = sorted(set(live_ix.keys()) - set(snap_ix.keys()))
    changed = []
    for p in sorted(set(snap_ix.keys()) & set(live_ix.keys())):
        a, b = snap_ix[p], live_ix[p]
        # if snapshot lacks size/hash, treat as unknown (don't flag changed)
        if a.get("sha256") is None and a.get("size") is None:
            continue
        if a.get("sha256") != b.get("sha256") or a.get("size") != b.get("size"):
            changed.append(p)

    if not missing and not extra and not changed:
        print(f"OK: ve_data matches snapshot seq-{args.seq:04d} ({len(live_manifest)} files)")
        sys.exit(0)

    if missing:
        print("MISSING:", *missing, sep="\n  ")
    if extra:
        print("EXTRA:", *extra, sep="\n  ")
    if changed:
        print("CHANGED:", *changed, sep="\n  ")

    sys.exit(2)

if __name__ == "__main__":
    main()

