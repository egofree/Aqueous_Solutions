# Build log - FLUX_PREP

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/FLUX_PREP.md`; sizing `docs-authority/sizing/FLUX_PREP.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 830 x 600 x 1200 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/FLUX_PREP/export/flux_prep.step`
- BOM `models/mfg/FLUX_PREP/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/FLUX_PREP/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/FLUX_PREP/draw_flux_prep.py`
- `models/mfg/FLUX_PREP/export/flux_prep.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
