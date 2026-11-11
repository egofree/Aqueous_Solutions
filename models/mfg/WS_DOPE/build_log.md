# Build log - WS_DOPE

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/WS_DOPE.md`; envelope per `models/mfg/WS_DOPE/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/WS_DOPE/ws_dope.py`

## Checks

- Build bbox 600 x 600 x 350 mm against the 600 x 600 x 350 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/WS_DOPE/export/ws_dope.step`; export STL closed and manifold, 1 solid(s); `cad/stl/WS_DOPE.stl` replaced from the build (ASCII, metres)
- Nozzles: all 5 rows of `docs-authority/nozzles/WS_DOPE.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-MACH: guard rail and slab anchors drawn; no purchased item named on the node or duty - none drawn (W12)
- Tank: node design_storage D 300 x H 300, wall 4.75 (AQS-DUTY-064); the 0.02 m3 nominal volume is reported for the record, no residence claim (W12)
- Schedule datums clamped into the 350 mm box; the N5 solids row drawn DN15, bore not calculated (plan W4) (holds, W12)
- BOM `models/mfg/WS_DOPE/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/WS_DOPE/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/WS_DOPE/ws_dope.py`
- `models/mfg/WS_DOPE/draw_ws_dope.py`
- `models/mfg/WS_DOPE/bom.csv`
- `models/mfg/WS_DOPE/fasteners.csv`
- `models/mfg/WS_DOPE/check.json`
- `models/mfg/WS_DOPE/WORK_ORDER.md`
- `build export `models/mfg/WS_DOPE/export/ws_dope.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH; holds named in WORK_ORDER W12.
