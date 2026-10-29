# Ground-source heat pump loop and backup generator

Document number: AQS-PWR-002  
Former number: AQS-PWR-001 (renumbered on 2026-10-15 to clear a duplicate)  
Revision: C  
Date: 2026-10-29  
Equipment lists: AQS-EQP-GEO-001 (`GEOTHERMAL_EQUIPMENT.md`), AQS-EQP-GEN-001 (`BACKUP_GEN_EQUIPMENT.md`)

| Rev | Description | Date |
|---|---|---|
| A | First issue: ground heat exchanger, heat pump and hydrogen generator on the inverter generator port | 2026-09-27 |
| B | Relationship to the fuel cell (AQS-FC-001) recorded | 2026-09-28 |
| C | Rewritten to the style guide and to the plant graph: the generator is dual-fuel as the graph states, the organic Rankine cycle unit is a sized standby option, and units and streams that are not in the graph are removed | 2026-10-29 |

## 1. Purpose and scope

This page states how the plant uses ground heat and how it keeps critical loads running when the solar array, the flow battery and the grid are all unavailable. It covers four units in the plant graph: the ground heat exchanger `GEO_GHEX`, the heat pump `GEO_HP`, the organic Rankine cycle (ORC) generator `GEO_ORC` and the standby generator `BACKUP_GEN`. It gives the design decisions, their reasons and the streams that connect the units.

The plant graph (`flow_graph/plant_flow_graph.json`) holds every rate, rating and size. This page names where each value is held and does not repeat it. The fuel cell is described in AQS-FC-001 (`FUEL_CELL.md`) and the storage and generation sizing in AQS-ELEC-007 (`POWER_SIZING.md`).

## 2. Summary

- The ground loop is a closed vertical bore field. Its fluid stays in its own circuit and never enters a process or potable water header.
- The heat pump lifts ground heat into the low-grade heat bus `Q4_BUS` only when that bus is short of heat. Two heat pumps are installed, each able to carry the full duty (2 × 100 %).
- The ORC generator is an installed standby unit sized for a study case. The present ground resource supports no useful electrical output, and no output is claimed until a site survey supports one.
- The backup generator is dual-fuel. It burns hydrogen from the plant store first and the plant's own C5 to C10 hydrocarbon cut when hydrogen is short. Both fuels are made by the plant, so an outage does not depend on a fuel delivery.
- The generator rating comes from the driver `backup_gen_rated_kW` in `flow_graph/param/drivers.json`: 125 % of the critical load list, rounded up in 5 kW steps, on the standby basis of NFPA 110-2025.

## 3. Ground loop and heat pump

### 3.1 Ground heat exchanger

`GEO_GHEX` is a closed-loop vertical bore field filled with a propylene glycol solution. A closed loop was chosen because an open well would bring groundwater or brine to the surface, and that water would then need treatment before it could touch any plant header. The bore count, bore depth, spacing, loop pipe size, loop flow and the heat the field can deliver are in `params.design` of the `GEO_GHEX` node. The ground conductivity and source temperature behind them are study values until a site survey replaces them (`survey_status` on the node).

**CAUTION**

Do not connect the ground loop to the ultrapure water header, the catch tank or the potable water system. The loop fluid contains glycol and is a dedicated closed circuit (stream S43).

### 3.2 Heat pump

`GEO_HP` is a water-source heat pump between the ground loop and `Q4_BUS`. It runs only when the heat recovered from the process does not cover the low-grade heat demand; otherwise it is idle and the ground loop carries no heat. The dispatch rule is stated in AQS-DUTY-010 (`EDGE_RATING_DUTY.md`). The lift, the coefficient of performance, the electrical draw and the heat exchanger areas are in `params.design` of the `GEO_HP` node. The source-loop circulator is sized in AQS-DUTY-076 and sits on `GEO_HP_CLOSED_LOOP`.

### 3.3 Organic Rankine cycle generator

`GEO_ORC` is a binary ORC unit with a scroll expander. It is kept in the graph as an installed standby option so that the design is ready if a site offers hotter ground. At the study site the ground temperature is too low for useful output, so the study endpoint is 0 kW of electricity. The machine geometry in `params.design` is sized for the dry-cooler heat case of A-M-244 so that the standby unit is a real machine (A-M-285). Its connection to the inverter, stream S48, carries no rate. The node lists the surveys that must be done before an output is claimed: ground conductivity, source temperature and the heat left over after the `Q4_BUS` demand.

## 4. Backup generator

### 4.1 Role

`BACKUP_GEN` feeds the generator port of the hybrid inverter `SOL_ARK_60K` (stream S47). It runs when the solar array, the zinc-bromine flow battery `ZNBR2` and the grid cannot carry the critical loads, and once a month for the exercise that NFPA 110-2025 section 8.4.2 requires. It does not feed the electrowinning rectifiers directly; they stay on the plant main alternating-current supply after the transfer switch.

### 4.2 Fuels

