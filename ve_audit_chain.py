from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AuditRecord:
    ts: str
    event_type: str
    actor: str
    payload: dict
    hash_prev: str
    hash_self: str
    signature: str


def canonical(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()


def sign(payload_hash: str, key: str) -> str:
    return hmac.new(key.encode("utf-8"), payload_hash.encode("utf-8"), hashlib.sha256).hexdigest()


def last_hash(path: Path) -> str:
    if not path.exists():
        return "0" * 64
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return "0" * 64
    return json.loads(lines[-1])["hash_self"]


@contextmanager
def audit_lock(path: Path, timeout_seconds: float = 5.0):
    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout_seconds
    handle = None
    while handle is None:
        try:
            handle = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"timeout acquiring audit lock: {lock_path}")
            time.sleep(0.05)
    try:
        os.write(handle, str(os.getpid()).encode("utf-8"))
        yield
    finally:
        os.close(handle)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def append_audit_record(path: Path, event_type: str, actor: str, payload: dict, signing_key: str) -> AuditRecord:
    with audit_lock(path):
        previous_hash = last_hash(path)
        body = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "actor": actor,
            "payload": payload,
            "hash_prev": previous_hash,
        }
        hash_self = sha256(body)
        signature = sign(hash_self, signing_key)
        record = AuditRecord(**body, hash_self=hash_self, signature=signature)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(record), sort_keys=True) + "\n")
        return record


def verify_audit_chain(path: Path, signing_key: str) -> bool:
    expected_prev = "0" * 64
    if not path.exists():
        return True
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            if item["hash_prev"] != expected_prev:
                return False
            body = {
                "ts": item["ts"],
                "event_type": item["event_type"],
                "actor": item["actor"],
                "payload": item["payload"],
                "hash_prev": item["hash_prev"],
            }
            expected_hash = sha256(body)
            if item["hash_self"] != expected_hash:
                return False
            if item["signature"] != sign(expected_hash, signing_key):
                return False
            expected_prev = item["hash_self"]
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="VE append-only signed audit chain")
    parser.add_argument("--ledger", default="ve_data/audit_chain.jsonl")
    parser.add_argument("--signing-key-env", default="VE_AUDIT_SIGNING_KEY")
    sub = parser.add_subparsers(dest="command", required=True)

    append = sub.add_parser("append")
    append.add_argument("--event-type", required=True)
    append.add_argument("--actor", required=True)
    append.add_argument("--payload-json", required=True)

    sub.add_parser("verify")

    args = parser.parse_args()
    signing_key = os.environ.get(args.signing_key_env, "demo-local-signing-key")
    path = Path(args.ledger)
    if args.command == "append":
        record = append_audit_record(path, args.event_type, args.actor, json.loads(args.payload_json), signing_key)
        print(json.dumps(asdict(record), indent=2))
        return 0
    ok = verify_audit_chain(path, signing_key)
    print(json.dumps({"ok": ok}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
