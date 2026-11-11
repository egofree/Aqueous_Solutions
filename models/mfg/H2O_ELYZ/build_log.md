# Build log - H2O_ELYZ

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/H2O_ELYZ.md`; envelope per `models/mfg/H2O_ELYZ/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/H2O_ELYZ/h2o_elyz.py`

## Checks

- Build bbox 3367 x 1050 x 2201 mm against the 3367 x 1050 x 2200 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/H2O_ELYZ/export/h2o_elyz.step`; export STL closed and manifold, 110 solid(s); `cad/stl/H2O_ELYZ.stl` replaced from the build (ASCII, metres)
- Nozzles: all 7 rows of `docs-authority/nozzles/H2O_ELYZ.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- Stack facts reported against A-M-459: 80 cells x 169.7 x 169.7 mm = 2.304 m2 cell-summed, 518.4 A at 148 V DC (76.72 kW DC)
- The node internals row drawn in full: stack + H2/O2 separators + deoxo on H2 + dryer (A-M-168 classes on the skid beds)
- Placement hold named: the seed block under-books the A-M-279 skid (W12(1)); nothing is resized
- H2_DRYER chain mismatch recorded, not fixed (W12(6))
- BOM `models/mfg/H2O_ELYZ/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/H2O_ELYZ/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/H2O_ELYZ/h2o_elyz.py`
- `models/mfg/H2O_ELYZ/draw_h2o_elyz.py`
- `models/mfg/H2O_ELYZ/bom.csv`
- `models/mfg/H2O_ELYZ/fasteners.csv`
- `models/mfg/H2O_ELYZ/check.json`
- `models/mfg/H2O_ELYZ/WORK_ORDER.md`
- `build export `models/mfg/H2O_ELYZ/export/h2o_elyz.step``

Status: accepted per AQS-PLAN-006 section 5 A-core; holds named in WORK_ORDER W12.
