# Build log - SHELL_BUILD

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/SHELL_BUILD.md`; sizing `docs-authority/sizing/SHELL_BUILD.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1545 x 800 x 1500 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/SHELL_BUILD/export/shell_build.step`
- BOM `models/mfg/SHELL_BUILD/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/SHELL_BUILD/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/SHELL_BUILD/shell_build.py`
- `models/mfg/SHELL_BUILD/draw_shell_build.py`
- `models/mfg/SHELL_BUILD/export/shell_build.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
