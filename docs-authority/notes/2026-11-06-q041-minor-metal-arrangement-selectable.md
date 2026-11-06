# 2026-11-06 Q-041 lane: the minor-metal EW arrangement carried both ways

Owner ruling Q-041 (2026-11-05): decide the minor-metal arrangement from first principles -
electrochemistry, current density, selectivity, mass transfer and energy - and if the analysis
yields no clear winner, carry both arrangements as selectable options in the design data. Gold
and silver stay on their own cells in either arrangement.

## The first-principles analysis (AQS-DUTY-051 section 4)

- Selectivity: lead and tin sit 10 mV apart (published standard potentials, about -0.13 and
  -0.14 V against SHE) and co-plate in either arrangement; nickel and cadmium sit 146 mV
  apart, the same order as the Nernst swing over the working deposit activities, so the
  separate arrangement needs per-cell potential control to hold purity and without it gives
  mixed deposits anyway.
- Hydrogen: zinc plates below the hydrogen potential in the chloride liquor in both
  arrangements (AQS-DUTY-051 finding 4). Not a differentiator.
- Energy: the DC load is the plated metal, identical in both.
- Hardware: the merged cell saves four tanks, four 250 A rectifier channels (6 kW of
  nameplate), four bus runs and four instrument sets.
- Cadmium: the differentiator - a merged cell carries cadmium into the powder blend; the
  separate cadmium cell holds it as a controlled stream.

Verdict: no clear winner, so both are carried.

## The selectable design data

- New driver `ew_minor_metal_arrangement` (selective | merged, register Q-041), default
  `selective` - the nine-cell cascade as sized and as built in the graph today.
- AQS-DUTY-051 Rev G publishes the merged alternative: one combined cell at the bounding
  183.9 A (the largest single-element current of the five, nickel basis - the envelope gives
  the lumped fraction to one element at a time), 2 cathodes, a 370 mm tank, one 250 A channel
  and one bus run, 0.45 kW DC against the selective set's 587.9 A over five tanks and seven
  cathodes.
- AQS-ELEC-004 (RECT_EW) finding 5 and AQS-EW-MOD-001 section 8 name the selectable and the
  five-channel shape of the merged arrangement. Switching the graph topology to the merged
  arrangement (one minor-metal unit in place of EW_4/5/6/8/9) is the EW-topology unit task,
  held until the owner selects it.
- `flow_graph/param/test_ew_deposit_basis.py` asserts the driver value and the merged
  alternative's bounding current.

No selective-arrangement figure changed. The regeneration ran in a scratch worktree and its
result was committed; the main working tree was never the regenerator's write target.
`pytest flow_graph/` passes (237 passed, 1 skipped, 1 xfailed). `scripts/check_all.sh --full`
passes on the committed tip.
