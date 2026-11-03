# Build log - AQUA_UV

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-FARM; A-MACH practice on the purchased lamp; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/AQUA_UV.md`; envelope per `models/mfg/AQUA_UV/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/AQUA_UV/aqua_uv.py`

## Checks

- Rebuild through the shared close-out builder (`models/mfg/farm_closeout.py`) confirms the Oct-31 cabinet at the node box: measured 400.0 x 350.0 x 750.0 mm, flush on all six faces, no section-7 misfit; `cad/stl/AQUA_UV.stl` replaced from the build (scope in `check.json` `cad_stl_scope`)
- Reactor train corrected: the Oct-31 reactor was a rectangular sheet shell (the `extras_mm` box idiom); the rebuild draws the tube the duty section 3 names - SS304 tube OD 90 x 280 (wall 2 mm study) on the centreline at z 250, quartz sleeve OD 60 x 260 inside it, and the 0.04 kW lamp as its envelope rod (purchased per plan rule 6, named with the node rating - A-MACH practice; the cabinet is the guard)
- Route-class hold named: `uv_sanitizer` has no AQS-PLAN-006 section 4 class; the F-FARM practice is the named study route
- Internals: node row `none`; the duty-named reactor train is drawn; sleeve and lamp diameters are study proportions (hold, W12)
- Nozzles: all 4 rows of `docs-authority/nozzles/AQUA_UV.csv` drawn at tag, face, height and bore as DN15 PP tube stubs flush at the envelope faces; N4 vent drawn at the envelope top (schedule z 800 predates the 750 box, stale datum, hold W12); atmospheric joints, no flange; schedule rating column carried verbatim
- BOM `models/mfg/AQUA_UV/bom.csv` (generated from the model: qty, material, mass, make-or-buy; the lamp and sleeve are the buy rows); `fasteners.csv` completed (base anchors 8.8 CS, saddle clamps A4-70 per the grade rule); WORK_ORDER rewritten to the W1-W12 items with holds named; no builder writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/AQUA_UV/aqua_uv.py`
- `models/mfg/AQUA_UV/export/aqua_uv.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-FARM; A-MACH practice recorded on the purchased lamp; route-class hold named in WORK_ORDER W12.
