# Build log - WS_PEROX

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/WS_PEROX.md`; envelope per `models/mfg/WS_PEROX/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/WS_PEROX/ws_perox.py`

## Checks

- Build bbox 600 x 600 x 350 mm against the 600 x 600 x 350 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/WS_PEROX/export/ws_perox.step`; export STL closed and manifold, 1 solid(s); `cad/stl/WS_PEROX.stl` replaced from the build (ASCII, metres)
- Nozzles: all 6 rows of `docs-authority/nozzles/WS_PEROX.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-MACH: guard rail and slab anchors drawn; PVDF pump (duty section 3) and the electrolysis cell (AQS-DSN-OX-001 2.1: 12.31 A, 246 cm2, 30.8 W) drawn as their envelopes (plan rule 6); ratings per the maker TDS at order (W12)
- Tank: 5 L nominal, 2.9 L net at the duty section 2 X-SAF-09 basis, levels reported; the 6 L own bund is the room-side containment (W12)
- Schedule datums clamped into the 350 mm box (holds, W12)
- BOM `models/mfg/WS_PEROX/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/WS_PEROX/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/WS_PEROX/ws_perox.py`
- `models/mfg/WS_PEROX/draw_ws_perox.py`
- `models/mfg/WS_PEROX/bom.csv`
- `models/mfg/WS_PEROX/fasteners.csv`
- `models/mfg/WS_PEROX/check.json`
- `models/mfg/WS_PEROX/WORK_ORDER.md`
- `build export `models/mfg/WS_PEROX/export/ws_perox.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH; holds named in WORK_ORDER W12.
