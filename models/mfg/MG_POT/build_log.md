# Build log - MG_POT

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-CELL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MG_POT.md`; envelope per `models/mfg/MG_POT/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/MG_POT/mg_pot.py`

## Checks

- Build bbox 800 x 800 x 1600 mm against the 800 x 800 x 1600 mm envelope: filled exactly, inside (tracker check green). The flush-hardware rebuild moves the N1 tap group (+X), the N5 reductant tap (-X), the N3/N4 launders (-Y) and the N2/N6 Cl2 stubs (+Y) to the envelope faces, so the A-core 2 overshoot the §7 row carried (889.5 x 850.0 x 1600.0) is cleared, not resized; `cad/stl/MG_POT.stl` replaced from the in-envelope build solid (scope in `check.json` `cad_stl_scope`)
- A-CELL: 4 anodes D50 x 1064 at 300 mm immersion; cathode plates corrected to the duty section 2 design row `cathodes 4` (the Oct-31 build drew three plates against a BOM qty of 4); plate 110 x 12 x 400 study (hold W12); pitch 176 mm (AL_POT interleave idiom); drawn anode j 0.0284 A/cm2 reported (A-M-282 class), no rate claimed. Bus rails 2 x 10 x 5 mm = the node busbar class 50 mm2 (POWER.md/AQS-BUS-001 state no row for this unit; the node design row is the basis)
- Nozzles: all 8 rows of `docs-authority/nozzles/MG_POT.csv` present at tag, face, height and bore, flush at the envelope faces; atmospheric joints, no flange (no process pressure stated); schedule rating column carried verbatim; the Oct-31 casing carried an unused -X pass from the CA_POT template - removed
- Internals: node row `none`; electrodes, hood and riser drawn as the machine per the duty sheet; bath inventory drawn as process-inventory solids, not BOM parts
- BOM `models/mfg/MG_POT/bom.csv` (generated from the model: qty, material, mass, make-or-buy); the Oct-31 BOM double-counted the N3/N4 inlet group (rows 12c and 14 both carried its mass) - row 14 removed; the drain row's schedule tag corrected to N7; fasteners 8.8 CS per the W5 grade rule; WORK_ORDER rewritten to the W1-W12 items with holds named (the Oct-31 builder wrote a work order titled CA_POT into this folder - the hand-authored W1-W12 item replaces it and the builder no longer writes the work order)
- Drawing set regenerated from the rebuilt solids (8 sheets: ga_front/ga_side/nozzle_orient/sh01/hd01/el01/aux01/iso01; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/MG_POT/draw_mg_pot.py`
- `models/mfg/MG_POT/mg_pot.py`
- `models/mfg/MG_POT/export/mg_pot.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-CELL; the machine-design detail (weld procedures, lining installation) follows the unit WORK_ORDER; holds named in WORK_ORDER W12.
