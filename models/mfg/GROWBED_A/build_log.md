# Build log - GROWBED_A

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GROWBED_A.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 3600 x 2100 x 500 mm: inside the envelope with margin (envelope 3600 x 2100 x 500 mm)
- Solid source: build export `models/mfg/GROWBED_A/export/growbed_a.step`
- BOM `models/mfg/GROWBED_A/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/GROWBED_A/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/GROWBED_A/draw_growbed_a.py`
- `models/mfg/GROWBED_A/export/growbed_a.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
