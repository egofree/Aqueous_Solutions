# 2026-11-06 CRYO_O2 and CRYO_CO2 saddle single-costing

This record states what the round changed and why, with the figures at the
commits named below. The graph, `drivers.json` and the node sizing records were
not touched; no regeneration of the document tree ran, only the unit builders
and the named derived-register generators.

## The BOM row 2 of both units is frame-only; saddles are priced once on row 3

The 2026-11-05 correction round left this as a named hold: both sisters folded
the saddles into the rack-frame row while row 3 priced the saddle set again, so
the cost register priced every saddle twice. This round applies the same
correction CRYO_H2 received.

- CRYO_O2: row 2 frame 3079.4 -> 2448.3 kg (the `check.json`
  `part_mass_kg.frame` value); row 3 keeps the full saddle costing (48 booked at
  the 13.148 kg drawn unit mass, 631.1 kg) and states it is the only saddle
  line.
- CRYO_CO2: row 2 frame 1880.0 -> 1470.2 kg; row 3 keeps 12 saddles at the
  drawn unit mass, 409.8 kg, as the only saddle line.
- The builders (`cryo_o2.py`, `cryo_co2.py`) write the same rows, so a rebuild
  reproduces the BOM. The WORK_ORDER W8 mass statements follow the frame/saddle
  split. The drawn STEP files carry the normalized stamp (no wall-clock day).
- The named generators (`_plant_bom.py`, `_eol.py`, `_cost_estimate.py`)
  regenerated the derived registers: the CRYO_O2 frame line 23,403.44 ->
  18,607.08 USD, the CRYO_CO2 frame line 14,288.00 -> 11,173.52 USD, the saddle
  lines unchanged, fabricated total 5,938,464.93 -> 5,930,554.09 USD (the
  1040.9 kg x 7.60 USD/kg double-count removed).

## Checks

`models/mfg/tracker.py --check` reports the same 16 named holds as before the
round and no new misfit; CRYO_O2 and CRYO_CO2 pass. `scripts/check_all.sh
--full` passes on the committed tip (tests, staleness, authority contract,
citations, style, and the scratch regeneration that changes nothing).

## Still held

- CRYO_H2, CRYO_O2 and CRYO_CO2 tier grids: the drawn tube-solid count against
  the booked tube count (the H2 grid draws 16 solids against 34 booked). The
  tier/row grid is derived from the booked tube data in the next item of this
  round, replacing the hard-coded `TIERS = N_TUBES // (HALVES * 4)` pattern.
