# Build log - C29_RECYCLE

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-PIPE; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/C29_RECYCLE.md`; envelope per `models/mfg/C29_RECYCLE/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/C29_RECYCLE/c29_recycle.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/C29_RECYCLE/export/c29_recycle.step`; export STL closed and manifold, 1 solid(s); `cad/stl/C29_RECYCLE.stl` replaced from the build (ASCII, metres)
- Nozzles: all 4 rows of `docs-authority/nozzles/C29_RECYCLE.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-PIPE: line_list.csv 3 rows (MAIN spool + C29_RECYCLE + C29_TO_PYRO), tag/from/to/DN/class/service/rating; edge coverage complete; no new edge
- Schedule datums draw as issued: 160 inlet and 600 outlet fit the 800 box; drain flush at the envelope bottom (50 datum); vent riser flush at the box top (800 datum) (holds, W12)
- Supports: trough plinth + 2 saddle stands + 4 slab anchors (the HDR_CO2 idiom at the schedule datum height)
- BOM `models/mfg/C29_RECYCLE/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/C29_RECYCLE/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/C29_RECYCLE/c29_recycle.py`
- `models/mfg/C29_RECYCLE/draw_c29_recycle.py`
- `models/mfg/C29_RECYCLE/bom.csv`
- `models/mfg/C29_RECYCLE/fasteners.csv`
- `models/mfg/C29_RECYCLE/line_list.csv`
- `models/mfg/C29_RECYCLE/check.json`
- `models/mfg/C29_RECYCLE/WORK_ORDER.md`
- `build export `models/mfg/C29_RECYCLE/export/c29_recycle.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-PIPE; holds named in WORK_ORDER W12.
