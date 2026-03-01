#!/usr/bin/env bash
# CI-safe: ensure QUICKCHECK_LOGS is non-empty and exists (handles empty or unset)
ensure_quickcheck_logs() {
  if [ -z "" ]; then
    QUICKCHECK_LOGS="E:\Echo_Nexus_Data\repos\echo-root-ve/.ve_logs/quickcheck"
  fi
  mkdir -p ""
}

# CI-safe default: ensure QUICKCHECK_LOGS exists
: ""
mkdir -p ""

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KERNEL="$HERE/ve_kernel.sh"

CMD="${1:-help}"
shift || true

case "$CMD" in
  run)
    USE_ENV=0
    if [[ $# -gt 0 && "$1" == "--envelope" ]]; then
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
    "$KERNEL" audit
    ;;
  revert)
    SEQ="${1:-0}"
    "$KERNEL" revert "$SEQ"
    ;;
  policy-hash)
    "$KERNEL" policy-hash
    ;;
  *)
    cat <<EOF
VE interface (Linux)
  ./ve_parse.sh run <cmd...>
  ./ve_parse.sh run --envelope <cmd...>
  ./ve_parse.sh audit
  ./ve_parse.sh revert <seq>
  ./ve_parse.sh policy-hash
EOF
    ;;
esac