# Rewrite batch 23: silicon feed to the wafer fab

Date: 2026-10-29

Owner decision of 2026-10-29: WAFER_FAB gets a silicon feed so that the wafers it sends to lithography have silicon behind them and the fab balance closes. The assumptions are registered as A-M-417.

## Design

The new module `flow_graph/param/fab_silicon.py` sizes the feed from the wafer need, and `flow_graph/param/balance.py` applies it as a transfer function before the reconciliation.

- Each 150 mm wafer takes its own thickness and the saw kerf along the ingot, and a share of the charge is lost as crown, tail, diameter grind and pot scrap.
- The charge of a pull is the larger of the need of one tool campaign and the least melt the crucible can hold. The least melt governs, so one pull serves many weeks of starts and the wafers are stored until started. The silicon feed per day follows the starts, not the charge.
- The plant makes only metallurgical-grade silicon, in SI_REDUCE, which is far below the purity a crystal charge needs. The charge is therefore imported as polysilicon through the dock into METAL_STORE, which holds the larger of one charge and one resupply interval. This meets the elimination rule of the localisation plan (AQS-PLAN-011): an import path with its resupply interval and holding. The fab is not an energy or life-support function, so the import path alone keeps it. An in-house refining route from SI_REDUCE, the backup of a different technology, is a task in AQS-PLAN-007.
- The wafers run from the fab to the three lithography units and back to the fab, then to the dock. Kerf and crop leave with the spent slurry to the leach.
- The CZ energy in `flow_graph/param/write_graph.py` now uses the derived charge and pull interval. Revision AC divided the energy of a pull, in kWh, by the campaign days and booked the result as kW, which overstated the load by a factor of 24; the energy is now divided by the days between pulls and by 24 h. The hot zone is now carried at a heater duty over the hours under gas, in place of a 4 h hold at 0.3 kW. The heater duty is a class value until a heat-loss model replaces it (task in AQS-PLAN-007).

Table 1. Streams added or given flow

| Stream | From | To | Basis |
| --- | --- | --- | --- |
| IA-SI-IMPORT | NORTH_DOCK | METAL_STORE | silicon feed per day |
| STOCK_TO_FAB | METAL_STORE | WAFER_FAB | silicon feed per day; this route carried no flow before |
| IA-FAB-WAFER | WAFER_FAB | LITHO_COAT | wafer starts times wafer mass |
| IA-LITHO-WAFER-A | LITHO_COAT | LITHO_ALIGN | the same wafers |
| IA-LITHO-WAFER-B | LITHO_ALIGN | LITHO_DEV | the same wafers |
| IA-LITHO-WAFER-RET | LITHO_DEV | WAFER_FAB | the same wafers back to the tool row |
| IA-FAB-PRODUCT | WAFER_FAB | NORTH_DOCK | finished wafers |
| IA-FAB-KERF | WAFER_FAB | LEACH_CSTR_1 | silicon feed less wafers |

## Effect on the plant values

Table 2. Values before and after this batch

| Value | Before | After |
| --- | --- | --- |
| WAFER_FAB average load | 0.4417 kW | 0.4069 kW |
| Plant bus demand (`ZNBR2.continuous_kw`) | 216.2817 kW | 216.2517 kW |
| PV average output (`PV_ARRAY.continuous_kw`) | 350.105 kW | 350.0702 kW |
| PV installed nameplate | 2,999 kWp | 2,998 kWp |
| Storage energy | 3,028 kWh | 3,028 kWh |

The PV value pinned in `flow_graph/param/test_system_tree.py` follows the bus demand. The owner question on the silicon charge is closed in `REWRITE_TODO.md`.
