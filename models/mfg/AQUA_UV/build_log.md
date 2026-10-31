# Build log - AQUA_UV

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/AQUA_UV.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 400 x 350 x 750 mm: inside the envelope with margin (envelope 400 x 350 x 750 mm)
- Solid source: build export `models/mfg/AQUA_UV/export/aqua_uv.step`
- BOM `models/mfg/AQUA_UV/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/AQUA_UV/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/AQUA_UV/draw_aqua_uv.py`
- `models/mfg/AQUA_UV/export/aqua_uv.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
