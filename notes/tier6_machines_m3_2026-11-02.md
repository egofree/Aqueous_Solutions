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

## The WS reagent-station family (FAB, tier 6, F-MACH, A-core + A-MACH) — commits 8–12

- Family recipe shared by all six stations: bund tray over the envelope
  (floor 20 + curb 60 × 10 — the drip tray; the duty own-bund figures are the
  room-side containment the placement seeds seat the stations in, named as a
  hold), day tank at the back (OD and fill basis per each unit's duty
  section 2/8), service-zone guard rail and slab anchors drawn (A-MACH), all
  schedule rows as atmospheric open-bore tube connections on tray risers flush
  at the envelope faces (side datums clamped into the 350 box; drain through
  the floor; vent riser on the tank head — 800 datums, W12). Purchased items
  are drawn only where the node or duty names them, as envelopes and
  interfaces per plan rule 6.
- Station notes per commit:

### WS_AMMONIA — commit 8

- Day-tank envelope (no vessel diameter on the node or duty — section 8
  "No vessel diameter"; no volume claimed, model volume reported for the
  record). PVC-U per duty section 3. All 8 schedule rows drawn (1 in, 5
  distribution draws out, drain, vent). No purchased item named — none drawn
  (the A-MACH criterion has nothing to match).
- Deliverables: exports, generated `bom.csv`, `fasteners.csv`, `check.json`,
  `WORK_ORDER.md` (W1–W12), six-sheet drawing set; `tracker --check
  WS_AMMONIA` green; duty section 7 names the model; tracker regen puts
  WS_AMMONIA at M3 (43).

### WS_KOH — commit 9

- Same family recipe; day-tank envelope (duty section 2 claims no holdup,
  0.27 kg/d in and out — no volume claimed, model volume reported for the
  record). PVC-U per duty section 3. All 4 schedule rows drawn (1 in, 1 out,
  drain, vent). No purchased item named — none drawn.
- Deliverables as commit 8; `tracker --check WS_KOH` green; duty section 7
  names the model; tracker regen puts WS_KOH at M3 (44).

### WS_NITRIC — commit 10

- 25 L PVC-U day tank (X-SAF-09: 14 d at 1.17 L/d = 16.4 L net, tank 25 L
  nominal, own bund 30 L room-side) + PVDF pump envelope in the guarded floor
  zone (plan rule 6; drive rating per the maker TDS at order). PVC-U tank and
  piping, PVDF pumps and valves, FKM or PTFE gaskets; 304L excluded (M3);
  AQS-DSN-OX-001 section 1. Levels reported at the X-SAF-09 basis (25 L
  nominal z 260.4, 16.4 L net z 184.6).
- All 7 schedule rows drawn; the N6 DN25 vent-to-NOX_SCRUB row carries no
  datum on the schedule and draws at the +Y band bound (layout choice, W12).
  Duty section 6 breather/NOX_SCRUB routing and the duty section 5 instruments
  named as loop hardware.
- Deliverables as commit 8; `tracker --check WS_NITRIC` green; duty section 7
  names the model; tracker regen puts WS_NITRIC at M3 (45).

### WS_PEROX — commit 11

- 5 L HDPE day tank (cross-linked, unpigmented, UV stabilized; X-SAF-09: 1 d
  at 2.94 L/d = 2.9 L net, tank 5 L nominal, own bund 6 L room-side) + PVDF
  pump envelope front-right and the electrolysis cell envelope front-left
  (AQS-DSN-OX-001 2.1: 12.31 A, 246 cm2, 30.8 W, anode held — designed
  in-house, drawn as its envelope per plan rule 6). PVDF piping, pump and
  valves, PTFE or FKM seals; no metal wetted part (M3). Levels reported at
  the X-SAF-09 basis (5 L nominal z 236.5, 2.9 L net z 154.0). Duty
  section 6: continuous filtered vent and the free-lifting manway cover
  (manway noted, not drawn — W12).
- All 6 schedule rows drawn (oxygen and dilution water in, peroxide out,
  drain, vent). Deliverables as commit 8; `tracker --check WS_PEROX` green;
  duty section 7 names the model; tracker regen puts WS_PEROX at M3 (46).

### WS_PHOS — commit 12

