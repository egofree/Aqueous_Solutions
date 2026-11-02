# Build log - FLOAT_SINK

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/FLOAT_SINK.md`; envelope per `models/mfg/FLOAT_SINK/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/FLOAT_SINK/float_sink.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/FLOAT_SINK/export/float_sink.step`; export STL closed and manifold, 1 solid(s); `cad/stl/FLOAT_SINK.stl` replaced from the build (ASCII, metres)
- Nozzles: all 6 rows of `docs-authority/nozzles/FLOAT_SINK.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-VES: liquor holdup 0.399 m3 at the 720 mm working level net of the weir and launder, reported from the model; the duty claims no holdup, so no residence time is derived
- Internals: weir + float launder drawn as layout solids from the duty section 1 separation duty; the node internals row is none (tracker hold, W12)
- BOM `models/mfg/FLOAT_SINK/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/FLOAT_SINK/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/FLOAT_SINK/float_sink.py`
- `models/mfg/FLOAT_SINK/draw_float_sink.py`
- `models/mfg/FLOAT_SINK/bom.csv`
- `models/mfg/FLOAT_SINK/fasteners.csv`
- `models/mfg/FLOAT_SINK/check.json`
- `models/mfg/FLOAT_SINK/WORK_ORDER.md`
- `build export `models/mfg/FLOAT_SINK/export/float_sink.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
