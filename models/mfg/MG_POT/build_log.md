# Build log - MG_POT

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MG_POT.md`; sizing `docs-authority/sizing/MG_POT.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 889 x 850 x 1600 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/MG_POT/export/mg_pot.step`
- BOM `models/mfg/MG_POT/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MG_POT/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/MG_POT/draw_mg_pot.py`
- `models/mfg/MG_POT/mg_pot.py`
- `models/mfg/MG_POT/export/mg_pot.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
