# Build log - COMMON_AREA

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/COMMON_AREA.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 4000 x 2500 x 2380 mm: inside the envelope with margin (envelope 4000 x 2500 x 2400 mm)
- Solid source: build export `models/mfg/COMMON_AREA/export/common_area.step`
- BOM `models/mfg/COMMON_AREA/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/COMMON_AREA/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/COMMON_AREA/draw_common_area.py`
- `models/mfg/COMMON_AREA/export/common_area.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
