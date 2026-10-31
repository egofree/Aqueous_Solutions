# Build log - FILM_CAST

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/FILM_CAST.md`; sizing `docs-authority/sizing/FILM_CAST.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1534 x 800 x 1500 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/FILM_CAST/export/film_cast.step`
- BOM `models/mfg/FILM_CAST/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/FILM_CAST/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/FILM_CAST/draw_film_cast.py`
- `models/mfg/FILM_CAST/film_cast.py`
- `models/mfg/FILM_CAST/export/film_cast.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
