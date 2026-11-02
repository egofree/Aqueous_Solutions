# Tier 6 process machines to M3 — 2026-11-02

Authority: AQS-PLAN-006 (`docs-authority/MFG_MODEL_PLAN.md`) sections 1–5 and 7;
per-unit recipe pattern in `models/mfg/HX8/WORK_ORDER.md` (vessel and machine
units) and the accepted header-spool lane (`models/mfg/HDR_CO2/`). Graph Rev AD.
One commit per unit (plan rule 4); this note gains a section per accepted unit.
Tier 6 lane: the process machines whose node internal row is none, ordered
BMED_ACID, BMED_BASE, POLISH_BANK, GREY_TREAT, REMIN, P_CA, REE_RECOVER,
WS_AMMONIA, WS_KOH, WS_NITRIC, WS_PEROX, WS_PHOS. The reagent, polish and treat
skids are dosing and make-up packages: every dimension comes from the unit's own
graph node, duty sheet and issued nozzle schedule; internals stay per the node
(mostly none), the dosing pumps and like purchased items are drawn as their
envelope and interface per plan rule 6, and misfits are §7-reported, never
resized.

## BMED_ACID (EDBM acid-side stack skid, DIGESTER, tier 6) — commit 1

- `models/mfg/BMED_ACID/bmed_acid.py` on the shared lib. Route F-CELL
  (the `bmed` class sits in the F-CELL row of plan section 4). Acceptance
  A-core + A-CELL. Build fills the node registry box 1000 × 600 × 350 exactly;
  one closed manifold solid; `cad/stl/BMED_ACID.stl` replaced from the build;
  `tracker --check BMED_ACID` green.
- Machine per the issued EDBM construction (AQS-DUTY-068 `docs-authority/
  sizing/BMED_STACK.md`, A-M-170/171; the same line AQS-TST-006 section 2 builds
  the bench apparatus to): Ti/MMO anode and 316L/Ni cathode end plates, two
  300 × 300 clamp frames, the 85-triplet laminate (1 bipolar + 2 monopolar
  membranes, 0.8 mm PE mesh spacers; drawn as the stack envelope, membranes a
  buy row), 200 × 200 active window (0.04 m² per cell), 4 tie rods, on a PVC-U
  drip tray with a hold-down beam on posts. The node internals row is none, so
  the tracker records no internal solid; the stack is the machine itself, drawn
  from the construction authority.
- A-CELL: plate count, plate size, pitch and active area reported from the
  model against the AQS-DUTY-068 / A-M-170/171 construction; duty section 2
  carries no plate row, so the section 5 match is against the sizing
  construction (hold); POWER.md states no bus bar for this class. The duty
  section 9 power (26.93 kW, A-M-088 SEC revision) and the sizing 1.67 V pilot
  class are both named; AQS-TST-006 section 5 holds the measured verification
  band. Nothing re-derived.
- All 10 schedule rows drawn as atmospheric open-bore tube connections on tray
  risers, flush at the envelope faces (duty section 4: atmospheric tube or
  hose; Class 150 column carried verbatim as text): N1/N9/N10 in on −Y at 160;
  N2/N3/N4/N5/N8 out on +Y, the 600 datums clamped down (the 350 box predates
  them, W12); N6 drain through the tray floor; N7 vent flush at the top face on
  the beam (800 datum, W12). Schedule row N4 was repaired to schedule quoting
  (an unquoted comma had shifted its face and height fields; the HX8 W12-7
  precedent; the generator only appends, hand rows preserved verbatim).
- Holds named in WORK_ORDER W12: the study registry box as envelope; PP frames
  named against the PVC-U duty section 3 (PVC-U drawn); study plate/tray
  thicknesses; the per-node stack allocation; the A-CELL basis; the derived
  triplet pitch; the repaired N4 row; the clamped datums; the Class 150 column
  against the atmospheric duty; the A-M-088 power figure against the sizing
  voltage class; fastener lengths and torque pattern.
- Deliverables: exports (STEP assembly + closed STL, `cad/stl` replaced),
  generated `bom.csv` (make: tray, frames, beam, tie rods, connections; buy:
  membranes, electrode plates), `fasteners.csv` (4 M10 wedge anchors, 4 M12
  tie rods), `check.json`, `WORK_ORDER.md` (W1–W12), and the six-sheet drawing
  set (GA front/side, connection orientation, stack01, aux01, iso01; stamped
  per AQS-DWG-002; the stale M2-era GA.md and SVGs regenerated through the
  draw/stamp/PDF sequence). Duty section 7 names the model; tracker regen puts
  BMED_ACID at M3 (36).

## BMED_BASE (EDBM base-side stack skid, DIGESTER, tier 6) — commit 2

- `models/mfg/BMED_BASE/bmed_base.py`, the BMED_ACID builder family at the
  base-side unit: same tray, stack construction, clamp and hold-down, filled
  to the same 1000 × 600 × 350 node registry box exactly; one closed manifold
  solid; `cad/stl/BMED_BASE.stl` replaced from the build.
