# Build log - ELECTRODE_COAT

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-SC (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/ELECTRODE_COAT.md`; envelope per `models/mfg/ELECTRODE_COAT/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/ELECTRODE_COAT/electrode_coat.py`

## Checks

- Build bbox 1200 x 800 x 1800 mm against the 1200 x 800 x 1800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/ELECTRODE_COAT/export/electrode_coat.step`; export STL closed and manifold, 7 solid(s); `cad/stl/ELECTRODE_COAT.stl` replaced from the build (ASCII, metres)
- Nozzles: all 4 rows of `docs-authority/nozzles/ELECTRODE_COAT.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Coating booth per the node design block and AQS-MFG-ELC-001 Rev D: open-front hood over a 316L drip tray, coat-head envelope (ELC-SPRAY-01), IR cure panel (ELC-CURE-01, 1.2 kW) and exhaust fan (ELC-EXH-01, 0.35 kW) as purchased envelopes per plan rule 6; recipes and nameplates are not designed - no internals invented (hold W12)
- Exhaust routing named at the vent: MET_AHU -> MET_SCRUB (S71-S72) per the node design line and AQS-MFG-ELC-001 section 3.2
- Guard frame pins the registry box so the build fills the envelope (X-PAR-04); anchors in fasteners.csv
- BOM `models/mfg/ELECTRODE_COAT/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/ELECTRODE_COAT/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/ELECTRODE_COAT/electrode_coat.py`
- `models/mfg/ELECTRODE_COAT/draw_electrode_coat.py`
- `models/mfg/ELECTRODE_COAT/bom.csv`
- `models/mfg/ELECTRODE_COAT/fasteners.csv`
- `models/mfg/ELECTRODE_COAT/check.json`
- `models/mfg/ELECTRODE_COAT/WORK_ORDER.md`
- `build export `models/mfg/ELECTRODE_COAT/export/electrode_coat.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-SC (route hold); holds named in WORK_ORDER W12.
