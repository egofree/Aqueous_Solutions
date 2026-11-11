# Build log - NCG_HEADER

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-PIPE; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/NCG_HEADER.md`; envelope per `models/mfg/NCG_HEADER/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/NCG_HEADER/ncg_header.py`

## Checks

- Build bbox 2000 x 33.7 x 33.7 mm against the 2000 x 33.7 x 33.7 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/NCG_HEADER/export/ncg_header.step`; export STL closed and manifold, 1 solid(s); `cad/stl/NCG_HEADER.stl` ; replaced from the build (ASCII, metres)
- Nozzles: all 4 rows of `docs-authority/nozzles/NCG_HEADER.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-PIPE line list: line_list.csv generated from the unit's graph edges and docs-authority/LINE_LIST.md (AQS-PIP-004): 3 rows (manifold spool + 2 lines), tag/from/to/DN/class/service/rating; edge coverage complete, no new edge
- Spool: DN25 OD 33.7 x wall 3.38 (Sch 40 table), bore 26.9 mm inside the 4.3 mm DN-8 sizing grid seat (AQS-DUTY-075); nothing resized; 304L heat-traced (node design), the tracing a purchased cable named in the BOM
- Build fills the envelope exactly; cad/stl replaced from the build
- Material basis conflict named: duty section 3 carries the carbon-steel text with a 1.5 mm allowance, the node design says 304L; 304L drawn, both facts recorded (hold, W12)
- Schedule datums clamped into the 50 mm cross-section: the DN15 datums 10 to 11.3 mm (holds, W12); the duty table datums (400 mm) predate the schedule
- BOM `models/mfg/NCG_HEADER/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/NCG_HEADER/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/NCG_HEADER/ncg_header.py`
- `models/mfg/NCG_HEADER/draw_ncg_header.py`
- `models/mfg/NCG_HEADER/bom.csv`
- `models/mfg/NCG_HEADER/fasteners.csv`
- `models/mfg/NCG_HEADER/line_list.csv`
- `models/mfg/NCG_HEADER/check.json`
- `models/mfg/NCG_HEADER/WORK_ORDER.md`
- `build export `models/mfg/NCG_HEADER/export/ncg_header.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-PIPE; holds named in WORK_ORDER W12.
