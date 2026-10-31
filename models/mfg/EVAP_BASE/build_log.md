# Build log - EVAP_BASE

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/EVAP_BASE.md`; sizing `docs-authority/sizing/EVAP_BASE.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 795 x 450 x 2950 mm: inside the envelope with margin (envelope 1250 x 800 x 3100 mm)
- Solids exported: `models/mfg/EVAP_BASE/export/` (STEP + STL); STL manifold-checked by the exporter
- Envelope STL `cad/stl/EVAP_BASE.stl` replaced from the build (X-PAR-04 registry form)
- BOM `models/mfg/EVAP_BASE/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/EVAP_BASE/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/EVAP_BASE/export/evap_base.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
