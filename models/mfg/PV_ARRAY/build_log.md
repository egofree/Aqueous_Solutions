# Build log - PV_ARRAY

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/PV_ARRAY.md`; envelope per `models/mfg/PV_ARRAY/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/PV_ARRAY/pv_array.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/PV_ARRAY/export/pv_array.step`; export STL closed and manifold, 6 solid(s); `cad/stl/PV_ARRAY.stl` replaced from the build (ASCII, metres)
- Nozzles: all 4 rows of `docs-authority/nozzles/PV_ARRAY.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Representative array-table section at the registry box (WAFER_FAB room-scale precedent): tilted module plane (3 strips, 60 % GCR coverage, A-M-103), table rails, 4 ballast feet; the array facts reported from the node - 15 tables over the 210 x 138 m roof, 6052 x 0.5 kW = 3026 kWp, 26574 m2, 451.8 t at A-M-184
- Tilt +10 deg about +X, +Y edge raised (equator-facing, site north = +Y heritage rule); the numeric tilt is a study value pending the PVWatts run (hold, WORK_ORDER W12)
- A-MACH: hold-down frame + ballast anchors drawn; modules purchased per plan rule 6 with the node ratings
- BOM `models/mfg/PV_ARRAY/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/PV_ARRAY/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/PV_ARRAY/pv_array.py`
- `models/mfg/PV_ARRAY/draw_pv_array.py`
- `models/mfg/PV_ARRAY/bom.csv`
- `models/mfg/PV_ARRAY/fasteners.csv`
- `models/mfg/PV_ARRAY/check.json`
- `models/mfg/PV_ARRAY/WORK_ORDER.md`
- `build export `models/mfg/PV_ARRAY/export/pv_array.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH; holds named in WORK_ORDER W12.
