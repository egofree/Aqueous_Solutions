# 2026-11-05 second correction round: CRYO_H2 booked/drawn labels and the saddle single-costing (qc-fail corr2)

This record states what the second correction round changed and why, with the figures at the
commits named below. The graph, `drivers.json` and the node sizing records were not touched;
no regeneration of the model tree ran, only the named derived-register generators.

## 1. CRYO_H2 WORK_ORDER labels booked 7084.0 kg vs drawn wall mass 3333.7 kg

W8 and W12(3) of `models/mfg/CRYO_H2/WORK_ORDER.md` called 7084.0 kg the "drawn wall mass".
7084.0 kg is the booked tube mass (34 tubes x 208.35 kg, node A-M-167 count); the tier grid
draws 16 tube solids, so the drawn wall mass is 3333.7 kg (16 solids x the booked tube mass,
density 8000 kg/m3). `check.json` already carried both values correctly (`drawn_mass_kg`
3333.7, `booked_mass_kg` 7084.0); only the WORK_ORDER wording was corrected
(commit 50a458cf1).

## 2. CRYO_H2 BOM row 2 is frame-only; saddles are priced once on row 3

Choice: **row 2 frame-only** (of the two allowed options). Rack frame row 4613.5 -> 3982.4 kg
(the `check.json` `part_mass_kg.frame` value); row 3 keeps the full saddle costing (102 booked
at the 13.15 kg drawn unit mass, 1341.1 kg) and now states it is the only saddle line. Before,
row 2 carried frame + drawn saddles (4613.5 = 3982.4 + 631.1) while row 3 priced the booked
saddle set again, so the cost register priced saddles twice. The builder (`cryo_h2.py`) writes
the same rows so a rebuild reproduces the BOM. The named generators (`_plant_bom.py`,
`_eol.py`, `_cost_estimate.py`) regenerated the derived registers: the CRYO_H2 frame line
35,062.60 -> 30,266.24 USD, the saddle line unchanged at 10,192.36 USD, fabricated total
5,943,261.29 -> 5,938,464.93 USD (the 631.1 kg x 7.60 USD/kg double-count removed)
(commit 794004923).

## 3. CRYO_H2 relief basis says 17 tubes per half booked; CRYO_ASU date on the stamp policy

The per-half figure 17 is the booked count (34 booked / 2 halves) even though the tier grid
draws 8 solids per half; the relief basis in `check.json` and its builder now say "booked"
(commit fca16db4c). The CRYO_ASU build-log Date line had been a template literal carrying the
wall-clock day of the last run (2026-11-05); the `lib/stamp_date.py` policy states a generated
output carries no wall-clock day, so the draw script now writes `deterministic_date()` (the
graph state date, 2026-11-01 today) and the committed build log matches it. The dated run note
(2026-11-05, superseding the 2026-11-01 Rev AC run) stays verbatim: it is the accepted record
of the rebuild event, not a regen stamp (commit ffc830163).

## 4. CRYO_O2 and CRYO_CO2 spot-check: no drawn/booked mix-up; row-2 saddle overlap left as a hold

The spot-checked mix-up class (a drawn mass booked off the full tube count while fewer solids
are drawn) does not exist in the two sisters: CRYO_O2 draws 16 solids against 16 booked
(2 tiers x 9 rows, 16 used) and CRYO_CO2 draws 4 against 4 (one tube per row), so
`drawn_mass_kg = N_TUBES x tube_mass` is genuinely the drawn set mass and equals the booked
set mass (3333.7 and 833.4 kg at the same 208.353 kg tube mass). The BOM "drawn set" wording
is accurate there and no change was made.

Observed but out of scope: both sisters' BOM row 2 folds the saddles into the frame row the
same way CRYO_H2 did (CRYO_O2 row 2 3079.4 = frame 2448.3 + saddles 631.1 against a separate
631.1 saddle row 3; CRYO_CO2 row 2 1880.0 = frame 1470.2 + saddles 409.8 against a separate
409.8 row 3). This is the fix-2 double-count class in the cost register, but the round scoped
the saddle correction to CRYO_H2; the sisters are left as a named hold for the next round.
