# Build log - IND_MELT

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/IND_MELT.md`; sizing `docs-authority/sizing/IND_MELT.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1060 x 1006 x 1500 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/IND_MELT/export/ind_melt.step`
- BOM `models/mfg/IND_MELT/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/IND_MELT/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/IND_MELT/ind_melt.py`
- `models/mfg/IND_MELT/draw_ind_melt.py`
- `models/mfg/IND_MELT/export/ind_melt.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.
