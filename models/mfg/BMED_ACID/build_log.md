# Build log - BMED_ACID

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-CELL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/BMED_ACID.md`; envelope per `models/mfg/BMED_ACID/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/BMED_ACID/bmed_acid.py`

## Checks

- Build bbox 1000 x 600 x 350 mm against the 1000 x 600 x 350 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/BMED_ACID/export/bmed_acid.step`; export STL closed and manifold, 1 solid(s); `cad/stl/BMED_ACID.stl` replaced from the build (ASCII, metres)
- Nozzles: all 10 rows of `docs-authority/nozzles/BMED_ACID.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-CELL: triplet count 85, frames 300 x 300, pitch 2.85 mm, active area 0.04 m2 per cell - the AQS-DUTY-068 / A-M-170/171 construction reported from the model; duty section 2 carries no plate row, so the match is against the sizing construction (W12); POWER.md states no bus bar for this class
- Duty section 9 books 26.93 kW stack power on this unit (A-M-088 SEC revision); the sizing design voltage class 1.22-1.67 V/triplet and the AQS-TST-006 acceptance band are the verification route - figures reported, band. Nothing recomputed here
- Schedule datums clamped into the 350 mm box: the 600 outlet datums down, the 800 vent flush at the top face, the 50 drain flush through the floor (holds, W12); N4 row repaired to schedule quoting (hold 7 of HX8 precedent)
- BOM `models/mfg/BMED_ACID/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/BMED_ACID/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/BMED_ACID/bmed_acid.py`
- `models/mfg/BMED_ACID/draw_bmed_acid.py`
- `models/mfg/BMED_ACID/bom.csv`
- `models/mfg/BMED_ACID/fasteners.csv`
- `models/mfg/BMED_ACID/check.json`
- `models/mfg/BMED_ACID/WORK_ORDER.md`
- `build export `models/mfg/BMED_ACID/export/bmed_acid.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-CELL; holds named in WORK_ORDER W12.
