# Build log - OIL_FRAC

Date: 2026-11-02. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-COL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/OIL_FRAC.md`; envelope per `models/mfg/OIL_FRAC/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/OIL_FRAC/oil_frac.py`

## Checks

- Build bbox 1000 x 600 x 800 mm against the 1000 x 600 x 800 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/OIL_FRAC/export/oil_frac.step`; export STL closed and manifold, 13 solid(s); `cad/stl/OIL_FRAC.stl` replaced from the build (ASCII, metres)
- Nozzles: all 14 rows of `docs-authority/nozzles/OIL_FRAC.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- M2 close-out per the HX8 close pattern: the style-builders column study verified through the current shared lib (unit-dir builder, 14-row issued schedule, tracker W2, section 5 artifacts completed); the stale envelope-era drawing set and GA.md superseded
- A-COL: no packing, distributor or demister is named on the node, so none is drawn (internals none); stages and HTU are not stated anywhere and stay a named hold (W12); the cut split rides the node cut_basis fractions (A-M-138, SU2018_PYRO) - a flowsheet allocation, not tray design
- Sump report: the duty section 2 sump 0.0006 m3 (30 min) stands 3.5 mm deep in the modeled bore - the sump zone is the bottom head; reported, nothing resized (plan rule 3)
- The shell is drawn to the node envelope (OD 480, wall 6 study): the duty states no diameter and no wall (holds, W12); a four-post hold-down frame pins the registry box (X-PAR-04)
- BOM `models/mfg/OIL_FRAC/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/OIL_FRAC/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/OIL_FRAC/oil_frac.py`
- `models/mfg/OIL_FRAC/draw_oil_frac.py`
- `models/mfg/OIL_FRAC/bom.csv`
- `models/mfg/OIL_FRAC/fasteners.csv`
- `models/mfg/OIL_FRAC/check.json`
- `models/mfg/OIL_FRAC/WORK_ORDER.md`
- `build export `models/mfg/OIL_FRAC/export/oil_frac.step``

Status: accepted per AQS-PLAN-006 section 5 A-core + A-COL; holds named in WORK_ORDER W12.
