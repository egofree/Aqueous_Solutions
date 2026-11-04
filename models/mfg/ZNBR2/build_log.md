# Build log - ZNBR2

Date: 2026-11-04. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-CELL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/ZNBR2.md`; envelope per `models/mfg/ZNBR2/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/ZNBR2/znbr2.py`

## Checks

- Build bbox 7900 x 6050 x 1971 mm against the 7900 x 6050 x 1970 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/ZNBR2/export/znbr2.step`; export STL closed and manifold, 811 solid(s); `cad/stl/ZNBR2.stl` replaced from the build (ASCII, metres)
- Nozzles: all 12 rows of `docs-authority/nozzles/ZNBR2.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-CELL: 47 modules x 95 plates of 995.8 x 500 active at the 6 mm pitch = 2223.12 m2 against the booked 2223.1 m2 (purge_basis; j.A = current closes; X-MFG-43, A-M-456)
- Electrolyte holdup reported (47 reservoirs, 2 M ZnBr2, A-M-457); no residence time derived (duty section 2 claims no holdup; A-VES rule)
- Purchased items as envelopes per plan rule 6: pumps (A-M-179 aux share) and coolers (A-M-455 charge-window rate), one of each per module
- Placement hold named: the seed block under-books the machine; floor-space reservation is the consequence (WORK_ORDER W12(1)); nothing is resized
- BOM `models/mfg/ZNBR2/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/ZNBR2/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/ZNBR2/znbr2.py`
- `models/mfg/ZNBR2/draw_znbr2.py`
- `models/mfg/ZNBR2/bom.csv`
- `models/mfg/ZNBR2/fasteners.csv`
- `models/mfg/ZNBR2/check.json`
- `models/mfg/ZNBR2/WORK_ORDER.md`
- `build export `models/mfg/ZNBR2/export/znbr2.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-CELL; holds named in WORK_ORDER W12.
