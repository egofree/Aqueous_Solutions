# Build log - ZNBR2_BR2_REGEN

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-COL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/ZNBR2_BR2_REGEN.md`; envelope per `models/mfg/ZNBR2_BR2_REGEN/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/ZNBR2_BR2_REGEN/znbr2_br2_regen.py`

## Checks

- Build bbox 400 x 400 x 3701 mm against the 400 x 400 x 3700 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/ZNBR2_BR2_REGEN/export/znbr2_br2_regen.step`; export STL closed and manifold, 12 solid(s); `cad/stl/ZNBR2_BR2_REGEN.stl` replaced from the build (ASCII, metres)
- Nozzles: all 4 rows of `docs-authority/nozzles/ZNBR2_BR2_REGEN.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-COL: bed 3000 mm (NTU 6 x HTU 0.5 m, duty-held), support plate, distributor and demister as solids; diameter at 1.5 m/s on the live purge (82.7 mm -> PVC-U DN100)
- Sump holdup reported (house class), no residence time derived (duty section 2 rule; A-VES rule)
- Duty 30 m3/h / 84 mm figures are the W12(1) class basis; the column sizes on the live purge the charge book re-solves (82.7 mm -> PVC-U DN100) and DN100 carries the larger of the two diameters
- HTU and NTU stay duty-held figures, not measured transfer units (hold, W12(2))
- BOM `models/mfg/ZNBR2_BR2_REGEN/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/ZNBR2_BR2_REGEN/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/ZNBR2_BR2_REGEN/znbr2_br2_regen.py`
- `models/mfg/ZNBR2_BR2_REGEN/draw_znbr2_br2_regen.py`
- `models/mfg/ZNBR2_BR2_REGEN/bom.csv`
- `models/mfg/ZNBR2_BR2_REGEN/fasteners.csv`
- `models/mfg/ZNBR2_BR2_REGEN/check.json`
- `models/mfg/ZNBR2_BR2_REGEN/WORK_ORDER.md`
- `build export `models/mfg/ZNBR2_BR2_REGEN/export/znbr2_br2_regen.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-COL; holds named in WORK_ORDER W12.
