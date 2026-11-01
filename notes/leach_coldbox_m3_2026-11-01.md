# LEACH_CSTR_1 and the tier 3 cold boxes to M3 — 2026-11-01

Authority: AQS-PLAN-006 (`docs-authority/MFG_MODEL_PLAN.md`) section 2 work order and section 5
acceptance; per-unit recipe pattern in `models/mfg/EW_1/WORK_ORDER.md`. Graph Rev AC. One commit
per unit (plan rule 4); this note gains a section per accepted unit.

## LEACH_CSTR_1 (leach CSTR, tier 2) — commit 1

- `models/mfg/LEACH_CSTR_1/leach_cstr_1.py` rebuilt on the shared lib. All 61 rows of the issued
  schedule `docs-authority/nozzles/LEACH_CSTR_1.csv` drawn at tag, face, height and bore:
  inlets on −Y (32 at z 160, 4 at z 280), outlets on +Y (15 at z 600, 4 at z 1050), N9 drain to
  its 50 datum, N10 vent at the 1400 lid datum; atmospheric hose barbs (duty sections 4 and 6),
  six solids rows at DN15 labeled bore not calculated (AQS-PLAN-006 W4), and the IA-E-LEACH
  conductor drawn as the +Y gland boss (duty section 4 prose; an electrical edge, so not a
  schedule row). Internals: three FRP belts C203x56x6.4 at z 300/560/900 segmented where the
  port rows cross their bands, the HX-5 coil annulus envelope on four PTFE pads (mass from the
  53.7 m of 25 × 3 mm tube, AQS-DUTY-049), and the PBT D 450 agitator (AQS-DUTY-050).
