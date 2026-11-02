# Build log - POLY_F

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-VES; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/POLY_F.md`; envelope per `models/mfg/POLY_F/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/POLY_F/poly_f.py`

## Checks

- Build bbox 600 x 600 x 1200 mm against the 600 x 600 x 1200 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/POLY_F/export/poly_f.step`; export STL closed and manifold, 7 solid(s); `cad/stl/POLY_F.stl` replaced from the build (ASCII, metres)
- Nozzles: all 8 rows of `docs-authority/nozzles/POLY_F.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Replaces the pre-plan M2 study build: the old +Y connection overhang (bbox 630 against the 600 envelope) is gone - hardware flush at the envelope faces, the envelope itself unchanged (nothing resized)
- Agitator drawn as solids per the node power basis (jacket loss + agitator, A-M-289) into the purchased drive envelope (plan rule 6)
- A-VES: gross shell volume reported for the record; no holdup claimed, no residence derived (W12)
- BOM `models/mfg/POLY_F/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/POLY_F/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/POLY_F/poly_f.py`
- `models/mfg/POLY_F/draw_poly_f.py`
- `models/mfg/POLY_F/bom.csv`
- `models/mfg/POLY_F/fasteners.csv`
- `models/mfg/POLY_F/check.json`
- `models/mfg/POLY_F/WORK_ORDER.md`
- `build export `models/mfg/POLY_F/export/poly_f.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-VES; holds named in WORK_ORDER W12.
