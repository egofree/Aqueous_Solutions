# Build log - EVAP_ACID

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/EVAP_ACID.md`; sizing `docs-authority/sizing/EVAP_ACID.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1090 x 450 x 3800 mm: inside the envelope with margin (envelope 1650 x 1300 x 3800 mm)
- Solid source: build export `models/mfg/EVAP_ACID/export/evap_acid.step`
- BOM `models/mfg/EVAP_ACID/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/EVAP_ACID/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/EVAP_ACID/export/evap_acid.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
