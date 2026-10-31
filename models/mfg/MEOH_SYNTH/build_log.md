# Build log - MEOH_SYNTH

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MEOH_SYNTH.md`; sizing `docs-authority/sizing/MEOH_SYNTH.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 195 x 165 x 1949 mm: inside the envelope with margin (envelope 414 x 414 x 2585 mm)
- Solid source: build export `models/mfg/MEOH_SYNTH/export/meoh_synth.step`
- BOM `models/mfg/MEOH_SYNTH/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MEOH_SYNTH/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/MEOH_SYNTH/export/meoh_synth.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
