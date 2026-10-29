# Rewrite batch 14: the rectifier trim heaters in the plant bus demand

Date: 2026-10-29

## Decision

The rectifier feeds four electric trim heaters: IA-TRIM-HX5 (15.88 kW), IA-TRIM-HX6 (4.16 kW), IA-Q4A-TRIM (1.61 kW) and IA-Q4B-TRIM (1.61 kW), 23.26 kW in all at the rated values on their graph edges. Before this change, no feeder of the rectifier and no term of the plant bus demand included them. By the owner's standing rule that every unit is sized for its edge case from actual need, they are now counted at rated load. The assumption is recorded as A-M-415.

## Source change

- `flow_graph/param/sizing/power.py` gains `rectifier_trims(g)`, which finds the heaters from the graph: every present edge out of `RECTIFIER` with a kW rate that is neither a direct-current channel to an electrowinning cell nor a loss of the rectifier (`IA-RECT-*`). No value is typed in.
- `docs-authority/_power_sizing.py` adds that sum to both the bounding and the reference case of the plant bus demand.
- `docs-authority/_one_line.py` adds a RECT-TRIM feeder sized from the same sum, in the same way as the RECT-EW feeder.
- `flow_graph/param/ess_tf.py` now rates the bus section for the plant bus demand that the power sizing writes (`mvs.electrical.need_kw`). It used to sum the inverter feed edges, which miss the loads with no feed edge (RECT-EW and the trim heaters), and so rated the section for 150.8 kW against a bus demand of 179.7 kW.
- `docs-authority/_load_list.py` and `docs-authority/_power_sizing_doc.py` reconcile the new term, use the shared helper and describe three rectifier feeders.
- `flow_graph/param/test_system_tree.py`: the pinned PV average follows the new value.

## Result

The extension hall that roofs the array grows with the array, and its heating, cooling, ventilation and lighting load grows with it. The plant bus demand therefore rises by more than the heater load.

Table 1. Values before and after

| Quantity | Before | After |
| --- | --- | --- |
| Plant bus demand, bounding (`mvs.electrical.need_kw`) | 179.72 kW | 216.27 kW |
| Plant bus demand, reference | 146.59 kW | 183.14 kW |
| Trim heaters at rated load | not counted | 23.26 kW |
| Extension hall load (`EXT_HALL.continuous_kw`) | 68.28 kW | 81.57 kW |
| Extension hall roof, bays | 29 × 23 | 38 × 21 |
| Extension hall footprint | 23580 m² | 28296 m² |
| Array nameplate (`PV_ARRAY.params.nameplate_kw`) | 2492 kWp | 2999 kWp |
| Roof capacity for the array | 2506.5 kWp | 2999.9 kWp |
| PV modules | 4984 | 5998 |
| PV average to the graph (`IA-PV-01`) | 336.81 kW | 350.10 kW |
| Storage (`ZNBR2`) | 817 kW, 2517 kWh | 984 kW, 3028 kWh |
| Inverters (`SOL_ARK_60K`) | 35 × 60 kW | 42 × 60 kW |
| Inverters per section | 9, 9, 9, 8 | 11, 11, 10, 10 |
| Section 4 breaker and transformer | 800 A, 500 kVA | 1000 A, 750 kVA |
| Bus section rating basis | 150.8 kW, 201.6 A | 216.3 kW, 289.0 A |
| Bus section rating | 300 A | 400 A |
| ZNBR2 purge (S69, S69B) | 26.58 m³/h | 31.99 m³/h |
| Operating mass in the hull design | 46442 t | 46579.5 t |

The rating of 400 A is the next NEC 240.6 rating above 125 % of 289.0 A at 480 V and a power factor of 0.9. The roof still holds the array. The larger heat pump compressors of the extension hall move into a new motor family, MF-28, and a new wire family, WF-30, follows.

## Changed outputs

The regeneration commit changes these outputs:

- Graph and views: `flow_graph/plant_flow_graph.json`, `flow_graph/placement_seed.json`, the PFD, MFD and electrical, storage and thermal EFD views in `flow_graph/views/`, and `design_tool/aqs_design_tool/data/candidate_mvs.json`.
- Derived registers: `flow_graph/derived/LOOP_CLOSURE.md`, `MASS_FLOW_DERIVED.md`, `STREAM_REGISTER_DERIVED.md` and `_regen_receipt.json`; `flow_graph/inventory/motor_family_ids.json` and `wire_family_ids.json`.
- Electrical pages: LOAD_LIST (Rev G), POWER_SIZING (Rev J), ONE_LINE (Rev F), PROTECTION, CABLE_SCHEDULE, COLLECTION_BUS, SITE_POWER, BUSBAR.json, LOAD_LIST.json, ONE_LINE.json and `docs-authority/plc/PLC-ELEC.st`.
- Unit pages: the duty and sizing pages of EXT_HALL, PV_ARRAY, ZNBR2 and ZNBR2_BR2_REGEN, with `_generated.json` and `_origins.json`, and `models/units/EXT_HALL/bom.csv`.
- Inventory: the motor, wire, other-item, bill-of-materials, commissioning, end-of-life, HVAC-room, instrument and self-copy files in `docs-authority/inventory/`, family sheets MF-07 and the new MF-28, and the new drawings `docs-authority/drawings/motor_fa/MF-28.svg` and `docs-authority/drawings/wire/WF-30.svg`.
- Other pages that print these values: ASSUMPTIONS_REGISTER, BLOCK_FAMILY_PLANS, BOUGHT_SPECS, CONTROL_ARCH, CONTROL_SOFTWARE, DESIGN_CHECK, DOC_REGISTER, DRAWING_REGISTER, EOL_RETURN, HALL_EGRESS, HULL_DESIGN, HVAC, ISO_ROUTES.json, MODEL_WORKBOOK.xlsx, MOTOR_FIRST_ARTICLE, PARAMETRIC_MODEL, PERF_TEST, PLANT_BOM, SELF_COPY_BOM, SITE_UNITS, SPARES, STARTUP, TASK_PLAN, TEST_PLAN, WIRE_SPECS, DERIVED_REVISIONS, `media/_generated.json` and `docs-authority/sizing/REACTOR_DESIGN._generated.json`.
- The P&ID sheets in `docs-authority/pid/`, whose only change is the graph SHA-256 in the title block.

## Open items

The questions on the trim heaters and on the bus section rating are closed in `REWRITE_TODO.md`. The question on the sanitation train load against the BLACK_DIGEST feed stays open for the owner. The backup generator rating is still held.
