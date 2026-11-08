# Build log - EW_8

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-CELL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/EW_8.md`; sizing `docs-authority/sizing/EW_CELLS.md`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/EW_8/ew_8.py` (a `cad_mfg_models` pipeline stage through `models/mfg/build_all.py`)

## Checks

- Build bbox 270.0 x 720.1 x 760.0 mm: inside the graph envelope 270 x 720 x 760 mm with margin (tracker check green)
- Solid source: build export `models/mfg/EW_8/export/ew_8.step`; export STL closed and manifold; `cad/stl/EW_8.stl` replaced from the build (ASCII, metres)
- Nozzles: all 8 rows of `docs-authority/nozzles/EW_8.csv` present at face, height, bore and rating, tagged; drawn flush per the house idiom
- A-CELL: 1 cathode / 2 anodes at 100 mm pitch, plates 600 x 420 immersed (0.504 m2 both faces, 0.5 m2 bank); bus pack 1 x 20 x 6.3 mm per pole Cu per AQS-BUS-001 Rev D
- BOM `models/mfg/EW_8/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/EW_8/drawings/` (GA front/side, nozzle orientation, 3 part sheets, iso; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/EW_8/ew_8.py`
- `models/mfg/EW_8/draw_ew_8.py`
- `models/mfg/EW_8/export/ew_8.step`
- `models/mfg/EW_8/bom.csv`
- `models/mfg/EW_8/fasteners.csv`
- `models/mfg/EW_8/check.json`
- `models/mfg/EW_8/WORK_ORDER.md`

Status: accepted per AQS-PLAN-006 section 5 A-core and A-CELL; the machine-design detail (weld procedures, hose makeup) follows the unit WORK_ORDER.
