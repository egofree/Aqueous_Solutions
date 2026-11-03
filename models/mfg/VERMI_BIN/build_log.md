# Build log - VERMI_BIN

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-FARM; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/VERMI_BIN.md`; envelope per `models/mfg/VERMI_BIN/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/VERMI_BIN/vermi_bin.py`

## Checks

- Flush rebuild through the shared close-out builder (`models/mfg/farm_closeout.py`) fills the node box exactly: measured 2100.0 x 1100.0 x 600.0 mm, flush on all six faces, no section-7 misfit. `cad/stl/VERMI_BIN.stl` replaced from the build (scope in `check.json` `cad_stl_scope`)
- The duty section 3 build-up is drawn: SS316 harvest screen as a false-floor mesh plate 2 mm over the bin floor (the worm tea drains below it to the N4 row; laps 1 mm into the walls per the manifold idiom; mesh mass ~0.15 of the drawn plate solid), and the bedding envelope at the 300 mm depth the size_basis names (the charge is a buy row - no bedding density row exists in the material table, mass carries 0.0; hold, W12). The PP working fork is a hand tool, not drawn
- A-FARM area reading: interior 2080 x 1080 = 2.25 m2 at the registry box, NOT shrunk to fit, against the node design bin_m2 2.0 (hold, W12)
- Route-class hold named: `worm_bin` has no AQS-PLAN-006 section 4 class; the F-FARM practice is the named study route
- Nozzles: all 6 rows of `docs-authority/nozzles/VERMI_BIN.csv` drawn at tag, face, height and bore as DN15 tube stubs flush at the envelope faces; N3/N4 (schedule z 600, the rim height) and N6 (z 800) drawn flush at the envelope top (hold W12); atmospheric joints, no flange; rating column carried verbatim
- BOM `models/mfg/VERMI_BIN/bom.csv` (generated from the model: qty, material, mass, make-or-buy; screen and bedding are the buy rows); `fasteners.csv` completed (base anchors 8.8 CS per the grade rule, screen clamps A4-70 polymer supplier rule); WORK_ORDER rewritten to the W1-W12 items with holds named; no builder writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/VERMI_BIN/vermi_bin.py`
- `models/mfg/VERMI_BIN/export/vermi_bin.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-FARM; route-class hold named in WORK_ORDER W12.
