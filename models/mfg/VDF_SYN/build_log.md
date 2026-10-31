# Build log - VDF_SYN

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/VDF_SYN.md`; sizing `docs-authority/sizing/VDF_SYN.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 600 x 600 x 1200 mm: no graph envelope; dims recorded
- Solids exported: `models/mfg/VDF_SYN/export/` (STEP + STL); STL manifold-checked by the exporter
- Envelope STL `cad/stl/VDF_SYN.stl` replaced from the build (X-PAR-04 registry form)
- BOM `models/mfg/VDF_SYN/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/VDF_SYN/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/VDF_SYN/export/vdf_syn.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
