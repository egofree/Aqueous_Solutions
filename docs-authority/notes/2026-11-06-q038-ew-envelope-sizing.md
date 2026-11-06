# 2026-11-06 Q-038 sizing lane: the EW cascade rated at the AQS-ASSAY-001 element envelope

This record states what the round changed and why, with the figures at the commit named
below. The owner ruling of 2026-11-05 (Q-038) directs a parametric algorithm whose cathode
counts, frame currents and power are sizing outputs, hardware snapped to commercial sizes,
computing the sizes from need under the standing plant rules (AGENTS.md sizing rule;
AQS-ASSAY-001). The graph, the drivers and the calculators changed together in one commit;
the regeneration ran in a scratch worktree and its result was committed, so the main working
tree was never the regenerator's write target.

## The sizing basis

Every cell is now rated for the largest deposit of its own element found in any feed case of
the IA-FEED-01 envelope (AQS-ASSAY-001 table 4.1), at the design feed rate and leach recovery
1.0 (new driver `ew_leach_recovery_design`; A-M-467 in the assumptions register). The five
minor plateable metals each carry the lumped fraction - the all-in-one-element reading of
table 4.1. The machine copy of the envelope now lives on the graph edge
(`params.assay_envelope.element_envelope`), where `solver.ew()`, `docs-authority/_ew_sizing.py`
and `flow_graph/param/write_graph.py` read it. The booked stream rates stay at the reference
S08 rows (solver.ew_products): a balance closes on one feed, the envelope sizes the equipment,
so no class B lot forces a resize.

## Results at the envelope

- Cell currents (A): EW_1 0.31, EW_2 1.00, EW_3 679.3, EW_4 52.1, EW_5 90.9, EW_6 183.9,
  EW_7 1207.8, EW_8 96.0, EW_9 165.1; total 2476.4 A.
- Cathodes: 1, 1, 7, 1, 1, 2, 12, 1, 2 (28 total); tank lengths 270 to 1370 mm.
- Rectifier frames snap to the commercial list: EW_3 rises 500 -> 1000 A, EW_7 falls
  2000 -> 1500 A, the rest stay 250 A; the frame total stays 4250 A and the DC nameplate
  25.5 kW at 6 V. The rectifier AC input moves 5.63 -> 7.491 kW (`params.rect_ac_input_kW`)
  and the conversion loss 1.125 -> 1.498 kW. The sum of the channel ratings is not a
  simultaneous load: the largest single-case load is the reference case.
- The EW aisle re-placed at the sized tanks (`flow_graph/place_ew_aisle.py`, X-RSZ-03);
  all ten machines fit the LEACH_EW block with the 914 mm aisle.

## Files and downstream consequences

- `flow_graph/param/solver.py` (ew) and `docs-authority/_ew_sizing.py` compute the envelope
  basis independently (the 1 percent misfit gate covers the pair); the stdout schema the
  spawners consume is unchanged.
- `docs-authority/_ew_busbar.py` now reads its currents from the AQS-DUTY-051 calculator
  instead of its own previous issue (the self-reading defect named in the Q-038 brief);
  AQS-BUS-001 re-solves at Rev D.
- `flow_graph/param/test_ew_deposit_basis.py` asserts the envelope plumbing and retires the
  old marked defect to what it actually covers: the booked S08 rows still exceed the
  reference feed's plateable metal (42.0 vs 35.96 kg/d) - that stays an expected failure
  under X-QA-04, the stream re-booking task.
- AQS-DUTY-051 Rev F publishes both deposit columns (envelope, booked S08). AQS-ELEC-004
  Rev F and AQS-ASSAY-001 Rev H follow: the table 4.1 held rows become bounded and the case B
  resize triggers close.
- The sized tanks moved the H2 train balance slightly: H2_DRYER re-solves 600 x 400 x 1028 to
  600 x 400 x 1000 mm, and its builder now checks the train fits the envelope instead of
  pinning the old height; the unit rebuilt and its drawing set was re-stamped.
- The X-PAR-04 envelope registry re-trayed EW_1 to EW_9 and H2_DRYER
  (`flow_graph/param/envelopes.py`). The EW manufacturing models are NOT rebuilt in this
  round: their builders carry pre-existing defects (a non-piped cable row unknown to
  `lib/dn.py`, nozzle stations tuned to the old tanks) - verified identical at clean HEAD -
  and the parked EW-regeneration stash is on the retired 42 kg/d basis. The tracker names
  the same 16 holds as before the round, with CRYO_H2 resolved by the 2026-11-06 tier-grid
  round and H2_DRYER rebuilt here.

## Checks

`pytest flow_graph/` passes (236 passed, 1 skipped, 1 xfailed: the X-QA-04 stream defect).
`scripts/check_all.sh --full` passes on the committed tip, including the 1 percent misfit
gate, the staleness gates, and the scratch regeneration that changes nothing.
