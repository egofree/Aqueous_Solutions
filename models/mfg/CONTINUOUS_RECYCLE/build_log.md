# Build log - CONTINUOUS_RECYCLE

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-PIPE; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CONTINUOUS_RECYCLE.md`; envelope per `models/mfg/CONTINUOUS_RECYCLE/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/CONTINUOUS_RECYCLE/continuous_recycle.py`

## Checks

- Build bbox 1500 x 60 x 60.3 mm against the 1500 x 60 x 60 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/CONTINUOUS_RECYCLE/export/continuous_recycle.step`; export STL closed and manifold, 1 solid(s); `cad/stl/CONTINUOUS_RECYCLE.stl` replaced from the build (ASCII, metres)
- Nozzles: all 5 rows of `docs-authority/nozzles/CONTINUOUS_RECYCLE.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-PIPE: line_list.csv 3 rows (MAIN spool + IA-POL-02 + IA-REC-01), tag/from/to/DN/class/service/rating; edge coverage complete; no new edge
- The DN50 hand rows N1/N2 drawn verbatim against the DN15 issued lines; they seat the 60 mm cross-section with 0.15 mm per side outside the box, inside the 1 mm house gate (holds, W12)
- PVC-U per duty section 3; above 60 C the thermoplastic is CPVC - the line temperature is not on the graph (hold, W12)
- BOM `models/mfg/CONTINUOUS_RECYCLE/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CONTINUOUS_RECYCLE/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/CONTINUOUS_RECYCLE/continuous_recycle.py`
- `models/mfg/CONTINUOUS_RECYCLE/draw_continuous_recycle.py`
- `models/mfg/CONTINUOUS_RECYCLE/bom.csv`
- `models/mfg/CONTINUOUS_RECYCLE/fasteners.csv`
- `models/mfg/CONTINUOUS_RECYCLE/line_list.csv`
- `models/mfg/CONTINUOUS_RECYCLE/check.json`
- `models/mfg/CONTINUOUS_RECYCLE/WORK_ORDER.md`
- `build export `models/mfg/CONTINUOUS_RECYCLE/export/continuous_recycle.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-PIPE; holds named in WORK_ORDER W12.
