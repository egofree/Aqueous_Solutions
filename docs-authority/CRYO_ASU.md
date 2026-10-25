# Cold box gas rate

Document number: AQS-DUTY-018
Revision: C
Date: 2026-10-25
Not a PE stamp. The column and expander geometry are in `SIDE_CRYO.md`.

| Rev | Description | Date |
|---|---|---|
| B | Gas rate, receiver sizes and open items for the cold box | 2026-10-12 |
| C | Rewritten to the documentation style guide (AQS-DOC-002); purpose and scope added. No value changed. | 2026-10-25 |

## 1. Purpose and scope

The cold box (unit CRYO_ASU in the CRYO sector) cools the plant's waste gases until they liquefy, so that nitrogen, carbon dioxide, argon and the other noble gases can be separated and stored. This page checks the gas flow into the cold box against the power assigned to the unit in the graph, and sizes the argon and noble-gas receivers. The values were calculated at revision B (2026-10-12); the current rates are held in the plant flow graph.

## 2. Basis

The cold box takes no outside air: the intake edge IA-AIR-IN carries 0 kg/d. Table 2.1 lists the gas streams that enter it.

Table 2.1. Gas into the cold box

| Stream | Rate (kg/d) |
|---|---|
| Nitrogen from the flue | 243.89 |
| Scrubbed CO₂ | 30 |
| Gas from the leach | 17.44 |
| Argon returned from the fab | 5.3 |
| Total | 296.6 |

## 3. Size

A flow of 296.6 kg/d of gas with properties close to nitrogen is about 10 m³/h. An isothermal compressor raising that flow to 8 bar needs 0.6 kW; a real machine needs about 1.5 kW. The expander shaft power is 5 kW (`SIDE_CRYO.md`). The graph assigns 18 kW to the CRYO_ASU node, which this gas rate does not support.

A 1 L can at 10 bar holds about 0.018 kg of argon, which is far too small for an argon flow of 5.3 kg/d. The argon receiver is therefore 20 L, which holds about one hour of flow. The helium, neon, krypton and xenon receivers stay at 1 L; their flows are 0.01 kg/d, 0.05 kg/d, 0.02 kg/d and 0.01 kg/d.

## 4. Materials

The receivers are 316L stainless steel. The column and the expander are as given in `SIDE_CRYO.md`.

## 5. Nozzles

The feed nozzle is DN25. The argon line to the fab and back is DN15. The noble-gas lines to the cans are DN15.

## 6. Instruments

Each can has a pressure transmitter. High pressure in a can stops the feed.

## 7. Relief

Each can relieves into the next can and then back to the feed. No can relieves into the room.

## 8. Code and open items

The code class recorded for the receivers is "shop". No page in the repository defines that class, so it is an open item.

The second open item is the power: the 18 kW assigned to the node does not match this gas flow. The power that the gas flow needs is that of the compressor and the expander.