- Day tank (OD 180 layout) with the duty section 2 seven-day charge basis
  (0.0043 m3 sets the working level z 253.8, reported; the box-over-flow
  line is explicitly not a residence time). PVC-U per duty section 3; duty
  section 8's "phosphoric concentration is not on the node, so 316L is not
  confirmed" carried as a hold. All 5 schedule rows drawn (1 in, 2 out,
  drain, vent). No purchased item named — none drawn.
- Deliverables as commit 8; `tracker --check WS_PHOS` green; duty section 7
  names the model; tracker regen puts WS_PHOS at M3 (47). Tier-6 lane
  complete: 12 units accepted this lane (47 at M3 overall).

## Tier-6 continuation lane (FAB reagent stations, recycle pipes, MeOH train,
POLYMERS reactors) — commits 13–24

- Continuation recipe: the same family patterns (the WS reagent-station recipe
  for the four remaining FAB stations; the accepted HDR_CO2 spool/line-list
  idiom for the two recycle pipes; per-node reactor construction for the MeOH
  train and the three POLYMERS reactors, internals per node and purchased items
  as envelopes per plan rule 6). Every dimension from the unit's own graph
  node, duty sheet and issued nozzle schedule; misfits §7-reported, never
  resized. One commit per unit (plan rule 4); subsections follow.

### WS_DOPE — commit 13

- `models/mfg/WS_DOPE/ws_dope.py` on the shared lib, the WS reagent-station
  family recipe: bund tray (floor 20 + curb 60 × 10), day tank at the back
  drawn to the node design_storage figures (D 300, H 300, wall 4.75, AQS-DUTY-064;
  the tracker W2 file does not carry design_storage, so the builder reads the
  graph - the sole topology authority), service-zone guard rail and 4 slab
  anchors (A-MACH). Node storage-sizing box 600 × 600 × 350 filled exactly;
  one closed manifold solid; `cad/stl/WS_DOPE.stl` replaced from the build.
- PE wetted per duty section 3 (the graph node material row); CA 0 mm on the
  polymer. All 5 schedule rows drawn as atmospheric open-bore tube connections
  on tray risers: N1 in on −Y at 160; N2 and N5 out on +Y (600 datums clamped
  down, W12); N3 drain through the tray floor; N4 vent riser beside the tank,
  flush at the envelope top (800 datum, W12). Row N5 carries the line-list
  classification `solids` (non-piped hand transfer): drawn DN15, bore not
  calculated, labeled (plan W4). Class 150 column carried verbatim, no flange.
- The design_storage nominal 0.02 m³ (30-day hold) is reported for the record
  (gross shell 21.2 L); duty section 2 claims no holdup, no residence derived
  (A-VES n/a). No purchased item named - none drawn (the A-MACH criterion has
  nothing to match).
- Deliverables as the family recipe: exports, generated `bom.csv`,
  `fasteners.csv`, `check.json`, `WORK_ORDER.md` (W1–W12), six-sheet drawing
  set; `tracker --check WS_DOPE` green; duty section 7 names the model;
  tracker regen puts WS_DOPE at M3 (48).

### WS_HF_ED — commit 14

- The WS_DOPE builder family at the HF day-station (`models/mfg/WS_HF_ED/
  ws_hf_ed.py`): same tray/tank/guard recipe, same node storage-sizing box
  600 × 600 × 350 filled exactly; one closed manifold solid;
  `cad/stl/WS_HF_ED.stl` replaced from the build.
- Materials: PVDF wetted per duty section 3 (AQS-STD-002 rules M1 and M2, no
  metal wetted part); IA-HF-SRC arrives from LEACH_CSTR_1 at up to 85 °C
  (X-MAT-09) and HF at that temperature takes PVDF (M1 compatibility, M5), not
  CPVC. The node design_storage material row reads PE - duty section 3 governs
  the alloy and PVDF is drawn (hold, W12). Tank D/H/wall stay the node
  design_storage figures (D 300, H 300, wall 4.75, AQS-DUTY-064).
