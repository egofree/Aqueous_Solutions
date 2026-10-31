# Build log - FEED_PREP

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/FEED_PREP.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1300 x 900 x 1700 mm: inside the envelope with margin (envelope 1300 x 900 x 1700 mm)
- Solid source: build export `models/mfg/FEED_PREP/export/feed_prep.step`
- BOM `models/mfg/FEED_PREP/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/FEED_PREP/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/FEED_PREP/draw_feed_prep.py`
- `models/mfg/FEED_PREP/export/feed_prep.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
