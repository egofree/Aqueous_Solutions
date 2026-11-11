# Build log - EXTRUDE

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core, A-MACH, A-SC (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/EXTRUDE.md`; envelope per `models/mfg/EXTRUDE/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/EXTRUDE/extrude.py`

## Checks

- Build bbox 1500 x 800 x 1500 mm against the 1500 x 800 x 1500 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/EXTRUDE/export/extrude.step`; export STL closed and manifold, 2 solid(s); `cad/stl/EXTRUDE.stl` replaced from the build (ASCII, metres)
- Nozzles: all 4 rows of `docs-authority/nozzles/EXTRUDE.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Standby N+1 alternate drawn per the node design block (A-M-282/A-M-283): real machine, standby-zero design-day rate; named in the BOM rows and the WORK_ORDER
- A-MACH: die-zone guard rail and slab anchors drawn; HPU skid and control pedestal are the purchased items named with the node rating
- H13 die is the purchased consumable (buy row); tool-steel container liner per duty section 3; CA 0 mm (AQS-STD-001)
- The 2 solids schedule rows are drawn at DN15 labeled bore not calculated (W4); A-SC make rows flagged and W11 cross-references AQS-BOM-SC-001
- BOM `models/mfg/EXTRUDE/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/EXTRUDE/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/EXTRUDE/extrude.py`
- `models/mfg/EXTRUDE/draw_extrude.py`
- `models/mfg/EXTRUDE/bom.csv`
- `models/mfg/EXTRUDE/fasteners.csv`
- `models/mfg/EXTRUDE/check.json`
- `models/mfg/EXTRUDE/WORK_ORDER.md`
- `build export `models/mfg/EXTRUDE/export/extrude.step``

Status: accepted per AQS-PLAN-006 section 5 A-core, A-MACH, A-SC (route hold); holds named in WORK_ORDER W12.
