# Build log - GREY_TREAT

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GREY_TREAT.md`; envelope per `models/mfg/GREY_TREAT/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/GREY_TREAT/grey_treat.py`

## Checks

- Build bbox 649 x 520 x 748 mm against the 649 x 520 x 748 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/GREY_TREAT/export/grey_treat.step`; export STL closed and manifold, 1 solid(s); `cad/stl/GREY_TREAT.stl` replaced from the build (ASCII, metres)
- Nozzles: all 11 rows of `docs-authority/nozzles/GREY_TREAT.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-VES: the 0.0955 m3 liquor volume at the study working level is reported - the duty section 2 claims no holdup and no residence time is derived
- Internals: none drawn - the node internals row is none and no study page issues internals for this unit (W12)
- The duty section 4 prose block (7 rows on the seed line 800 x 800 x 1100) predates the issued 11-row schedule and the node box; the node and the schedule govern (W12)
- BOM `models/mfg/GREY_TREAT/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/GREY_TREAT/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/GREY_TREAT/grey_treat.py`
- `models/mfg/GREY_TREAT/draw_grey_treat.py`
- `models/mfg/GREY_TREAT/bom.csv`
- `models/mfg/GREY_TREAT/fasteners.csv`
- `models/mfg/GREY_TREAT/check.json`
- `models/mfg/GREY_TREAT/WORK_ORDER.md`
- `build export `models/mfg/GREY_TREAT/export/grey_treat.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
