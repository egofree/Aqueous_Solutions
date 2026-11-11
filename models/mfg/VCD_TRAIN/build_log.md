# Build log - VCD_TRAIN

Date: 2026-11-01. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/VCD_TRAIN.md`; envelope per `models/mfg/VCD_TRAIN/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/VCD_TRAIN/vcd_train.py`

## Checks

- Build bbox 1400 x 600 x 1201 mm against the 1400 x 600 x 1200 mm envelope: inside (tracker check green) (bbox read back from the export STL: the CAD kernel's bounding box of the lofted barb faces is loose; the mesh is the gate measure)
- Solid source: build export `models/mfg/VCD_TRAIN/export/vcd_train.step`; export STL closed and manifold, 54 solid(s); `cad/stl/VCD_TRAIN.stl` replaced from the build (ASCII, metres)
- Nozzles: all 11 rows of `docs-authority/nozzles/VCD_TRAIN.csv` present at face, height and bore (per-tag notes in check.nozzles_drawn)
- A-HX: bundle 19 tubes x 0.6375 m2 drawn against the booked 0.627 m2 (latent / (U 2.8 x 5 K), PERRY9_EVAP class, on the node 8.436 kW latent duty)
- Both installed modules drawn (2 x 100 %, X-RED-05); sump holdup 13.8 L equals the duty working-volume book (A-VES rule, reported)
- Purchased per plan rule 6: scroll compressors as envelopes and interfaces
- Route-class hold named: evaporator carries no section 4 class (W12(1))
- BOM `models/mfg/VCD_TRAIN/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners and WORK_ORDER beside it
- Drawing set `models/mfg/VCD_TRAIN/drawings/` (GA front/side, nozzle orientation, part sheets, iso; title blocks per AQS-DWG-002); the stale envelope `drawings/GA.md` is superseded where one existed

## Sources

- `models/mfg/VCD_TRAIN/vcd_train.py`
- `models/mfg/VCD_TRAIN/draw_vcd_train.py`
- `models/mfg/VCD_TRAIN/bom.csv`
- `models/mfg/VCD_TRAIN/fasteners.csv`
- `models/mfg/VCD_TRAIN/check.json`
- `models/mfg/VCD_TRAIN/WORK_ORDER.md`
- `build export `models/mfg/VCD_TRAIN/export/vcd_train.step``

Status: accepted per AQS-PLAN-006 section 5 A-core; holds named in WORK_ORDER W12.
