# PEM fuel cell on plant hydrogen and oxygen

Document number: AQS-FC-001
Revision: C
Date: 2026-10-29
Equipment list: AQS-EQP-FC-001 (`FUEL_CELL_EQUIPMENT.md`)
Authority: plant graph Rev AC; AQS-REQ-KW-001 (`CONTINUOUS_KW_REQUIREMENTS.md`); AQS-PWR-002 (`GEOTHERMAL_BACKUP.md`); AQS-MeOH-001 (`MEOH_TRAIN.md`). Study. Not a PE stamp.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue: a PEM fuel cell on the battery side of the inverters, with its heat to the Q4 header, kept separate from the backup generator | 2026-09-28 |
| B | Methanol fuel cell added as a second path alongside the PEM fuel cell; continuous power requirements stated | 2026-10-01 |
| C | Rewritten against graph Rev AC: streams, rates and destinations taken from the graph; the electrolyser that now feeds the hydrogen store described; references to files outside the repository removed | 2026-10-29 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

This page describes the proton exchange membrane (PEM) fuel cell `FUEL_CELL`. The fuel cell turns hydrogen and oxygen from the plant stores into direct-current electricity, low-grade heat and water. The page states its role, its streams, its electrical and thermal connections, and its safety requirements. The stack itself, its controls and its internals are bought equipment and are listed in AQS-EQP-FC-001.

The page does not cover the standby generator `BACKUP_GEN` (AQS-PWR-002), the methanol fuel cell `MEOH_FC` (AQS-MeOH-001) or the sizing of the photovoltaic array and the flow battery (AQS-ELEC-007, `POWER_SIZING.md`).

## 2. Role

The fuel cell gives the plant a continuous source of electricity that does not depend on the sun. It closes a reversible loop with the PEM water electrolyser `H2O_ELYZ`: the electrolyser makes hydrogen and oxygen when there is surplus power, the stores hold them, and the fuel cell turns them back into electricity. The graph records the loop in `FUEL_CELL.params.reversible_loop`. On the basis stated there, the electrolyser uses 55 kWh per kilogram of hydrogen and the fuel cell returns 20 kWh per kilogram, so the round trip returns 36.4 % of the energy.

The continuous output is the requirement REQ-FC-CONT of AQS-REQ-KW-001. The graph carries it as `FUEL_CELL.continuous_kw`.

The fuel cell and the backup generator are different machines with different roles. The generator is an engine that feeds alternating current to the generator port of the inverters when the plant is islanded, burning hydrogen or the C5 to C10 cut (AQS-PWR-002). The fuel cell feeds direct current to the battery side of the inverters. Neither replaces the other. The methanol fuel cell `MEOH_FC` is a second, independent path on the same direct-current side; it does not replace the PEM fuel cell.

## 3. Streams

Table 3.1 lists the streams of the fuel cell as the graph holds them.

Table 3.1. Fuel cell streams

| Stream | From | To | Phase | Carries | Rate |
| --- | --- | --- | --- | --- | --- |
| S49 | `CRYO_H2` | `FUEL_CELL` | Gas | Dry hydrogen fuel | 4.8 kg/d |
| S50 | `CRYO_O2` | `FUEL_CELL` | Gas | Oxygen | 38.4 kg/d |
| S51 | `FUEL_CELL` | `SOL_ARK_60K` | Electricity | Direct current | 4.0 kW |
| S52 | `FUEL_CELL` | `VCD_TRAIN` | Liquid | Product water | 42.88 kg/d |
| S53 | `FUEL_CELL` | `Q4_BUS` | Heat | Heat below 80 °C | 1.14 kW |
| IA-FC-LEACH | `FUEL_CELL` | `LEACH_CSTR_1` | Liquid | Cell water | 0.32 kg/d |
| IA-FC-FIX | `FUEL_CELL` | `NOX_SCRUB` | Solid and liquid | Cell water | 0 kg/d |

The oxygen and the water are in the stoichiometric ratio to the hydrogen: 8 kg of oxygen and 9 kg of water for each kilogram of hydrogen. The product water goes to the vapour compression distillation train `VCD_TRAIN`, so it is treated before any use and is not drinking water as it leaves the stack (AQS-WTR-001, `WATER_PURIFICATION.md`).

## 4. Connections

### 4.1 Fuel and oxidant

The hydrogen comes from the store `CRYO_H2`, which holds dry hydrogen from the dryer and the electrolyser. The fuel cell has its own branch with an isolation valve, separate from the generator branch S45. The oxygen comes from the store `CRYO_O2`. The fuel cell uses pure oxygen, not air. The hydrogen and oxygen manifolds are kept apart as AQS-HSE-001 (`HAZARD_SEPARATION.md`) requires, and they never meet outside the stack.

### 4.2 Electrical

The fuel cell feeds direct current to the battery side of the hybrid inverters `SOL_ARK_60K`, which the flow battery `ZNBR2` shares. A direct-current converter matches the stack voltage to the battery port. The fuel cell is never connected to a rectifier bus of the process, which carries loads, nor to the generator port of the inverters, which is reserved for the backup generator.

### 4.3 Heat

The stack heat goes through a heat exchanger to the Q4 low-grade heat header `Q4_BUS`, as for the other low-grade heat sources. Only water below 80 °C reaches the habitation and farm heating. Exhaust from the backup generator or from the afterburner is never mixed into the air of the habitation or the farm.

## 5. Location

The fuel cell stands on level L0 near the inverters and the flow battery, either outdoors or in a fire-rated room as NFPA 2 requires for hydrogen equipment indoors. Its envelope is in `models/units/FUEL_CELL/` and `cad/stl/FUEL_CELL.stl`. Its process and instrumentation diagram is `docs-authority/pid/FUEL_CELL.svg`, its duty sheet is `docs-authority/duties/FUEL_CELL.md`, and its flow diagram is drawn by `flow_graph/exporters/matplotlib/fuel_cell_pfd.py`.

## 6. Safety

1. The hydrogen inventory of the stores, the dryer and the fuel cell and generator manifolds stays within the inventory limit of AQS-HSE-001.
2. The hazardous-area classification for hydrogen (Class I, Division 2, Group B) extends to the hydrogen flanges and manifolds of the fuel cell.
3. The oxygen manifold is kept apart from hydrogen and from organic materials.
4. If the fuel cell is enclosed, the room is ventilated and has hydrogen detectors. At 25 % of the lower flammability limit they shut off the fuel and trip the rectifiers, as the existing hydrogen logic does.
5. The bromine scrubber of the flow battery is not shared with the purge of the fuel cell.

## 7. Open items

1. The direct-current converter between the stack and the battery port of the inverters is not a unit on the graph. It is to be added to the graph or named as part of the stack package in AQS-EQP-FC-001.
2. The sizing page `docs-authority/sizing/FUEL_CELL.md` reports an empty envelope and a polyethylene vessel, which do not describe a fuel cell. Its generator needs a case for bought stacks.