- All 5 schedule rows drawn as atmospheric open-bore tube connections on tray
  risers: N1 (fluoride to HF) and N5 (aqueous HF to the fab reagent fork) in on
  −Y at 160; N2 HF (aq) out on +Y (600 datum clamped down, W12); N3 drain
  through the tray floor; N4 vent riser beside the tank (800 datum, W12).
  Class 150 column carried verbatim, no flange. Nominal 0.02 m³ reported for
  the record; no purchased item named - none drawn.
- Deliverables as the family recipe; `tracker --check WS_HF_ED` green; duty
  section 7 names the model; tracker regen puts WS_HF_ED at M3 (49).

### WS_SLURRY — commit 15

- The WS_DOPE builder family at the slurry day-station
  (`models/mfg/WS_SLURRY/ws_slurry.py`): same tray/tank/guard recipe, node
  storage-sizing box 600 × 600 × 350 filled exactly; one closed manifold solid;
  `cad/stl/WS_SLURRY.stl` replaced from the build. Tank D/H/wall per node
  design_storage (AQS-DUTY-064).
- PE wetted per duty section 3 (the graph node material row); the colloidal
  silica slurry is abrasive - the issued PE section carries no wear allowance
  and none is invented (hold, W12). All 4 schedule rows drawn: N1 silicate to
  slurry in on −Y at 160; N2 slurry out on +Y (600 datum clamped down, W12);
  N3 drain through the tray floor; N4 vent riser beside the tank (800 datum,
  W12). Class 150 column carried verbatim, no flange. Nominal 0.02 m³ reported
  for the record; no purchased item named - none drawn.
- Deliverables as the family recipe; `tracker --check WS_SLURRY` green; duty
  section 7 names the model; tracker regen puts WS_SLURRY at M3 (50).

### WS_SOLV — commit 16

- The WS_DOPE builder family at the solvent day-station
  (`models/mfg/WS_SOLV/ws_solv.py`): same tray/tank/guard recipe, node
  storage-sizing box 600 × 600 × 350 filled exactly; one closed manifold solid;
  `cad/stl/WS_SOLV.stl` replaced from the build. Tank D/H/wall per node
  design_storage (AQS-DUTY-064, the 304L row: D 300, H 300, wall 3.0).
- SA-240 304L welded per duty section 3 (the graph node material row; the
  design_storage material row matches); CA 0 mm on the 300-series alloy. The
  solvent (ethanol/acetone) is flammable - the guard rail and the room-side
  bund are the fire measures on the skid; the relief stays atmospheric as
  issued (duty section 6). The duty section 4 prose list (IA-ABE-ETOH …
  IA-SOLV-WB at 550 datums, no drain/vent rows) predates the issued 7-row
  schedule; the schedule governs (hold, W12).
- All 7 schedule rows drawn: N1/N2/N3/N7 in on −Y at 160 (4-row pack); N4 out
  on +Y (600 datum clamped down, W12); N5 drain through the tray floor; N6
  vent riser beside the tank (800 datum, W12). Class 150 column carried
  verbatim, no flange. Nominal 0.02 m³ reported for the record; no purchased
  item named - none drawn.
- Deliverables as the family recipe; `tracker --check WS_SOLV` green; duty
  section 7 names the model; tracker regen puts WS_SOLV at M3 (51). The
  reagent-station family is complete: all six FAB stations at M3.

### C29_RECYCLE — commit 17

- `models/mfg/C29_RECYCLE/c29_recycle.py` on the accepted HDR_CO2 spool/line-list
  idiom: one DN15 carbon-steel x-run at the schedule inlet datum (z 160) with a
  mid-run inlet branch from the −Y face and a bend riser to the schedule outlet
  datum (z 600) at the +Y face; trough plinth with two saddle stands and 4 slab
  anchors. The node study registry box 1000 × 600 × 800 (its size_note says so)
  is filled exactly by the run, the inlet face and the vent top; the duty §4
  prose line "Size 2000 × 60 × 60" and its height-30 L1/L2 rows are an older
  study frame — the node governs (hold, W12).
- Wall on the lib/dn Sch 40 table (schedule not stated on the node, W12); CA
  1.5 mm per the AQS-STD-001 hydrocarbon rule carried in the procurement basis;
  the dry support steel stays CA-free (the HDR_CO2 basis). All 4 schedule rows
  drawn as atmospheric tube stubs; datums draw as issued (160/600 fit the 800
  box; drain flush at the envelope bottom, vent riser flush at the box top);
  Class 150 column carried verbatim, no flange.
