from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_EXCLUDES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ve_logs",
    ".ve_snapshots",
    "archive",
    "ve_data",
}


@dataclass(frozen=True)
class RepoMapEntry:
    path: str
    kind: str
    size: int


def should_exclude(path: Path, root: Path, excludes: set[str]) -> bool:
    relative_parts = path.relative_to(root).parts
    if any(part in excludes for part in relative_parts):
        return True
    if len(relative_parts) >= 2 and relative_parts[0] == "receipts":
        name = relative_parts[-1]
        return name.endswith(".jsonl") or (name.startswith("repo_map_") and name.endswith(".json"))
    return False


def build_repo_map(root: Path, depth: int = 3, excludes: set[str] | None = None) -> list[RepoMapEntry]:
    root = root.resolve()
    excludes = set(DEFAULT_EXCLUDES if excludes is None else excludes)
    entries: list[RepoMapEntry] = []

    for item in sorted(root.rglob("*"), key=lambda value: value.relative_to(root).as_posix().lower()):
        if should_exclude(item, root, excludes):
            continue
        relative = item.relative_to(root)
        if len(relative.parts) > depth:
            continue
        kind = "dir" if item.is_dir() else "file"
        size = 0 if item.is_dir() else item.stat().st_size
        entries.append(RepoMapEntry(relative.as_posix(), kind, size))

    return entries


def canonical_map(entries: list[RepoMapEntry]) -> str:
    rows = [entry.__dict__ for entry in entries]
    return json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def map_hash(entries: list[RepoMapEntry]) -> str:
    return hashlib.sha256(canonical_map(entries).encode("utf-8")).hexdigest()


def entries_to_rows(entries: list[RepoMapEntry]) -> list[dict[str, Any]]:
    return [entry.__dict__ for entry in entries]


def rows_to_entries(rows: list[dict[str, Any]]) -> list[RepoMapEntry]:
    return [RepoMapEntry(path=str(row["path"]), kind=str(row["kind"]), size=int(row["size"])) for row in rows]


def build_snapshot(root: Path, depth: int, entries: list[RepoMapEntry], excludes: set[str]) -> dict[str, Any]:
    return {
        "snapshot_type": "repo_map_snapshot",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "root_name": root.resolve().name,
        "depth": depth,
        "excludes": sorted(excludes),
        "entry_count": len(entries),
        "map_hash": map_hash(entries),
        "entries": entries_to_rows(entries),
    }


def write_snapshot(path: Path, snapshot: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_snapshot(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_delta_receipt(previous_snapshot: dict[str, Any], current_snapshot: dict[str, Any]) -> dict[str, Any]:
    previous_entries = {entry.path: entry for entry in rows_to_entries(previous_snapshot.get("entries", []))}
    current_entries = {entry.path: entry for entry in rows_to_entries(current_snapshot.get("entries", []))}

    previous_paths = set(previous_entries)
    current_paths = set(current_entries)
    added = sorted(current_paths - previous_paths)
    removed = sorted(previous_paths - current_paths)
    kind_changed = []
    size_changed = []

    for path in sorted(previous_paths & current_paths):
        previous = previous_entries[path]
        current = current_entries[path]
        if previous.kind != current.kind:
            kind_changed.append({"path": path, "previous": previous.kind, "current": current.kind})
        elif previous.size != current.size:
            size_changed.append({"path": path, "previous": previous.size, "current": current.size})

    return {
        "receipt_type": "repo_map_delta",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "root_name": current_snapshot.get("root_name", ""),
        "previous_hash": previous_snapshot.get("map_hash", ""),
        "current_hash": current_snapshot.get("map_hash", ""),
        "previous_entry_count": int(previous_snapshot.get("entry_count", 0)),
        "current_entry_count": int(current_snapshot.get("entry_count", 0)),
        "added": added,
        "removed": removed,
        "kind_changed": kind_changed,
        "size_changed": size_changed,
        "unchanged_paths": len((previous_paths & current_paths) - {item["path"] for item in kind_changed} - {item["path"] for item in size_changed}),
        "claim_boundary": "Structure delta only. Size changes are not proof of semantic content changes; unchanged size is not proof of unchanged content.",
    }


def render_text(entries: list[RepoMapEntry]) -> str:
    lines: list[str] = []
    for entry in entries:
        label = "/" if entry.kind == "dir" else ""
        size = "" if entry.kind == "dir" else f" {entry.size}B"
        lines.append(f"{entry.path}{label}{size}")
    return "\n".join(lines)


def build_receipt(root: Path, depth: int, entries: list[RepoMapEntry], excludes: set[str]) -> dict:
    return {
        "receipt_type": "repo_map",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "root_name": root.resolve().name,
        "depth": depth,
        "excludes": sorted(excludes),
        "entry_count": len(entries),
        "map_hash": map_hash(entries),
        "orientation_use": "Use this as a human/AI repo-shape receipt before deeper search. It is not proof of file health or freshness.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic repo map receipt")
    parser.add_argument("--root", default=".")
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--json", action="store_true", help="Print receipt JSON instead of text map")
    parser.add_argument("--write-snapshot", help="Write full repo-map snapshot JSON for later delta comparison")
    parser.add_argument("--delta-from", help="Compare current map against a previous snapshot JSON")
    args = parser.parse_args()

    root = Path(args.root)
    excludes = set(DEFAULT_EXCLUDES)
    excludes.update(args.exclude)
    entries = build_repo_map(root, depth=args.depth, excludes=excludes)
    snapshot = build_snapshot(root, args.depth, entries, excludes)

    if args.write_snapshot:
        write_snapshot(Path(args.write_snapshot), snapshot)

    if args.delta_from:
        delta = build_delta_receipt(read_snapshot(Path(args.delta_from)), snapshot)
        print(json.dumps(delta, indent=2, sort_keys=True))
        return 0

    if args.json:
        print(json.dumps(build_receipt(root, args.depth, entries, excludes), indent=2, sort_keys=True))
    else:
        print(render_text(entries))
        print()
        print(json.dumps(build_receipt(root, args.depth, entries, excludes), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
