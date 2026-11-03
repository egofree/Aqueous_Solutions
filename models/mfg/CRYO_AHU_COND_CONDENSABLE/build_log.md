# Build log - CRYO_AHU_COND_CONDENSABLE

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CRYO_AHU_COND_CONDENSABLE.md`; envelope per `models/mfg/CRYO_AHU_COND_CONDENSABLE/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/CRYO_AHU_COND_CONDENSABLE/cryo_ahu_cond_condensable.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/CRYO_AHU_COND_CONDENSABLE/export/cryo_ahu_cond_condensable.step`; export STL closed and manifold, 1 solid(s); `cad/stl/CRYO_AHU_COND_CONDENSABLE.stl` replaced from the build (ASCII, metres)
- Nozzles: all 4 rows of `docs-authority/nozzles/CRYO_AHU_COND_CONDENSABLE.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Condensable knock-out vessel per the duty section 3 row (316L, condensation, no carbon steel) in the FLUE_KO weir/launder idiom: drum OD 540 (wall 8, study), weir plate to z 360, launder trough lip top z 360
- Route hold carried by name: the node class is blank - no section 4 class (AFTERBURNER_FLUE/REE_RECOVER precedent); the duty/seed 600 x 400 x 600 figures predate the node study box (hold, W12)
- Sump volume reported from the model (A-VES-style report, no residence time derived - duty section 8 has no holdup basis); hose-barb nozzles per the schedule (bores not calculated, hose, atmospheric)
- BOM `models/mfg/CRYO_AHU_COND_CONDENSABLE/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CRYO_AHU_COND_CONDENSABLE/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/CRYO_AHU_COND_CONDENSABLE/cryo_ahu_cond_condensable.py`
- `models/mfg/CRYO_AHU_COND_CONDENSABLE/draw_cryo_ahu_cond_condensable.py`
- `models/mfg/CRYO_AHU_COND_CONDENSABLE/bom.csv`
- `models/mfg/CRYO_AHU_COND_CONDENSABLE/fasteners.csv`
- `models/mfg/CRYO_AHU_COND_CONDENSABLE/check.json`
- `models/mfg/CRYO_AHU_COND_CONDENSABLE/WORK_ORDER.md`
- `build export `models/mfg/CRYO_AHU_COND_CONDENSABLE/export/cryo_ahu_cond_condensable.step``

Status: accepted per AQS-PLAN-006 section 5 A-core; holds named in WORK_ORDER W12.
