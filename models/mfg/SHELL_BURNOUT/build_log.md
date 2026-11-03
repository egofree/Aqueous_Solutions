# Build log - SHELL_BURNOUT

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/SHELL_BURNOUT.md`; envelope per `models/mfg/SHELL_BURNOUT/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/SHELL_BURNOUT/shell_burnout.py`

## Checks

- Build bbox 1000 x 1000 x 1500 mm against the 1000 x 1000 x 1500 mm envelope: filled exactly, inside (tracker check green). The flush-hardware rebuild moves the N1 green-shell inlet (-X), the N2 fired-shell outlet (+X), the N3/N4 stubs (+Y) and the N5 off-gas stub (-Y) to the envelope faces, so the A-core 2 overshoot the §7 row carried (1060.0 x 1040.0 x 1500.0) is cleared, not resized; `cad/stl/SHELL_BURNOUT.stl` replaced from the in-envelope build solid (scope in `check.json` `cad_stl_scope`)
- Door integrity repair: the Oct-31 "door opening" cut floated inside the casing cavity and removed nothing - the rebuild cuts the opening through the -X wall and the hot-face throat, and the door slab seats flush at the face over it; the phantom +Y stub casing passes (cut from W+5, missing the wall) are corrected to pass through the +Y wall; the N1 inlet gets its real pass behind the -X chute and moves beside the door (the registered layout keeps N1 on -X at z 160)
- Route-class hold named: `furnace` has no AQS-PLAN-006 section 4 class; the furnace practice (RES_HEAT/COMB_HEAT idiom) is the named study route. The 0.25 kW element set purchases at fabrication (named on BOM row 2, held in W12)
- Internals: node row `none`; the machine the design block names (flash-dewax + shell fire furnace at 900 C) is drawn as the unit - casing, hot face, hearth, condensate pan, off-gas collector; the shell racks are process-inventory solids, not BOM parts
- Nozzles: all 7 rows of `docs-authority/nozzles/SHELL_BURNOUT.csv` present at tag, face, height and bore, flush at the envelope faces; solids rows drawn as chutes/outlet boxes, bore not calculated per W4; atmospheric joints, no flange; schedule rating column carried verbatim
- BOM `models/mfg/SHELL_BURNOUT/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners 8.8 CS per the W5 grade rule (door hinges + slab anchors); WORK_ORDER rewritten to the W1-W12 items with holds named; the builder no longer writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets: ga_front/ga_side/nozzle_orient/sh01/hd01/el01/aux01/iso01; title blocks per AQS-DWG-002, graph Rev AD; the stale "Graph revision AC" iso note corrected to the live revision)

## Sources

- `models/mfg/SHELL_BURNOUT/draw_shell_burnout.py`
- `models/mfg/SHELL_BURNOUT/shell_burnout.py`
- `models/mfg/SHELL_BURNOUT/export/shell_burnout.step`

Status: accepted per AQS-PLAN-006 section 5 A-core; route-class hold named in WORK_ORDER W12.
