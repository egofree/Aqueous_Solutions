# Build log - LEACH_CSTR_1

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/LEACH_CSTR_1.md`; sizing `docs-authority/sizing/LEACH_CSTR_1.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 2000 x 1199 x 1400 mm: no graph envelope; dims recorded
- Solids exported: `models/mfg/LEACH_CSTR_1/export/` (STEP + STL); STL manifold-checked by the exporter
- Envelope STL `cad/stl/LEACH_CSTR_1.stl` replaced from the build (X-PAR-04 registry form)
- BOM `models/mfg/LEACH_CSTR_1/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/LEACH_CSTR_1/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/LEACH_CSTR_1/leach_cstr_1.py`
- `models/mfg/LEACH_CSTR_1/export/leach_cstr_1.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
