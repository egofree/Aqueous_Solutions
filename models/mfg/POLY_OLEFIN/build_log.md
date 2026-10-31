# Build log - POLY_OLEFIN

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/POLY_OLEFIN.md`; sizing `docs-authority/sizing/POLY_OLEFIN.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 200 x 200 x 985 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/POLY_OLEFIN/export/poly_olefin.step`
- BOM `models/mfg/POLY_OLEFIN/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/POLY_OLEFIN/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/POLY_OLEFIN/export/poly_olefin.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
