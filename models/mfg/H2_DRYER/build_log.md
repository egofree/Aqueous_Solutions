# Build log - H2_DRYER

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/H2_DRYER.md`; envelope per `models/mfg/H2_DRYER/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/H2_DRYER/h2_dryer.py`

## Checks

- Build bbox 600 x 400 x 1028 mm against the 600 x 400 x 1028 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/H2_DRYER/export/h2_dryer.step`; export STL closed and manifold, 17 solid(s); `cad/stl/H2_DRYER.stl` replaced from the build (ASCII, metres)
- Nozzles: all 9 rows of `docs-authority/nozzles/H2_DRYER.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Skid per the node design block: dryer vessel OD 60.3 x 628, wall 3.91 (316L annealed per M6/AQS-REV-H2-001), 38 mm insulation; 2 deoxo DN25 x 328, 2 guard DN25 x 300, 2 TSA DN50 x 300 bed tubes with media envelopes; PVC-U inlet KO pot (duty section 3)
- A-MACH: guard frame drawn (four posts, top rail) and 8 anchors; purchased items named with the node ratings (heater 1.03 W regen_W; sieve 0.353 kg; guard media 0.032 kg; deoxo catalyst 0.183 L charges - buy rows)
- The N4 vent is the S24 relief edge to RELIEF_H2 (duty section 6) with the destination named; the N7 solids row drawn DN15, bore not calculated (plan W4); bed stations are the layout choice (hold, W12)
- BOM `models/mfg/H2_DRYER/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/H2_DRYER/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/H2_DRYER/h2_dryer.py`
- `models/mfg/H2_DRYER/draw_h2_dryer.py`
- `models/mfg/H2_DRYER/bom.csv`
- `models/mfg/H2_DRYER/fasteners.csv`
- `models/mfg/H2_DRYER/check.json`
- `models/mfg/H2_DRYER/WORK_ORDER.md`
- `build export `models/mfg/H2_DRYER/export/h2_dryer.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH; holds named in WORK_ORDER W12.
