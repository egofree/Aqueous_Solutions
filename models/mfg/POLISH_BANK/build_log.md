# Build log - POLISH_BANK

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/POLISH_BANK.md`; envelope per `models/mfg/POLISH_BANK/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/POLISH_BANK/polish_bank.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/POLISH_BANK/export/polish_bank.step`; export STL closed and manifold, 1 solid(s); `cad/stl/POLISH_BANK.stl` replaced from the build (ASCII, metres)
- Nozzles: all 7 rows of `docs-authority/nozzles/POLISH_BANK.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-VES: the 0.0827 m3 liquor volume at the duty-basis working level is reported - the duty section 2 figure is an existing holdup basis (30-minute hold), not a new residence claim; duty section 8: the vessel is not built, so this is not a measured volume
- Internals: none drawn - the node internals row is none and no authority dimensions the polish media (W12); the PK_1..PK_9 seed history is named and the model covers the column set as the node defines it
- The duty section 4 prose bore line (DN15) predates the issued DN50 tail rows; the schedule governs (W12)
- BOM `models/mfg/POLISH_BANK/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/POLISH_BANK/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/POLISH_BANK/polish_bank.py`
- `models/mfg/POLISH_BANK/draw_polish_bank.py`
- `models/mfg/POLISH_BANK/bom.csv`
- `models/mfg/POLISH_BANK/fasteners.csv`
- `models/mfg/POLISH_BANK/check.json`
- `models/mfg/POLISH_BANK/WORK_ORDER.md`
- `build export `models/mfg/POLISH_BANK/export/polish_bank.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
