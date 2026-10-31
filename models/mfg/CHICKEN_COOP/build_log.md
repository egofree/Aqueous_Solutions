# Build log - CHICKEN_COOP

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CHICKEN_COOP.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 2500 x 1300 x 1900 mm: inside the envelope with margin (envelope 2500 x 1300 x 1900 mm)
- Solid source: build export `models/mfg/CHICKEN_COOP/export/chicken_coop.step`
- BOM `models/mfg/CHICKEN_COOP/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CHICKEN_COOP/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/CHICKEN_COOP/draw_chicken_coop.py`
- `models/mfg/CHICKEN_COOP/export/chicken_coop.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
