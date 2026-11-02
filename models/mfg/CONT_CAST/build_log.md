# Build log - CONT_CAST

Date: 2026-10-31. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CONT_CAST.md`; sizing `docs-authority/sizing/CONT_CAST.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `models/mfg/build_all.py`

## Checks

- Build bbox 1540 x 806 x 1500 mm: no graph envelope; dims recorded
- Solid source: build export `models/mfg/CONT_CAST/export/cont_cast.step`
- BOM `models/mfg/CONT_CAST/bom.csv`; fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CONT_CAST/drawings/` (GA front/side + iso01; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/CONT_CAST/cont_cast.py`
- `models/mfg/CONT_CAST/draw_cont_cast.py`
- `models/mfg/CONT_CAST/export/cont_cast.step`

Status: envelope-class build accepted per AQS-PLAN-006 section 5 A-core; the machine-design detail (internals, weld procedures) follows the unit WORK_ORDER.

## M3 close - 2026-11-02 (AQS-PLAN-006 section 5)

- Flush-hardware rebuild through the current lib: the -X melt inlet and the +Y stock stubs moved to the envelope faces, face overhang 0 mm on all four faces (was 40/6 mm); the A-core 2 gate reads the export STL, not the CAD kernel box.
- `python3 models/mfg/tracker.py --check CONT_CAST`: no named failures (bbox 1500.0 x 800.0 x 1500.0 inside size_mm; STL manifold; STEP present; BOM complete; nozzle count 5 = schedule).
- Nozzles: all 5 schedule rows drawn at tag, face and bore; the solids rows (N2 billet/slab, N3 as-cast stock) drawn at DN15 labeled bore not calculated (WORK_ORDER W4); datums are the schedule placeholders (holds, W12).
- BOM `bom.csv` complete with make-or-buy (all rows make); `fasteners.csv` grade 8.8 carbon steel per the W5 grade rule; WORK_ORDER rewritten to the W1-W12 items with holds named; A-SC make rows cross-referenced to AQS-BOM-SC-001 (W11).
- Drawing set regenerated from the rebuilt solids (8 sheets, ga_front/ga_side/nozzle_orient/sh01/hd01/el01/aux01/iso01; title blocks per AQS-DWG-002, graph Rev AD).
- Duty section 7 already named the model source (`models/mfg/CONT_CAST/cont_cast.py`, AQS-PLAN-006).