The generator keeps two fuels, each made by the plant, so that losing one does not stop the generator. Table 4.1 gives the order in which they are used. The table is taken from `params.fuel_selection` of the `BACKUP_GEN` node, which `flow_graph/param/backup_fuel.py` writes.

Table 4.1. Backup generator fuels in order of use

| Order | Fuel | Source unit | Stream | When it is used |
|---|---|---|---|---|
| 1 | Hydrogen | `CRYO_H2` | S45 | Whenever the hydrogen store holds hydrogen, including the monthly exercise |
| 2 | C5 to C10 hydrocarbon cut | `PROD_C5_C10` | CUT-1-OUT | When hydrogen is short. The product tank keeps a reserve that is not shipped. |
| 3 | Methanol or digester gas | `MEOH_TANK` or the sanitation digester | none | Not piped. These are candidates only if both fuels above run short. |

The reserve of the C5 to C10 cut covers the critical load list for the autonomy period in the driver `crit_autonomy_d`, on the assumption that the hydrogen store is empty when the outage starts. The reserve mass and its basis are in the same graph entry. Combustion air arrives as oxygen (IA-GEN-O2) and nitrogen diluent (IA-GEN-AIR) from the plant headers. The exhaust, stream S46, goes to the nitrogen oxide scrubber `NOX_SCRUB` and is never sent to a habitation air system.

### 4.3 Rating

The generator is a standby machine. Its rating is set by the driver `backup_gen_rated_kW` and written to the graph by `flow_graph/param/write_graph.py`; AQS-ELEC-007 and AQS-RED-001 (`RED_AUDIT.md`) give the critical load list it must carry. Its daily average draw in the graph is the exercise energy only, because the generator does not run on a normal day.

**WARNING**

Hydrogen fuel equipment outdoors is in a classified area. Do not connect the process hydrogen capture header to the generator fuel line without a flame arrester and an isolation valve that separate it from the electrowinning cathode gas.

## 5. Streams

Table 5.1 lists the streams that connect these units. The stream register AQS-STR-001 (`STREAM_REGISTER.md`) gives their rates.

Table 5.1. Streams of the ground loop and the backup generator

| Stream | From | To | Carries |
|---|---|---|---|
| S43 | `GEO_GHEX` | `GEO_HP_CLOSED_LOOP` | Ground loop heat |
| S44 | `GEO_HP` | `Q4_BUS` | Low-grade heat lifted by the heat pump |
| S45 | `CRYO_H2` | `BACKUP_GEN` | Hydrogen fuel |
| CUT-1-OUT | `PROD_C5_C10` | `BACKUP_GEN` | C5 to C10 hydrocarbon fuel |
| IA-GEN-O2 | `HDR_O2` | `BACKUP_GEN` | Combustion oxygen |
| IA-GEN-AIR | `HDR_N2` | `BACKUP_GEN` | Nitrogen diluent |
| S46 | `BACKUP_GEN` | `NOX_SCRUB` | Exhaust |
| S47 | `BACKUP_GEN` | `SOL_ARK_60K` | Electricity to the generator port |
| S48 | `GEO_ORC` | `SOL_ARK_60K` | Electricity from the ORC unit; no rate claimed |

## 6. Relationship to the fuel cell

The fuel cell `FUEL_CELL` (AQS-FC-001) and the backup generator are two different technologies that can each carry critical load, which is the diverse backup that AGENTS.md asks for. They do not replace each other. The fuel cell takes hydrogen (S49) and oxygen (S50) from the plant stores and delivers direct current to `SOL_ARK_60K` (S51); its heat goes to `Q4_BUS` (S53). The generator delivers alternating current to the generator port of the same inverter. The hydrogen store is shared, so `CRYO_H2` is sized for the generator, the fuel cell and the relief contingency together (AQS-EQP-CRY-001, `CRYO_EQUIPMENT.md`).

## 7. Placement

The units stand in the power yard at level 0. `models/freecad/electrical_yard.py` places them and sets the service clearances around the generator and the heat pump pad. The generator envelope is `size_mm` on the `BACKUP_GEN` node. The bore field is outside the building plate; the model shows only its header at the yard edge.

## 8. Drawings

The process flow diagrams AQS-PFD-GEO-001 and AQS-PFD-GEN-001 are drawn from the graph by `flow_graph/exporters/matplotlib/geothermal_pfd.py` and `flow_graph/exporters/matplotlib/backup_gen_pfd.py`. The images are not committed; run the scripts to produce them.

## 9. References

1. NFPA 110-2025, *Standard for Emergency and Standby Power Systems*, section 8.4.2 (monthly exercise).
2. AQS-DUTY-010, `docs-authority/EDGE_RATING_DUTY.md`: heat pump and generator dispatch.
3. AQS-ELEC-007, `docs-authority/POWER_SIZING.md`: storage and generation sizing.
4. AQS-RED-001, `docs-authority/RED_AUDIT.md`: redundancy audit.
5. AQS-FC-001, `docs-authority/FUEL_CELL.md`: fuel cell.
