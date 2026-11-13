# The Q-041 minor-metal EW arrangement made a selectable option

Date: 2026-11-13. Task: X-QA-05 (AQS-PLAN-007). Closes the X-QA-05 item:
the low-duty electrowinning cells are designed as selectable options
(selective cascade or merged cell), not shipped only as five one-element
cells.

## Decision

The minor-metal arrangement is a live option on driver
`ew_minor_metal_arrangement` (values `selective` and `merged`; the driver and
`ew_minor_metal_cells` landed with AQS-DUTY-051 Rev G, registered to Q-041).
New assumption A-M-494 records the option: it is a layout choice, not a
physics change.

- `selective` (the default) is today's booking: EW_4/5/6/8/9 stay five cells,
  each rated at the full lumped other_plateable envelope deposit at its own
  metal. Every committed figure is unchanged.
- `merged` carries the same lumped blend on the first minor cell (EW_4),
  rated at the worst minor composition - the smallest minor molar mass, the
  nickel basis, which is the largest of the five selective ratings (183.87 A
  at the design feed). The other four minor cells carry no current; the
  sizing sheet reports them as not built. Their booked element rows stay, so
  the ledger (A-M-470 even split, 3.0804 kg/d of blend) is
  arrangement-independent and the operating Faraday load does not move.

The change lives in `flow_graph/param/solver.py ew()` and
`docs-authority/_ew_sizing.py` (rows and section 4; AQS-DUTY-051 Rev I).
`flow_graph/param/ew_cells.py` stays the element map in both arrangements.
`flow_graph/param/test_ew_deposit_basis.py` gains the option-seam test: the
blend books fully under `merged`, the current-carrying minor-cell count
drops from five to one, the merged rating equals the largest selective
rating and the sizing sheet's merged cell, and `selective` restores the
committed book.

## Reason

Owner ruling Q-041 (2026-11-05): decide from first principles and carry both
arrangements if no clear winner. The first-principles analysis
(AQS-DUTY-051 section 4, Rev G) found no winner - lead and tin sit 10 mV
apart so a selective cascade cannot separate the minor metals on potential,
the DC load is the same plated metal in both, and the merged cell saves four
tanks, four rectifier channels and their bus runs while giving up separate
cadmium handling. Rev G carried the merged cell as a paper alternative only;
X-QA-05 asked for the option to be real in the sizing data. The rating
seam follows the same logic the sheet already published: under `selective`
each minor cell is rated for the whole lumped class in its own metal (the
all-in-one-element reading of AQS-ASSAY-001 table 4.1), so the merged rating
is that same class mass at the highest-amperage minor metal.

The graph keeps its nine cascade nodes in both arrangements: the liquor
order interleaves EW_7 (iron) between the minor cells, so collapsing the
idle minor tanks re-routes the cascade and stays the held EW-topology unit
task. Under `merged` the four idle nodes are pass-throughs in the liquor
path and carry no electrical book.

## Numbers (design feed, reference-point basis)

- Blend booked: 3.0804 kg/d in both arrangements (5 x 0.61608, A-M-470).
- Minor rated current: 587.9 A across five cells, dropping to 183.87 A on
  the one merged cell (nickel basis); rectifier total 2476.4 A dropping to
  2072.3 A; channel DC 5.99 kW dropping to 5.02 kW.
- Merged EW_4 equipment row: deposit 4.1072 kg/d (class envelope mass),
  183.9 A, 2 cathodes, 182 A/m2, 0.39 kW.
- The default tree is unchanged by the option: `selective` regenerates the
  committed figures byte-identically (AQS-DUTY-051 Rev I adds text only).
