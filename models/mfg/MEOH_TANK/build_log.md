# Build log - MEOH_TANK

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MEOH_TANK.md`; envelope per `models/mfg/MEOH_TANK/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/MEOH_TANK/meoh_tank.py`

## Checks

- Build bbox 600 x 600 x 600 mm against the 600 x 600 x 600 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/MEOH_TANK/export/meoh_tank.step`; export STL closed and manifold, 1 solid(s); `cad/stl/MEOH_TANK.stl` replaced from the build (ASCII, metres)
- Nozzles: all 15 rows of `docs-authority/nozzles/MEOH_TANK.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-VES: the 0.1028 m3 liquor volume is reported - the duty working volume (0.0421 m3, 7 days) stays the booked basis and no residence time is derived
- Duty sheet shell line 800 x 800 x 1100 vs node AQS-DUTY-064 box: the node governs, the sheet line is a named hold (W12)
- BOM `models/mfg/MEOH_TANK/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MEOH_TANK/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/MEOH_TANK/meoh_tank.py`
- `models/mfg/MEOH_TANK/draw_meoh_tank.py`
- `models/mfg/MEOH_TANK/bom.csv`
- `models/mfg/MEOH_TANK/fasteners.csv`
- `models/mfg/MEOH_TANK/check.json`
- `models/mfg/MEOH_TANK/WORK_ORDER.md`
- `build export `models/mfg/MEOH_TANK/export/meoh_tank.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
