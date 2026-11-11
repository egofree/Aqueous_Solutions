# Build log - P_CA

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/P_CA.md`; envelope per `models/mfg/P_CA/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/P_CA/p_ca.py`

## Checks

- Build bbox 300 x 300 x 400 mm against the 300 x 300 x 400 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/P_CA/export/p_ca.step`; export STL closed and manifold, 1 solid(s); `cad/stl/P_CA.stl` replaced from the build (ASCII, metres)
- Nozzles: all 6 rows of `docs-authority/nozzles/P_CA.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Route hold: the node class precip has no AQS-PLAN-006 section 4 route class; the tracker records the hold (A-core, route hold) and the vessel work follows the F-VES operations as the nearest family (W10)
- PP-H vessel + PP agitator per duty section 3 (X-MAT-22); wall and agitator dimensions study values (holds, W12); the 316L mixed-build alternative named; the duty section 8 'material selection pending' line predates the issued X-MAT-22 selection
- Relief case study pending (unit task 07): no set point claimed; instrument loops are loop hardware, not modeled
- BOM `models/mfg/P_CA/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/P_CA/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/P_CA/p_ca.py`
- `models/mfg/P_CA/draw_p_ca.py`
- `models/mfg/P_CA/bom.csv`
- `models/mfg/P_CA/fasteners.csv`
- `models/mfg/P_CA/check.json`
- `models/mfg/P_CA/WORK_ORDER.md`
- `build export `models/mfg/P_CA/export/p_ca.step``

Status: accepted per AQS-PLAN-006 section 5 A-core (route hold); holds named in WORK_ORDER W12.
