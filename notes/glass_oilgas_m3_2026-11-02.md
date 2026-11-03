# Glass line and oil/gas thermal train to M3 — 2026-11-02

Authority: AQS-PLAN-006 (`docs-authority/MFG_MODEL_PLAN.md`) sections 1–5 and 7;
per-unit recipe pattern in `models/mfg/HX8/WORK_ORDER.md` (vessel close), the
accepted spool lane (`models/mfg/HDR_CO2/`) and the accepted thermal-reactor lane
(`models/mfg/MEOH_SYNTH/`). Graph Rev AD. One commit per unit (plan rule 4); this
note gains a section per accepted unit. Lane: GLASS_BURNOUT, GLASS_MILL,
GLASS_RINSE, GLASS_DIGEST (M2 close-out), AFTERBURNER, AFTERBURNER_FLUE,
OIL_DRYER, H2_DRYER, OIL_FRAC (M2 close-out), CRU. Every dimension comes from the
unit's own graph node, duty sheet and issued nozzle schedule; purchased items are
drawn as their envelope and interface per plan rule 6; misfits are §7-reported,
never resized.

## GLASS_BURNOUT (burnout rotary furnace, GLASS, tier 5) — commit 1

- `models/mfg/GLASS_BURNOUT/glass_burnout.py` on the shared lib. Route F-PIPE
  (the `intra` class sits in the F-PIPE row of plan section 4). Acceptance
  A-core + A-PIPE. Build 800 × 600 × 1200 mm against the node envelope: inside,
  exact; one closed manifold mesh; `cad/stl/GLASS_BURNOUT.stl` replaced from the
  build; `tracker --check GLASS_BURNOUT` green.
- Machine per the unit's own duty sheet and the ported AQS-MFG-001 form
  (`mfg_burnout_rotary.scad`): horizontal 316L drum OD 560 × 700, wall 12 mm
  (study — no drum dimension on the node or duty), two tire rings, trunnion
  stands over a 20 mm plinth. Drum-full volume 0.1579 m³ reported against the
  duty section 2 seven-day charge 0.2100 m³ — nothing resized (plan rule 3).
  No drive drawn: none named on the node or duty (WORK_ORDER W12).
- Nozzles: all 7 schedule rows at tag, face, height and bore, atmospheric hose
  barbs flush at the envelope faces (duty section 4). The N3/N4 schedule rows
  carried an unquoted comma ("Q2 burnout, not Q4") that shifted their face and
  height fields (the same defect class HX8 W12 (7) repaired); the rows were
  repaired to the schedule quoting in `docs-authority/nozzles/GLASS_BURNOUT.csv`
  (the generator only appends, hand rows are preserved verbatim). The two Q2
  rows ride graph edges whose presence is study; drawn verbatim, no new edge.
- A-PIPE line list `line_list.csv`: generated from the unit's present graph
  edges and the issued AQS-PIP-004 rows; study-edge lines carry the study note.
- Drawing set `models/mfg/GLASS_BURNOUT/drawings/`: ga_front, ga_side,
  nozzle_orient, drum01, stands01, aux01, iso01 (SVG + PDF, title blocks per
  AQS-DWG-002); the stale envelope-era sheet set and `GA.md` were superseded.
- WORK_ORDER W1–W12 beside the model; BOM generated from the model with
  make-or-buy; fasteners per the W5 grade rule; build log acceptance line
  "accepted per AQS-PLAN-006 section 5 (A-core + A-PIPE)"; check.json bbox
  record. Added to the tracker ACCEPTED row set; tracker and full regen run;
  `scripts/check_all.sh` green.

## GLASS_MILL (jar mill, GLASS, tier 5) — commit 2

- `models/mfg/GLASS_MILL/glass_mill.py` on the shared lib. Route F-PIPE,
  acceptance A-core + A-PIPE. Build 800 × 600 × 800 mm against the node
  envelope: inside, exact; one closed manifold mesh; `cad/stl/GLASS_MILL.stl`
  replaced from the build; `tracker --check GLASS_MILL` green.
