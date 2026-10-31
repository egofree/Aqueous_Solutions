# Build log - BLACK_DIGEST

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/BLACK_DIGEST.md`; sizing `docs-authority/sizing/BLACK_DIGEST.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 910 x 910 x 771 mm: inside the envelope with margin (envelope 1100 x 1100 x 1260 mm)
- Solids exported: `models/mfg/BLACK_DIGEST/export/` (STEP + STL); STL manifold-checked by the exporter
- Envelope STL `cad/stl/BLACK_DIGEST.stl` replaced from the build (X-PAR-04 registry form)
- BOM `models/mfg/BLACK_DIGEST/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/BLACK_DIGEST/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/BLACK_DIGEST/export/black_digest.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
