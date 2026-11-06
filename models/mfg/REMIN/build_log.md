# Build log - REMIN

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/REMIN.md`; envelope per `models/mfg/REMIN/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/REMIN/remin.py`

## Checks

- Build bbox 600 x 600 x 600 mm against the 600 x 600 x 600 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/REMIN/export/remin.step`; export STL closed and manifold, 1 solid(s); `cad/stl/REMIN.stl` replaced from the build (ASCII, metres)
- Nozzles: all 6 rows of `docs-authority/nozzles/REMIN.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-VES: the 0.07 m3 working volume at the duty-basis level is reported - the duty section 2 carries the holdup basis (7 days at the 10 L/d potable tap); no new residence-time claim
- Purchased items per plan rule 6: 2 x metering diaphragm pumps (Ca slurry, MgCl2) and the UV unit after the dose, named from the node design block and drawn as their envelope and interface only; wetted parts and drive ratings per the maker TDS at order (W12)
- Material conditional: PVC-U drawn per duty section 3 rule M1; the HDPE alternative is a named hold (W12)
- BOM `models/mfg/REMIN/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/REMIN/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/REMIN/remin.py`
- `models/mfg/REMIN/draw_remin.py`
- `models/mfg/REMIN/bom.csv`
- `models/mfg/REMIN/fasteners.csv`
- `models/mfg/REMIN/check.json`
- `models/mfg/REMIN/WORK_ORDER.md`
- `build export `models/mfg/REMIN/export/remin.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
