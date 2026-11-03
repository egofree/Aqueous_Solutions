# Build log - MFG_SHOP

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-MACH + A-SC; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MFG_SHOP.md`; envelope per `models/mfg/MFG_SHOP/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/MFG_SHOP/mfg_shop.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/MFG_SHOP/export/mfg_shop.step`; export STL closed and manifold, 34 solid(s); `cad/stl/MFG_SHOP.stl` replaced from the build (ASCII, metres)
- Nozzles: all 33 rows of `docs-authority/nozzles/MFG_SHOP.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Machine-shop fitout per AQS-MFG-010 rev C Table 2.1: six shop machine tools as purchased-class envelopes (CNC mill 7.5, lathe 5.5, band saw 1.5, compressor 4.0, welder 6.0, bench set 2.0 kW; connected 26.5 kW, average 2.55 kW); shop-air DN15 header with four drops
- A-MACH: hold-down/guard frame + 8 anchors; purchased items named with the tool-row nameplates (plan rule 6); A-SC: bench, frame, header and connections flagged with the AQS-BOM-SC-001 cross-reference - this is the shop that makes the plant's AQS-BOM-SC-001 make rows
- The four metal-forming tools are metered at their own units (rev C split); the 19 solids rows are drawn DN15 bore not calculated (W4); machine footprints are study values (holds, WORK_ORDER W12)
- BOM `models/mfg/MFG_SHOP/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/MFG_SHOP/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/MFG_SHOP/mfg_shop.py`
- `models/mfg/MFG_SHOP/draw_mfg_shop.py`
- `models/mfg/MFG_SHOP/bom.csv`
- `models/mfg/MFG_SHOP/fasteners.csv`
- `models/mfg/MFG_SHOP/check.json`
- `models/mfg/MFG_SHOP/WORK_ORDER.md`
- `build export `models/mfg/MFG_SHOP/export/mfg_shop.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-MACH + A-SC; holds named in WORK_ORDER W12.
