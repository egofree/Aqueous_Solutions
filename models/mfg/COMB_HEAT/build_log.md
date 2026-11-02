# Build log - COMB_HEAT

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core (route hold); MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/COMB_HEAT.md`; envelope per `models/mfg/COMB_HEAT/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/COMB_HEAT/comb_heat.py`

## Checks

- Build bbox 1000 x 1000 x 1500 mm against the 1000 x 1000 x 1500 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/COMB_HEAT/export/comb_heat.step`; export STL closed and manifold, 2 solid(s); `cad/stl/COMB_HEAT.stl` replaced from the build (ASCII, metres)
- Nozzles: all 3 rows of `docs-authority/nozzles/COMB_HEAT.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Standby tertiary N+1 alternate drawn per duty section 3 (A-M-282/A-M-283): real machine, standby-zero design-day rate; named in the BOM rows and the WORK_ORDER
- Alumina-silica brick + castable crown hot face on the mild-steel shell; 310S radiant burner tube keeps combustion products off the charge (duty section 3); CA 0 mm (AQS-STD-001)
- Purchased controls cabinet (0.05 kW connected, node design) drawn as its envelope per plan rule 6; burner train purchased at fabrication (W12)
- BOM `models/mfg/COMB_HEAT/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/COMB_HEAT/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/COMB_HEAT/comb_heat.py`
- `models/mfg/COMB_HEAT/draw_comb_heat.py`
- `models/mfg/COMB_HEAT/bom.csv`
- `models/mfg/COMB_HEAT/fasteners.csv`
- `models/mfg/COMB_HEAT/check.json`
- `models/mfg/COMB_HEAT/WORK_ORDER.md`
- `build export `models/mfg/COMB_HEAT/export/comb_heat.step``

Status: accepted per AQS-PLAN-006 section 5 A-core (route hold); holds named in WORK_ORDER W12.
