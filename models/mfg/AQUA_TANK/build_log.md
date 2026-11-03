# Build log - AQUA_TANK

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-FARM; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/AQUA_TANK.md`; envelope per `models/mfg/AQUA_TANK/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/AQUA_TANK/aqua_tank.py`

## Checks

- Rebuild through the shared close-out builder (`models/mfg/farm_closeout.py`) confirms the Oct-31 tank at the node box: measured 2100.0 x 1100.0 x 1100.0 mm, flush on all six faces, no section-7 misfit; `cad/stl/AQUA_TANK.stl` replaced from the build (scope in `check.json` `cad_stl_scope`)
- Liner corrected: the Oct-31 liner was a solid block filling the cavity (2230.4 kg); the rebuild draws the 5 mm liner sheet the params name (`liner_mm` 5, duty section 3 LDPE liner class; floor + four walls, the GROW_BED ponded-zone idiom) - liner mass 41.9 kg, carried at the HDPE table density until the supplier TDS (hold, WORK_ORDER W12)
- Route-class hold named: `fish_tank` has no AQS-PLAN-006 section 4 class; the F-FARM practice is the named study route
- Internals: node row `none`; the duty-named liner sheet is drawn; the design-block aeration (air stones) is not drawn - no position or rating on the node (hold, W12)
- Nozzles: all 8 rows of `docs-authority/nozzles/AQUA_TANK.csv` drawn at tag, face, height and bore as DN15 CPVC tube stubs flush at the envelope faces; N8 vent drawn at the envelope top (schedule z 800 predates the 1100 box, stale datum, hold W12); atmospheric joints, no flange; schedule rating column carried verbatim
- BOM `models/mfg/AQUA_TANK/bom.csv` (generated from the model: qty, material, mass, make-or-buy); `fasteners.csv` completed (lid hold-downs A4-70 polymer-joint rule, base anchors 8.8 CS per the grade rule); WORK_ORDER rewritten to the W1-W12 items with holds named; no builder writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/AQUA_TANK/aqua_tank.py`
- `models/mfg/AQUA_TANK/export/aqua_tank.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-FARM; route-class hold named in WORK_ORDER W12.