- Machine per the unit's own duty sheet and the ported AQS-MFG-001 form
  (`mfg_mill.scad`): horizontal 316L jar OD 350 × 500, wall 8 mm (study — no
  jar dimension on the node or duty), trunnion journals in two V-roll cradle
  stands over a 20 mm plinth. Jar-full volume 0.0438 m³ reported against the
  duty section 2 seven-day charge 0.2577 m³ — nothing resized (plan rule 3).
  Media charge not drawn: the node carries internals none. No drive drawn:
  none named on the node or duty (WORK_ORDER W12).
- Nozzles: all 6 schedule rows at tag, face, height and bore, atmospheric
  hose barbs flush at the envelope faces; the N6 solids row (spent ceramic
  shell) drawn DN15, bore not calculated (plan W4). Line list generated from
  the unit's present edges and AQS-PIP-004, no new edge.
- 7-sheet drawing set (GA front/side, nozzle orientation, jar, stands, aux,
  iso) replaces the stale envelope-era set; WORK_ORDER W1–W12, BOM
  make-or-buy, fasteners, build log acceptance line, check.json. Added to the
  tracker ACCEPTED row set; tracker and full regen run; `--check` and
  `check_all` green.

## GLASS_RINSE (rinse/dewater bath, GLASS, tier 5) — commit 3

- `models/mfg/GLASS_RINSE/glass_rinse.py` on the shared lib. Route F-PIPE,
  acceptance A-core + A-PIPE. Build 1200 × 600 × 800 mm against the node
  envelope: inside, exact; one closed manifold mesh;
  `cad/stl/GLASS_RINSE.stl` replaced from the build;
  `tracker --check GLASS_RINSE` green.
- Machine per the unit's own duty sheet and the ported AQS-MFG-001 form
  (`mfg_rinse.scad`): open-topped 316L rinse bath to the envelope, walls 10 mm
  (study — no wall thickness on the node or duty), on a 20 mm plinth. Bath
  volume to the 100 mm freeboard 0.4585 m³ reported against the duty section 2
  seven-day charge 0.2577 m³ — nothing resized (plan rule 3). Dewater pump not
  drawn: no pump named on the node or duty (WORK_ORDER W12; the legacy form
  carried a DN80 pump hint only).
- Nozzles: all 4 schedule rows at tag, face, height and bore, atmospheric hose
  barbs flush at the envelope faces. Line list generated from the unit's
  present edges and AQS-PIP-004, no new edge.
- 7-sheet drawing set (GA front/side, nozzle orientation, bath, plinth, aux,
  iso) replaces the stale envelope-era set; WORK_ORDER W1–W12, BOM
  make-or-buy, fasteners, build log acceptance line, check.json. Added to the
  tracker ACCEPTED row set; tracker and full regen run; `--check` and
  `check_all` green.

## GLASS_DIGEST (NaOH cullet digestor, GLASS, tier 6) — commit 4 (M2 close-out)

- `models/mfg/GLASS_DIGEST/glass_digest.py` on the shared lib. Route F-VES,
  acceptance A-core + A-VES. Build 460 × 700 × 900 mm inside the 700 × 700 ×
  900 node envelope; one closed manifold mesh; `cad/stl/GLASS_DIGEST.stl`
  replaced from the build; `tracker --check GLASS_DIGEST` green.
- Close-out per the HX8 close pattern: the Oct-31-era `reactors.py` study
  build (M2) verified through the current shared lib — the issued X-MFG-31
  construction (CPVC OD 400 × wall 4 × H 400, bolted lid, 4 legs, PBT D133
  agitator at 358 rpm with 0.09 kW gearmotor envelope, Q3 PVDF DN15 coil)
  carried through the lib, the 12-row issued schedule replacing the 5-row
  study layout, placeholder datums clamped into the shell span (holds), and
  the section 5 artifacts completed: WORK_ORDER W1–W12 (the old 4-line route
  note superseded), BOM with make-or-buy and mass, fasteners via the lib,
  check.json, build log acceptance line, 7-sheet drawing set (the stale
  envelope-era sheets superseded), duty §7 pointer, tracker ACCEPTED row.
