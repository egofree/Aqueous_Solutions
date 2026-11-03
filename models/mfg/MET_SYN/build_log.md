# Build log - MET_SYN

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MET_SYN.md`; envelope per `models/mfg/MET_SYN/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/MET_SYN/met_syn.py`

## Checks

- Build bbox 1500 x 1000 x 1800 mm against the 1500 x 1000 x 1800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/MET_SYN/export/met_syn.step`; export STL closed and manifold, 10 solid(s); `cad/stl/MET_SYN.stl` replaced from the build (ASCII, metres)
- Nozzles: all 6 rows of `docs-authority/nozzles/MET_SYN.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Bench fume-hood synthesis train per the node sizing/design blocks and duty section 3: borosilicate glass-lined reactor column (2 L working volume), 3 SS304 feed tanks, Hastelloy C crystalliser, PTFE-lined transfer lines
- Connected set 0.2 kW (node: jacket + stirrer + metering pumps) drawn as purchased-class envelopes per plan rule 6; A-MACH practice: hold-down frame and 8 anchors; purchased items named with the node rating
- Route hold carried by name: chemical_synthesis has no AQS-PLAN-006 section 4 class; shell dimensions are study values (holds, WORK_ORDER W12)
- BOM `models/mfg/MET_SYN/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MET_SYN/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/MET_SYN/met_syn.py`
- `models/mfg/MET_SYN/draw_met_syn.py`
- `models/mfg/MET_SYN/bom.csv`
- `models/mfg/MET_SYN/fasteners.csv`
- `models/mfg/MET_SYN/check.json`
- `models/mfg/MET_SYN/WORK_ORDER.md`
- `build export `models/mfg/MET_SYN/export/met_syn.step``

Status: accepted per AQS-PLAN-006 section 5 A-core; holds named in WORK_ORDER W12.
