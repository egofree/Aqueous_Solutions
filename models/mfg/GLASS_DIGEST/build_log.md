# Build log - GLASS_DIGEST

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GLASS_DIGEST.md`; sizing `docs-authority/sizing/GLASS_DIGEST.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 485 x 495 x 870 mm: inside the envelope with margin (envelope 700 x 700 x 900 mm)
- Solids exported: `models/mfg/GLASS_DIGEST/export/` (STEP + STL); STL manifold-checked by the exporter
- Envelope STL `cad/stl/GLASS_DIGEST.stl` replaced from the build (X-PAR-04 registry form)
- BOM `models/mfg/GLASS_DIGEST/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/GLASS_DIGEST/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/GLASS_DIGEST/export/glass_digest.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
