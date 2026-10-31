# Build log - CONT_CAST

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CONT_CAST.md`; sizing `docs-authority/sizing/CONT_CAST.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1540 x 806 x 1500 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/CONT_CAST/export/cont_cast.step`
- BOM `models/mfg/CONT_CAST/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CONT_CAST/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/CONT_CAST/cont_cast.py`
- `models/mfg/CONT_CAST/draw_cont_cast.py`
- `models/mfg/CONT_CAST/export/cont_cast.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
