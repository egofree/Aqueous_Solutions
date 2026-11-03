# Build log - TI_CELL

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-CELL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/TI_CELL.md`; envelope per `models/mfg/TI_CELL/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/TI_CELL/ti_cell.py`

## Checks

- Rebuild through the current lib confirms the Oct-31 build as issued: no protruding hardware (face overhang 0/0/0/0 mm), no §7 misfit on this unit, so no geometry changed. Skid frame spans the 800 x 800 x 1600 envelope exactly (retort lift beam pins the top); the vessel-group bbox 680 x 230 x 752 mm is recorded beside it in check.json; `cad/stl/TI_CELL.stl` replaced from the build (scope in `check.json` `cad_stl_scope`, `external_parts` empty)
- A-CELL record: the duty section 2 design row is thermochemical (I_A 0, no electrolysis - AQS-BAL-KROLL), so the plate count/size/pitch/active-area criteria carry no duty-stated values; the class acceptance runs on A-core with the record named in WORK_ORDER W3/W12. The 0.5 kW hold duty is resistance elements in the chlorinator band and furnace box. No bus (no electrolysis); the busbar rule of AQS-BUS-001/POWER.md does not apply
- Nozzles: all 14 rows of `docs-authority/nozzles/TI_CELL.csv` present at tag, face, height and bore, attached to their vessels; solids rows (N1/N2/N4/N5/N8/N10/N11) drawn as chutes/ports/spouts, bore not calculated per W4; atmospheric joints, no flange; schedule rating column carried verbatim
- Internals: node row `none`; the Ti sponge is a process-inventory solid (study campaign fill), not a BOM part; the retort vacuum/Ar hardware and the condenser coolant loop are loop hardware (hold W12)
- Hygiene: the slab-anchor row added to `fasteners.csv` (the Oct-31 file carried no anchor row for the bolted skid-to-slab joint); WORK_ORDER rewritten to the W1-W12 items with holds named; the builder no longer writes the work order, so a rebuild never clobbers it
- Drawing set regenerated (8 sheets: ga_front/ga_side/nozzle_orient/sh01/hd01/el01/aux01/iso01; title blocks per AQS-DWG-002, graph Rev AD; the stale "Graph revision AC" iso note corrected to the live revision)

## Sources

- `models/mfg/TI_CELL/draw_ti_cell.py`
- `models/mfg/TI_CELL/ti_cell.py`
- `models/mfg/TI_CELL/export/ti_cell.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-CELL; the machine-design detail (weld procedures, refractory installation) follows the unit WORK_ORDER; holds named in WORK_ORDER W12.
