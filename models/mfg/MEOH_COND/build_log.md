# Build log - MEOH_COND

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MEOH_COND.md`; envelope per `models/mfg/MEOH_COND/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/MEOH_COND/meoh_cond.py`

## Checks

- Build bbox 400 x 400 x 600 mm against the 400 x 400 x 600 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/MEOH_COND/export/meoh_cond.step`; export STL closed and manifold, 1 solid(s); `cad/stl/MEOH_COND.stl` replaced from the build (ASCII, metres)
- Nozzles: all 5 rows of `docs-authority/nozzles/MEOH_COND.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-VES: the 0.0584 m3 liquor volume is reported against the node drum_L 71.19 nominal figure; no residence time is derived (the duty section 2 box sentence is explicitly not a residence time)
- Coil area: the drawn 0.0314 m2 is 0.0013 m2 over the node book 0.0301 (nominal figure) - reported, nothing resized (W12)
- BOM `models/mfg/MEOH_COND/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MEOH_COND/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/MEOH_COND/meoh_cond.py`
- `models/mfg/MEOH_COND/draw_meoh_cond.py`
- `models/mfg/MEOH_COND/bom.csv`
- `models/mfg/MEOH_COND/fasteners.csv`
- `models/mfg/MEOH_COND/check.json`
- `models/mfg/MEOH_COND/WORK_ORDER.md`
- `build export `models/mfg/MEOH_COND/export/meoh_cond.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
