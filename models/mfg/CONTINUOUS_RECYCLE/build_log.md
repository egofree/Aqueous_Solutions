# Build log - CONTINUOUS_RECYCLE

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CONTINUOUS_RECYCLE.md`; sizing `docs-authority/sizing/CONTINUOUS_RECYCLE.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1500 x 60 x 60 mm: inside the envelope with margin (envelope 1500 x 60 x 60 mm)
- Solid source: build export `models/mfg/CONTINUOUS_RECYCLE/export/continuous_recycle.step`
- BOM `models/mfg/CONTINUOUS_RECYCLE/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CONTINUOUS_RECYCLE/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/CONTINUOUS_RECYCLE/export/continuous_recycle.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
