# Build log - HYDRO_SET

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/HYDRO_SET.md`; envelope per `models/mfg/HYDRO_SET/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/HYDRO_SET/hydro_set.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/HYDRO_SET/export/hydro_set.step`; export STL closed and manifold, 3 solid(s); `cad/stl/HYDRO_SET.stl` replaced from the build (ASCII, metres)
- Nozzles: all 3 rows of `docs-authority/nozzles/HYDRO_SET.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Pumped-hydro powerhouse set per the node backup_basis (A-M-145 lane; Q-006/Q-009 closed): N+1 backup of ZNBR2 to NFPA 111 Level 1 Class X (14 h at 14.46 kW = 202.4 kWh); turbine (14.46 kW at 36.21 m, eta 0.8), generator, pump-motor (49.6 kW recharge, eta 0.85) and cabinet envelopes per plan rule 6
- Reservoir interface per the Q-009 facts: upper = building top floors (3 levels x 3.06 m over 367 m2, 2 cells/level), lower = CATCH_TANK (9.17 m over 367 m2); penstock/tailrace pads drawn, bores not calculated (W4) - the reservoirs are building scope (AQS-BLD-014, A-M-187)
- A-MACH: hold-down/guard frame + 8 anchors; purchased items named with the node ratings; no machine type invented (holds, WORK_ORDER W12)
- BOM `models/mfg/HYDRO_SET/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/HYDRO_SET/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/HYDRO_SET/hydro_set.py`
- `models/mfg/HYDRO_SET/draw_hydro_set.py`
- `models/mfg/HYDRO_SET/bom.csv`
- `models/mfg/HYDRO_SET/fasteners.csv`
- `models/mfg/HYDRO_SET/check.json`
- `models/mfg/HYDRO_SET/WORK_ORDER.md`
- `build export `models/mfg/HYDRO_SET/export/hydro_set.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH; holds named in WORK_ORDER W12.