- Envelope: the node carries no `size_mm` (tracker hold); the duty section 2 box
  2000 × 1200 × 1400 mm is the claimed envelope. Build bbox 2000.0 × 1200.3 × 1400.0 mm, one
  closed manifold solid. Holdup 1.855 m³ net of internals at the 1100 mm working level against
  the 2.14 m³ AQS-DUTY-050 fill basis (A-VES; the 13.2 h residence stays the duty's figure).
- Deliverables: exports (STEP assembly + closed STL), generated `bom.csv` with mass and
  make-or-buy, `fasteners.csv` (36 M12 PVDF lid bolts counted from the model), `check.json`,
  `WORK_ORDER.md` (W1–W12; the M2-era `WO.md` superseded), the seven-sheet drawing set
  (GA front/side, nozzle orientation, shell, internals, aux, iso; stamped per AQS-DWG-002), and
  `cad/stl/LEACH_CSTR_1.stl` replaced from the build (~173454 facets).
- Acceptance evidence: `python3 models/mfg/tracker.py --check LEACH_CSTR_1` green. Holds named
  in WORK_ORDER W12: missing node `size_mm`; duty §4 prose (46 rows incl. the conductor) vs the
  issued 61-row CSV — the CSV is drawn verbatim and the prose refresh is the duty generator's
  run; the schedule rating column (Class 150) carried as text against the atmospheric duty; the
  port-row/belt-band segmentation; study belt section, lid/gasket, Zwietering test, coil
  envelope, liquor density.
- The lane surfaced a stale-export finding first: a full regen rebuilds every style-builder
  unit, and the committed STEP/STL files predated the current builder and graph. The refresh is
  deterministic current-code output (verified by rebuilding two units from a clean HEAD checkout
  and matching the regen bytes) and landed as its own housekeeping commit before this one.

## CRYO_ASU (13X TSA cold box, tier 3) — commit 2

- `models/mfg/CRYO_ASU/cryo_asu.py`: every internal named on the node drawn as a solid — three
  13X TSA beds at the node design geometry (bed_D_mm 414.4, bed_L_mm 1243.1, 20 mm support
  grids, sorbent charges as solids between the grids: 294.5 kg drawn against 326.9 kg booked at
  the 700 kg/m³ study bulk density), the CO2 two-stage compressor, condenser and heated Ar
  getter as purchased envelopes rated from the node design kW (AQS-PLAN-006 rule 6), on a
  plinth skid. All 16 rows of the schedule drawn at tag, face, height and bore: bed-shell rows
  at z 400 (inlets) and z 1500 (outlets), frame-level rows at z 160 through the plinth, the
  drain beside the bed 1 pedestal to its 50 datum, and a DN15 vent standpipe on the bed 1 top
  head to the 2000 mm datum (API 2000 open-vent relief basis, A-M-155; no flange anywhere, the
  schedule rating column carried as text).
- Envelope: the node `size_mm` [300, 300, 2000] is the M0 study registry box (params
  `size_note`) and the beds at their design diameter cannot fit it. The build measures
  2460.0 × 592.1 × 2000.1 mm; the misfit is reported on the tracker board per plan rule 3 and
  nothing is resized (AL_POT precedent). `cad/stl/CRYO_ASU.stl` carries the in-envelope subset
  of the build so the X-PAR-04 gate holds (bbox exactly 300 × 300 × 2000); the full build lives
  in `export/` and the STEP, which is what the board misfit reads.
- Deliverables: generated BOM with mass and make-or-buy, `fasteners.csv`, `check.json`,
  `WORK_ORDER.md` (W1–W12), the seven-sheet drawing set; the stale envelope `drawings/GA.md`
  superseded. `tracker --check CRYO_ASU` reports exactly the board-mandated misfit row.
- Holds named in WORK_ORDER W12: the study-box misfit; the duty section 2 column prose
  ("column diameter 150 mm, 20 trays") vs the issued node design (TSA beds) the model draws;
  internals-row two-stage vs design-block comp_stages 4; house-plate shell/grid thicknesses;
  sorbent bulk density; no distributor/demister named for TSA service (A-COL); the TSA
  valve/regeneration manifold row left to the piping scope.

## CRYO_CO2 (cylinder bank, tier 3) — commit 3

- `models/mfg/CRYO_CO2/cryo_co2.py`: the node's storage bank drawn as the machine — 4 SA-312
  TP316L seamless DN100 Sch 160 tubes (OD 114.3 × t 13.49, 6.096 m, bores drawn open, 833.4 kg
  drawn wall mass against the node steel_kg 690.07 sizing record, carried not recalculated),
  one tube per row at y 187.5/562.5/937.5/1312.5 on 3 saddles each over a 316L SHS rack frame
  that fills the A-M-167 envelope 6696 × 1500 × 450 exactly. Rows y < 750 / > 750 are the two
  relief halves of the node API 520/521 fire case (2 tubes per half, 4.378 m² exposed), with
  one 9 mm relief-valve envelope per half at the +X end posts (AQS-PLAN-006 rule 6).
- All 10 rows of the schedule drawn at tag, face and bore on the side rails; the z 400/160
  rows as issued, the z 1500/2000/50 datums clamped onto the rack with named holds (they were
  issued against the 300 × 300 × 2000 study boxes that predate the rack envelope).
- Deliverables: generated BOM with mass and make-or-buy, `fasteners.csv`, `check.json`,
  `WORK_ORDER.md` (W1–W12; holds led by the Class 150 schedule rating column against the
  2200 kPa node design — no flange drawn, lib/dn.py carries no table above Class 150 — the
  clamped datums, the steel_kg basis difference, and the study frame sections), and the
  seven-sheet drawing set; the stale envelope `drawings/GA.md` superseded.
- `tracker --check CRYO_CO2` green; `cad/stl/CRYO_CO2.stl` replaced from the build (~9236 f).

## CRYO_H2 (hydrogen bank + compression, tier 3) — commit 4

- `models/mfg/CRYO_H2/cryo_h2.py`: 32 SA-312 TP316L DN100 Sch 160 tubes (OD 114.3 × t 13.49,
  6.096 m, bores drawn open, 6547.8 kg drawn wall mass against the node steel_kg 5520.54 sizing
  record, carried not recalculated) in 4 tiers × 8 rows over a 316L SHS rack frame that fills
  the A-M-167 envelope 6696 × 1500 × 900 exactly; grooved tier combs at every tier lap the
  tubes and land on the end posts and side rails. Rows y < 750 / > 750 are the two relief
  halves of the node API 520/521 fire case (16 tubes per half). The 2 five-stage diaphragm
  hydrogen compressors of node compressor_design (17-4PH H1150 / 316L heads, 301 SS
  triple-layer diaphragms, 0.9325 kW average / 2.797 kW peak) are purchased envelopes in the
  +X end bay (AQS-PLAN-006 rule 6).
- All 8 rows of the schedule drawn at tag, face and bore on the side rails; z 400/600/160 as
  issued, z 1500/2000/50 clamped with named holds.
- tracker.py: the node `compressor_design` now passes through the W2 merge (the builder reads
  params.json only; CRYO_H2 is the only node that carries it). CRYO_H2 joins ACCEPTED.
- Deliverables as per the batch recipe; `tracker --check CRYO_H2` green;
  `cad/stl/CRYO_H2.stl` replaced from the build; the stale envelope `drawings/GA.md`
  superseded. Holds led by the Class 150 schedule rating column against the 22000 kPa node
  design, the clamped datums, the steel_kg basis difference, and study frame sections.

## CRYO_N2 (nitrogen shell machine, tier 3) — commit 5

- `models/mfg/CRYO_N2/cryo_n2.py`: the node carries no design, no internals and no diameter
  (duty section 8), so the build is the shell machine the house rule prescribes — welded 316L
  shell t 3 closed top and bottom on a 20 mm skid, exactly the node size_mm box
  300 × 300 × 2000 (bbox 300.0 × 300.0 × 2000.0, one closed manifold solid). No vacuum jacket
  (not named anywhere) and no invented internals.
- All 8 rows of the schedule drawn at tag, face, height and bore; every datum fits this
  envelope and is drawn as issued (inlet −Y z 400; outlets +Y z 1500 and 600; drain flush at
  z 0 to its 50 datum; vent flush at the 2000 top). Atmospheric hose per duty sections 4 and
  6; no flange; the Class 150 schedule rating column carried as text.
- Deliverables as per the batch recipe; `tracker --check CRYO_N2` green;
  `cad/stl/CRYO_N2.stl` replaced from the build; the stale envelope `drawings/GA.md`
  superseded. Holds led by the missing diameter/design (unit task 02), the unnamed internals
  with A-COL stages left a hold, the study shell/skid thicknesses, and the unnamed vacuum
  jacket.

## CRYO_O2 (oxygen bank, tier 3) — commit 6

- `models/mfg/CRYO_O2/cryo_o2.py`: 16 SA-312 TP316L DN100 Sch 160 tubes (OD 114.3 × t 13.49,
  6.096 m, bores drawn open, O2-cleaned to ASTM G93, 3273.9 kg drawn wall mass against the
  node steel_kg 2760.27 sizing record, carried not recalculated) in 2 tiers × 9 rows over a
  316L SHS rack frame that fills the A-M-167 envelope 6696 × 1500 × 600 exactly. Main bank
  14 tubes (rows 1–7, both tiers); the crew reserve is the 2-tube separate bank behind a
  divider plate at y 1166.7 (node banks + crew_reserve_basis, NFPA 2 ch. 7). Rows y < 750 /
  > 750 are the two relief halves of the node API 520/521 fire case (8 tubes per half), with
  one 9 mm relief-valve envelope per half at the +X end posts (AQS-PLAN-006 rule 6).
- All 9 rows of the schedule drawn at tag, face and bore on the side rails; z 400/160 as
  issued, z 1500/600/2000/50 clamped with named holds.
- Deliverables as per the batch recipe; `tracker --check CRYO_O2` green;
  `cad/stl/CRYO_O2.stl` replaced from the build; the stale envelope `drawings/GA.md`
  superseded. Holds led by the Class 150 schedule rating column against the 22000 kPa node
  design, the clamped datums, the steel_kg basis difference, and study frame sections.

## Batch close

Six units accepted in six commits (LEACH_CSTR_1, CRYO_ASU, CRYO_CO2, CRYO_H2, CRYO_N2,
CRYO_O2). Tracker at 16 units on M3, 149 at M2, 32 at M0, 3 accounting nodes. The lane also
landed a housekeeping commit ahead of the batch (a full-regen refresh of the style-builder
exports that predated the current builder and graph). Rev-stamp register stamped in a
dedicated commit after the batch, per house convention.





