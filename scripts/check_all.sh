#!/usr/bin/env bash
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
#
# Run every check a change must pass before it is submitted. The checks run on
# the contributor's own machine; the project uses no hosted build service.
#
#   scripts/check_all.sh          tests, staleness, authority contract, citations, style
#   scripts/check_all.sh --full   the same, then a full regeneration of HEAD twice
#                                 (slow; commit first)
#
# Exit status is non-zero if any check fails.
set -u
cd "$(dirname "$0")/.." || exit 2

full=0
for arg in "$@"; do
  case "$arg" in
    --full) full=1 ;;
    -h|--help) sed -n '5,12p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

failed=()
run() {
  local name="$1"; shift
  echo "== $name: $*"
  if "$@"; then echo "   pass"; else echo "   FAIL"; failed+=("$name"); fi
}

run tests               python3 -m pytest -q flow_graph/
run staleness           python3 -m flow_graph.param.regen --check
run authority-contract  python3 flow_graph/check_authority_contract.py
run citations           python3 -m flow_graph.check_citations
run doc-style           python3 -m flow_graph.check_doc_style
if [ "$full" = 1 ]; then
  run regen-idempotent  python3 flow_graph/check_regen_idempotent.py
fi

if [ "${#failed[@]}" -gt 0 ]; then
  echo "Failed: ${failed[*]}"
  exit 1
fi
echo "All checks passed."
