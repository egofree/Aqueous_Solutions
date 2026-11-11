# Build log - MEOH_FC

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-CELL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MEOH_FC.md`; envelope per `models/mfg/MEOH_FC/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/MEOH_FC/meoh_fc.py`

## Checks

- Build bbox 1800 x 800 x 700 mm against the 1800 x 800 x 700 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/MEOH_FC/export/meoh_fc.step`; export STL closed and manifold, 10 solid(s); `cad/stl/MEOH_FC.stl` replaced from the build (ASCII, metres)
- Nozzles: all 11 rows of `docs-authority/nozzles/MEOH_FC.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-CELL: 28 cells, 200 cm2 active each (0.56 m2 total per the node design), plate 160 x 160 at 6 mm pitch enclosing the 141.4 mm active window; duty section 2 carries no plate row, so the match is against the node design (hold, W12)
- Bus: copper per duty section 3; POWER.md states no bus-bar section for this unit - the criterion has nothing to match (W12)
- The N5 (MEOH DC) row drawn as the copper conductor pad per duty section 4 prose (holds, W12)
- BOM `models/mfg/MEOH_FC/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MEOH_FC/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/MEOH_FC/meoh_fc.py`
- `models/mfg/MEOH_FC/draw_meoh_fc.py`
- `models/mfg/MEOH_FC/bom.csv`
- `models/mfg/MEOH_FC/fasteners.csv`
- `models/mfg/MEOH_FC/check.json`
- `models/mfg/MEOH_FC/WORK_ORDER.md`
- `build export `models/mfg/MEOH_FC/export/meoh_fc.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-CELL; holds named in WORK_ORDER W12.
