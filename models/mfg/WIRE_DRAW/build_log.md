# Build log - WIRE_DRAW

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH + A-SC; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/WIRE_DRAW.md`; envelope per `models/mfg/WIRE_DRAW/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/WIRE_DRAW/wire_draw.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/WIRE_DRAW/export/wire_draw.step`; export STL closed and manifold, 11 solid(s); `cad/stl/WIRE_DRAW.stl` replaced from the build (ASCII, metres)
- Nozzles: all 8 rows of `docs-authority/nozzles/WIRE_DRAW.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Bull-block wire drawer per the AQS-MFG-010 tool row (nameplate 1.1 kW; A-M-177 strain-3.0 energy basis), built on the DRAW accepted idiom (commit 30f5abf4) scaled to the node box: bench bed, die stand with the carbide die set (buy consumable), bull-block drum OD 300, wire guides, fume hood over the die zone (N4 to the house scrubber train)
- A-MACH: die-zone/drum guard rail + hold-down frame + 8 anchors; purchased items named with the node ratings (drive group and cabinet, plan rule 6); A-SC: shop-made hardware flagged with the AQS-BOM-SC-001 cross-reference
- Dry forming machine (no wetted stream); CA 0 mm; drum/bench/die-count study values (holds, WORK_ORDER W12)
- BOM `models/mfg/WIRE_DRAW/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/WIRE_DRAW/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/WIRE_DRAW/wire_draw.py`
- `models/mfg/WIRE_DRAW/draw_wire_draw.py`
- `models/mfg/WIRE_DRAW/bom.csv`
- `models/mfg/WIRE_DRAW/fasteners.csv`
- `models/mfg/WIRE_DRAW/check.json`
- `models/mfg/WIRE_DRAW/WORK_ORDER.md`
- `build export `models/mfg/WIRE_DRAW/export/wire_draw.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH + A-SC; holds named in WORK_ORDER W12.
