# Bounding-case resize sweep

Document number: AQS-PLAN-010
Revision: A
Date: 2026-10-15
Authority: AGENTS.md §Sizing; AQS-PLAN-007 X-RSZ-07. Study. Not a PE stamp.

Rule. Edges carry the design day. A unit whose bounding case exceeds its design-day flow gets params.design_capacity_kg_d on the node. Loads with a complete calculation are booked on the graph.

| Item | Was | Now | Basis | Status |
| --- | --- | --- | --- | --- |
| Acid regeneration (BMED_ACID, IA-ACID-01) | held ×4.5 | resized | X-RSZ-01 | done |
| EW power, PV, storage, inverters | held | resized | X-RSZ-02 | done |
| EW aisle (750 mm pitch) | held | re-placed | X-RSZ-03 | done |
| BMED trim cooling | held | booked 1.81 kW | X-RSZ-04 | done |
| FARM block | full | tier + FARM_AQ | X-RSZ-05 | done |
| IA-POT-01 potable path | leach liquor | via VCD/UPW/REMIN | X-RSZ-06 | done |
| FLOAT_SINK | 376.10 kg/d | design 459.27 kg/d | case A, covers MSW + unassigned | done |
| OIL_DRYER, OIL_PYRO | 33.0 kg/d | design 45.0 kg/d | MSW case | done |
| Unassigned class (MSW 35.0 kg/d) | held with reason | reports to FLOAT_SINK capacity | assumption | done |
| GROW_BED load | 5.0 kW study | 2.25 kW booked; PV average −2.75 kW | AQS-ELEC-003 | done |
| BMED_UPW_POLISH load | 6.0 kW study | 0.038 kW booked | AQS-ELEC-003 | done |
| CRYO_ASU load | 18.0 kW study | kept 18.0 kW | calculation is a lower bound (3.03 kW) | open: vendor data |
| Loads without graph feeds | bus 137 kW vs graph sources | not booked | most loads have continuous_kw but no SOL_ARK feed | open: X-ELS-02 feed edges |
| H₂ purifier (S45, S49 "purifier held") | not on the graph | not added | ISO 14687 Grade D needs a unit | open: unit to add with CRYO_H2 storage mode |
| VCD_TRAIN energy for +123 kg/d | not recalculated | — | about 0.1 kW at 20 kWh/m³ | open: X-ELS-02 |
