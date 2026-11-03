# Build log - LITHO_DEV

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH + A-SC; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/LITHO_DEV.md`; envelope per `models/mfg/LITHO_DEV/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/LITHO_DEV/litho_dev.py`

## Checks

- Build bbox 1200 x 600 x 900 mm against the 1200 x 600 x 900 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/LITHO_DEV/export/litho_dev.step`; export STL closed and manifold, 6 solid(s); `cad/stl/LITHO_DEV.stl` replaced from the build (ASCII, metres)
- Nozzles: all 4 rows of `docs-authority/nozzles/LITHO_DEV.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Wet develop bench per the node design block and note (A-M-287): develop bowl in 316L per duty section 3 with the puddle dispense point envelope (40 mL/wafer); the TMAH class developer is the shared WET_BENCH chemistry fork; waste on the S38-class loop to OIL_FRAC
- Duty section 2 prose carries the seed figure 500 x 500 x 800; the node 1200 x 600 x 900 governs, the older figure named (hold W12)
- Hold-down frame pins the registry box so the build fills the envelope (X-PAR-04); no purchased item is named, so none is drawn (WS_SOLV precedent)
- BOM `models/mfg/LITHO_DEV/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/LITHO_DEV/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/LITHO_DEV/litho_dev.py`
- `models/mfg/LITHO_DEV/draw_litho_dev.py`
- `models/mfg/LITHO_DEV/bom.csv`
- `models/mfg/LITHO_DEV/fasteners.csv`
- `models/mfg/LITHO_DEV/check.json`
- `models/mfg/LITHO_DEV/WORK_ORDER.md`
- `build export `models/mfg/LITHO_DEV/export/litho_dev.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH + A-SC; holds named in WORK_ORDER W12.
