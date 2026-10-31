# Build log - MEOH_FERM

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MEOH_FERM.md`; sizing `docs-authority/sizing/MEOH_FERM.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 222 x 234 x 420 mm: inside the envelope with margin (envelope 425 x 425 x 600 mm)
- Solid source: build export `models/mfg/MEOH_FERM/export/meoh_ferm.step`
- BOM `models/mfg/MEOH_FERM/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MEOH_FERM/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/MEOH_FERM/export/meoh_ferm.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
