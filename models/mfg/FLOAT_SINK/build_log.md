# Build log - FLOAT_SINK

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/FLOAT_SINK.md`; sizing `docs-authority/sizing/FLOAT_SINK.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1000 x 600 x 800 mm: inside the envelope with margin (envelope 1000 x 600 x 800 mm)
- Solid source: envelope box from the graph `params.size_mm` (envelope-class unit; no build export yet)
- BOM `models/mfg/FLOAT_SINK/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/FLOAT_SINK/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources


Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
