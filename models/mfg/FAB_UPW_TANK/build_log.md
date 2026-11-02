# Build log - FAB_UPW_TANK

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/FAB_UPW_TANK.md`; envelope per `models/mfg/FAB_UPW_TANK/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/FAB_UPW_TANK/fab_upw_tank.py`

## Checks

- Build bbox 600 x 600 x 600 mm against the 600 x 600 x 600 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/FAB_UPW_TANK/export/fab_upw_tank.step`; export STL closed and manifold, 1 solid(s); `cad/stl/FAB_UPW_TANK.stl` replaced from the build (ASCII, metres)
- Nozzles: all 4 rows of `docs-authority/nozzles/FAB_UPW_TANK.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-VES: the 0.1014 m3 liquor volume is reported - the vessel is not built (duty section 8) and no residence time is derived
- Duty seven-day figure vs node box: named hold, nothing resized (W12)
- BOM `models/mfg/FAB_UPW_TANK/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/FAB_UPW_TANK/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/FAB_UPW_TANK/fab_upw_tank.py`
- `models/mfg/FAB_UPW_TANK/draw_fab_upw_tank.py`
- `models/mfg/FAB_UPW_TANK/bom.csv`
- `models/mfg/FAB_UPW_TANK/fasteners.csv`
- `models/mfg/FAB_UPW_TANK/check.json`
- `models/mfg/FAB_UPW_TANK/WORK_ORDER.md`
- `build export `models/mfg/FAB_UPW_TANK/export/fab_upw_tank.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
