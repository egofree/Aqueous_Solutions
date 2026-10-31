# Build log - STOCK_OUT

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/STOCK_OUT.md`; sizing `docs-authority/sizing/STOCK_OUT.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1200 x 800 x 1500 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/STOCK_OUT/export/stock_out.step`
- BOM `models/mfg/STOCK_OUT/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/STOCK_OUT/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/STOCK_OUT/stock_out.py`
- `models/mfg/STOCK_OUT/draw_stock_out.py`
- `models/mfg/STOCK_OUT/export/stock_out.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
