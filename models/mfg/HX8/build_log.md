# Build log - HX8

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-HX; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/HX8.md`; envelope per `models/mfg/HX8/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/HX8/hx8.py`

## Checks

- Build bbox 600 x 400 x 600 mm against the 600 x 400 x 600 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/HX8/export/hx8.step`; export STL closed and manifold, 1 solid(s); `cad/stl/HX8.stl` replaced from the build (ASCII, metres)
- Nozzles: all 7 rows of `docs-authority/nozzles/HX8.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-HX: tube area 0.5202 m2 from the model against the 0.51 m2 duty figure (46 tubes OD 10 x 360); the duty carries the heat rate (4.59 kW at U 1500, LMTD 6 K), so the area is duty-sized and reported, not recalculated as a claim
- Bundle: real PVDF tubes between two tube sheets (duty section 3; AQS-STD-002 section 4.5 owner adoption; titanium withdrawn, no graphite)
- BOM `models/mfg/HX8/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/HX8/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/HX8/hx8.py`
- `models/mfg/HX8/draw_hx8.py`
- `models/mfg/HX8/bom.csv`
- `models/mfg/HX8/fasteners.csv`
- `models/mfg/HX8/check.json`
- `models/mfg/HX8/WORK_ORDER.md`
- `build export `models/mfg/HX8/export/hx8.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-HX; holds named in WORK_ORDER W12.
