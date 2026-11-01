# Build log - REE_RECOVER

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/REE_RECOVER.md`; sizing `docs-authority/sizing/REE_RECOVER.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 800 x 600 x 1400 mm: inside the envelope with margin (envelope 800 x 600 x 1400 mm)
- Solid source: build export `models/mfg/REE_RECOVER/export/ree_recover.step`
- BOM `models/mfg/REE_RECOVER/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/REE_RECOVER/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/REE_RECOVER/export/ree_recover.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
