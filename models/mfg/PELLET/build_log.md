# Build log - PELLET

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/PELLET.md`; sizing `docs-authority/sizing/PELLET.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1450 x 550 x 875 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/PELLET/export/pellet.step`
- BOM `models/mfg/PELLET/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/PELLET/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/PELLET/export/pellet.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
