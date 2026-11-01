# Build log - F_RECOVER

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/F_RECOVER.md`; sizing `docs-authority/sizing/F_RECOVER.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 679 x 560 x 1174 mm: inside the envelope with margin (envelope 679 x 560 x 1174 mm)
- Solid source: build export `models/mfg/F_RECOVER/export/f_recover.step`
- BOM `models/mfg/F_RECOVER/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/F_RECOVER/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/F_RECOVER/export/f_recover.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
