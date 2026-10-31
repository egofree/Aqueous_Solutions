# Build log - AQUA_TANK

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/AQUA_TANK.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 2100 x 1100 x 1100 mm: inside the envelope with margin (envelope 2100 x 1100 x 1100 mm)
- Solid source: build export `models/mfg/AQUA_TANK/export/aqua_tank.step`
- BOM `models/mfg/AQUA_TANK/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/AQUA_TANK/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/AQUA_TANK/draw_aqua_tank.py`
- `models/mfg/AQUA_TANK/export/aqua_tank.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
