# Build log - AFTERBURNER_FLUE

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/AFTERBURNER_FLUE.md`; envelope per `models/mfg/AFTERBURNER_FLUE/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/AFTERBURNER_FLUE/afterburner_flue.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/AFTERBURNER_FLUE/export/afterburner_flue.step`; export STL closed and manifold, 5 solid(s); `cad/stl/AFTERBURNER_FLUE.stl` replaced from the build (ASCII, metres)
- Nozzles: all 5 rows of `docs-authority/nozzles/AFTERBURNER_FLUE.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-PIPE line list: line_list.csv generated from the unit's graph edges and docs-authority/LINE_LIST.md (AQS-PIP-004): 4 rows (MAIN spool + 3 issued lines), tag/from/to/DN/class/service/rating; edge coverage complete, no new edge
- Spool: DN100 OD 114.3 x wall 6.02 (ASME B36.10M Sch 40 named values), 1000 mm representative spool of the 20 m node-design run; the 102.26 mm bore sits inside the DN100 seat over the 17 mm required bore; nothing resized
- Route hold: no plan section 4 route class for flue_junction - A-core with the hold named; the A-PIPE idiom follows the node duct design
- Material: 316L per duty section 3 (issued selection); the node design block says CS Sch 40 insulated per AQS-THM-003 - conflict carried as a hold (W12); insulation thickness 40 mm a study value (hold, W12)
- BOM `models/mfg/AFTERBURNER_FLUE/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/AFTERBURNER_FLUE/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/AFTERBURNER_FLUE/afterburner_flue.py`
- `models/mfg/AFTERBURNER_FLUE/draw_afterburner_flue.py`
- `models/mfg/AFTERBURNER_FLUE/bom.csv`
- `models/mfg/AFTERBURNER_FLUE/fasteners.csv`
- `models/mfg/AFTERBURNER_FLUE/line_list.csv`
- `models/mfg/AFTERBURNER_FLUE/check.json`
- `models/mfg/AFTERBURNER_FLUE/WORK_ORDER.md`
- `build export `models/mfg/AFTERBURNER_FLUE/export/afterburner_flue.step``

Status: accepted per AQS-PLAN-006 section 5 A-core (route hold); holds named in WORK_ORDER W12.
