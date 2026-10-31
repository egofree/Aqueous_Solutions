# Build log - DRAW

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/DRAW.md`; sizing `docs-authority/sizing/DRAW.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1500 x 800 x 1500 mm: no graph envelope; dims recorded
- Solids exported: `models/mfg/DRAW/export/` (STEP + STL); STL manifold-checked by the exporter
- Envelope STL `cad/stl/DRAW.stl` replaced from the build (X-PAR-04 registry form)
- BOM `models/mfg/DRAW/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/DRAW/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/DRAW/export/draw.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
