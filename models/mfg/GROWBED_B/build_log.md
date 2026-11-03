# Build log - GROWBED_B

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-FARM; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/GROWBED_B.md`; envelope per `models/mfg/GROWBED_B/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/GROWBED_B/growbed_b.py`

## Checks

- Flush rebuild through the shared close-out builder (`models/mfg/farm_closeout.py`) fills the node box exactly: measured 3600.0 x 2100.0 x 500.0 mm, flush on all six faces, no section-7 misfit. `cad/stl/GROWBED_B.stl` replaced from the build (scope in `check.json` `cad_stl_scope`)
- The duty section 3 build-up is drawn: EPDM liner sheet 5 mm (floor + four walls, the GROW_BED ponded-zone idiom; the Oct-31 build drew a floor-only liner block), geotextile separation cloth 2 mm, and the LECA media envelope at the 300 mm depth GROWBED_A's size_note names for the pair (charge is a buy row, plan rule 6)
- A-FARM area reading: interior 3580 x 2080 = 7.45 m2 at the registry box, NOT shrunk to fit; the design block's area_m2 14.56 is the A+B dual-root-zone pair (hold, W12). The anaerobic mineralisation zone runs at depth (duty section 3); cold rabbit manure lands direct on the media (N3)
- Route-class hold named: `growbed` has no AQS-PLAN-006 section 4 class; the F-FARM practice is the named study route
- Nozzles: all 9 rows of `docs-authority/nozzles/GROWBED_B.csv` drawn at tag, face, height and bore as DN15 CPVC tube stubs flush at the envelope faces; the schedule z 600 rows (N1/N2/N7/N8) and N5 (z 800) predate the 500 box - drawn with their tops flush at the envelope top (stale datum, hold W12); atmospheric joints, no flange; rating column carried verbatim
- BOM `models/mfg/GROWBED_B/bom.csv` (generated from the model: qty, material, mass, make-or-buy; liner, cloth and media are the buy rows); `fasteners.csv` completed (base anchors 8.8 CS per the grade rule, liner battens A4-70 polymer supplier rule); WORK_ORDER rewritten to the W1-W12 items with holds named; no builder writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/GROWBED_B/growbed_b.py`
- `models/mfg/GROWBED_B/export/growbed_b.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-FARM; route-class hold named in WORK_ORDER W12.
