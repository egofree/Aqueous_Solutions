# Build log - DUCKWEED

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/DUCKWEED.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 30100 x 10100 x 700 mm: inside the envelope with margin (envelope 30100 x 10100 x 700 mm)
- Solid source: build export `models/mfg/DUCKWEED/export/duckweed.step`
- BOM `models/mfg/DUCKWEED/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/DUCKWEED/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/DUCKWEED/draw_duckweed.py`
- `models/mfg/DUCKWEED/export/duckweed.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
