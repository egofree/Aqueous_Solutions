# Build log - RES_HEAT

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/RES_HEAT.md`; envelope per `models/mfg/RES_HEAT/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/RES_HEAT/res_heat.py`

## Checks

- Build bbox 1000 x 1000 x 1500 mm against the 1000 x 1000 x 1500 mm envelope: inside (tracker check green)
- Solid source: build export `models/mfg/RES_HEAT/export/res_heat.step`; export STL closed and manifold, 4 solid(s); `cad/stl/RES_HEAT.stl` replaced from the build (ASCII, metres)
- Nozzles: no piped process connection on the graph; no nozzle schedule is issued (duty section 4) - no nozzle hardware drawn (hold, WORK_ORDER W12)
- Standby N+1 alternate drawn per the node design block (A-M-282/A-M-283): real machine, standby-zero design-day rate; named in the BOM rows and the WORK_ORDER
- Casing, fibre module lining and 80Ni-20Cr elements per duty section 3; CA 0 mm (AQS-STD-001); the element set is the purchased consumable (buy row)
- Purchased controls cabinet (12 kW connected, node design) drawn as its envelope per plan rule 6; SCR package purchased at fabrication (W12)
- BOM `models/mfg/RES_HEAT/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/RES_HEAT/drawings/` (GA front/side, part sheets, iso; title blocks per AQS-DWG-002); no nozzle sheet - no schedule

## Sources

- `models/mfg/RES_HEAT/res_heat.py`
- `models/mfg/RES_HEAT/draw_res_heat.py`
- `models/mfg/RES_HEAT/bom.csv`
- `models/mfg/RES_HEAT/fasteners.csv`
- `models/mfg/RES_HEAT/check.json`
- `models/mfg/RES_HEAT/WORK_ORDER.md`
- build export `models/mfg/RES_HEAT/export/res_heat.step`

Status: accepted per AQS-PLAN-006 section 5 A-core (route hold); holds named in WORK_ORDER W12.
