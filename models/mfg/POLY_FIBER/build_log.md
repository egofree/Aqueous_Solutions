# Build log - POLY_FIBER

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/POLY_FIBER.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 3100 x 1300 x 1900 mm: inside the envelope with margin (envelope 3100 x 1300 x 1900 mm)
- Solid source: build export `models/mfg/POLY_FIBER/export/poly_fiber.step`
- BOM `models/mfg/POLY_FIBER/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/POLY_FIBER/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/POLY_FIBER/draw_poly_fiber.py`
- `models/mfg/POLY_FIBER/export/poly_fiber.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
