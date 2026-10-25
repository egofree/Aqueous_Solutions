# Localization merge, README note and documentation batch 20

Date: 2026-10-25. Scope: main after the docs-rewrite and localization branch merges; no graph topology change.

## Branch merges

- `origin/docs-rewrite` (20 commits, batches 1-19 of the documentation rewrite) merged to main; the single conflict was the generated derived-revisions register, resolved by regeneration. The two untracked working pages in the `docs-authority/` root were moved to `docs-authority/internal/` per the repository rule that agent-only material stays there; this also closed the last failing document-map check.
- `origin/localization` (28 commits, X-LOC-01 to X-LOC-06) merged to main. Their thirteen new open questions entered the register as Q-021 to Q-032; the documentation batch's own Q-020 kept its number and the localization batch's colliding Q-020 was renumbered Q-033, with the citing page updated. The full pipeline was regenerated after the merge; the baseline output moves stay within the recorded small deltas, and the reconciliation gate reports no move outside tolerance.

## Documentation batch 20 (all on main)

CO2_HEADER_DUTY (Rev D, updated to graph Rev AC through the extended header study; setpoint question recorded as Q-033), CAMPUS_PLAN (Rev C), CRYO_COLD_BOX (Rev D), ASME_CODE_INTENT (Rev D, through `_asme_class.py`), BALANCE_RECONCILIATION (Rev E, through `balance.py`; section renumbering chased into `closure_tf.py` and assumptions A-M-120/A-M-123). Glossary additions in the same changes: SG, PQ, BH, AUD. Fixed in passing: the assumptions-register scan crashed on any model `params.json` whose `assumptions` entry is a list; the CAST_LINE file was converted to the keyed form and the register runs again.

## README

Section 2.4 describes the site-profile system and the locale studies in progress; the status section points at it. The task plan now names the evidence for X-LOC-06 (`SITE_POWER.md`) instead of an empty evidence cell.

## Checks

`scripts/check_all.sh --full` run on the merged tree before this push: tests, staleness, authority contract, citations, documentation style, and the double full regeneration of the committed tree that must change nothing.
