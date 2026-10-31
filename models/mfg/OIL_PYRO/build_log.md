# Build log - OIL_PYRO

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/OIL_PYRO.md`; sizing `docs-authority/sizing/OIL_PYRO.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 320 x 320 x 491 mm: inside the envelope with margin (envelope 500 x 500 x 670 mm)
- Solids exported: `models/mfg/OIL_PYRO/export/` (STEP + STL); STL manifold-checked by the exporter
- Envelope STL `cad/stl/OIL_PYRO.stl` replaced from the build (X-PAR-04 registry form)
- BOM `models/mfg/OIL_PYRO/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/OIL_PYRO/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/OIL_PYRO/export/oil_pyro.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
