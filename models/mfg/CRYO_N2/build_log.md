# Build log - CRYO_N2

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-COL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CRYO_N2.md`; envelope is the node size_mm box).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/CRYO_N2/cryo_n2.py`

## Checks

- Build bbox 300.0 x 300.0 x 2000.0 mm: fills the node size_mm box 300 x 300 x 2000 mm exactly (tracker check green)
- Solid source: build export `models/mfg/CRYO_N2/export/cryo_n2.step`; export STL closed and manifold; `cad/stl/CRYO_N2.stl` replaced from the build (ASCII, metres)
- Nozzles: all 8 rows of `docs-authority/nozzles/CRYO_N2.csv` present at face, height, bore and tag; every schedule datum fits the envelope and is drawn as issued
- A-COL: no packing, distributor, demister or diameter is named on the node or the duty sheet - the shell machine stands and the gaps are named holds (WORK_ORDER W12)
- BOM `models/mfg/CRYO_N2/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CRYO_N2/drawings/` (GA front/side, nozzle orientation, 2 part sheets, iso; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/CRYO_N2/cryo_n2.py`
- `models/mfg/CRYO_N2/draw_cryo_n2.py`
- `build export `models/mfg/CRYO_N2/export/cryo_n2.step``
- `models/mfg/CRYO_N2/bom.csv`
- `models/mfg/CRYO_N2/fasteners.csv`
- `models/mfg/CRYO_N2/check.json`
- `models/mfg/CRYO_N2/WORK_ORDER.md`

Status: accepted per AQS-PLAN-006 section 5 A-core and A-COL with the named design holds; the machine-design detail (internals, diameter, insulation) follows the unit WORK_ORDER.