- A-VES report: model shell volume 48.3 L against the node V_L 49.9724 L
  (V_work 37.4793, tau 22.5014 h); no residence claim added. Duty section 3
  names 316L, the node design names CPVC — conflict carried as a hold
  (W12), nothing resized. The N4 schedule row quoting repaired ("digest
  NaOH, 20 wt%" — unquoted comma shifted face and height). Tracker and full
  regen run; `--check` and `check_all` green.

## AFTERBURNER (waste-gas combustion chamber, OIL, tier 6) — commit 5

- `models/mfg/AFTERBURNER/afterburner.py` on the shared lib. Route F-HX (the
  `thermal` class sits in the F-HX row of plan section 4), acceptance
  A-core + A-HX. Build 1000 × 600 × 800 mm against the node envelope: inside,
  filled exactly; one closed manifold mesh; `cad/stl/AFTERBURNER.stl` replaced
  from the build; `tracker --check AFTERBURNER` green.
- Machine per duty section 8 (AQS-DUTY-063 Rev B section 6, X-SAN-01):
  horizontal combustion chamber ID 200 × 600, ≥ 850 C for ≥ 2 s (Directive
  2010/75/EU Art. 50), steel shell wall 6 and refractory lining 50 as study
  values ("refractory and burner detail open" — holds, W12), on saddles over a
  20 mm plinth. Purchased envelopes per plan rule 6 from the node equipment
  list: burner + ignition transformer + BMS 0.05 kW, flue ID fan 0.1332 kW,
  dampers + flame monitor 0.01 kW.
- A-HX report: chamber volume 0.01885 m³; residence at the AFTERBURNER_FLUE
  node design flow 0.0018 m³/s (200 C flue class) is 10.5 s against the ≥ 2 s
  requirement — reported, not called a calculated design.
- Nozzles: all 12 schedule rows at tag, face, height and bore, atmospheric
  open-bore tube stubs flush at the envelope faces; the N12 solids row drawn
  DN15, bore not calculated (plan W4); the N4/N5 schedule row quoting repaired
  ("Q1 flue, not Q4" — unquoted comma shifted face and height).
- 7-sheet drawing set (GA front/side, nozzle orientation, chamber,
  supports+purchased envelopes, hardware, iso); WORK_ORDER W1–W12, BOM
  make-or-buy, fasteners, build log acceptance line, check.json. Added to the
  tracker ACCEPTED row set; tracker and full regen run; `--check` and
  `check_all` green.

## AFTERBURNER_FLUE (flue junction duct, GAS, tier 6) — commit 6 (route hold)

- `models/mfg/AFTERBURNER_FLUE/afterburner_flue.py` on the shared lib. Route
  hold: the `flue_junction` class has no plan section 4 route class, so the
  acceptance is A-core with the hold named (COMB_HEAT/RES_HEAT precedent);
  the node design block defines a duct, so the model follows the A-PIPE idiom
  (spool + line list) and the tracker keeps the route hold on the board.
  Build 1000 × 600 × 800 mm against the node envelope: inside, filled
  exactly; one closed manifold mesh; `cad/stl/AFTERBURNER_FLUE.stl` replaced
  from the build; `tracker --check AFTERBURNER_FLUE` green.
- Spool per the node design block: DN100 seat, 20 m run (0.133 m³) modeled as
  a 1000 mm representative spool on a 20 mm trough plinth (HDR_CO2 idiom);
  OD 114.3 × wall 6.02 as named ASME B36.10M Sch 40 values (DN100 sits
  outside the lib/dn DN15-DN50 table — hold, W12). Material 316L per duty
  section 3 (issued selection); the node design block says CS Sch 40
  insulated per AQS-THM-003 — conflict carried as a hold (W12), nothing
  resized. Insulation jacket 40 mm (study thickness, hold W12) with the
  dielectric isolating flange at the FLUE_KO end bare (AQS-STD-002 section
  4.3, drawn as the interface disc).
- Nozzles: all 5 schedule rows at tag, face, height and bore, atmospheric
  tube stubs flush at the envelope faces, stopping at the insulation surface.
- A-PIPE line list `line_list.csv`: MAIN spool row + the 3 issued lines
  (IA-AB-FLUE, IA-AB-AIR, S67), generated from the graph edges and
  AQS-PIP-004; no new edge.
- 7-sheet drawing set (GA front/side, nozzle orientation, spool+isolating
  flange, insulation, trough+branches, iso); WORK_ORDER W1–W12 with the route
  hold named first, BOM make-or-buy, fasteners, build log acceptance line,
  check.json. Added to the tracker ACCEPTED row set; tracker and full regen
  run; `--check` and `check_all` green.

## OIL_DRYER (jacketed drum dryer, OIL, tier 6) — commit 7

- `models/mfg/OIL_DRYER/oil_dryer.py` on the shared lib. Route F-MACH (the
  `dryer` class sits in the F-MACH row of plan section 4), acceptance
  A-core + A-MACH. Build 1000 × 600 × 800 mm against the node envelope:
  inside, filled exactly (the guard frame pins the registry box, X-PAR-04);
  one closed manifold mesh; `cad/stl/OIL_DRYER.stl` replaced from the build;
  `tracker --check OIL_DRYER` green.
- Machine per the unit's own duty sheet: horizontal jacketed drying drum OD
  500 × 700 (wall 6 study, hold W12) with a heating jacket OD 540 / annulus
  20 (study, hold W12) as the HX-4 Q3 heat surface (schedule N1/N2 service
  text verbatim), on saddles over a 20 mm plinth. A-MACH: guard frame drawn
  (four posts, mid and top rails), 8 anchors; no purchased items named on the
  node or duty — none drawn (hold, W12). Duty section 8: no holdup basis for
  this class — none claimed.
- Nozzles: all 7 schedule rows at tag, face, height and bore, atmospheric
  open-bore tube stubs flush at the envelope faces.
- 7-sheet drawing set (GA front/side, nozzle orientation, drum+jacket,
  frame+supports, hardware, iso); WORK_ORDER W1–W12, BOM make-or-buy,
  fasteners, build log acceptance line, check.json. Added to the tracker
  ACCEPTED row set; tracker and full regen run; `--check` and `check_all`
  green.

## H2_DRYER (molecular-sieve H2 dryer skid, GAS, tier 6) — commit 8

- `models/mfg/H2_DRYER/h2_dryer.py` on the shared lib. Route F-MACH, acceptance
  A-core + A-MACH. Build 600 × 400 × 1028 mm against the node envelope:
  inside, filled exactly (guard frame pins the registry box, X-PAR-04); one
  closed manifold mesh; `cad/stl/H2_DRYER.stl` replaced from the build;
  `tracker --check H2_DRYER` green.
- Skid per the node design block: dryer vessel OD 60.3 × 628, wall 3.91 (316L
  annealed per M6/AQS-REV-H2-001) with 38 mm insulation; 2 deoxo DN25 × 328;
  2 guard DN25 × 300; 2 TSA DN50 × 300 bed tubes with molecular-sieve and
  guard-media envelopes (sieve_kg 0.353, guard_kg 0.032); regeneration heater
  envelope (regen_W 1.03, purchased per plan rule 6); PVC-U inlet knock-out
  pot (duty section 3). A-MACH: guard frame drawn, 8 anchors. Bed stations
  are the layout choice (hold, W12).
- Nozzles: all 9 schedule rows at tag, face, height and bore, atmospheric
  open-bore tube stubs flush at the envelope faces; the N7 solids row drawn
  DN15, bore not calculated (plan W4); the N4 vent is the S24 relief edge to
  RELIEF_H2 (duty section 6) with the destination named.
- 7-sheet drawing set (GA front/side, nozzle orientation, vessel,
  beds+media, aux, iso); WORK_ORDER W1–W12, BOM make-or-buy with the four
  buy rows, fasteners, build log acceptance line, check.json. Added to the
  tracker ACCEPTED row set; tracker and full regen run; `--check` and
  `check_all` green.

## OIL_FRAC (fractionator column, OIL, tier 6) — commit 9 (M2 close-out)

- `models/mfg/OIL_FRAC/oil_frac.py` on the shared lib. Route F-COL, acceptance
  A-core + A-COL. Build 1000 × 600 × 800 mm against the node envelope
  (stage-owned by the write_graph scrubber pass — the builder reads it from
  params and does not pin it): inside, filled exactly (hold-down frame,
  X-PAR-04); one closed manifold mesh; `cad/stl/OIL_FRAC.stl` replaced from
  the build; `tracker --check OIL_FRAC` green.
- Close-out per the HX8 close pattern: the style-builders column study (M2)
  rebuilt through the current shared lib — vertical CS column shell OD 480,
  wall 6 (study; the duty states no diameter and no wall — drawn to the
  envelope, holds W12), heads and skirt seat inside a four-post hold-down
  frame; the 14-row issued schedule replacing the study layout; the section 5
  artifacts completed (WORK_ORDER W1–W12, make-or-buy BOM, fasteners —
  previously missing, check.json, build log acceptance line, 7-sheet drawing
  set, duty §7 pointer, tracker ACCEPTED row).
- A-COL: stages/HTU not stated anywhere — named hold; no packing, distributor
  or demister named on the node (internals none), so none drawn; the cut
  split rides the node cut_basis fractions (A-M-138) — a flowsheet
  allocation, not tray design. Sump report: the duty 0.0006 m³ (30 min) stands
  3.5 mm deep in the modeled bore — the sump zone is the bottom head; nothing
  resized (plan rule 3). Tracker and full regen run; `--check` and
  `check_all` green.

## CRU (chlorine-recovery chlorate vessel, DIGESTER, tier 6) — commit 10

- `models/mfg/CRU/cru.py` on the shared lib. Route F-VES (the `cru` class
  sits in the F-VES row of plan section 4), acceptance A-core + A-VES.
  Build 1000 × 600 × 800 mm against the node envelope: inside, filled
  exactly (hold-down frame pins the registry box, X-PAR-04); one closed
  manifold mesh; `cad/stl/CRU.stl` replaced from the build;
  `tracker --check CRU` green.
- Vessel per the unit's own duty sheet: vertical PVC-U chlorate-finish shell
  OD 520, wall 10 (study — the duty states no diameter and no wall: drawn to
  the envelope, holds W12), welded top and bottom, on a seat over a 20 mm
  plinth. Material per duty section 3: PVC-U wetted (AQS-STD-002 rules M1
  and M2; no metal wetted part); CA does not apply to the polymer. The
  temperature watch is a named hold (above 60 C the thermoplastic is CPVC,
  never metal; the graph gives no temperature for this unit).
- A-VES: the vessel holds 104.1 L to 100 mm below the top weld; the duty
  states no holdup basis for this class, so no residence time is derived.
- Nozzles: all 12 schedule rows at tag, face, height and bore, atmospheric
  open-bore tube stubs flush at the envelope faces; the six gas rows (cell
  gas in, chlorine out) stay on their gas edges, not the room.
- 7-sheet drawing set (GA front/side, nozzle orientation, vessel, frame,
  hardware, iso); WORK_ORDER W1–W12, BOM make-or-buy, fasteners, build log
  acceptance line, check.json. Added to the tracker ACCEPTED row set;
  tracker and full regen run; `--check` and `check_all` green.
