#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LEDGER="$ROOT_DIR/ve_ledger.jsonl"
POLICY_FILE="$ROOT_DIR/policies/ve_policy.json"
CHECKPOINT_DIR="$ROOT_DIR/checkpoints"
SECRETS_DIR="$ROOT_DIR/secrets"
SHARED_KEY_FILE="$SECRETS_DIR/ve_shared.key"

mkdir -p "$ROOT_DIR/policies" "$ROOT_DIR/checkpoints" "$ROOT_DIR/secrets"

get_policy_hash() {
  if [[ -f "$POLICY_FILE" ]]; then
    sha256sum "$POLICY_FILE" | awk '{print $1}'
  else
    echo "no-policy"
  fi
}

get_ve_secret() {
  if [[ -f "$SHARED_KEY_FILE" ]]; then
    cat "$SHARED_KEY_FILE"
  else
    echo ""
  fi
}

write_ledger() {
  local status="$1"
  local action="$2"
  local msg="$3"
  local ts
  ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  local ph
  ph="$(get_policy_hash)"
  printf '{"ts":"%s","status":"%s","action":"%s","policy_hash":"%s","msg":"%s"}\n' \
    "$ts" "$status" "$action" "$ph" "$msg" >> "$LEDGER"
}

new_vecrosstalk_envelope() {
  local payload_json="$1"
  local ts
  ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  local ph
  ph="$(get_policy_hash)"
  local nonce
  nonce="$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid)"
  local secret
  secret="$(get_ve_secret)"

  local body
  body=$(printf '{"ver":1,"ts":"%s","policy_hash":"%s","nonce":"%s","payload":%s}' \
    "$ts" "$ph" "$nonce" "$payload_json")

  local sig=""
  if [[ -n "$secret" ]]; then
    sig="$(printf '%s' "$body" | openssl dgst -sha256 -hmac "$secret" 2>/dev/null | awk '{print $2}')"
  fi

  printf '{"ver":1,"ts":"%s","policy_hash":"%s","nonce":"%s","payload":%s,"sig":"%s"}\n' \
    "$ts" "$ph" "$nonce" "$payload_json" "$sig"
}

do_audit() {
  local qc="$ROOT_DIR/QUICKCHECK_LOGS"
  if [[ -d "$qc" ]]; then
    echo "[AUDIT] OK"
    write_ledger "ok" "audit" "QUICKCHECK_LOGS present"
    exit 0
  else
    echo "[AUDIT] missing QUICKCHECK_LOGS"
    write_ledger "fail" "audit" "QUICKCHECK_LOGS missing"
    exit 20
  fi
}

do_revert() {
  local seq="${1:-0}"
  local cp="$CHECKPOINT_DIR/cp_${seq}.json"
  if [[ ! -s "$cp" ]]; then
    echo "[REVERT] no checkpoint"
    write_ledger "fail" "revert" "no checkpoint for seq=$seq"
    exit 1
  fi
  echo "[REVERT] restored seq=$seq"
  write_ledger "ok" "revert" "restored seq=$seq"
  exit 0
}

do_exec() {
  local envelope=0
  if [[ $# -gt 0 && "$1" == "--envelope" ]]; then
    envelope=1
    shift
  fi

  if [[ $# -eq 0 ]]; then
    echo "VE kernel (linux): empty exec command"
    write_ledger "fail" "exec" "empty exec command"
    exit 1
  fi

  local out rc
  out="$("$@" 2>&1)" || rc=$?
  rc=${rc:-0}

  if [[ $rc -ne 0 ]]; then
    echo "$out"
    write_ledger "fail" "exec" "rc=$rc; out=$out"
    if [[ $envelope -eq 1 ]]; then
      if command -v jq >/dev/null 2>&1; then
        new_vecrosstalk_envelope "$(printf '{"rc":%d,"out":%s}' "$rc" "$(printf '%s' "$out" | jq -Rs .)")"
      else
        new_vecrosstalk_envelope "$(printf '{"rc":%d,"out":"%s"}' "$rc" "$out")"
      fi
    fi
    exit "$rc"
  else
    if [[ $envelope -eq 1 ]]; then
      if command -v jq >/dev/null 2>&1; then
        new_vecrosstalk_envelope "$(printf '{"rc":0,"out":%s}' "$(printf '%s' "$out" | jq -Rs .)")"
      else
        new_vecrosstalk_envelope "$(printf '{"rc":0,"out":"%s"}' "$out")"
      fi
    else
      echo "$out"
    fi
    write_ledger "ok" "exec" "rc=0; out=$out"
    exit 0
  fi
}

MODE="${1:-help}"
shift || true

case "$MODE" in
  audit)
    do_audit
    ;;
  revert)
    do_revert "$@"
    ;;
  policy-hash)
    get_policy_hash
    ;;
  exec)
    do_exec "$@"
    ;;
  *)
    cat <<EOF
Vulpine Echo (Linux) kernel
  ./ve_kernel.sh exec <cmd...>
  ./ve_kernel.sh exec --envelope <cmd...>
  ./ve_kernel.sh audit
  ./ve_kernel.sh revert <seq>
  ./ve_kernel.sh policy-hash
EOF
    ;;
esac
