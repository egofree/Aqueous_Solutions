# Build log - WAX_PATTERN

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/WAX_PATTERN.md`; sizing `docs-authority/sizing/WAX_PATTERN.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 830 x 600 x 1200 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/WAX_PATTERN/export/wax_pattern.step`
- BOM `models/mfg/WAX_PATTERN/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/WAX_PATTERN/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/WAX_PATTERN/draw_wax_pattern.py`
- `models/mfg/WAX_PATTERN/export/wax_pattern.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
