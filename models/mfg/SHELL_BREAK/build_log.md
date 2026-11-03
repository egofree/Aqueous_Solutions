# Build log - SHELL_BREAK

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/SHELL_BREAK.md`; envelope per `models/mfg/SHELL_BREAK/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/SHELL_BREAK/shell_break.py`

## Checks

- Build bbox 1500 x 800 x 1500 mm against the 1500 x 800 x 1500 mm envelope: filled exactly, inside (tracker check green). The flush-hardware rebuild moves the N1 cast inlet (-X) and the N4/N5 outlet boxes (+Y) to the envelope faces, clearing the CAD-compound overhang the Oct-31 check.json recorded (30/0/0/10 mm; the Oct-31 export STL read 1500 x 800 x 1500 but the on-disk artifacts disagreed with the builder's own record - this rebuild makes the export STL, check.json and builder agree at 0/0/0/0 mm); nothing resized; `cad/stl/SHELL_BREAK.stl` replaced from the in-envelope build solid (scope in `check.json` `cad_stl_scope`)
- A-VES: the model holdup (reclaim pan, 5.2 L) is reported in check.json `reclaim_pan_volume_litres`; it is not used as a residence time (the duty carries the A-M-286 mass split, not a holdup basis)
- Internals: node row `none`; the machine the design block names (vibratory shell knock-out station with reclaim sieve) is drawn as the unit per the duty sheet - vibratory table 700 x 400 x 60 with the 0.4 kW drive, inclined reclaim sieve with mesh window, reclaim pan, dust enclosure hood; the cast tree is a process-inventory solid, not a BOM part
- Nozzles: all 7 rows of `docs-authority/nozzles/SHELL_BREAK.csv` present at tag, face, height and bore, flush at the envelope faces; solids rows drawn as chutes/outlet boxes, bore not calculated per W4; atmospheric joints, no flange; schedule rating column carried verbatim
- BOM `models/mfg/SHELL_BREAK/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners completed with the table-mount and hood-bolt rows beside the slab anchors (8.8 CS per the W5 grade rule); WORK_ORDER rewritten to the W1-W12 items with holds named; the builder no longer writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets: ga_front/ga_side/nozzle_orient/sh01/hd01/el01/aux01/iso01; title blocks per AQS-DWG-002, graph Rev AD; the stale "Graph revision AC" iso note corrected to the live revision)

## Sources

- `models/mfg/SHELL_BREAK/draw_shell_break.py`
- `models/mfg/SHELL_BREAK/shell_break.py`
- `models/mfg/SHELL_BREAK/export/shell_break.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; the machine-design detail (isolation mounts, dust tie-in) follows the unit WORK_ORDER; holds named in WORK_ORDER W12.
