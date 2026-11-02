# Build log - CAST_LINE

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CAST_LINE.md`; sizing `docs-authority/sizing/CAST_LINE.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1500 x 800 x 1500 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/CAST_LINE/export/cast_line.step`
- BOM `models/mfg/CAST_LINE/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CAST_LINE/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/CAST_LINE/draw_cast_line.py`
- `models/mfg/CAST_LINE/cast_line.py`
- `models/mfg/CAST_LINE/export/cast_line.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.

## M3 close - 2026-11-02 (AQS-PLAN-006 section 5)

- Rebuild through the current lib confirms the build as issued: the flush-hardware convention is already this machine (check.json `connection_check` green, `bbox_exact` true), so no geometry changed and the drawing set stays current (8 sheets, title blocks per AQS-DWG-002, graph Rev AD).
- `python3 models/mfg/tracker.py --check CAST_LINE`: no named failures (bbox 1500.0 x 800.0 x 1500.0 inside size_mm; STL manifold; STEP present; BOM complete; nozzle count 6 = schedule).
- Nozzles: all 6 schedule rows drawn at tag, face and bore; the solids rows (N2 scrap return, N3/N4 billets) drawn at DN15 labeled bore not calculated (WORK_ORDER W4); datums are the schedule placeholders (holds, W12).
- BOM `bom.csv` complete with make-or-buy (all rows make); `fasteners.csv` grade 8.8 carbon steel per the W5 grade rule; WORK_ORDER rewritten to the W1-W12 items with holds named; A-SC make rows cross-referenced to AQS-BOM-SC-001 (W11).
- Duty section 7 already named the model source (`models/mfg/CAST_LINE/cast_line.py`, AQS-PLAN-006).
