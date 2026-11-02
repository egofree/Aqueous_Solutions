# Build log - FORGE

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core, A-SC (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/FORGE.md`; envelope per `models/mfg/FORGE/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/FORGE/forge.py`

## Checks

- Build bbox 1500 x 800 x 1500 mm against the 1500 x 800 x 1500 mm envelope: inside (tracker check green)
- Solid source: build export `models/mfg/FORGE/export/forge.step`; export STL closed and manifold, 1 solid(s); `cad/stl/FORGE.stl` replaced from the build (ASCII, metres)
- Nozzles: no piped process connection on the graph; no nozzle schedule is issued (duty section 4) - no nozzle hardware drawn (hold, WORK_ORDER W12)
- Standby N+1 alternate drawn per the node design block (A-M-282/A-M-283): real machine, standby-zero design-day rate; named in the BOM rows and the WORK_ORDER
- A-MACH: die-zone guard rail and slab anchors drawn; HPU skid and control pedestal are the purchased items named with the node rating
- H13 die pair is the purchased consumable (buy row); cast-steel frame per duty section 3; CA 0 mm (AQS-STD-001)
- A-SC: the press forges the bar stock the shop uses; make rows flagged and W11 cross-references AQS-BOM-SC-001
- BOM `models/mfg/FORGE/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/FORGE/drawings/` (GA front/side, part sheets, iso; title blocks per AQS-DWG-002); no nozzle sheet - no schedule

## Sources

- `models/mfg/FORGE/forge.py`
- `models/mfg/FORGE/draw_forge.py`
- `models/mfg/FORGE/bom.csv`
- `models/mfg/FORGE/fasteners.csv`
- `models/mfg/FORGE/check.json`
- `models/mfg/FORGE/WORK_ORDER.md`
- build export `models/mfg/FORGE/export/forge.step`

Status: accepted per AQS-PLAN-006 section 5 A-core, A-SC (route hold); holds named in WORK_ORDER W12.
