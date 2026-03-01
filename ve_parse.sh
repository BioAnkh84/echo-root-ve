#!/usr/bin/env bash

# CI-safe default: ensure QUICKCHECK_LOGS exists
: ""
mkdir -p ""

set -euo pipefail

ensure_quickcheck_logs() {
  if [ -z "${QUICKCHECK_LOGS:-}" ]; then
    local workspace="${GITHUB_WORKSPACE:-$(pwd)}"
    QUICKCHECK_LOGS="${workspace}/.ve_logs/quickcheck"
  fi
  export QUICKCHECK_LOGS
  mkdir -p "$QUICKCHECK_LOGS"
}

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KERNEL="$HERE/ve_kernel.sh"

CMD="${1:-help}"
shift || true

case "$CMD" in
  run)
    USE_ENV=0
    if [[ $# -gt 0 && "${1:-}" == "--envelope" ]]; then
      USE_ENV=1
      shift
    fi
    if [[ $# -eq 0 ]]; then
      echo "VE (linux): no command provided to run"
      exit 1
    fi
    if [[ $USE_ENV -eq 1 ]]; then
      "$KERNEL" exec --envelope "$@"
    else
      "$KERNEL" exec "$@"
    fi
    ;;
  audit)
    ensure_quickcheck_logs || true

    set +e
    "$KERNEL" audit
    rc=$?
    set -e

    # CI soft-fail mode (only active if explicitly enabled)
    if [[ ${VE_CI_SOFT_AUDIT:-0} -eq 1 && $rc -eq 20 ]]; then
      echo "[AUDIT] WARN (soft): missing QUICKCHECK_LOGS (rc=20) — continuing due to VE_CI_SOFT_AUDIT=1"
      exit 0
    fi

    exit $rc
    ;;
  revert)
    SEQ="${1:-0}"
    "$KERNEL" revert "$SEQ"
    ;;
  policy-hash)
    "$KERNEL" policy-hash
    ;;
  *)
    cat <<'EOF'
VE interface (Linux)
  ./ve_parse.sh run <cmd...>
  ./ve_parse.sh run --envelope <cmd...>
  ./ve_parse.sh audit
  ./ve_parse.sh revert <seq>
  ./ve_parse.sh policy-hash
EOF
    ;;
esac