# Build log - DUCK_PEN

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-FARM; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/DUCK_PEN.md`; envelope per `models/mfg/DUCK_PEN/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/DUCK_PEN/duck_pen.py`

## Checks

- Flush rebuild through the shared close-out builder (`models/mfg/farm_closeout.py`) confirms the Oct-31 frame at the node box: measured 2500.0 x 1300.0 x 1300.0 mm, flush on all six faces, no section-7 misfit. `cad/stl/DUCK_PEN.stl` replaced from the build (scope in `check.json` `cad_stl_scope`)
- The wallow strip the size_basis names is drawn as the liner duty section 3 specifies: EPDM patch 800 x 600 x 5 on the drop board at the -X end (permanently wet class, standing water governs); patch layout is a study choice (hold, W12). The SS316 waterers are not drawn - no rating on the node (hold, W12)
- Route-class hold named: `pen` has no AQS-PLAN-006 section 4 class; the F-FARM practice is the named study route
- Nozzles: all 9 rows of `docs-authority/nozzles/DUCK_PEN.csv` drawn at tag, face, height and bore as DN15 tube stubs flush at the envelope faces; N7 drain lands over the wallow end; N8 vent drawn at the envelope top (schedule z 800 predates the 1300 box, stale datum, hold W12); the elevations are schedule placeholders (duty tasks 02/06) and the cloth-wall backing is a fabrication detail (hold W12); atmospheric joints, no flange; rating column carried verbatim
- BOM `models/mfg/DUCK_PEN/bom.csv` (generated from the model: qty, material, mass, make-or-buy; cloth and wallow liner are the buy rows); `fasteners.csv` completed (base anchors 8.8 CS, wallow batten screws A4-70 polymer supplier rule); WORK_ORDER rewritten to the W1-W12 items with holds named; no builder writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/DUCK_PEN/duck_pen.py`
- `models/mfg/DUCK_PEN/export/duck_pen.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-FARM; route-class hold named in WORK_ORDER W12.
