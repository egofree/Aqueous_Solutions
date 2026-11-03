# Build log - MET_MELT

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES + A-SC; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MET_MELT.md`; envelope per `models/mfg/MET_MELT/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/MET_MELT/met_melt.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/MET_MELT/export/met_melt.step`; export STL closed and manifold, 9 solid(s); `cad/stl/MET_MELT.stl` replaced from the build (ASCII, metres)
- Nozzles: all 7 rows of `docs-authority/nozzles/MET_MELT.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Coreless induction melt furnace per the AQS-MFG-010 tool row (10 kg Cu crucible, nameplate 7.5 kW): CS casing OD 420, refractory hot face 40 mm, coil band, clay-graphite crucible (buy consumable), tilt trunnions and pour lip toward +Y, fume hood with the vent riser at the box top
- A-VES: duty section 2 holdup basis (0.0006 m3, 1 h charge); the crucible melt line is sized to it and the model figure reported, no new rate; A-SC: shop-made hardware flagged with the AQS-BOM-SC-001 cross-reference
- A-MACH: hold-down frame + 8 anchors; purchased items named with the node ratings (crucible consumable; 7.5 kW power cabinet, plan rule 6)
- BOM `models/mfg/MET_MELT/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MET_MELT/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/MET_MELT/met_melt.py`
- `models/mfg/MET_MELT/draw_met_melt.py`
- `models/mfg/MET_MELT/bom.csv`
- `models/mfg/MET_MELT/fasteners.csv`
- `models/mfg/MET_MELT/check.json`
- `models/mfg/MET_MELT/WORK_ORDER.md`
- `build export `models/mfg/MET_MELT/export/met_melt.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES + A-SC; holds named in WORK_ORDER W12.
