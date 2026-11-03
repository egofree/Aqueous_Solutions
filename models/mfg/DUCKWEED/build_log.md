# Build log - DUCKWEED

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-FARM; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/DUCKWEED.md`; envelope per `models/mfg/DUCKWEED/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/DUCKWEED/duckweed.py`

## Checks

- Flush rebuild through the shared close-out builder (`models/mfg/farm_closeout.py`) fills the node box exactly: measured 30100.0 x 10100.0 x 700.0 mm, flush on all six faces, no section-7 misfit. `cad/stl/DUCKWEED.stl` replaced from the build (scope in `check.json` `cad_stl_scope`)
- Liner drawn as the sheet the params name: EPDM 5 mm floor + four walls to the berm base at z 500 (the GROW_BED ponded-zone idiom; the Oct-31 build drew a floor-only liner block); berm band bare per the size_note
- Water line reported not drawn: the 400 mm line is a size_note figure; water and duckweed mat are process inventory, not BOM parts. Raceway flow layout not drawn - no node layout (hold, W12)
- Route-class hold named: `duckweed` has no AQS-PLAN-006 section 4 class; the F-FARM practice is the named study route
- Nozzles: all 17 rows of `docs-authority/nozzles/DUCKWEED.csv` drawn at tag, face, height and bore as DN15/DN50 tube stubs flush at the envelope faces (N2 is the DN50 row); N8 vent drawn at the envelope top (schedule z 400 predates the 700 box, stale datum, hold W12); atmospheric joints, no flange; rating column carried verbatim
- BOM `models/mfg/DUCKWEED/bom.csv` (generated from the model: qty, material, mass, make-or-buy; the liner roll is the buy row); `fasteners.csv` completed (liner batten bolts A4-70 polymer supplier rule, base anchors 8.8 CS per the grade rule); WORK_ORDER rewritten to the W1-W12 items with holds named; no builder writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/DUCKWEED/duckweed.py`
- `models/mfg/DUCKWEED/export/duckweed.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-FARM; route-class hold named in WORK_ORDER W12.
