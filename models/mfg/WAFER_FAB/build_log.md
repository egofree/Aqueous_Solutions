# Build log - WAFER_FAB

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH + A-SC; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/WAFER_FAB.md`; envelope per `models/mfg/WAFER_FAB/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/WAFER_FAB/wafer_fab.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/WAFER_FAB/export/wafer_fab.step`; export STL closed and manifold, 15 solid(s); `cad/stl/WAFER_FAB.stl` replaced from the build (ASCII, metres)
- Nozzles: all 14 rows of `docs-authority/nozzles/WAFER_FAB.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Machine per the node equipment list: CZ puller (0.2317 kW), ingot cool/anneal (0.02 kW), crop/grind/edge tools (0.04 kW), FAB_TOOL dry row (0.12 kW) as purchased-class station envelopes per plan rule 6; N2 purge distribution (0.03 kW) as the DN15 header with four drop legs; station arrangement is the layout choice (W12)
- A-MACH guard: the four-post hold-down frame pins the registry box so the build fills the envelope (X-PAR-04); 8 slab anchors in fasteners.csv
- Material per duty section 3: 316L where the stream is wet; CA 0 mm (AQS-STD-001); the node note (ISO 14644-1 Class 7 wet bench, Class 6 tool row) carried as text
- BOM `models/mfg/WAFER_FAB/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/WAFER_FAB/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/WAFER_FAB/wafer_fab.py`
- `models/mfg/WAFER_FAB/draw_wafer_fab.py`
- `models/mfg/WAFER_FAB/bom.csv`
- `models/mfg/WAFER_FAB/fasteners.csv`
- `models/mfg/WAFER_FAB/check.json`
- `models/mfg/WAFER_FAB/WORK_ORDER.md`
- `build export `models/mfg/WAFER_FAB/export/wafer_fab.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH + A-SC; holds named in WORK_ORDER W12.
