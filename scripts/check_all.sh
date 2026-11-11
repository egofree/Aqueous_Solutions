#!/usr/bin/env bash
# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
#
# Run every check a change must pass before it is submitted. The checks run on
# the contributor's own machine; the project uses no hosted build service.
#
#   scripts/check_all.sh          commit identity, tests, staleness, authority contract,
#                                 citations, style
#   scripts/check_all.sh --full   the same, then a full regeneration of HEAD twice and a
#                                 CAD-lane rebuild gated byte for byte (slow; commit first)
#
# Exit status is non-zero if any check fails.
set -u
cd "$(dirname "$0")/.." || exit 2

full=0
for arg in "$@"; do
  case "$arg" in
    --full) full=1 ;;
    -h|--help) sed -n '5,13p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

failed=()
run() {
  local name="$1"; shift
  echo "== $name: $*"
  if "$@"; then echo "   pass"; else echo "   FAIL"; failed+=("$name"); fi
}

check_identity() {
  # A commit must carry a real author identity. A placeholder address left in a
  # machine-wide Git setting is rejected here before it reaches the history.
  local email
  email="$(git config user.email || true)"
  if [ -z "$email" ]; then echo "   git user.email is not set"; return 1; fi
  case "$email" in
    *@example.com|*@example.org|*@example.net|*@local|*@localhost|*.local)
      echo "   git user.email '$email' is a placeholder; set your own identity"; return 1 ;;
  esac
}

cad_snapshot() {
  # sha256 over the declared CAD outputs (manifest stage cad_mfg_models) of the tree at $1.
  ( cd "$1" && find models/mfg \( -path '*/export/*' -o -path '*/drawings/*' \) -type f \
      | sort | xargs -r sha256sum ) 2>/dev/null
}

cad_outputs() {
  # CAD-lane regeneration gate (F-20261110-12): rebuild the CAD lane from HEAD in a
  # temporary worktree and compare every declared CAD output byte for byte against the
  # committed tree. The stage takes the design lock itself (flow_graph.param.design_lock);
  # this script never shell-wraps flock around it.
  if ! python3 -c 'import cadquery' 2>/dev/null; then
    echo "   cadquery not importable; the pipeline would skip the stage too - not checked"
    return 0
  fi
  local tmp wt before after
  tmp="$(mktemp -d "${TMPDIR:-/tmp}/aqs-cad-gate-XXXXXX")" || return 1
  wt="$tmp/wt"
  if ! git worktree add --detach "$wt" HEAD >/dev/null 2>&1; then
    echo "   cannot create the temporary worktree (commit first, as --full requires)"
    rm -rf "$tmp"; return 1
  fi
  before="$(cad_snapshot "$wt")"
  if ! ( cd "$wt" && python3 -m flow_graph.param.regen --stage cad_mfg_models ) >"$tmp/build.log" 2>&1; then
    echo "   CAD lane build failed; log tail:"
    tail -15 "$tmp/build.log" | sed 's/^/     /'
    git worktree remove --force "$wt" >/dev/null 2>&1; rm -rf "$tmp"; return 1
  fi
  after="$(cad_snapshot "$wt")"
  git worktree remove --force "$wt" >/dev/null 2>&1
  rm -rf "$tmp"
  if [ "$before" != "$after" ]; then
    echo "   rebuilt CAD lane differs from the committed tree:"
    diff <(printf '%s\n' "$before") <(printf '%s\n' "$after") \
      | grep -E '^[<>]' | awk '{print "     " $2}' | sort -u | head -25
    echo "   ($(diff <(printf '%s\n' "$before") <(printf '%s\n' "$after") \
      | grep -cE '^[<>]') changed or missing declared output(s); rebuild and commit)"
    return 1
  fi
}

run commit-identity     check_identity
run tests               python3 -m pytest -q flow_graph/
run staleness           python3 -m flow_graph.param.regen --check
run authority-contract  python3 flow_graph/check_authority_contract.py
run citations           python3 -m flow_graph.check_citations
run doc-style           python3 -m flow_graph.check_doc_style
if [ "$full" = 1 ]; then
  run regen-idempotent  python3 flow_graph/check_regen_idempotent.py
  run cad-outputs       cad_outputs
fi

if [ "${#failed[@]}" -gt 0 ]; then
  echo "Failed: ${failed[*]}"
  exit 1
fi
echo "All checks passed."
