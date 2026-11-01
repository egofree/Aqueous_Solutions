# Build log - CRYO_CO2

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-COL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CRYO_CO2.md`; rack envelope from the node design block, A-M-167).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/CRYO_CO2/cryo_co2.py`

## Checks

- Build bbox 6696.0 x 1500.0 x 450.1 mm: fills the node rack envelope 6696 x 1500 x 450 mm exactly (tracker check green)
- Solid source: build export `models/mfg/CRYO_CO2/export/cryo_co2.step`; export STL closed and manifold; `cad/stl/CRYO_CO2.stl` replaced from the build (ASCII, metres)
- Nozzles: all 10 rows of `docs-authority/nozzles/CRYO_CO2.csv` present at face and bore; heights that fit the 450 rack drawn as issued, the rest clamped with named holds (check.nozzles_drawn)
- A-COL: the tube bank is the machine here; relief per the node API 520/521 fire case per half bank (2 valves, 9 mm)
- BOM `models/mfg/CRYO_CO2/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/CRYO_CO2/drawings/` (GA front/side, nozzle orientation, 2 part sheets, iso; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/CRYO_CO2/cryo_co2.py`
- `models/mfg/CRYO_CO2/draw_cryo_co2.py`
- `build export `models/mfg/CRYO_CO2/export/cryo_co2.step``
- `models/mfg/CRYO_CO2/bom.csv`
- `models/mfg/CRYO_CO2/fasteners.csv`
- `models/mfg/CRYO_CO2/check.json`
- `models/mfg/CRYO_CO2/WORK_ORDER.md`

Status: accepted per AQS-PLAN-006 section 5 A-core and A-COL; the machine-design detail (piping hookup, relief valve selection) follows the unit WORK_ORDER.
