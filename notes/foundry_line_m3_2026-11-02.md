# Foundry line to M3 — 2026-11-02

Authority: AQS-PLAN-006 (`docs-authority/MFG_MODEL_PLAN.md`) sections 1–5 and 7;
per-unit recipe patterns in `models/mfg/MEOH_SYNTH/` (machine family with an
issued schedule), `models/mfg/WS_PHOS/` and `models/mfg/HX8/WORK_ORDER.md`.
Graph Rev AD. One commit per unit (plan rule 4); this note gains a section per
accepted unit. Lane: the FOUNDRY train and its N+1 forming alternates, in the
work order IND_MELT, VAC_IND, VAC_CAST, INV_CAST, CONT_CAST, CAST_LINE,
COMB_HEAT, RES_HEAT, RF_HEAT, FORGE, EXTRUDE, DRAW. Every dimension comes from
the unit's own graph node, duty sheet and issued nozzle schedule; connection
hardware draws flush at the envelope faces (nothing protrudes, A-core 2);
misfits are §7-reported, never resized; the standby_rated N+1 alternates
(A-M-282/A-M-283) are real machines drawn per their design blocks, named as
standby in their work orders and BOMs, not placeholder boxes.

## IND_MELT (medium-frequency coreless induction remelt furnace, FOUNDRY, tier 6) — commit 1

- Rebuild through the current lib in `models/mfg/IND_MELT/ind_melt.py`; the
  Oct-31 protruding hardware (charge chute −35 mm, +X trunnion pin +25 mm,
  +Y melt stubs +6 mm) moved flush to the envelope faces, so the A-core 2
  overshoot the §7 row carried since the flush idiom landed is cleared, not
  resized: measured 1000.0 × 1000.0 × 1500.0 mm, face overhang 0 mm all round.
  `tracker --check IND_MELT` green; `cad/stl/IND_MELT.stl` replaced from the
  in-envelope build solid (scope in `check.json` `cad_stl_scope`).
- All 17 schedule rows drawn (melt stubs set in through the +Y wall at z 600;
  the ten solids rows on the −X charge chute and the +X slag spout at DN15,
  bore not calculated per W4; N16 drain flush at the bottom; N17 vent on the
  hood). BOM complete with make-or-buy (crucible and the 25 kW PSU are the buy
  rows); fasteners grade 8.8 carbon steel per the W5 grade rule.
- WORK_ORDER.md rewritten to the W1–W12 items with the holds named (route-class
  hold for `furnace`, placeholder elevations, solids bores, pending relief case,
  purchased ratings); the builder no longer writes the work order, so a rebuild
  never clobbers it.
- Drawing set regenerated from the rebuilt solids (8 sheets; title blocks per
  AQS-DWG-002, graph Rev AD). Duty section 7 already named the model source.
  Tracker row 80: M3, misfit cleared. Route hold stays reported.

## VAC_IND (vacuum induction skull-melt furnace, FOUNDRY N+1 alternate, tier 6) — commit 2

- New per-unit model `models/mfg/VAC_IND/vac_ind.py` on the shared lib, the
  POLY_COND installed-standby idiom: the standby_rated N+1 alternate (A-M-282/
  A-M-283) is drawn as the real machine per its node design block and duty
  section 3 — 304L vacuum chamber (t6) with the ceramic-fibre insulation
  package inside the vacuum boundary, water-cooled Cu crucible (no
  wetted-refractory interface), ISM coil and lead to the 15 kW PSU bay, tilt
  pour about the z 500 trunnions — replacing the placeholder envelope box.
  Standby named in the WORK_ORDER header, the BOM rows and the build log.
- All 5 schedule rows drawn flush at the envelope faces (N1/N3 +Y melt rows at
  z 600; N2 solids charge port at DN15, bore not calculated; N4 drain through
  the plinth; N5 vent riser on the chamber lid; the 800 datum is the schedule
  placeholder, W12). The inlet/outlet face words map to compass by the
  registered layout in the params layout block.
- Build fills the node box exactly (1000 × 1000 × 1500, zero face overhang);
  `tracker --check VAC_IND` green; `cad/stl/VAC_IND.stl` replaced from the
  build; BOM complete with make-or-buy (PSU cabinet is the buy row); fasteners
  grade rule W5 (8.8 CS anchors, A4-70 on the 304L lid studs); WORK_ORDER
  rewritten to W1–W12 with holds named (route-class hold for `furnace`, study
  chamber wall, placeholder elevations, pending vacuum/relief case, purchased
  ratings, loop hardware).
- Drawing set: new 7-sheet set (ga_front/ga_side/nozzle_orient/chamber01/
  melt01/aux01/iso01; title blocks per AQS-DWG-002, graph Rev AD); the stale
  Oct-31 3-sheet GA SVGs are regenerated into it. Duty section 7 now names the
  model source via `docs-authority/_duty_basis.py`. Tracker row 127: M3.
  Route hold stays reported.
