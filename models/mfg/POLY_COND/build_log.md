# Build log - POLY_COND

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/POLY_COND.md`; envelope per `models/mfg/POLY_COND/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/POLY_COND/poly_cond.py`

## Checks

- Build bbox 600 x 600 x 1200 mm against the 600 x 600 x 1200 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/POLY_COND/export/poly_cond.step`; export STL closed and manifold, 2 solid(s); `cad/stl/POLY_COND.stl` replaced from the build (ASCII, metres)
- Nozzles: all 3 rows of `docs-authority/nozzles/POLY_COND.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Installed standby: the node envelope state is standby and the duty flows are 0; the model covers the installed geometry (W12)
- Agitator drawn as solids per the node design row (0.18 kW) into the purchased drive envelope (plan rule 6)
- A-VES: gross shell volume reported for the record; no holdup claimed, no residence derived (W12)
- BOM `models/mfg/POLY_COND/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/POLY_COND/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/POLY_COND/poly_cond.py`
- `models/mfg/POLY_COND/draw_poly_cond.py`
- `models/mfg/POLY_COND/bom.csv`
- `models/mfg/POLY_COND/fasteners.csv`
- `models/mfg/POLY_COND/check.json`
- `models/mfg/POLY_COND/WORK_ORDER.md`
- `build export `models/mfg/POLY_COND/export/poly_cond.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
