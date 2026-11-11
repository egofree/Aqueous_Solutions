# Build log - SOLAR_PV_CELL

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH + A-SC; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/SOLAR_PV_CELL.md`; envelope per `models/mfg/SOLAR_PV_CELL/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/SOLAR_PV_CELL/solar_pv_cell.py`

## Checks

- Build bbox 2400 x 1200 x 1600 mm against the 2400 x 1200 x 1600 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/SOLAR_PV_CELL/export/solar_pv_cell.step`; export STL closed and manifold, 6 solid(s); `cad/stl/SOLAR_PV_CELL.stl` replaced from the build (ASCII, metres)
- Nozzles: all 7 rows of `docs-authority/nozzles/SOLAR_PV_CELL.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn); the N5 cable power-terminal row is carried verbatim, not drawn
- In-house PV cell line per the node design block (X-MFG-38, A-M-178, AQS-DUTY-071): seven named stations drawn as envelopes with the node ratings; PV-EMIT-01 internally resolved per its node dims (quartz tube 200 x 1000 with the 200 mm ceramic-fibre annulus at face value)
- Wetted material per duty section 3: 316L where the stream is wet; the node station texts name PP tanks - the duty selection governs (plan rule 5; hold W12); tube quartz and screen stainless shop-cut per AQS-PV-001 section 3
- Hold-down frame pins the registry box so the build fills the envelope (X-PAR-04); anchors in fasteners.csv
- BOM `models/mfg/SOLAR_PV_CELL/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/SOLAR_PV_CELL/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/SOLAR_PV_CELL/solar_pv_cell.py`
- `models/mfg/SOLAR_PV_CELL/draw_solar_pv_cell.py`
- `models/mfg/SOLAR_PV_CELL/bom.csv`
- `models/mfg/SOLAR_PV_CELL/fasteners.csv`
- `models/mfg/SOLAR_PV_CELL/check.json`
- `models/mfg/SOLAR_PV_CELL/WORK_ORDER.md`
- `build export `models/mfg/SOLAR_PV_CELL/export/solar_pv_cell.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH + A-SC; holds named in WORK_ORDER W12.
