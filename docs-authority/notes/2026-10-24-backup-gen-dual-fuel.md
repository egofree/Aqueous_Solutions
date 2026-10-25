# Standby generator fuel: hydrogen first, C5-C10 cut as fallback

Date: 2026-10-24. Units: BACKUP_GEN, CRYO_H2, PROD_C5_C10.

## Decision

The standby generator (BACKUP_GEN) is a dual-fuel engine. It burns dried process hydrogen from CRYO_H2 (stream S45) whenever the hydrogen store holds gas, including the monthly exercise that NFPA 110 requires. The C5-C10 hydrocarbon cut from PROD_C5_C10 (stream CUT-1-OUT) is the fallback fuel, and methanol or digester gas are the third choice and are not piped. The reason is the redundancy principle: the plant's standby power should not depend on one fuel, and hydrogen is made on site every day while the liquid cut can be stored for long periods.

## Sizing of the fallback store

The bounding case is an outage that starts when the hydrogen store is empty. The fallback reserve held in PROD_C5_C10 is the critical load list times 24 h times the `crit_autonomy_d` driver, divided by the engine efficiency and the lower heating value of the cut. The reserve is held and not shipped. The graph records the selection order in the BACKUP_GEN `fuel_selection` parameter and the reserve in the PROD_C5_C10 `genset_reserve_kg` parameter.

## Code and inputs

- `flow_graph/param/backup_fuel.py` holds the critical load list, the fuel plan and the selection order.
- `flow_graph/param/o2_close.py` writes S45, CUT-1-OUT and the oxygen feed IA-GEN-O2 from that plan.
- The engine efficiency on hydrogen and the hydrogen lower heating value are drivers under `ELEC.generation-train.BACKUP_GEN`, with basis A-M-383.
- Because hydrogen needs less oxygen than the liquid cut, the oxygen plant draws slightly less power and the solved PV average falls with it; `flow_graph/param/test_system_tree.py` records the new value.

## Retired feeds checked against the redundancy principle

No feed was removed. The retired edges in the graph were checked:

- HL-HX8-Q3-A and HL-HX8-Q3-B carried the exchanger HX8's electrowinning heat to the Q3 stores. The Q3 stores run at a higher temperature than the electrolyte, so this heat cannot flow into them. HX8 still delivers its heat to both Q4 stores (HL-HX8-Q4-A and HL-HX8-Q4-B), so the retirement removes no backup. The HX8 unit note still says "to Q3" and should be corrected.
- SF-LITHO_STUB was retired with the LITHO_STUB unit, whose duty the real lithography tools now carry with their own feeds.
- S86, S87 and S88 were retired at an earlier mass-flow revision and are present again in the graph.
