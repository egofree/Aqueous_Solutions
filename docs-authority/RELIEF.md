# Relief

Document number: AQS-REL-001
Revision: B
Date: 2026-10-25

| Rev | Description | Date |
|---|---|---|
| A | Per-node relief list withdrawn | Not recorded |
| B | Rewritten to the documentation style guide (AQS-DOC-002); purpose and scope added. No rule changed. | 2026-10-25 |

## 1. Purpose and scope

This page records the withdrawal of an earlier relief list and states the rule that replaces it. The relief case, set point and destination for each unit are given on that unit's duty sheet in `docs-authority/duties/`.

## 2. Withdrawn list

An earlier list assigned a set pressure of about 17.8 kPa and a relief orifice of 3.3 mm to every unit. That list is withdrawn, for the following reasons.

The pressure was the height of the unit envelope taken as a column of water, plus 10 kPa. It was applied to crops, electrical nodes, the expander and the silicon-carbide furnace, and it is not a set point. On the expander, for example, the process inlet pressure is 500 kPa, while the stored value of 14.9 kPa was the height of its 500 mm envelope taken as a water column.

The orifice size was the American Petroleum Institute (API) liquid relief orifice for 1 kg/s of water at that pressure, with a discharge coefficient Kd of 0.65. It is not the relief load of the process and it is not the nozzle size. The list also still held deleted nodes (`LITHO`, `BLOW`, `ELCOAT`, `PV_CELL` and `FORM_RX`).

## 3. Rule

No set point is assigned until the relief case for the unit is stated. Where a relief nozzle is needed, it is DN15 and discharges back to the process, to the hood or to the suction of the cold box. It never discharges to the room or to a stack. Each unit's duty sheet states which destination applies. A machine that is not a liquid tank is not a pressure vessel.
