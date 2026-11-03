# Build log - CA_POT

Date: 2026-11-03. Authority: AQS-PLAN-006 section 5 (acceptance) A-core + A-CELL; MFG_MODEL_PLAN (AQS-PLAN-006).
Graph: `flow_graph/plant_flow_graph.json` (duty sheet `docs-authority/duties/CA_POT.md`; envelope per `models/mfg/CA_POT/params.json`).

## Tool versions

- CadQuery 2.8.0 (CADQUERY_PYTHON)
- Python 3.13.7; build run headless via `python3 models/mfg/CA_POT/ca_pot.py`

## Checks

- Build bbox 800 x 800 x 1600 mm against the 800 x 800 x 1600 mm envelope: filled exactly, inside (tracker check green). The flush-hardware rebuild moves the N1 tap group (+X), N2 brine chute (-X) and N3 Cl2 stub (+Y) to the envelope faces, so the A-core 2 overshoot the §7 row carried (879.5 x 805.0 x 1600.0) is cleared, not resized; `cad/stl/CA_POT.stl` replaced from the in-envelope build solid (scope in `check.json` `cad_stl_scope`)
- A-CELL: 3 anodes D50 x 1064 at 250 mm immersion; cathode plates corrected to the duty section 2 design row `cathodes 3` (the Oct-31 build drew one plate against a params count of 2 and a BOM qty of 2); plate 110 x 12 x 300 study (hold W12); pitch 264 mm (AL_POT interleave idiom); drawn anode j 0.0029 A/cm2 reported (A-M-282 class), no rate claimed. Bus rails 2 x 5 x 5 mm = the node busbar class 25 mm2 (POWER.md/AQS-BUS-001 state no row for this unit; the node design row is the basis)
- Nozzles: all 5 rows of `docs-authority/nozzles/CA_POT.csv` present at tag, face, height and bore, flush at the envelope faces; atmospheric joints, no flange (no process pressure stated); schedule rating column carried verbatim
- Internals: node row `none`; electrodes, hood and riser drawn as the machine per the duty sheet; bath inventory (122 L) drawn as process-inventory solids, not BOM parts
- BOM `models/mfg/CA_POT/bom.csv` (generated from the model: qty, material, mass, make-or-buy); fasteners 8.8 CS per the W5 grade rule; WORK_ORDER rewritten to the W1-W12 items with holds named; the builder no longer writes the work order, so a rebuild never clobbers it
- Drawing set regenerated from the rebuilt solids (8 sheets: ga_front/ga_side/nozzle_orient/sh01/hd01/el01/aux01/iso01; title blocks per AQS-DWG-002, graph Rev AD)

## Sources

- `models/mfg/CA_POT/draw_ca_pot.py`
- `models/mfg/CA_POT/ca_pot.py`
- `models/mfg/CA_POT/export/ca_pot.step`

Status: accepted per AQS-PLAN-006 section 5 A-core + A-CELL; the machine-design detail (weld procedures, lining installation) follows the unit WORK_ORDER; holds named in WORK_ORDER W12.
