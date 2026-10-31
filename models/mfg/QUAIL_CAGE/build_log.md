# Build log - QUAIL_CAGE

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/QUAIL_CAGE.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1300 x 700 x 1700 mm: inside the envelope with margin (envelope 1300 x 700 x 1700 mm)
- Solid source: build export `models/mfg/QUAIL_CAGE/export/quail_cage.step`
- BOM `models/mfg/QUAIL_CAGE/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/QUAIL_CAGE/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/QUAIL_CAGE/draw_quail_cage.py`
- `models/mfg/QUAIL_CAGE/export/quail_cage.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
