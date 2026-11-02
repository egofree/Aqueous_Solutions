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