- A-PIPE: `line_list.csv` 3 rows (MAIN spool + the issued C29_RECYCLE and
  C29_TO_PYRO lines, DN15 class M2 per AQS-PIP-004), edge coverage complete, no
  new edge; the routed run stays in the route lengths.
- Deliverables: exports, generated `bom.csv`, `fasteners.csv`, `line_list.csv`,
  `check.json`, `WORK_ORDER.md` (W1–W12), six-sheet drawing set;
  `tracker --check C29_RECYCLE` green; duty section 7 names the model; tracker
  regen puts C29_RECYCLE at M3 (52).

### CONTINUOUS_RECYCLE — commit 18

- The C29_RECYCLE builder family at the continuous-line liquor return
  (`models/mfg/CONTINUOUS_RECYCLE/continuous_recycle.py`): one DN15 PVC-U spool
  at the cross-section centre of the node box 1500 × 60 × 60, on the HDR_CO2
  trough plinth with 6 slab anchors; one closed manifold solid;
  `cad/stl/CONTINUOUS_RECYCLE.stl` replaced from the build.
- PVC-U per duty section 3 (rules M1 and M2, no metal wetted part); above 60 C
  the thermoplastic is CPVC, never metal - the line temperature is not on the
  graph (the IA-REC-01 class P2 line carries hot leach liquor; hold, W12). All
  5 schedule rows drawn as atmospheric tube stubs; the DN50 hand rows N1/N2
  drawn verbatim against the DN15 issued lines and they seat the 60 mm
  cross-section with 0.15 mm per side outside the box, inside the 1 mm house
  gate and reported in check.json (holds, W12); the DN15 160 datum clamps to
  48.65; drain flush at the bottom, vent flush at the top; Class 150 column
  carried verbatim, no flange.
- A-PIPE: `line_list.csv` 3 rows (MAIN spool + IA-POL-02 class P1 + IA-REC-01
  class P2, DN15 per AQS-PIP-004), edge coverage complete, no new edge.
- Deliverables as the C29 commit; `tracker --check CONTINUOUS_RECYCLE` green;
  duty section 7 names the model; tracker regen puts CONTINUOUS_RECYCLE at M3
  (53). Both recycle pipes accepted; the tier-5 pipe lane is complete.

### MEOH_SYNTH — commit 19

- `models/mfg/MEOH_SYNTH/meoh_synth.py`: the fixed-bed synthesis tube of the
  node design block (X-MFG-31, A-M-156) — DN50 tube (OD 60.3 × wall 3.91,
  L_bed 1485 + 400), DN50 Class 600 flange pair (B16.5 OD 165 × 32), DN100
  thermal-oil jacket to Q3, the catalyst bed envelope (3.54 kg Cu/ZnO/Al2O3,
  3.2143 L) and support grids at running clearance in the bore, and the feed
  preheater (0.818 kW) as a purchased envelope (plan rule 6). Node envelope
  414 × 414 × 2585 filled exactly; two closed solids (the vessel chain and the
  bed-with-grids envelope); `cad/stl/MEOH_SYNTH.stl` replaced from the build.
- Materials: 316L per duty section 3 (API 941, AQS-REV-H2-001 section 5 — no
  carbon steel above 200 C with H2 partial pressure); the node SA-106 B tube
  row is superseded, the drawn wall keeps the node t_nom 3.91 (t_req 2.88,
  t_ok) and the alloy changes; the wall geometry stays the node figure
  (hold, W12). Studs follow
  the alloy (A193 B8M / A194 8MA).
- All 9 schedule rows drawn: N1/N2 in and N8 at the −Y 160 pack; N3/N6/N7/N9
  out at the +Y 600 pack (datums draw as issued — both fit the 2585 box; the
  elevations are the schedule placeholders pending vessel design, W12); N4
  drain boss under the bottom flange; N5 vent riser on the top flange flush at
  the box top. Class 150 column carried verbatim at the faces; the pressure
  part carries the Class 600 node rating.
