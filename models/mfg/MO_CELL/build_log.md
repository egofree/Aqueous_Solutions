# Build log - MO_CELL

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MO_CELL.md`; sizing `docs-authority/sizing/MO_CELL.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 879 x 851 x 1600 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/MO_CELL/export/mo_cell.step`
- BOM `models/mfg/MO_CELL/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MO_CELL/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/MO_CELL/mo_cell.py`
- `models/mfg/MO_CELL/draw_mo_cell.py`
- `models/mfg/MO_CELL/export/mo_cell.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
