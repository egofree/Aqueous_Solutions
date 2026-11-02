# Build log - REE_RECOVER

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/REE_RECOVER.md`; envelope per `models/mfg/REE_RECOVER/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/REE_RECOVER/ree_recover.py`

## Checks

- Build bbox 800 x 600 x 1400 mm against the 800 x 600 x 1400 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/REE_RECOVER/export/ree_recover.step`; export STL closed and manifold, 1 solid(s); `cad/stl/REE_RECOVER.stl` replaced from the build (ASCII, metres)
- Nozzles: all 2 rows of `docs-authority/nozzles/REE_RECOVER.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Route hold: the node class precip has no AQS-PLAN-006 section 4 route class; the tracker records the hold (A-core, route hold) and the skid work follows the F-MACH frame and F-VES vessel operations as the nearest families (W10)
- Purchased equipment per plan rule 6: the duty section 2 sizing line names the set (demag oven, 10 L glass-lined reactor, PP-H filter, 900 C muffle); each is drawn as its envelope and interface only; envelope positions are the layout choice (W12)
- Relief case pending (unit task 07) and no instrument loop yet (unit task 08): no trip or set point specified; nozzle elevations are schedule placeholders
- BOM `models/mfg/REE_RECOVER/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/REE_RECOVER/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/REE_RECOVER/ree_recover.py`
- `models/mfg/REE_RECOVER/draw_ree_recover.py`
- `models/mfg/REE_RECOVER/bom.csv`
- `models/mfg/REE_RECOVER/fasteners.csv`
- `models/mfg/REE_RECOVER/check.json`
- `models/mfg/REE_RECOVER/WORK_ORDER.md`
- `build export `models/mfg/REE_RECOVER/export/ree_recover.step``

Status: accepted per AQS-PLAN-006 section 5 A-core (route hold); holds named in WORK_ORDER W12.
