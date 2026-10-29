# Rewrite batch 22: metal-forming tool design set from the graph

Date: 2026-10-29

Owner decision of 2026-10-29: the die schedule of the wire drawer, the gauge and width of the cold mill and the batch rate of the atomiser are set now. They are derived from the graph throughputs through the sizing code and its drivers, not typed in, and the assumptions are registered as A-M-416.

## What changed

- `docs-authority/_mfg_tools.py` now designs the atomiser and the cold mill (AQS-MFG-010 revision E). The atomiser batch is the daily powder feed in as few heats as the melt charge allows. The pour rate follows from the flow through the melt nozzle, and the argon for a pour is held in a receiver that the compressor recharges between heats. The cold mill rolls a cast slab whose width follows from the slab mass, at constant width, in passes of a set reduction. The fixed pour time driver `atom_batch_min` is withdrawn.
- `docs-authority/_mfg_equipment.py` adds Section 7 to METAL_FORMING_EQUIPMENT (revision F): the die schedule, read from the wire families of AQS-INV-007, the gauge after each pass and the roll face of the cold mill, and the batch, pour, argon and receiver of the atomiser. The regenerator stage `doc_mfg_equipment` now runs after `doc_wire_specs`, which it reads.
- Nine drivers were added in `flow_graph/param/drivers.json` with register A-M-416.
- The owner question on the forming tool design is closed in `REWRITE_TODO.md`.

## Effect on the plant values

Table 1. Values before and after this batch

| Value | Before | After |
| --- | --- | --- |
| Atomiser nameplate | 5.5 kW | 0.5 kW |
| Atomiser average load (`GAS_ATOMIZER.continuous_kw`) | 0.0781 kW | 0.0836 kW |
| Tool list connected load (AQS-MFG-010) | 42.8 kW | 37.8 kW |
| Tool list coincident peak, which frames MCC-1 | 24.5 kW | 19.5 kW |
| Plant bus demand (`ZNBR2.continuous_kw`) | 216.2717 kW | 216.2817 kW |
| PV average output (`PV_ARRAY.continuous_kw`) | 350.0995 kW | 350.105 kW |
| PV installed nameplate | 2,999 kWp | 2,999 kWp |
| Storage energy | 3,028 kWh | 3,028 kWh |

The atomiser nameplate falls because the compressor now recharges the receiver over the hours between heats instead of running at the pour rate. Its energy rises because the receiver is charged above the nozzle supply pressure. The PV value pinned in `flow_graph/param/test_system_tree.py` follows the bus demand. The array, the storage and the inverters do not change at their stated precision.
