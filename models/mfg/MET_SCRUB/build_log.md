# Build log - MET_SCRUB

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-COL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MET_SCRUB.md`; envelope per `models/mfg/MET_SCRUB/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/MET_SCRUB/met_scrub.py`

## Checks

- Build bbox 1200 x 1200 x 4103 mm against the 1200 x 1200 x 4103 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/MET_SCRUB/export/met_scrub.step`; export STL closed and manifold, 1 solid(s); `cad/stl/MET_SCRUB.stl` replaced from the build (ASCII, metres)
- Nozzles: all 9 rows of `docs-authority/nozzles/MET_SCRUB.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-COL: packing height (2303 mm in two beds), support grid, redistribution disc, liquid distributor and PP mesh demister are solids (envelope solids; ring count not modelled); no stage or HTU count is claimed anywhere
- Internals basis: node design block (D 800, packed 2303, H 3803) and duty section 3 materials; bed elevations are the layout choice (hold, W12)
- BOM `models/mfg/MET_SCRUB/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MET_SCRUB/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/MET_SCRUB/met_scrub.py`
- `models/mfg/MET_SCRUB/draw_met_scrub.py`
- `models/mfg/MET_SCRUB/bom.csv`
- `models/mfg/MET_SCRUB/fasteners.csv`
- `models/mfg/MET_SCRUB/check.json`
- `models/mfg/MET_SCRUB/WORK_ORDER.md`
- `build export `models/mfg/MET_SCRUB/export/met_scrub.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-COL; holds named in WORK_ORDER W12.
