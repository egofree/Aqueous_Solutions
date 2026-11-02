# Build log - MET_HX_Q4

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-HX; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MET_HX_Q4.md`; envelope per `models/mfg/MET_HX_Q4/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/MET_HX_Q4/met_hx_q4.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/MET_HX_Q4/export/met_hx_q4.step`; export STL closed and manifold, 1 solid(s); `cad/stl/MET_HX_Q4.stl` replaced from the build (ASCII, metres)
- Nozzles: all 3 rows of `docs-authority/nozzles/MET_HX_Q4.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-HX: the 3.9188 m2 bundle area is reported as DRAWN, not called calculated - the node has no heat rate (duty section 2)
- Material conditional: drawn 316L per duty section 3 s wet branch; the carbon-steel alternative is a named hold (W12)
- BOM `models/mfg/MET_HX_Q4/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MET_HX_Q4/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/MET_HX_Q4/met_hx_q4.py`
- `models/mfg/MET_HX_Q4/draw_met_hx_q4.py`
- `models/mfg/MET_HX_Q4/bom.csv`
- `models/mfg/MET_HX_Q4/fasteners.csv`
- `models/mfg/MET_HX_Q4/check.json`
- `models/mfg/MET_HX_Q4/WORK_ORDER.md`
- `build export `models/mfg/MET_HX_Q4/export/met_hx_q4.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-HX; holds named in WORK_ORDER W12.
