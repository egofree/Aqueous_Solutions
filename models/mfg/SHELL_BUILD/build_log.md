# Build log - SHELL_BUILD

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-SC; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/SHELL_BUILD.md`; envelope per `models/mfg/SHELL_BUILD/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/SHELL_BUILD/shell_build.py`

## Checks

- Build bbox 1500 x 800 x 1500 mm against the 1500 x 800 x 1500 mm envelope: filled exactly, inside (tracker check green). The flush-hardware rebuild moves the N1 pattern chute and the N3/N4 silica inlets (-X) and the N2 green-shell outlet (+X) to the envelope faces, so the A-core 2 overshoot the §7 row carried (1545.0 x 800.0 x 1500.0) is cleared, not resized; `cad/stl/SHELL_BUILD.stl` replaced from the in-envelope build solid (scope in `check.json` `cad_stl_scope`)
- A-SC (tier 7): every BOM make row carries the AQS-BOM-SC-001 flag and WORK_ORDER W11 cross-references the register (the booth builds the foundry's own investment shells); the agitator and hoist drives purchase at fabrication (hold W12)
- Route-class hold named: `coater` has no AQS-PLAN-006 section 4 class; the F-MACH practice is the named study route (ELECTRODE_COAT/LITHO_COAT precedent)
- Internals: node row `none`; the machine the design block names (dip-coat + rainfall-stucco booth, 6 dips, 40 L slurry) is drawn as the unit per the duty sheet
- Nozzles: all 6 rows of `docs-authority/nozzles/SHELL_BUILD.csv` present at tag, face, height and bore, flush at the envelope faces; solids rows drawn as chutes/outlet boxes, bore not calculated per W4; atmospheric joints, no flange; schedule rating column carried verbatim
- BOM `models/mfg/SHELL_BUILD/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners completed with the tank hold-down and mast base-plate rows beside the slab anchors (8.8 CS, A4-70 at the 316L tank joints per the W5 grade rule); WORK_ORDER rewritten to the W1-W12 items with holds named; the builder no longer writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets: ga_front/ga_side/nozzle_orient/sh01/hd01/el01/aux01/iso01; title blocks per AQS-DWG-002, graph Rev AD; the stale "Graph revision AC" iso note corrected to the live revision)

## Sources

- `models/mfg/SHELL_BUILD/draw_shell_build.py`
- `models/mfg/SHELL_BUILD/shell_build.py`
- `models/mfg/SHELL_BUILD/export/shell_build.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-SC; route-class hold named in WORK_ORDER W12.
