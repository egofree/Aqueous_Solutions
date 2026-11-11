# Build log - COLD_MILL

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH + A-SC; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/COLD_MILL.md`; envelope per `models/mfg/COLD_MILL/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/COLD_MILL/cold_mill.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/COLD_MILL/export/cold_mill.step`; export STL closed and manifold, 6 solid(s); `cad/stl/COLD_MILL.stl` replaced from the build (ASCII, metres)
- Nozzles: all 5 rows of `docs-authority/nozzles/COLD_MILL.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Two-high cold rolling mill per the AQS-MFG-010 tool row (nameplate 2.2 kW; A-M-177 energy basis): bedplate, housings 40 x 360 with crown tie, work rolls OD 120 x 300 (5 mm gap) with outboard journals, screw-downs, strip tables on the pass line z 302.5
- A-MACH: hold-down frame + roll-zone guard rail + 8 anchors; purchased items named with the node ratings (2.2 kW drive set, control cabinet, plan rule 6); A-SC: shop-made hardware flagged with the AQS-BOM-SC-001 cross-reference
- Dry forming machine (no wetted stream on the graph); CA 0 mm; housing/roll dimensions are study values (holds, WORK_ORDER W12)
- BOM `models/mfg/COLD_MILL/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/COLD_MILL/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/COLD_MILL/cold_mill.py`
- `models/mfg/COLD_MILL/draw_cold_mill.py`
- `models/mfg/COLD_MILL/bom.csv`
- `models/mfg/COLD_MILL/fasteners.csv`
- `models/mfg/COLD_MILL/check.json`
- `models/mfg/COLD_MILL/WORK_ORDER.md`
- `build export `models/mfg/COLD_MILL/export/cold_mill.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH + A-SC; holds named in WORK_ORDER W12.