- All 8 schedule rows drawn as atmospheric open-bore tube connections on tray
  risers: N1 DN25 and N7 DN15 in on −Y at 160; N2/N6/N8 DN15 and N3 DN25 out
  on +Y (600 datums clamped down, W12); N4 drain through the tray floor; N5
  vent flush at the top face on the beam (800 datum, W12). Schedule row N3 was
  repaired to schedule quoting (the HX8 W12-7 precedent, as N4 on BMED_ACID).
- The pair's stack power stays booked on BMED_ACID (this unit's duty section 9
  says so); the A-CELL facts are the same AQS-DUTY-068 / A-M-170/171
  construction figures, reported from the model.
- Deliverables as commit 1: exports, generated `bom.csv`, `fasteners.csv`,
  `check.json`, `WORK_ORDER.md` (W1–W12), six-sheet drawing set; `tracker
  --check BMED_BASE` green; duty section 7 names the model; tracker regen puts
  BMED_BASE at M3 (37).

## POLISH_BANK (polish bank vessel, DIGESTER, tier 6) — commit 3

- `models/mfg/POLISH_BANK/polish_bank.py` on the shared lib, the accepted
  vessel idiom (CATCH_TANK pattern): vertical PVC-U vessel, shell OD 540
  (min(L,W) − 60), wall 10 (study fab page — hold), plinth with heads, filling
  the node registry box 1000 × 600 × 800 exactly; one closed manifold solid;
  `cad/stl/POLISH_BANK.stl` replaced from the build.
- History handled: the placement seed once carried the polish bank as separate
  columns (the PK_1..PK_9 label era); the present graph defines one unit and
  the model covers that column set as the node defines it — one vessel skid
  (named in WORK_ORDER W12 and params.layout).
- Internals: none drawn — the node internals row is none and no authority
  dimensions the polish media (duty section 5 names a differential-pressure
  instrument across the packing; no packing height, media class or column
  count exists); nothing invented (W12).
- All 7 schedule rows drawn as atmospheric hose barbs flush at the envelope
  faces (shell 30 off the ±Y faces, within the barb reach): N1 DN50 and N7
  DN15 in on −Y at 160; N2/N3 DN50 and N6 DN15 out on +Y at 600 (datums fit
  the box, no clamp); N4 drain boss to its 50 datum; N5 vent flush at the top
  head (the 800 datum is the envelope top). The duty section 4 prose bore
  line (6.25 mm, DN15) is not a specification and predates the issued DN50
  tail rows — schedule governs (W12).
- A-VES: the duty section 2 figure is an existing holdup basis (0.0827 m³ at
  a 30-minute hold) — the model working level (z 449.4) is set by it and
  reported (0.0827 m³; full shell 0.1529 m³); no new residence-time claim;
  duty section 8's "not a measured volume" line is carried.
- Deliverables: exports, generated `bom.csv`, `fasteners.csv`, `check.json`,
  `WORK_ORDER.md` (W1–W12), six-sheet drawing set; `tracker --check
  POLISH_BANK` green; duty section 7 names the model; tracker regen puts
  POLISH_BANK at M3 (38).

## GREY_TREAT (greywater treatment vessel, WTR, tier 6) — commit 4

- `models/mfg/GREY_TREAT/grey_treat.py` on the shared lib, the accepted vessel
  idiom at the same registry box as CATCH_TANK (649 × 520 × 748): vertical
  PVC-U vessel, shell OD 460 (min(L,W) − 60), wall 10 (study fab page —
  hold), plinth with heads, filling the box exactly; one closed manifold
  solid; `cad/stl/GREY_TREAT.stl` replaced from the build.
- Internals: none — the node row is none and no study page issues internals
  for this unit (W12). The duty section 4 prose block (7 rows on the seed
  line "Size 800 × 800 × 1100 mm") predates both the issued 11-row schedule
  and the node box; the node and the schedule govern (holds).
- All 11 schedule rows drawn as atmospheric hose barbs flush at the envelope
  faces: N1 DN50 and five DN15 inlets on −Y at 160; N3 DN25, N4 DN50 and N7
  DN15 outlets on +Y at 600 (datums fit the box, no clamp); N5 drain boss to
  its 50 datum; N6 vent flush at the top head (its 800 datum predates the
  box, W12). Class 150 column carried verbatim as text, no flange drawn.
- A-VES: the 0.0955 m³ liquor volume at the study working level is reported;
  the duty section 2 claims no holdup and no residence time is derived.
- Deliverables: exports, generated `bom.csv`, `fasteners.csv`, `check.json`,
  `WORK_ORDER.md` (W1–W12), six-sheet drawing set; `tracker --check
  GREY_TREAT` green; duty section 7 names the model; tracker regen puts
  GREY_TREAT at M3 (39).

## REMIN (remineralization dosing skid, WTR, tier 6) — commit 5

