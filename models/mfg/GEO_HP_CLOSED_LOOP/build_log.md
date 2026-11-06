# Build log - GEO_HP_CLOSED_LOOP

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GEO_HP_CLOSED_LOOP.md`; envelope per `models/mfg/GEO_HP_CLOSED_LOOP/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/GEO_HP_CLOSED_LOOP/geo_hp_closed_loop.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/GEO_HP_CLOSED_LOOP/export/geo_hp_closed_loop.step`; export STL closed and manifold, 3 solid(s); `cad/stl/GEO_HP_CLOSED_LOOP.stl` replaced from the build (ASCII, metres)
- Nozzles: all 4 rows of `docs-authority/nozzles/GEO_HP_CLOSED_LOOP.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn); the N4 cable power-terminal row is carried verbatim, not drawn
- Closed source-loop distribution skid per the node design block: DN32 HDPE supply/return header runs, the loop buffer manifold vessel (study, W12), the circulator envelope (AQS-DUTY-076, 125.7 W node stamp, purchased per plan rule 6), and the tie stubs (interface indications)
- Route hold carried by name: the node class is blank - no section 4 class (AFTERBURNER_FLUE/REE_RECOVER precedent); the buried ground array is the GHEX/site lane's (hold, W12)
- Hose-barb nozzles per the schedule (bores not calculated, hose, atmospheric); skid stations study values (holds, WORK_ORDER W12)
- BOM `models/mfg/GEO_HP_CLOSED_LOOP/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/GEO_HP_CLOSED_LOOP/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/GEO_HP_CLOSED_LOOP/geo_hp_closed_loop.py`
- `models/mfg/GEO_HP_CLOSED_LOOP/draw_geo_hp_closed_loop.py`
- `models/mfg/GEO_HP_CLOSED_LOOP/bom.csv`
- `models/mfg/GEO_HP_CLOSED_LOOP/fasteners.csv`
- `models/mfg/GEO_HP_CLOSED_LOOP/check.json`
- `models/mfg/GEO_HP_CLOSED_LOOP/WORK_ORDER.md`
- `build export `models/mfg/GEO_HP_CLOSED_LOOP/export/geo_hp_closed_loop.step``

Status: accepted per AQS-PLAN-006 section 5 A-core; holds named in WORK_ORDER W12.
