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
