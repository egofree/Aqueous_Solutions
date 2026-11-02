# Build log - VAC_CAST

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core, A-SC (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/VAC_CAST.md`; envelope per `models/mfg/VAC_CAST/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/VAC_CAST/vac_cast.py`

## Checks

- Build bbox 1500 x 800 x 1500 mm against the 1500 x 800 x 1500 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/VAC_CAST/export/vac_cast.step`; export STL closed and manifold, 6 solid(s); `cad/stl/VAC_CAST.stl` replaced from the build (ASCII, metres)
- Nozzles: all 3 rows of `docs-authority/nozzles/VAC_CAST.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Standby N+1 alternate drawn per the node design block (A-M-282/A-M-283): real machine, standby-zero design-day rate; named in the BOM rows and the WORK_ORDER
- 304L vacuum chamber per duty section 3; graphite crucible + alumina backup as the consumable buy set; CA 0 mm (AQS-STD-001)
- Purchased vacuum pump skid and control cabinet (7.5 kW connected, node design) drawn as their envelopes per plan rule 6
- BOM `models/mfg/VAC_CAST/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/VAC_CAST/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/VAC_CAST/vac_cast.py`
- `models/mfg/VAC_CAST/draw_vac_cast.py`
- `models/mfg/VAC_CAST/bom.csv`
- `models/mfg/VAC_CAST/fasteners.csv`
- `models/mfg/VAC_CAST/check.json`
- `models/mfg/VAC_CAST/WORK_ORDER.md`
- `build export `models/mfg/VAC_CAST/export/vac_cast.step``

Status: accepted per AQS-PLAN-006 section 5 A-core, A-SC (route hold); holds named in WORK_ORDER W12.
