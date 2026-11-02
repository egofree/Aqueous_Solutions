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
