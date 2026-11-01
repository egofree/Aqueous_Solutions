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

