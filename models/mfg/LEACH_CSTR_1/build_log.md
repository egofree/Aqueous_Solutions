# Build log - LEACH_CSTR_1

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/LEACH_CSTR_1.md`; envelope basis AQS-DUTY-050 per duty section 2).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/LEACH_CSTR_1/leach_cstr_1.py`

## Checks

- Build bbox 2000.0 x 1200.3 x 1400.0 mm: inside the duty envelope 2000.0 x 1200.0 x 1400.0 mm (the node carries no size_mm; tracker hold, WORK_ORDER W12)
- Solid source: build export `models/mfg/LEACH_CSTR_1/export/leach_cstr_1.step`; export STL closed and manifold; `cad/stl/LEACH_CSTR_1.stl` replaced from the build (ASCII, metres)
- Nozzles: all 72 rows of `docs-authority/nozzles/LEACH_CSTR_1.csv` present at face, height, bore and tag; drawn flush per the house idiom; the IA-E-LEACH conductor is the +Y gland (duty section 4 prose)
- A-VES: holdup 1.855 m3 drawn net of internals at the 1100 mm working level against the 2.14 m3 fill basis (AQS-DUTY-050); residence stays the duty's 13.2 h figure
- BOM `models/mfg/LEACH_CSTR_1/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/LEACH_CSTR_1/drawings/` (GA front/side, nozzle orientation, 2 part sheets, iso; title blocks per AQS-DWG-002)

## Sources

- `models/mfg/LEACH_CSTR_1/leach_cstr_1.py`
- `models/mfg/LEACH_CSTR_1/draw_leach_cstr_1.py`
- `build export `models/mfg/LEACH_CSTR_1/export/leach_cstr_1.step``
- `models/mfg/LEACH_CSTR_1/bom.csv`
- `models/mfg/LEACH_CSTR_1/fasteners.csv`
- `models/mfg/LEACH_CSTR_1/check.json`
- `models/mfg/LEACH_CSTR_1/WORK_ORDER.md`

Status: accepted per AQS-PLAN-006 section 5 A-core and A-VES; the machine-design detail (belt segmentation, weld procedures, port bores) follows the unit WORK_ORDER.
