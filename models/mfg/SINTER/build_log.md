# Build log - SINTER

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core; route hold named; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/SINTER.md`; envelope per `models/mfg/SINTER/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/SINTER/sinter.py`

## Checks

- Build bbox 1000 x 1000 x 1500 mm against the 1000 x 1000 x 1500 mm envelope: filled exactly, inside (tracker check green). The Oct-31 envelope-only placeholder box (foundry.py standby placeholder, ~28 facets) is replaced by the real machine per the node design block - the installed-standby idiom (VAC_IND/RES_HEAT precedent): the standby_rated N+1 alternate of ROLL is drawn as the real machine, not a placeholder; `tracker --check SINTER` green; `cad/stl/SINTER.stl` replaced from the build
- Machine: water-cooled nickel-free steel jacket (double wall t4 with the 15 mm cooling-water annulus; the water circuit is loop hardware, hold W12), ceramic-fibre board between jacket and hot zone (study), 95 % alumina muffle OD 260 x 480 with lid on the alumina hearth (inert/vacuum chamber, buy consumable), graphite resistance elements OD 24 in wall and crown racks at the 1300 C design (buy consumable, 8 kW connected node design), charge door on -X, 8 kW controls cabinet as a purchased envelope on the +X bay per plan rule 6. The 0.5 kg design-case powder charge is a process-inventory solid, not a BOM part
- Route-class hold named: `furnace` has no AQS-PLAN-006 section 4 class; the furnace practice (RES_HEAT/COMB_HEAT idiom) is the named study route. Standby named in the WORK_ORDER header, the BOM rows and this log (A-M-282/A-M-283)
- Nozzles: all 3 rows of `docs-authority/nozzles/SINTER.csv` present at tag, face, height and bore, flush at the envelope faces; the solids row (N1 sintered stock) is drawn as an outlet chute, bore not calculated per W4; atmospheric joints, no flange; schedule rating column carried verbatim
- BOM `models/mfg/SINTER/bom.csv` (generated from the model: qty, material, mass, make-or-buy; the Oct-31 placeholder BOM carried no mass and no make-or-buy); fasteners per the W5 grade rule via the shared lib writer (8.8 CS anchors and studs); WORK_ORDER rewritten to the W1-W12 items with holds named; the builder does not write the work order
- Drawing set: new 7-sheet set (ga_front/ga_side/nozzle_orient/shell01/muffle01/aux01/iso01; title blocks per AQS-DWG-002, graph Rev AD); the stale Oct-31 3-sheet GA SVGs are superseded by it

## Sources

- `models/mfg/SINTER/draw_sinter.py`
- `models/mfg/SINTER/sinter.py`
- `models/mfg/SINTER/bom.csv`
- `models/mfg/SINTER/fasteners.csv`
- `models/mfg/SINTER/check.json`
- `models/mfg/SINTER/WORK_ORDER.md`
- build export `models/mfg/SINTER/export/sinter.step`

Status: accepted per AQS-PLAN-006 section 5 A-core; route-class hold named in WORK_ORDER W12.
