# Build log - BIOFILTER

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/BIOFILTER.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1100 x 900 x 1012 mm: OVER ENVELOPE - open item (envelope 1100 x 900 x 1000 mm)
- Solid source: build export `models/mfg/BIOFILTER/export/biofilter.step`
- BOM `models/mfg/BIOFILTER/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/BIOFILTER/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/BIOFILTER/draw_biofilter.py`
- `models/mfg/BIOFILTER/export/biofilter.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
