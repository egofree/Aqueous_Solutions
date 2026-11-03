# Build log - CHICKEN_COOP

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-FARM; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CHICKEN_COOP.md`; envelope per `models/mfg/CHICKEN_COOP/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/CHICKEN_COOP/chicken_coop.py`

## Checks

- Flush rebuild through the shared close-out builder (`models/mfg/farm_closeout.py`) confirms the Oct-31 frame at the node box: measured 2500.0 x 1300.0 x 1900.0 mm, flush on all six faces, no section-7 misfit. `cad/stl/CHICKEN_COOP.stl` replaced from the build (scope in `check.json` `cad_stl_scope`)
- The size_basis fittings are drawn: the perch the size_basis names (HDG rod OD 40 on two posts that lap through the wire floor and into the rod - the volumetric-overlap idiom that keeps the export manifold; the face-to-face first attempt left it non-manifold) and the HDPE drop-board liner sheet duty section 3 names (5 mm over the board)
- Nest row = the purchased envelope (plan rule 6): drawn as its box envelope, bought complete; the drawn-envelope mass is the HDG table-density figure, the purchase mass is the maker's (hold, W12). The SS316 feeders and waterers are not drawn - no rating on the node (hold, W12)
- Route-class hold named: `coop` has no AQS-PLAN-006 section 4 class; the F-FARM practice is the named study route
- Nozzles: all 10 rows of `docs-authority/nozzles/CHICKEN_COOP.csv` drawn at tag, face, height and bore as DN15 tube stubs flush at the envelope faces; N8 vent drawn at the envelope top (schedule z 800 predates the 1900 box, stale datum, hold W12); the elevations are schedule placeholders (duty tasks 02/06) and the cloth-wall backing is a fabrication detail (hold W12); atmospheric joints, no flange; rating column carried verbatim
- BOM `models/mfg/CHICKEN_COOP/bom.csv` (generated from the model: qty, material, mass, make-or-buy; cloth and nest row are the buy rows); `fasteners.csv` completed (nest-row bolts and base anchors 8.8 CS per the grade rule); WORK_ORDER rewritten to the W1-W12 items with holds named; no builder writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/CHICKEN_COOP/chicken_coop.py`
- `models/mfg/CHICKEN_COOP/export/chicken_coop.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-FARM; route-class hold named in WORK_ORDER W12.
