# Build log - GAS_ATOMIZER

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH + A-SC; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GAS_ATOMIZER.md`; envelope per `models/mfg/GAS_ATOMIZER/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/GAS_ATOMIZER/gas_atomizer.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/GAS_ATOMIZER/export/gas_atomizer.step`; export STL closed and manifold, 7 solid(s); `cad/stl/GAS_ATOMIZER.stl` replaced from the build (ASCII, metres)
- Nozzles: all 8 rows of `docs-authority/nozzles/GAS_ATOMIZER.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Close-coupled gas atomiser with Ar recirculation per the AQS-MFG-010 tool row (nameplate 5.5 kW; GMR 2.5 at 30 bar + tundish 1 kW, A-M-177): tower OD 300 with powder pot, gas ring at the neck, heated tundish on a stand, DN32 Ar loop to the compressor bay
- A-MACH: hold-down frame + 8 anchors; purchased items named with the node ratings (compressor 30 bar class, cabinet 5.5 kW, tundish heater 1 kW, plan rule 6); A-SC: shop-made hardware flagged with the AQS-BOM-SC-001 cross-reference
- No design_kPa on the node; the 30 bar loop class is the A-M-177 study basis and the relief case is pending (unit task 07) - no flange drawn (W4 110 % rule); tower/tundish dimensions are study values (holds, WORK_ORDER W12)
- BOM `models/mfg/GAS_ATOMIZER/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/GAS_ATOMIZER/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/GAS_ATOMIZER/gas_atomizer.py`
- `models/mfg/GAS_ATOMIZER/draw_gas_atomizer.py`
- `models/mfg/GAS_ATOMIZER/bom.csv`
- `models/mfg/GAS_ATOMIZER/fasteners.csv`
- `models/mfg/GAS_ATOMIZER/check.json`
- `models/mfg/GAS_ATOMIZER/WORK_ORDER.md`
- `build export `models/mfg/GAS_ATOMIZER/export/gas_atomizer.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH + A-SC; holds named in WORK_ORDER W12.
