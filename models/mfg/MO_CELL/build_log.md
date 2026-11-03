# Build log - MO_CELL

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-CELL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/MO_CELL.md`; envelope per `models/mfg/MO_CELL/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/MO_CELL/mo_cell.py`

## Checks

- Build bbox 800 x 800 x 1600 mm against the 800 x 800 x 1600 mm envelope: filled exactly, inside (tracker check green). The flush-hardware rebuild moves the N4 tap group (+X), the N5/N6 feed chutes (-X), the N2 liquor stub (-Y) and the N1/N3/N7 stubs (+Y) to the envelope faces, so the A-core 2 overshoot the §7 row carried (879.5 x 851.0 x 1600.0) is cleared, not resized; `cad/stl/MO_CELL.stl` replaced from the in-envelope build solid (scope in `check.json` `cad_stl_scope`)
- A-CELL: 3 anodes D50 x 1064 at 250 mm immersion; cathode plates corrected to the duty section 2 design row `cathodes 3` (the Oct-31 build drew two plates against the design row and the BOM qty of 3); plate 110 x 12 x 300 study (hold W12); pitch 264 mm (AL_POT interleave idiom); drawn anode j 0.0021 A/cm2 reported (A-M-282 class), no rate claimed. Bus rails 2 x 5 x 5 mm = the node busbar class 25 mm2 (POWER.md/AQS-BUS-001 state no row for this unit; the node design row is the basis)
- Nozzles: all 9 rows of `docs-authority/nozzles/MO_CELL.csv` present at tag, face, height and bore, flush at the envelope faces; atmospheric joints, no flange (no process pressure stated); schedule rating column carried verbatim; the riser vent row corrected to its schedule tag N9 in the BOM
- Internals: node row `none`; electrodes, hood and riser drawn as the machine per the duty sheet; bath inventory drawn as process-inventory solids, not BOM parts; the carbochlorination loop hardware is the unit task 12 work order (hold W12)
- BOM `models/mfg/MO_CELL/bom.csv` (generated from the model: qty, material, mass, make-or-buy); the 650 C bath temperature wording corrected where the CA_POT template carried 700 C; fasteners 8.8 CS per the W5 grade rule; WORK_ORDER rewritten to the W1-W12 items with holds named (the Oct-31 builder wrote a work order titled CA_POT into this folder - the hand-authored W1-W12 item replaces it and the builder no longer writes the work order)
- Drawing set regenerated from the rebuilt solids (8 sheets: ga_front/ga_side/nozzle_orient/sh01/hd01/el01/aux01/iso01; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/MO_CELL/draw_mo_cell.py`
- `models/mfg/MO_CELL/mo_cell.py`
- `models/mfg/MO_CELL/export/mo_cell.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-CELL; the machine-design detail (weld procedures, lining installation) follows the unit WORK_ORDER; holds named in WORK_ORDER W12.
