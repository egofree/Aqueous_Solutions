# Build log - OIL_DRYER

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/OIL_DRYER.md`; envelope per `models/mfg/OIL_DRYER/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/OIL_DRYER/oil_dryer.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/OIL_DRYER/export/oil_dryer.step`; export STL closed and manifold, 6 solid(s); `cad/stl/OIL_DRYER.stl` replaced from the build (ASCII, metres)
- Nozzles: all 7 rows of `docs-authority/nozzles/OIL_DRYER.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Machine: horizontal jacketed drying drum OD 500 x 700 (wall 6, study), jacket annulus 20 (study) as the HX-4 Q3 heat surface, on saddles over a 20 mm plinth (holds, W12)
- A-MACH: guard frame drawn (four posts, mid and top rails) and anchors in fasteners.csv; no purchased items named on the node or duty - none drawn (hold, W12)
- Duty basis: float plastics 33 kg/d dried and out to OIL_PYRO; the internals row is none and the duty claims no holdup basis, so none is drawn
- BOM `models/mfg/OIL_DRYER/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/OIL_DRYER/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/OIL_DRYER/oil_dryer.py`
- `models/mfg/OIL_DRYER/draw_oil_dryer.py`
- `models/mfg/OIL_DRYER/bom.csv`
- `models/mfg/OIL_DRYER/fasteners.csv`
- `models/mfg/OIL_DRYER/check.json`
- `models/mfg/OIL_DRYER/WORK_ORDER.md`
- `build export `models/mfg/OIL_DRYER/export/oil_dryer.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH; holds named in WORK_ORDER W12.
