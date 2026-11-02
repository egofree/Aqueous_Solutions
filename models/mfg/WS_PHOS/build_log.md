# Build log - WS_PHOS

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/WS_PHOS.md`; envelope per `models/mfg/WS_PHOS/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/WS_PHOS/ws_phos.py`

## Checks

- Build bbox 600 x 600 x 350 mm against the 600 x 600 x 350 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/WS_PHOS/export/ws_phos.step`; export STL closed and manifold, 1 solid(s); `cad/stl/WS_PHOS.stl` replaced from the build (ASCII, metres)
- Nozzles: all 5 rows of `docs-authority/nozzles/WS_PHOS.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-MACH: guard rail and slab anchors drawn; no purchased item named on the node or duty - none drawn (W12)
- Tank: the seven-day charge 0.0043 m3 (duty section 2) sets the working level, reported; the box-over-flow line is not a residence time (W12)
- Schedule datums clamped into the 350 mm box (holds, W12)
- BOM `models/mfg/WS_PHOS/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/WS_PHOS/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/WS_PHOS/ws_phos.py`
- `models/mfg/WS_PHOS/draw_ws_phos.py`
- `models/mfg/WS_PHOS/bom.csv`
- `models/mfg/WS_PHOS/fasteners.csv`
- `models/mfg/WS_PHOS/check.json`
- `models/mfg/WS_PHOS/WORK_ORDER.md`
- `build export `models/mfg/WS_PHOS/export/ws_phos.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH; holds named in WORK_ORDER W12.
