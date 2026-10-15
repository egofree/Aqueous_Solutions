# Redundancy audit, energy and life support

Document number: AQS-RED-001
Revision: A
Date: 2026-10-15
Authority: AQS-PLAN-007 X-RED-01; owner redundancy rule (AGENTS.md, Mike Matthews 2026-10-15). Graph Rev BH. Study.

Each system is listed with its primary source, the backups now on the graph and the single points of failure (SPOF). A SPOF gets a follow-up task that sizes an N+1 or diverse backup by calculation.

| System | Primary | Backups on the graph | Calculated cover | SPOF found | Action |
|---|---|---|---|---|---|
| Electric power, night | ZNBR2 4059 kWh | HYDRO_SET (A-M-145), FUEL_CELL + 19 kg H2 bank, BACKUP_GEN standby 40 kW (NFPA 110) | hydro 14 h x 32 kW critical (NFPA 111 Class X); H2 bank 2 d fuel-cell autonomy (AQS-ELEC-007) | none at the store level; hydro reservoir unsited | X-RED-02 (Q-009) |
| Electric power, conversion | 56 x 60 kW inverters | inverter count above the 290 kW load | N+50 by count | single collection bus and main panel not yet audited | X-RED-03 |
| O2 for the crew | H2O_ELYZ (11.1 kg/d H2) | grow-bed and crop O2, cold-box excess O2, CRYO_O2 bank 150.8 kg | bank / crew draw 3.04 kg/d = 49.6 d, but the bank is also the fuel-cell oxidant | closed: separate crew bank 6.08 kg (A-M-146) | X-RED-04 done |
| Water | ROOF_TANK 200 m3, AHU condensate return, VCD_TRAIN | CATCH_TANK inventory, potable make-up | 200 m3 / 131.5 kg/d potable draw = 1520 d | closed: 2 x 100 % stills, inventory as diverse backup (A-M-149) | X-RED-05 done |
| CO2 removal (crew air) | HAB sorbent bed (S90, 4.02 kg/d) | crop uptake 2.8 kg/d on the farm air (partial) | crops cover 70 % of crew CO2 only if the air is shared | closed: second full 2-bed 5A assembly, 40 kg/bed (A-M-147) | X-RED-06 done |
| Thermal | HEAT_SINK, GEO_HP 2 kW | heat ladder stores Q1-Q4 | not calculated | single heat pump and single heat sink | X-RED-07 |
| Food | farm units (bed, veg, fruit, peanut, stock, fish, mushrooms) | diversity of crops and stock | no stored reserve | closed: 80 d dry reserve 13.5 kg DM in HAB_GALLEY (A-M-148) | X-RED-08 done |
| Sanitation | COMPOST_TOILET | none | - | closed: 2 x 100 % toilets (A-M-149) | X-RED-09 done |
