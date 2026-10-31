# Build log - SHELL_BURNOUT

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/SHELL_BURNOUT.md`; sizing `docs-authority/sizing/SHELL_BURNOUT.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1060 x 1040 x 1500 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/SHELL_BURNOUT/export/shell_burnout.step`
- BOM `models/mfg/SHELL_BURNOUT/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/SHELL_BURNOUT/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/SHELL_BURNOUT/shell_burnout.py`
- `models/mfg/SHELL_BURNOUT/draw_shell_burnout.py`
- `models/mfg/SHELL_BURNOUT/export/shell_burnout.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
