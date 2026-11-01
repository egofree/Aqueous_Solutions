# Build log - Q2_A

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/Q2_A.md`; sizing `docs-authority/sizing/Q2_A.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 800 x 800 x 1200 mm: inside the envelope with margin (envelope 800 x 800 x 1200 mm)
- Solid source: build export `models/mfg/Q2_A/export/q2_a.step`
- BOM `models/mfg/Q2_A/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/Q2_A/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/Q2_A/export/q2_a.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
