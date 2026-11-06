# Regeneration checks in agent rounds run in a scratch worktree, never in place

Date: 2026-11-05. Branch: `qc/batch-1-farm-design-tool-placement`.

## Finding

A regeneration run inside the main working tree was killed between its two
GA_CHECK writer stages (`docs-authority/_ga_check.py` and
`docs-authority/_cad_clash.py`). The published page was left with the
envelope sections only, and the truncation read as a deliberate edit. The
page was restored by a full scratch regeneration, not by hand.

## Decision

1. An OpenCode round does not run the regenerator (`python3 -m
   flow_graph.param.regen`) in the main working tree. Every regeneration
   check goes through `scripts/check_all.sh --full`, which runs
   `flow_graph/check_regen_idempotent.py`: a temporary worktree is
   regenerated from the committed state and compared with it, so the working
   tree is never the write target.
2. A regeneration that has started is never killed. It is left to finish or
   fail on its own, and its receipt is read afterwards.

## Where the rule is written

`AGENTS.md`, new section "OpenCode rounds"; `CONTRIBUTING.md`, new section
"Regeneration during agent and automation rounds".

## Checks

This commit changes instructions only, so its check is the standing
documentation one: `scripts/check_all.sh` passed (tests, staleness,
authority contract, citations, style) after the commit, and the follow-up
`--full` run before the next stop re-proves the tree against a scratch
regeneration.