- A-VES: the bed volume (3.213 L model against the node 3.2143 L) is reported;
  no residence time derived (duty section 2 claims no holdup; a fixed bed).
- Deliverables: exports, generated `bom.csv` (make/buy per rule 6),
  `fasteners.csv`, `check.json`, `WORK_ORDER.md` (W1–W12), six-sheet drawing
  set; `tracker --check MEOH_SYNTH` green; duty section 7 names the model;
  tracker regen puts MEOH_SYNTH at M3 (54).

### MEOH_FERM — commit 20

- `models/mfg/MEOH_FERM/meoh_ferm.py`: the fermenter vessel per the node design
  block (X-MFG-31) — PVC-U shell OD 125 × wall 4.0 × H 100 with heads on a
  support-ring stand, the 50 mm PIR insulation envelope (node material row),
  and the node mixer row's daily recirculation pump plus the 0.74 W heater mat
  as purchased envelopes (plan rule 6) with a DN15 recirculation loop (pump to
  the top head, base tap to pump). Node envelope 425 × 425 × 600 filled
  exactly; the skid chain fuses to one solid, the four CATCH_TANK-idiom face
  stubs stay separate until the connecting lines make their joints
  (`check.solids_note`); `cad/stl/MEOH_FERM.stl` replaced from the build.
- PVC-U wetted per duty section 3 (rules M1 and M2); the node HDPE row is
  superseded for the wetted parts (hold, W12); T_C 35 sits inside the class.
  The duty §2 prose line "Envelope 2200 × 900 × 1400" predates the node box
  (hold, W12).
- All 6 schedule rows drawn: N1 in on −Y at 160; N2/N3 out on +Y (600 datums
  clamped to 570.7, W12); N6 solids row (digestate) drawn DN15, bore not
  calculated (plan W4); N4 drain boss under the base; N5 vent riser on the top
  head flush at the box top. Class 150 column carried verbatim, no flange.
- A-VES: the 48 h working volume V = 0.0007 m³ (duty section 2) is an existing
  holdup basis — the model level (z 305.1) is set by it and reported; no new
  residence-time claim.
- Deliverables: exports, generated `bom.csv`, `fasteners.csv`, `check.json`,
  `WORK_ORDER.md` (W1–W12), six-sheet drawing set; `tracker --check MEOH_FERM`
  green; duty section 7 names the model; tracker regen puts MEOH_FERM at M3
  (55).

### MEOH_FC — commit 21

- `models/mfg/MEOH_FC/meoh_fc.py`: the direct methanol fuel-cell skid per the
  node design block (AQS-DUTY-077) — the 28-cell stack (0.6 V at 0.3 A/cm2 on
  200 cm2 cells, 0.56 m2, IEC 62282-3-100 module class) as 316L end plates
  around the MEA (membrane-electrode assembly) laminate envelope (buy,
  plan rule 6) at 6 mm pitch enclosing
  the 141.4 mm active window, the 316L reformer shell (OD 150, Cu/ZnO class bed
  envelope, buy), and the copper bus (30 × 5, duty section 3) running from the
  stack end plate to the +Y face at the N5 datum. Node envelope 1800 × 800 ×
  700 filled exactly; the duty prose 1600 skid line predates the node box
  (hold, W12); `cad/stl/MEOH_FC.stl` replaced from the build.
- All 11 schedule rows drawn: N1..N4 in on −Y at 160; N6/N7/N8/N11 out on +Y at
  600; N5 (MEOH DC) drawn as the copper conductor pad — duty section 4 prose
  rates it "conductor, not a hose", a conductor has no bore (hold, W12); N9
  drain boss under the reformer; N10 vent riser flush at the box top. Class
  150 column carried verbatim, no flange hardware.
- A-CELL: count and active area per the node design block reported from the
  model (duty section 2 carries no plate row — the match is against the node
  design, hold W12); POWER.md states no bus-bar section for this unit, so the
  bus criterion has nothing to match (named, W12).
- Deliverables: exports, generated `bom.csv` (make/buy per rule 6),
  `fasteners.csv`, `check.json`, `WORK_ORDER.md` (W1–W12), six-sheet drawing
  set; `tracker --check MEOH_FC` green; duty section 7 names the model;
  tracker regen puts MEOH_FC at M3 (56).







