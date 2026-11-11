# Build log - BAGHOUSE

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/BAGHOUSE.md`; envelope per `models/mfg/BAGHOUSE/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/BAGHOUSE/baghouse.py`

## Checks

- Build bbox 1250 x 1000 x 2276.5 mm against the 1250 x 1000 x 2276 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/BAGHOUSE/export/baghouse.step`; export STL closed and manifold, 41 solid(s); `cad/stl/BAGHOUSE.stl` replaced from the build (ASCII, metres)
- Nozzles: all 7 rows of `docs-authority/nozzles/BAGHOUSE.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-MACH: purchased items named with the rating (rotary valve at the 7.77 kg/d dust class, pulse diaphragm valves at the 0.5 MPa class, solenoid enclosure); drive guard and plinth anchors drawn
- Cloth 11.31 m2 drawn (20 bags) against the 10.5 m2 basis at the 1.2 m3/min/m2 EPA-453 class (A-M-458); capture air 756 m3/h
- No fan on this unit (duty 0.0 kW): the baghouse dP rides the tool-extraction air mover - stated, not omitted (W12(3))
- Placement seed under-books the height by 0.78 m (W12(1)); nothing is resized
- BOM `models/mfg/BAGHOUSE/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/BAGHOUSE/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/BAGHOUSE/baghouse.py`
- `models/mfg/BAGHOUSE/draw_baghouse.py`
- `models/mfg/BAGHOUSE/bom.csv`
- `models/mfg/BAGHOUSE/fasteners.csv`
- `models/mfg/BAGHOUSE/check.json`
- `models/mfg/BAGHOUSE/WORK_ORDER.md`
- `build export `models/mfg/BAGHOUSE/export/baghouse.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH; holds named in WORK_ORDER W12.
