# Build log - INV_CAST

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/INV_CAST.md`; sizing `docs-authority/sizing/INV_CAST.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1530 x 834 x 1500 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/INV_CAST/export/inv_cast.step`
- BOM `models/mfg/INV_CAST/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/INV_CAST/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/INV_CAST/draw_inv_cast.py`
- `models/mfg/INV_CAST/inv_cast.py`
- `models/mfg/INV_CAST/export/inv_cast.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
