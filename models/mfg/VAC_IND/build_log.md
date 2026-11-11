# Build log - VAC_IND

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/VAC_IND.md`; envelope per `models/mfg/VAC_IND/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/VAC_IND/vac_ind.py`

## Checks

- Build bbox 1000 x 1000 x 1500 mm against the 1000 x 1000 x 1500 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/VAC_IND/export/vac_ind.step`; export STL closed and manifold, 11 solid(s); `cad/stl/VAC_IND.stl` replaced from the build (ASCII, metres)
- Nozzles: all 5 rows of `docs-authority/nozzles/VAC_IND.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Standby N+1 alternate drawn per the node design block (A-M-282/A-M-283): real machine, standby-zero design-day rate; named in the BOM rows and the WORK_ORDER
- Water-cooled Cu crucible per duty section 3: no wetted-refractory interface; 304L vacuum chamber; CA 0 mm (AQS-STD-001)
- Purchased PSU cabinet (15 kW connected, node design) drawn as its envelope per plan rule 6
- BOM `models/mfg/VAC_IND/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/VAC_IND/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/VAC_IND/vac_ind.py`
- `models/mfg/VAC_IND/draw_vac_ind.py`
- `models/mfg/VAC_IND/bom.csv`
- `models/mfg/VAC_IND/fasteners.csv`
- `models/mfg/VAC_IND/check.json`
- `models/mfg/VAC_IND/WORK_ORDER.md`
- `build export `models/mfg/VAC_IND/export/vac_ind.step``

Status: accepted per AQS-PLAN-006 section 5 A-core (route hold); holds named in WORK_ORDER W12.
