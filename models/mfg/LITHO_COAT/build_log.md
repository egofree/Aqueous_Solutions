# Build log - LITHO_COAT

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-SC (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/LITHO_COAT.md`; envelope per `models/mfg/LITHO_COAT/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/LITHO_COAT/litho_coat.py`

## Checks

- Build bbox 1200 x 800 x 1400 mm against the 1200 x 800 x 1400 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/LITHO_COAT/export/litho_coat.step`; export STL closed and manifold, 8 solid(s); `cad/stl/LITHO_COAT.stl` replaced from the build (ASCII, metres)
- Nozzles: all 7 rows of `docs-authority/nozzles/LITHO_COAT.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn); the N5 cable power-terminal row is carried verbatim, not drawn
- Spin-coater line per the node design block and note (A-M-287): spin bowl and coat catch bowl in 316L per duty section 3, the 150 mm vacuum chuck (node chuck_mm) on the spindle, and the spin-chuck motor (0.75 kW peak) and softbake hotplate (0.3 kW, 100 C hold) as purchased envelopes per plan rule 6 with the node ratings
- Duty section 2 prose carries the seed figure 600 x 500 x 800; the node 1200 x 800 x 1400 governs, the older figure named (hold W12)
- Guard frame pins the registry box so the build fills the envelope (X-PAR-04); anchors in fasteners.csv
- BOM `models/mfg/LITHO_COAT/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/LITHO_COAT/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/LITHO_COAT/litho_coat.py`
- `models/mfg/LITHO_COAT/draw_litho_coat.py`
- `models/mfg/LITHO_COAT/bom.csv`
- `models/mfg/LITHO_COAT/fasteners.csv`
- `models/mfg/LITHO_COAT/check.json`
- `models/mfg/LITHO_COAT/WORK_ORDER.md`
- `build export `models/mfg/LITHO_COAT/export/litho_coat.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-SC (route hold); holds named in WORK_ORDER W12.
