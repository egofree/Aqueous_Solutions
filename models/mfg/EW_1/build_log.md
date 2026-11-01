# Build log - EW_1

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/EW_1.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 2670 x 720 x 760 mm: OVER ENVELOPE - open item (envelope 600 x 420 x 650 mm)
- Solid source: build export `models/mfg/EW_1/export/ew_1.step`
- BOM `models/mfg/EW_1/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/EW_1/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/EW_1/export/ew_1.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
