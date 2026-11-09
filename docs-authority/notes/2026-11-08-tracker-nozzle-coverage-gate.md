# 2026-11-08: the tracker checks nozzle schedule coverage

This record states what changed and why. The occasion is the EW rebuild record of
today: EW_2's build had dropped its DN50 launder-discharge row while the tracker
reported the unit green. The tracker (`models/mfg/tracker.py --check`) compared the
row count in `params.json` against the schedule CSV; it never opened `check.json` -
the record the builder writes at acceptance - so a builder that failed to draw or
carry a scheduled row passed every gate.

## The new check

For every unit that has a build export and a nozzle schedule, the tracker now reads
the unit's `check.json` and requires the `nozzles_drawn` section to account for every
row of `docs-authority/nozzles/<unit>.csv`. Three failure wordings:

- "schedule rows not drawn or carried: ..." - the record exists but lists a subset of
  the schedule.
- "check.nozzles_drawn tags not in the schedule: ..." - the record lists rows the
  schedule does not carry.
- "check.json does not record nozzle coverage (no nozzles_drawn section)" - the
  record predates the section and cannot answer the question.

The check only runs where a `check.json` exists; units without a build export were
never in scope of the nozzle check.

## What the check found on its first pass

Named failures go from 7 units to 45. Besides the 7 bounding-box holds, the gate
exposes three classes of pre-existing gaps:

- 24 units whose `check.json` has no `nozzles_drawn` section (an older acceptance
  record; the builders predate the section).
- 15 units missing one to three cable or solids rows - all added to the schedules by
  the 2026-11-03 terminal-service-rows round, whose builders predate the carry idiom.
  Cables are not drawn by design, so these are record gaps, not missing geometry.
- 3 piped rows in the header schedules that their builders' records do not account
  for: HDR_H2 N17 (ZNBR2 hydrogen strip), HDR_N2 N2 (sweep nitrogen) and HDR_N2 N14
  (aisle make-up air). Unlike the cable rows these are piped connections, so each may
  be a genuinely unbuilt connection; they need per-unit review.

The repair of the 44 units is not part of this change; the gate makes the work
visible and countable.
