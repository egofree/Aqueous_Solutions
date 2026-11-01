# Build log - Q4_BUS

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/Q4_BUS.md`; sizing `docs-authority/sizing/Q4_BUS.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 2000 x 50 x 50 mm: inside the envelope with margin (envelope 2000 x 50 x 50 mm)
- Solid source: build export `models/mfg/Q4_BUS/export/q4_bus.step`
- BOM `models/mfg/Q4_BUS/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/Q4_BUS/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/Q4_BUS/export/q4_bus.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
