# Build log - STOCK_OUT

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/STOCK_OUT.md`; envelope per `models/mfg/STOCK_OUT/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/STOCK_OUT/stock_out.py`

## Checks

- Rebuild through the current lib confirms the Oct-31 build as issued: the flush-hardware gate reads 0/0/0/0 mm face overhang and there is no §7 misfit on this unit, so no geometry changed. The Oct-31 `external_parts` claim on the issue sill is corrected - the sill sits inside the +X face (x 1190..1200), so the in-envelope build solid is the whole rack and `external_parts` is empty; `cad/stl/STOCK_OUT.stl` replaced from the build (scope in `check.json` `cad_stl_scope`)
- Route-class hold named: `store` has no AQS-PLAN-006 section 4 class; the frame-weldment practice (F-MACH row) is the named study route
- Internals: node row `none`; the machine the design block names (three-tier bar/plate/ingot staging rack) is drawn as the unit - six uprights, tier decks at z 160/600/1000, back guard, issue-face edge stops and sill; the stock loads are process-inventory solids, not BOM parts
- Nozzles: all 10 rows of `docs-authority/nozzles/STOCK_OUT.csv` present at tag, face, height and bore; the seven solids inlet rows land on the tier decks at z 160 (registered layout choice), N8 issues at +X z 600, bore not calculated per W4; atmospheric joints, no flange; schedule rating column carried verbatim
- BOM `models/mfg/STOCK_OUT/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners completed with the deck-bolt row beside the slab anchors (8.8 CS per the W5 grade rule); WORK_ORDER rewritten to the W1-W12 items with holds named; the builder no longer writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets: ga_front/ga_side/nozzle_orient/sh01/hd01/el01/aux01/iso01; title blocks per AQS-DWG-002, graph Rev AD; the stale "Graph revision AC" iso note corrected to the live revision)

## Sources

- `models/mfg/STOCK_OUT/draw_stock_out.py`
- `models/mfg/STOCK_OUT/stock_out.py`
- `models/mfg/STOCK_OUT/export/stock_out.step`

Status: accepted per AQS-PLAN-006 section 5 A-core; route-class hold named in WORK_ORDER W12.
