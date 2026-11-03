# Build log - BEE_HIVE

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-FARM; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/BEE_HIVE.md`; envelope per `models/mfg/BEE_HIVE/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/BEE_HIVE/bee_hive.py`

## Checks

- Rebuild through the shared close-out builder (`models/mfg/farm_closeout.py`) confirms the Oct-31 hive as issued: measured 650.0 x 550.0 x 1150.0 mm - the section-7-reported misfit against size_mm 600 x 500 x 1100 is CARRIED, by design and not resized (plan rule 3): the stand laps 25 mm a side, the telescoping lid laps 20 mm a side, and the box stack tops at z 1150; the node states no per-box heights, so fitting under 1100 would invent dimensions. `cad/stl/BEE_HIVE.stl` keeps the X-PAR-04 study envelope box (the registry gate: the registry bbox matches size_mm within 1 mm; no in-envelope module of this build fills the node box) - the full build lives in `export/` and the STEP, the misfit section-7-reported (the GROW_BED registry treatment; scope in `check.json` `cad_stl_scope`)
- Screen board material corrected on the BOM: the Oct-31 row carried the pine density; the duty section 3 names SS316 - the row now carries the mesh-class mass (~0.15 of the drawn plate solid, the hardware-cloth idiom)
- Route-class hold named: `hive` has no AQS-PLAN-006 section 4 class; the F-FARM practice is the named study route
- Internals: node row `none`; the hive is drawn as the unit (stand, deep + medium boxes, screen board, lid); frames and foundation are the buy woodenware the size_basis names (count hold, W12)
- Nozzles: all 5 rows of `docs-authority/nozzles/BEE_HIVE.csv` drawn at tag, face, height and bore as DN15 tube stubs flush at the envelope faces (loop accounting rows); N5 vent drawn at the envelope top (schedule z 800 predates the 1100 box, stale datum, hold W12); atmospheric joints, no flange; schedule rating column carried verbatim
- BOM `models/mfg/BEE_HIVE/bom.csv` (generated from the model: qty, material, mass, make-or-buy; frames + foundation are the buy row); `fasteners.csv` completed (A4-70 box screws - no copper-bearing alloys per duty section 3; stand anchors 8.8 CS); WORK_ORDER rewritten to the W1-W12 items with holds named; no builder writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/BEE_HIVE/bee_hive.py`
- `models/mfg/BEE_HIVE/export/bee_hive.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-FARM; the section-7-reported misfit is carried, nothing resized; route-class hold named in WORK_ORDER W12.