- `models/mfg/REMIN/remin.py` on the shared lib: a dosing skid in the node
  storage-sizing box 600 × 600 × 600, filled exactly; one closed manifold
  solid; `cad/stl/REMIN.stl` replaced from the build. PVC-U day tank OD 460
  (wall 10, study — hold) on a tray with heads, plus the purchased envelopes
  the node design block names: 2 × metering diaphragm pumps (Ca slurry, MgCl2)
  and the UV unit after the dose — envelope and interface only, plan rule 6
  (A-MACH-style naming on an A-VES unit; the maker TDS carries the wetted
  parts and drive/lamp ratings at order).
- Duty section 2's older shell line (600 × 400 × 800) predates the
  storage-sizing box; the node governs (W12). The duty section 3
  PVC-U-or-HDPE conditional holds (PVC-U drawn, CATCH_TANK idiom).
- All 5 schedule rows drawn: N1 in on −Y at 160 and N2/N5 out on +Y ride tray
  risers flush at the faces (600 datums clamped down, W12); N3 drain through
  the tray floor; N4 vent flush at the tank top head (800 datum, W12).
- A-VES: the duty carries a holdup basis (7 days at the 10 L/d potable tap =
  0.07 m³) — the model working level (z 520.4) is set by it and reported; no
  new residence claim.
- Deliverables: exports, generated `bom.csv` (make: tray, tank, connections;
  buy: pumps, UV), `fasteners.csv` (anchors + envelope hold-down bolts),
  `check.json`, `WORK_ORDER.md` (W1–W12), seven-sheet drawing set; `tracker
  --check REMIN` green; duty section 7 names the model; tracker regen puts
  REMIN at M3 (40).

## P_CA (calcium-soap precipitation vessel, DIGESTER, tier 6) — commit 6

- `models/mfg/P_CA/p_ca.py` on the shared lib: PP-H precipitation vessel
  (OD 250, wall 6 study — hold) with heads on a steel frame plinth, PP
  agitator (shaft up through the top head into the purchased drive envelope,
  two blades) — the duty section 3 X-MAT-22 selection. Node seed envelope
  300 × 300 × 400 filled exactly; one closed manifold solid;
  `cad/stl/P_CA.stl` replaced from the build.
- Route hold handled: the node class `precip` has no section 4 route class —
  the tracker records "A-core (route hold)", the WORK_ORDER W10 states the
  F-VES-operations-as-nearest-family intent with the hold named, and the
  tracker keeps the unit at M3 (the acceptance set is A-core alone, which
  passes; the orchestrator rule "skip if A-core cannot pass" does not fire).
- All 2 schedule rows drawn (drain and vent utilities only — no piped process
  connection on the graph yet; PE slurry lines wait for rated edges, hold):
  N1 drain open-bore through the plinth and base head (50 datum), N2 vent
  flush at the vessel top head (800 datum, W12).
- A-core met on the files; the duty section 6 relief-pending and section 8
  open items are named in check.json and W12; working volume 0.0159 m³
  reported for the record (no holdup basis, no residence claim).
- Deliverables: exports, generated `bom.csv`, `fasteners.csv`, `check.json`,
  `WORK_ORDER.md` (W1–W12 + the route-hold W10), seven-sheet drawing set;
  `tracker --check P_CA` green; duty section 7 names the model; tracker regen
  puts P_CA at M3 (41).

## REE_RECOVER (rare-earth campaign bench skid, MFG, tier 6) — commit 7

- `models/mfg/REE_RECOVER/ree_recover.py` on the shared lib: the AQS-MOD-002
  frame pattern (80 × 5 tube, 316L wet-bench class — layout choice) with two
  shelves and a floor drip plate, carrying the duty-named equipment set as
  purchased envelopes per plan rule 6: demag oven (> 320 C, 5 L class) and the
  10 L glass-lined leach reactor (55 C jacket, stirrer, H2 vent) lower shelf,
  PP-H vacuum filter and the 900 C 316L-shell muffle upper shelf. Node skid
  box 800 × 600 × 1400 filled exactly; one closed manifold solid;
  `cad/stl/REE_RECOVER.stl` replaced from the build.
- Route hold carried (class precip): tracker records "A-core (route hold)",
  WORK_ORDER W10 states the F-MACH/F-VES-operations intent with the hold
  named; A-core met on the files.
- Both schedule rows drawn as open-bore tube: N1 drain through the floor
  plate (50 datum), N2 the H2 vent riser to the box top (the acid-scrubber
  header route, duty section 2 sizing; 800 datum, W12). Campaign figures
  (1.618 kg NdFeB, 0.585 kg REO, 10 L, 0.3 kW) reported from the graph node
  sizing block; relief (task 07) and instrument (task 08) pending items named.
- Deliverables: exports, generated `bom.csv` (buy rows carry the envelope-mass
  caveat), `fasteners.csv` (anchors + equipment hold-downs), `check.json`,
  `WORK_ORDER.md` (W1–W12 + route-hold W10), eight-sheet drawing set;
  `tracker --check REE_RECOVER` green; duty section 7 names the model;
  tracker regen puts REE_RECOVER at M3 (42).






