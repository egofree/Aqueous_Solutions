# Build log - GLASS_MILL

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-PIPE; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GLASS_MILL.md`; envelope per `models/mfg/GLASS_MILL/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/GLASS_MILL/glass_mill.py`

## Checks

- Build bbox 800 x 600 x 800 mm against the 800 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/GLASS_MILL/export/glass_mill.step`; export STL closed and manifold, 6 solid(s); `cad/stl/GLASS_MILL.stl` replaced from the build (ASCII, metres)
- Nozzles: all 6 rows of `docs-authority/nozzles/GLASS_MILL.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-PIPE line list: line_list.csv generated from the unit's graph edges and docs-authority/LINE_LIST.md (AQS-PIP-004): 5 rows, tag/from/to/DN/class/service/rating; edge coverage complete, no new edge
- Machine: jar mill OD 350 x 500, wall 8 (study), on V-roll cradle stands; jar-full 0.0438 m3 against the 0.2577 m3 duty section 2 seven-day charge - reported, nothing resized (plan rule 3); media charge not drawn (node internals none)
- BOM `models/mfg/GLASS_MILL/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/GLASS_MILL/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/GLASS_MILL/glass_mill.py`
- `models/mfg/GLASS_MILL/draw_glass_mill.py`
- `models/mfg/GLASS_MILL/bom.csv`
- `models/mfg/GLASS_MILL/fasteners.csv`
- `models/mfg/GLASS_MILL/line_list.csv`
- `models/mfg/GLASS_MILL/check.json`
- `models/mfg/GLASS_MILL/WORK_ORDER.md`
- `build export `models/mfg/GLASS_MILL/export/glass_mill.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-PIPE; holds named in WORK_ORDER W12.
