# Build log - WS_AMMONIA

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/WS_AMMONIA.md`; envelope per `models/mfg/WS_AMMONIA/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/WS_AMMONIA/ws_ammonia.py`

## Checks

- Build bbox 600 x 600 x 350 mm against the 600 x 600 x 350 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/WS_AMMONIA/export/ws_ammonia.step`; export STL closed and manifold, 1 solid(s); `cad/stl/WS_AMMONIA.stl` replaced from the build (ASCII, metres)
- Nozzles: all 8 rows of `docs-authority/nozzles/WS_AMMONIA.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-MACH: guard rail and slab anchors drawn; no purchased item named on the node or duty - none drawn (W12)
- Tank: station day-tank envelope, no volume claimed (duty section 8: no vessel diameter; W12)
- Schedule datums clamped into the 350 mm box (the 600 outlet datums down, the 800 vent flush at the envelope top; holds, W12)
- BOM `models/mfg/WS_AMMONIA/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/WS_AMMONIA/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/WS_AMMONIA/ws_ammonia.py`
- `models/mfg/WS_AMMONIA/draw_ws_ammonia.py`
- `models/mfg/WS_AMMONIA/bom.csv`
- `models/mfg/WS_AMMONIA/fasteners.csv`
- `models/mfg/WS_AMMONIA/check.json`
- `models/mfg/WS_AMMONIA/WORK_ORDER.md`
- `build export `models/mfg/WS_AMMONIA/export/ws_ammonia.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH; holds named in WORK_ORDER W12.
