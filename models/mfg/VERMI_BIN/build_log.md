# Build log - VERMI_BIN

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/VERMI_BIN.md`; sizing per the duty sheet section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 2100 x 1100 x 600 mm: inside the envelope with margin (envelope 2100 x 1100 x 600 mm)
- Solid source: build export `models/mfg/VERMI_BIN/export/vermi_bin.step`
- BOM `models/mfg/VERMI_BIN/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/VERMI_BIN/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/VERMI_BIN/draw_vermi_bin.py`
- `models/mfg/VERMI_BIN/export/vermi_bin.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
