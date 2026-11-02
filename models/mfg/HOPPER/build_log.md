# Build log - HOPPER

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/HOPPER.md`; node envelope from AQS-DUTY-064 storage sizing).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/HOPPER/hopper.py`

## Checks

- Build bbox 600.0 x 600.0 x 600.0 mm: fills the node envelope 600 x 600 x 600 mm exactly (tracker check green)
- Solid source: build export `models/mfg/HOPPER/export/hopper.step`; export STL closed and manifold, one solid; `cad/stl/HOPPER.stl` replaced from the build (ASCII, metres)
- Nozzles: all 10 rows of `docs-authority/nozzles/HOPPER.csv` present at face, height and bore, drawn as atmospheric hose barbs per duty section 4; heights at the envelope top clamped with named holds (check.nozzles_drawn)
- A-VES: hopper holdup 0.1424 m3 computed from the model and reported; the duty claims no holdup, so no residence time is derived (duty section 8)
- BOM `models/mfg/HOPPER/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/HOPPER/drawings/` (GA front/side, nozzle orientation, 2 part sheets, aux, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded

## Sources

- `models/mfg/HOPPER/hopper.py`
- `models/mfg/HOPPER/draw_hopper.py`
- `build export `models/mfg/HOPPER/export/hopper.step``
- `models/mfg/HOPPER/bom.csv`
- `models/mfg/HOPPER/fasteners.csv`
- `models/mfg/HOPPER/check.json`
- `models/mfg/HOPPER/WORK_ORDER.md`

Status: accepted per AQS-PLAN-006 section 5 A-core and A-VES; holds named in WORK_ORDER W12 (study wall thickness, clamped schedule datums, the Class 150 rating column against the atmospheric duty, and the missing duty size line).
