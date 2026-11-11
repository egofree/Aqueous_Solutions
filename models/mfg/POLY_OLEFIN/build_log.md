# Build log - POLY_OLEFIN

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/POLY_OLEFIN.md`; envelope per `models/mfg/POLY_OLEFIN/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/POLY_OLEFIN/poly_olefin.py`

## Checks

- Build bbox 600 x 600 x 1200 mm against the 600 x 600 x 1200 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/POLY_OLEFIN/export/poly_olefin.step`; export STL closed and manifold, 5 solid(s); `cad/stl/POLY_OLEFIN.stl` replaced from the build (ASCII, metres)
- Nozzles: all 6 rows of `docs-authority/nozzles/POLY_OLEFIN.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Wall 3.8 mm per the node design row (UG-27 at the 5 MPa design); SA-240 316L welded per duty section 3 (the node row matches)
- A-VES: gross shell volume 3.6 L reported; the 1 d hold-up of the naphtha feed is the node envelope basis (existing), no new residence time derived
- The N3 solids row drawn DN15, bore not calculated (plan W4); no agitator and no jacket named on the node - none drawn (W12)
- BOM `models/mfg/POLY_OLEFIN/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/POLY_OLEFIN/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/POLY_OLEFIN/poly_olefin.py`
- `models/mfg/POLY_OLEFIN/draw_poly_olefin.py`
- `models/mfg/POLY_OLEFIN/bom.csv`
- `models/mfg/POLY_OLEFIN/fasteners.csv`
- `models/mfg/POLY_OLEFIN/check.json`
- `models/mfg/POLY_OLEFIN/WORK_ORDER.md`
- `build export `models/mfg/POLY_OLEFIN/export/poly_olefin.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
