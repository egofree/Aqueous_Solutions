# Build log - WS_NITRIC

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/WS_NITRIC.md`; envelope per `models/mfg/WS_NITRIC/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/WS_NITRIC/ws_nitric.py`

## Checks

- Build bbox 600 x 600 x 350 mm against the 600 x 600 x 350 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/WS_NITRIC/export/ws_nitric.step`; export STL closed and manifold, 1 solid(s); `cad/stl/WS_NITRIC.stl` replaced from the build (ASCII, metres)
- Nozzles: all 7 rows of `docs-authority/nozzles/WS_NITRIC.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-MACH: guard rail and slab anchors drawn; PVDF pump named from duty section 3 and drawn as its envelope (plan rule 6); drive rating per the maker TDS at order (W12)
- Tank: 25 L nominal, 16.4 L net at the duty section 2 X-SAF-09 basis, levels reported; the 30 L own bund is the room-side containment (W12)
- Schedule datums clamped into the 350 mm box; the N6 vent-to-scrubber row carries no datum and draws at the +Y band bound (holds, W12)
- BOM `models/mfg/WS_NITRIC/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/WS_NITRIC/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/WS_NITRIC/ws_nitric.py`
- `models/mfg/WS_NITRIC/draw_ws_nitric.py`
- `models/mfg/WS_NITRIC/bom.csv`
- `models/mfg/WS_NITRIC/fasteners.csv`
- `models/mfg/WS_NITRIC/check.json`
- `models/mfg/WS_NITRIC/WORK_ORDER.md`
- `build export `models/mfg/WS_NITRIC/export/ws_nitric.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH; holds named in WORK_ORDER W12.
