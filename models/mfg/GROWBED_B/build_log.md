# Build log - GROWBED_B

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GROWBED_B.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 3600 x 2100 x 500 mm: inside the envelope with margin (envelope 3600 x 2100 x 500 mm)
- Solid source: build export `models/mfg/GROWBED_B/export/growbed_b.step`
- BOM `models/mfg/GROWBED_B/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/GROWBED_B/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/GROWBED_B/draw_growbed_b.py`
- `models/mfg/GROWBED_B/export/growbed_b.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
