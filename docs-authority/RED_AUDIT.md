# Redundancy audit, energy and life support

Document number: AQS-RED-001
Revision: C
Date: 2026-10-25
Authority: AQS-PLAN-007 task X-RED-01; the redundancy rule in `AGENTS.md`, section "Redundancy". Graph Rev BH. Study.

| Rev | Description | Date |
|---|---|---|
| A | First issue | Not recorded |
| B | Water tower, EXPANDER backup, fire water N+1 and receiver halves added | 2026-10-16 |
| C | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No row changed. | 2026-10-25 |

## 1. Purpose and scope

The plant supports a crew, so every system that supplies energy or keeps the crew alive must keep working when one of its parts fails. The project rule is that each such system has either a spare unit of the same kind (N+1) or a second source of a different kind (a diverse backup), sized by calculation for a defined outage of the primary.

This audit lists each energy and life-support system with its primary source, the backups present in the graph and the cover they give. It names each single point of failure (SPOF), meaning a part whose failure alone stops the system, and the task that closed it. A backup that looks surplus to the daily balance is intentional and is not removed on need alone.

## 2. Audit

Table 2.1 gives the result for each system. "Action" names the task (X-RED, X-SAF) or open question (Q) that closed the single point of failure.

Table 2.1. Redundancy of energy and life-support systems

| System | Primary | Backups on the graph | Calculated cover | SPOF found | Action |
|---|---|---|---|---|---|
| Electric power, night | ZNBR2 4059 kWh | HYDRO_SET (A-M-145), FUEL_CELL + 19 kg H2 bank, BACKUP_GEN standby 40 kW (NFPA 110) | hydro 14 h x 14.31 kW critical = 200.3 kWh (NFPA 111 Class X); H2 bank 2 d fuel-cell autonomy (AQS-ELEC-007) | closed: hydro sited as the water tower (Q-009, AQS-BLD-014): 35.73 m head, 2,707 m3 live in 6 cells on 3 levels, one cell out leaves 83 % | X-RED-02 done |
| Electric power, conversion | 56 x 60 kW inverters | inverter count above the 290 kW load | N+50 by count | closed: main-tie-main bus, MCC-1A/1B, 2 x T-1, critical ATS (A-M-152) | X-RED-03 done |
| O2 for the crew | H2O_ELYZ (11.1 kg/d H2) | grow-bed and crop O2, cold-box excess O2, CRYO_O2 bank 150.8 kg | bank / crew draw 3.04 kg/d = 49.6 d, but the bank is also the fuel-cell oxidant | closed: separate crew bank 6.08 kg (A-M-146) | X-RED-04 done |
| Water | ROOF_TANK (2 d hold-up from need, 1.38 m3), AHU condensate return, VCD_TRAIN | water tower 2,707 m3 live (clean water; drawing it costs stored energy) and the CATCH_TANK lower reservoir | 2,707 m3 / 131.5 kg/d potable draw = about 20,000 d | closed: 2 x 100 % stills, inventory as diverse backup (A-M-149) | X-RED-05 done |
| CO2 removal (crew air) | HAB sorbent bed (S90, 4.02 kg/d) | crop uptake 2.8 kg/d on the farm air (partial) | crops cover 70 % of crew CO2 only if the air is shared | closed: second full 2-bed 5A assembly, 40 kg/bed (A-M-147) | X-RED-06 done |
| Thermal | HEAT_SINK, GEO_HP 2 kW | heat ladder stores Q1-Q4 | not calculated | closed: 3 x 50 % sink modules on 146.5 kW, 2 x 100 % heat pumps (A-M-150) | X-RED-07 done |
| Food | farm units (bed, veg, fruit, peanut, stock, fish, mushrooms) | diversity of crops and stock | no stored reserve | closed: 80 d dry reserve 13.5 kg DM in HAB_GALLEY (A-M-148) | X-RED-08 done |
| Sanitation | COMPOST_TOILET | none | - | closed: 2 x 100 % toilets (A-M-149) | X-RED-09 done |
| Cold-box refrigeration (CO2 condenser) | condenser chiller COP 2.5 | EXPANDER N2 reverse-Brayton loop, standby | 0.082 kW cold each, 100 % (A-M-186) | closed: owner kept the EXPANDER (Q-010) | Q-010 closed |
| Fire water | gravity reserve 451 m3 in the water tower (dead storage) | NFPA 20 fire pump from CATCH_TANK | each 100 % of the L0 EH1 demand (AQS-SAF-005) | closed | X-SAF-05 done |
| Gas receivers H2 / O2 / CO2 | tube bank half A | half B, own relief valve | 50 % each, a leaking half is isolated | closed (receivers.py, AQS-SAF-005) | - |
