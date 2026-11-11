# Build log - HDR_UPW

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-PIPE; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/HDR_UPW.md`; envelope per `models/mfg/HDR_UPW/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/HDR_UPW/hdr_upw.py`

## Checks

- Build bbox 2000 x 33.7 x 33.8 mm against the 2000 x 33.7 x 33.7 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/HDR_UPW/export/hdr_upw.step`; export STL closed and manifold, 1 solid(s); `cad/stl/HDR_UPW.stl` ; replaced from the build (ASCII, metres)
- Nozzles: all 5 rows of `docs-authority/nozzles/HDR_UPW.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-PIPE line list: line_list.csv generated from the unit's graph edges and docs-authority/LINE_LIST.md (AQS-PIP-004): 5 rows (manifold spool + 4 lines), tag/from/to/DN/class/service/rating; edge coverage complete, no new edge
- Spool: DN25 OD 33.7 x wall 3.38 (Sch 40 table; the node material carries SDR 21, confirmed at order), bore 26.9 mm inside the 0.8 mm DN-8 sizing grid seat (AQS-DUTY-075); nothing resized; PVDF fusion-welded
- Build fills the envelope exactly; cad/stl replaced from the build
- Schedule datums clamped into the 50 mm cross-section: the DN25 inlet 10 to 17.6 mm, the DN25 37 mm outlet datum to 32.4 mm (holds, W12); the UPW_TO_FAB edge carries no distinct schedule row (hold, W12)
- BOM `models/mfg/HDR_UPW/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/HDR_UPW/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/HDR_UPW/hdr_upw.py`
- `models/mfg/HDR_UPW/draw_upw.py`
- `models/mfg/HDR_UPW/bom.csv`
- `models/mfg/HDR_UPW/fasteners.csv`
- `models/mfg/HDR_UPW/line_list.csv`
- `models/mfg/HDR_UPW/check.json`
- `models/mfg/HDR_UPW/WORK_ORDER.md`
- `build export `models/mfg/HDR_UPW/export/hdr_upw.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-PIPE; holds named in WORK_ORDER W12.
