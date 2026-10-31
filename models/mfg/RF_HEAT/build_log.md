# Build log - RF_HEAT

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/RF_HEAT.md`; sizing `docs-authority/sizing/RF_HEAT.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1000 x 1000 x 1500 mm: no graph envelope; dims recorded
- Solids exported: `models/mfg/RF_HEAT/export/` (STEP + STL); STL manifold-checked by the exporter
- Envelope STL `cad/stl/RF_HEAT.stl` replaced from the build (X-PAR-04 registry form)
- BOM `models/mfg/RF_HEAT/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/RF_HEAT/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/RF_HEAT/export/rf_heat.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
