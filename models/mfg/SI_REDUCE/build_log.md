# Build log - SI_REDUCE

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/SI_REDUCE.md`; envelope per `models/mfg/SI_REDUCE/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/SI_REDUCE/si_reduce.py`

## Checks

- Build bbox 1200 x 1000 x 1600 mm against the 1200 x 1000 x 1600 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/SI_REDUCE/export/si_reduce.step`; export STL closed and manifold, 1 solid(s); `cad/stl/SI_REDUCE.stl` replaced from the build (ASCII, metres)
- Nozzles: no piped process connection on the graph; no nozzle schedule is issued (duty section 4) - no nozzle hardware drawn (hold, WORK_ORDER W12)
- Carbothermic reduction retort per the duty section 3 lining stack (X-MAT-22; SCHACHT2004 ch. 8): mild-steel casing OD 700, alumina brick backup 60 mm, graphite hot face 40 mm (dry, M7); Kroll-class retort idiom (AQS-DUTY-072 lineage)
- Charge hopper on the lid (dry char + silica feed handling, duty section 3); heater band envelope at the node 5.0 kW continuous rating, purchased per plan rule 6
- No nozzles: duty section 4 states no piped process connection and no schedule issued; route hold carried by name (furnace class); shell radii are study values (holds, WORK_ORDER W12)
- BOM `models/mfg/SI_REDUCE/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/SI_REDUCE/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/SI_REDUCE/si_reduce.py`
- `models/mfg/SI_REDUCE/draw_si_reduce.py`
- `models/mfg/SI_REDUCE/bom.csv`
- `models/mfg/SI_REDUCE/fasteners.csv`
- `models/mfg/SI_REDUCE/check.json`
- `models/mfg/SI_REDUCE/WORK_ORDER.md`
- `build export `models/mfg/SI_REDUCE/export/si_reduce.step``

Status: accepted per AQS-PLAN-006 section 5 A-core; holds named in WORK_ORDER W12.
