# Build log - GLASS_RINSE

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-PIPE; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GLASS_RINSE.md`; envelope per `models/mfg/GLASS_RINSE/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/GLASS_RINSE/glass_rinse.py`

## Checks

- Build bbox 1200 x 600 x 800 mm against the 1200 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/GLASS_RINSE/export/glass_rinse.step`; export STL closed and manifold, 2 solid(s); `cad/stl/GLASS_RINSE.stl` replaced from the build (ASCII, metres)
- Nozzles: all 4 rows of `docs-authority/nozzles/GLASS_RINSE.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-PIPE line list: line_list.csv generated from the unit's graph edges and docs-authority/LINE_LIST.md (AQS-PIP-004): 2 rows, tag/from/to/DN/class/service/rating; edge coverage complete, no new edge
- Machine: open-topped rinse bath to the envelope, walls 10 (study); bath volume 0.4585 m3 to the 100 mm freeboard against the 0.2577 m3 duty section 2 seven-day charge - reported, nothing resized (plan rule 3); dewater pump not drawn (no pump named on the node or duty, hold W12)
- BOM `models/mfg/GLASS_RINSE/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/GLASS_RINSE/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/GLASS_RINSE/glass_rinse.py`
- `models/mfg/GLASS_RINSE/draw_glass_rinse.py`
- `models/mfg/GLASS_RINSE/bom.csv`
- `models/mfg/GLASS_RINSE/fasteners.csv`
- `models/mfg/GLASS_RINSE/line_list.csv`
- `models/mfg/GLASS_RINSE/check.json`
- `models/mfg/GLASS_RINSE/WORK_ORDER.md`
- `build export `models/mfg/GLASS_RINSE/export/glass_rinse.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-PIPE; holds named in WORK_ORDER W12.
