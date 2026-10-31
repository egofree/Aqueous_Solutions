# Build log - RABBIT_HUTCH

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/RABBIT_HUTCH.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1900 x 700 x 1600 mm: inside the envelope with margin (envelope 1900 x 700 x 1600 mm)
- Solid source: build export `models/mfg/RABBIT_HUTCH/export/rabbit_hutch.step`
- BOM `models/mfg/RABBIT_HUTCH/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/RABBIT_HUTCH/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/RABBIT_HUTCH/draw_rabbit_hutch.py`
- `models/mfg/RABBIT_HUTCH/export/rabbit_hutch.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
