# Build log - CATCH_TANK

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CATCH_TANK.md`; envelope per `models/mfg/CATCH_TANK/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/CATCH_TANK/catch_tank.py`

## Checks

- Build bbox 649 x 520 x 748 mm against the 649 x 520 x 748 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/CATCH_TANK/export/catch_tank.step`; export STL closed and manifold, 1 solid(s); `cad/stl/CATCH_TANK.stl` replaced from the build (ASCII, metres)
- Nozzles: all 6 rows of `docs-authority/nozzles/CATCH_TANK.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-VES: the 0.0893 m3 liquor volume is reported - the duty section 2 two-minute figure is not a designed volume and no residence time is derived
- Material conditional: PVC-U drawn per duty section 3 rule M1; the HDPE alternative is a named hold (W12)
- Internals: dip pipe + stilling well per fab/CATCH_TANK.md (AQS-MFG-001); dimensions study values (W12)
- BOM `models/mfg/CATCH_TANK/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CATCH_TANK/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/CATCH_TANK/catch_tank.py`
- `models/mfg/CATCH_TANK/draw_catch_tank.py`
- `models/mfg/CATCH_TANK/bom.csv`
- `models/mfg/CATCH_TANK/fasteners.csv`
- `models/mfg/CATCH_TANK/check.json`
- `models/mfg/CATCH_TANK/WORK_ORDER.md`
- `build export `models/mfg/CATCH_TANK/export/catch_tank.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
