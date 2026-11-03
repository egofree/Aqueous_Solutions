# Build log - GEO_GHEX

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-HX; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GEO_GHEX.md`; envelope per `models/mfg/GEO_GHEX/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/GEO_GHEX/geo_ghex.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/GEO_GHEX/export/geo_ghex.step`; export STL closed and manifold, 3 solid(s); `cad/stl/GEO_GHEX.stl` replaced from the build (ASCII, metres)
- Nozzles: all 3 rows of `docs-authority/nozzles/GEO_GHEX.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Ground heat exchanger manifold skid per the node design block (design_survey_locked, ST-ORC-01): DN32 HDPE flow/return headers, two bore-pair tie-in stubs to below grade (interface indication), pump envelope (125.7 W, node) and glycol fill pot
- A-HX: loop area 186 m DN32 = 24.8 m2 reported from the model plus the node-quoted buried run - not called a calculated duty (the duty states no mass throughput; q_per_m/Q_ceiling are the survey-locked class figures)
- The boreholes are drilled subsurface works (site/well lane): depth/spacing named, not drawn to depth (hold W12); hose-barb nozzles per the schedule (bores not calculated, hose, atmospheric)
- BOM `models/mfg/GEO_GHEX/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/GEO_GHEX/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/GEO_GHEX/geo_ghex.py`
- `models/mfg/GEO_GHEX/draw_geo_ghex.py`
- `models/mfg/GEO_GHEX/bom.csv`
- `models/mfg/GEO_GHEX/fasteners.csv`
- `models/mfg/GEO_GHEX/check.json`
- `models/mfg/GEO_GHEX/WORK_ORDER.md`
- `build export `models/mfg/GEO_GHEX/export/geo_ghex.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-HX; holds named in WORK_ORDER W12.
