# 2026-11-06 CRYO tube-rack tier grid derived from the A-M-167 drivers

This record states what the round changed and why, with the figures at the
commits named below. The graph, `drivers.json` and the node sizing records were
not touched; no regeneration of the document tree ran. The builders and the
drawing sets were rebuilt, and the named derived-register generators ran.

## The tier grid is derived, and drawn equals booked on all three racks

The 2026-11-05 round left the hold: the CRYO_H2 tier grid drew 16 tube solids
against 34 booked tubes, from the hard-coded pattern
`TIERS = N_TUBES // (HALVES * 4)` (the halves factor never reached the draw
loop). The owner ruling of 2026-11-05 directs the tier or row grid to be
derived from the booked tube data so the drawn solids match the booked count.

The new shared helper `models/mfg/lib/rack_grid.py` derives the grid for all
three units from the data the authorities already hold: the booked tube count
and the bank split from the graph node design block, and the tubes-per-row,
row-pitch, rack-allowance and manifold-halves values from the `rcv_*` drivers
(register A-M-167, the same values `flow_graph/param/receivers.py` used to set
each rack envelope). The helper asserts the envelope consistency (height minus
allowance equals the derived tier count times the pitch; width minus allowance
equals the tubes-per-row times the pitch) and fills the grid banks-first,
tier by tier, the two relief halves interleaved station by station, so drawn
equals booked and each manifolded half receives its exact share:

- CRYO_H2: 5 tiers (z 231/381/531/681/831) x 8 stations, 34 of 40 slots filled,
  17 tubes per half (was 4 tiers x 4 rows, 16 of 32 filled, 16 drawn).
- CRYO_O2: 2 tiers (z 231/381) x 8 stations, 16 of 16 filled, 8 tubes per half
  exactly (was 2 x 9 rows, 16 of 18 filled; the old y-split gave 10/8, not the
  8/8 the node fire case assumes).
- CRYO_CO2: 1 tier (z 231), 4 tubes on interleaved stations of 8, 2 per half
  exactly (was 4 rows spread over the full width).

The CRYO_O2 crew reserve moves to the last station of each half on the upper
tier (the graph bank order fills main first), behind two divider plates at
y 600 / 1200 lapping the crew tier band (was one plate at y 1166.7); the
plate count is now a BOM line of 2 at 82.5 kg (was 1 at 98.5 kg).

## Masses and registers

- CRYO_H2 frame 3982.4 -> 3675.2 kg (combs now at every derived tier); the
  drawn tube set equals the booked 7084.0 kg, and the saddle row 3 is priced at
  102 solids 1341.0 kg, drawn and booked agreeing.
- CRYO_O2 frame 2448.3 -> 2454.7 kg (comb grooves cut only at filled
  stations); divider 98.5 -> 82.5 kg over two plates.
- CRYO_CO2 unchanged frame 1470.2 kg (no combs; the derived stations and tier
  centre z 231 match the old centred single tier).
- Named generators (`_plant_bom.py`, `_eol.py`, `_cost_estimate.py`)
  regenerated the derived registers: fabricated total 5,930,554.09 ->
  5,928,145.65 USD, the arithmetic being -307.2 kg (H2 frame), -0.1 kg (H2
  saddle union rounding), +6.4 kg (O2 frame), -16.0 kg (O2 divider) at
  7.60 USD/kg.

The WORK_ORDER W3/W6/W8/W12 texts were rewritten for the derived grid; the W12
tier-grid hold is closed on all three units (the frame-section study-size hold
stays). CRYO_O2 W8 also carried a stale tube mass, 3273.9 kg against the
check.json 3333.7 kg; it now states the drawn/booked 3333.7 kg. The drawing
sets (SVG/PDF) were regenerated, re-stamped and re-hashed in
`DRAWING_REGISTER.md`.

## Checks

`models/mfg/tracker.py --check` reports the same 16 named holds as before the
round and no new misfit. `scripts/check_all.sh --full` passes on the committed
tip (tests, staleness, authority contract, citations, style, and the scratch
regeneration that changes nothing).
