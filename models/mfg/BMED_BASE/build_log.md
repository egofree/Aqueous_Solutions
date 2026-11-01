# Build log - BMED_BASE

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/BMED_BASE.md`; sizing `docs-authority/sizing/BMED_BASE.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1000 x 600 x 230 mm: inside the envelope with margin (envelope 1000 x 600 x 230 mm)
- Solid source: build export `models/mfg/BMED_BASE/export/bmed_base.step`
- BOM `models/mfg/BMED_BASE/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/BMED_BASE/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/BMED_BASE/export/bmed_base.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
