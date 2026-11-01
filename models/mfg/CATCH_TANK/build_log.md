# Build log - CATCH_TANK

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CATCH_TANK.md`; sizing `docs-authority/sizing/CATCH_TANK.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 649 x 520 x 748 mm: inside the envelope with margin (envelope 649 x 520 x 748 mm)
- Solid source: build export `models/mfg/CATCH_TANK/export/catch_tank.step`
- BOM `models/mfg/CATCH_TANK/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CATCH_TANK/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/CATCH_TANK/export/catch_tank.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
