# Build log - BMED_UPW_POLISH

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/BMED_UPW_POLISH.md`; envelope per `models/mfg/BMED_UPW_POLISH/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/BMED_UPW_POLISH/bmed_upw_polish.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/BMED_UPW_POLISH/export/bmed_upw_polish.step`; export STL closed and manifold, 7 solid(s); `cad/stl/BMED_UPW_POLISH.stl` replaced from the build (ASCII, metres)
- Nozzles: all 8 rows of `docs-authority/nozzles/BMED_UPW_POLISH.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn); the N8 cable power-terminal row is carried verbatim, not drawn
- Skid per the node internals row and design block (X-MFG-34, A-M-176, AQS-DUTY-070): 2 flat-sheet TFC RO module envelopes (membrane_m2 0.2652, feed 6.859 bar, recovery 0.9547), 2 EDI stack envelopes (EDI_A 0.00973 A / 0.39 W), the UV-TOC lamp envelope (15 W), the RO pump envelope (2.6 W), and the potable bypass run (206.77 kg/d, 2 x 100% trains per A-M-176)
- A-M-072 vendor-class energy bases (RO 3.0 / EDI 0.5 kWh/m3) carried as a named hold pending the X-MFG-34 bench test; module internals are the X-MFG-34 design task, not invented (plan rule 6)
- Hold-down frame pins the registry box so the build fills the envelope (X-PAR-04); anchors in fasteners.csv
- BOM `models/mfg/BMED_UPW_POLISH/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/BMED_UPW_POLISH/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/BMED_UPW_POLISH/bmed_upw_polish.py`
- `models/mfg/BMED_UPW_POLISH/draw_bmed_upw_polish.py`
- `models/mfg/BMED_UPW_POLISH/bom.csv`
- `models/mfg/BMED_UPW_POLISH/fasteners.csv`
- `models/mfg/BMED_UPW_POLISH/check.json`
- `models/mfg/BMED_UPW_POLISH/WORK_ORDER.md`
- `build export `models/mfg/BMED_UPW_POLISH/export/bmed_upw_polish.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH; holds named in WORK_ORDER W12.
