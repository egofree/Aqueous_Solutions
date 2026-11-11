# Build log - DRAW

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core, A-MACH, A-SC; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/DRAW.md`; envelope per `models/mfg/DRAW/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/DRAW/draw.py`

## Checks

- Build bbox 1500 x 800 x 1500 mm against the 1500 x 800 x 1500 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/DRAW/export/draw.step`; export STL closed and manifold, 7 solid(s); `cad/stl/DRAW.stl` replaced from the build (ASCII, metres)
- Nozzles: all 3 rows of `docs-authority/nozzles/DRAW.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Standby N+1 alternate drawn per the node design block (A-M-282/A-M-283): real machine, standby-zero design-day rate; named in the BOM rows and the WORK_ORDER
- A-MACH: die-zone and capstan guard rail and slab anchors drawn; drive group and control cabinet are the purchased items named with the node rating
- Carbide die set is the purchased consumable (buy row); steel bench per duty section 3; CA 0 mm (AQS-STD-001)
- The solids schedule row (N1 wire) is drawn at DN15 labeled bore not calculated (W4); A-SC make rows flagged and W11 cross-references AQS-BOM-SC-001
- BOM `models/mfg/DRAW/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/DRAW/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/DRAW/draw.py`
- `models/mfg/DRAW/draw_draw.py`
- `models/mfg/DRAW/bom.csv`
- `models/mfg/DRAW/fasteners.csv`
- `models/mfg/DRAW/check.json`
- `models/mfg/DRAW/WORK_ORDER.md`
- `build export `models/mfg/DRAW/export/draw.step``

Status: accepted per AQS-PLAN-006 section 5 A-core, A-MACH, A-SC; holds named in WORK_ORDER W12.
