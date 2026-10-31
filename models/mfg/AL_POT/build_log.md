# Build log - AL_POT

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/AL_POT.md`; sizing `docs-authority/sizing/AL_POT.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 894 x 880 x 1600 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/AL_POT/export/al_pot.step`
- BOM `models/mfg/AL_POT/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/AL_POT/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/AL_POT/draw_al_pot.py`
- `models/mfg/AL_POT/al_pot.py`
- `models/mfg/AL_POT/export/al_pot.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
