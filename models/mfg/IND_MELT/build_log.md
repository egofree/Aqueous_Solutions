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

## M3 close - 2026-11-02 (AQS-PLAN-006 section 5)

- Flush-hardware rebuild through the current lib: the charge chute, trunnion pins and melt stubs moved to the envelope faces, face overhang 0 mm on all four faces (was 35/25/6 mm); the A-core 2 gate reads the export STL, not the CAD kernel box.
- `python3 models/mfg/tracker.py --check IND_MELT`: no named failures (bbox 1000.0 x 1000.0 x 1500.0 inside size_mm; STL manifold; STEP present; BOM complete; nozzle count 17 = schedule).
- Nozzles: all 17 schedule rows drawn at tag, face and bore; solids rows drawn at DN15 labeled bore not calculated (WORK_ORDER W4); datums are the schedule placeholders (holds, W12).
- BOM `bom.csv` complete with make-or-buy (crucible and 25 kW PSU are the buy rows); `fasteners.csv` grade 8.8 carbon steel per the W5 grade rule; WORK_ORDER rewritten to the W1-W12 items with holds named.
- Drawing set regenerated from the rebuilt solids (8 sheets, ga_front/ga_side/nozzle_orient/sh01/hd01/el01/aux01/iso01; title blocks per AQS-DWG-002, graph Rev AD).
- Duty section 7 names the model source (`models/mfg/IND_MELT/ind_melt.py`, AQS-PLAN-006).
