# Build log - FLUE_KO

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/FLUE_KO.md`; envelope per `models/mfg/FLUE_KO/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/FLUE_KO/flue_ko.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/FLUE_KO/export/flue_ko.step`; export STL closed and manifold, 1 solid(s); `cad/stl/FLUE_KO.stl` replaced from the build (ASCII, metres)
- Nozzles: all 8 rows of `docs-authority/nozzles/FLUE_KO.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-VES: the 0.0345 m3 sump volume is reported - the duty claims no holdup for this class (section 8) and no residence time is derived
- Materials per duty section 3: FRP vinyl ester + C-veil liner, borosilicate glass 3.3 spool, PVDF pad and hardware; no metal wetted part
- Internals: the weir/launder separation layout is unsized (duty section 8) - named hold (W12)
- BOM `models/mfg/FLUE_KO/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/FLUE_KO/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/FLUE_KO/flue_ko.py`
- `models/mfg/FLUE_KO/draw_flue_ko.py`
- `models/mfg/FLUE_KO/bom.csv`
- `models/mfg/FLUE_KO/fasteners.csv`
- `models/mfg/FLUE_KO/check.json`
- `models/mfg/FLUE_KO/WORK_ORDER.md`
- `build export `models/mfg/FLUE_KO/export/flue_ko.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
