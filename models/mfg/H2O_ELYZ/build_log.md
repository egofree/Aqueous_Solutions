# Build log - H2O_ELYZ

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/H2O_ELYZ.md`; sizing `docs-authority/sizing/H2O_ELYZ.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1800 x 800 x 1000 mm: inside the envelope with margin (envelope 1800 x 800 x 1000 mm)
- Solid source: build export `models/mfg/H2O_ELYZ/export/h2o_elyz.step`
- BOM `models/mfg/H2O_ELYZ/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/H2O_ELYZ/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/H2O_ELYZ/export/h2o_elyz.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
