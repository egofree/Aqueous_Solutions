# Build log - BEE_HIVE

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/BEE_HIVE.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 650 x 550 x 1150 mm: OVER ENVELOPE - open item (envelope 600 x 500 x 1100 mm)
- Solid source: build export `models/mfg/BEE_HIVE/export/bee_hive.step`
- BOM `models/mfg/BEE_HIVE/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/BEE_HIVE/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/BEE_HIVE/draw_bee_hive.py`
- `models/mfg/BEE_HIVE/export/bee_hive.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
