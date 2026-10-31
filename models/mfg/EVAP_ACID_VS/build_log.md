# Build log - EVAP_ACID_VS

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/EVAP_ACID_VS.md`; sizing `docs-authority/sizing/EVAP_ACID_VS.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 318 x 318 x 1480 mm: OVER ENVELOPE - open item (envelope 400 x 400 x 1400 mm)
- Solids exported: `models/mfg/EVAP_ACID_VS/export/` (STEP + STL); STL manifold-checked by the exporter
- Envelope STL `cad/stl/EVAP_ACID_VS.stl` replaced from the build (X-PAR-04 registry form)
- BOM `models/mfg/EVAP_ACID_VS/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/EVAP_ACID_VS/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/EVAP_ACID_VS/export/evap_acid_vs.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
