# Owner decisions of 5 November 2026 (8:20 PM CT)

Mike Matthews ruled the open design and process questions below. The rulings
are recorded here and, where a question number exists, in
`docs-authority/OPEN_QUESTIONS.md` (AQS-OQ-001 Rev G). No graph, driver, duty,
sizing, model or view file changed in this commit; the sizing lanes and the
approved next rounds follow the order at the end of this note.

## Q-038 Electrowinning cascade sizing

CLOSED (owner, 2026-11-05). The cascade is sized by a parametric algorithm.
Cathode count, frame current and power are sizing outputs. Hardware snaps to
commercial standard sizes. The design does not lock a fixed choice between the
reference-point option and the bounding-envelope option of the 2026-11-04
decision brief; the algorithm computes the sizes from need under the standing
plant rules (AGENTS.md sizing rule; AQS-ASSAY-001). Graph and driver edits
follow in the Q-038 sizing lane after the cryogenic BOM round.

## Electrowinning selective versus merged minor-metal cells

CLOSED (owner, 2026-11-05). Decide from first principles (electrochemistry,
current density, selectivity, mass transfer and energy). If that analysis does
not yield a clear winner, carry both arrangements as selectable options in the
design data. Gold and silver stay on their own cells. Work follows after Q-038.

## Q-040 BACKUP_GEN rating

CLOSED (owner, 2026-11-05) for the generator rating. The standby generator
rating is parametric from the live critical-load list under AQS-ELEC-007 /
AQS-RED-001 (125 percent, rounded up in 5 kW steps), not a hard-coded
nameplate in the driver file. The pumped-hydro store basis remains the Q-009
ruling as already stated on Q-040. Graph edits follow in the BACKUP_GEN sizing
lane after the EW cell work.

## qa-audit branch

CLOSED (owner, 2026-11-05) on method. Merge the best engineering content from
`qa-audit` into the feature branch by a strategic review, not a mechanical
replay of every commit. No force-push. Timing: after Q-038, EW cells and
BACKUP_GEN.

## Pipeline simplification steps 2 to 7

APPROVED (owner, 2026-11-05). Steps 2 to 7 of
`docs-authority/notes/2026-11-04-pipeline-simplification-plan.md` may proceed,
consistent with the other rulings on this page. Timing: after qa-audit.

## Push of qc/batch-1-farm-design-tool-placement

APPROVED (owner, 2026-11-05). Fast-forward push to origin, including Git LFS
objects. Confirm origin tip is still `789c05529` and is an ancestor of HEAD
before the push. Never push `refs/review-backup/*`, the stashes, or `eca4e87`.
Do not force-push. The merge of this branch into `main` still needs a separate
owner go. Report the resulting tip hash and any LFS or quota errors.

## Cryogenic BOM follow-ups (QC proposals)

APPROVED (owner, 2026-11-05) as the next engineering round after the push:

1. CRYO_O2 and CRYO_CO2: correct the row-2 saddle double-cost the same way
   CRYO_H2 was corrected (frame-only on the frame row; saddles priced once).
2. CRYO_H2, CRYO_O2 and CRYO_CO2: derive the tier or row grid from the booked
   tube data so drawn solids match the booked count; replace the hard-coded
   `TIERS = N_TUBES // (HALVES * 4)` pattern.

## Work order after this record

1. Finish the atomic GA_CHECK / regen-ban process commits and their QC handoff
   (done at tip before this note if already landed).
2. Push the feature branch tip (this note included) under the push ruling.
3. Cryogenic BOM round (O2/CO2 saddles; H2/O2/CO2 tier grid), then QC.
4. Q-038 sizing lane, then EW selective-versus-merged, then BACKUP_GEN.
5. qa-audit strategic merge; then pipeline steps 2 to 7.
6. Push small batches after each QC pass. No force-push.

## Changed files in the decision commit

- `docs-authority/OPEN_QUESTIONS.md`: Rev G; Q-038 and Q-040 closed; Q-041 added
  and closed for selective versus merged EW cells.
- `docs-authority/DOC_REGISTER.md`: regenerated for AQS-OQ-001 Rev G.
- This note.
