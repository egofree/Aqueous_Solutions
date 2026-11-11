# Build log - Q4_BUS

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-PIPE; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/Q4_BUS.md`; envelope per `models/mfg/Q4_BUS/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/Q4_BUS/q4_bus.py`

## Checks

- Build bbox 2000 x 42.4 x 42.4 mm against the 2000 x 42.4 x 42.4 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/Q4_BUS/export/q4_bus.step`; export STL closed and manifold, 1 solid(s); `cad/stl/Q4_BUS.stl` ; replaced from the build (ASCII, metres)
- Nozzles: all 9 rows of `docs-authority/nozzles/Q4_BUS.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-PIPE line list: line_list.csv generated from the unit's graph edges and docs-authority/LINE_LIST.md (AQS-PIP-004): 20 rows (manifold spool + 19 lines), tag/from/to/DN/class/service/rating; edge coverage complete, no new edge
- Spool: DN32 OD 42.4 x wall 3.56 (Sch 40 table), bore 35.3 mm inside the 17.2 mm DN-8 sizing grid seat (AQS-DUTY-075); nothing resized; PP-H SDR 11 (node design)
- Build fills the envelope exactly; cad/stl replaced from the build
- Material basis conflict named: the issued rows class the Q4 water lines M1 (316L, the AQS-STD-002 water-loop audit) and the node design says PP-H SDR 11; PP-H drawn, both facts recorded (hold, W12)
- Schedule datums clamped into the 50 mm cross-section: the DN15 datums 10 to 11.3 mm, the 160 mm datum clamped down (holds, W12); the duty section 4 table predates the schedule and its GEO_ORC row is superseded by AQS-PIP-004 (DRY_COOLER); HL-Q4-A/B-BUS are issued lines whose graph edges carry presence study
- BOM `models/mfg/Q4_BUS/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/Q4_BUS/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/Q4_BUS/q4_bus.py`
- `models/mfg/Q4_BUS/draw_q4_bus.py`
- `models/mfg/Q4_BUS/bom.csv`
- `models/mfg/Q4_BUS/fasteners.csv`
- `models/mfg/Q4_BUS/line_list.csv`
- `models/mfg/Q4_BUS/check.json`
- `models/mfg/Q4_BUS/WORK_ORDER.md`
- `build export `models/mfg/Q4_BUS/export/q4_bus.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-PIPE; holds named in WORK_ORDER W12.
