# Cold box gas rate

Document number: AQS-DUTY-018
Revision: B
Date: 2026-10-12
Not a PE stamp. Column and expander geometry are in SIDE_CRYO.md.

1. Basis. Gas into the box is flue nitrogen 243.89 kg/d, scrubbed CO₂ 30 kg/d, leach gas 17.44 kg/d, and argon return 5.3 kg/d. Sum 296.6 kg/d. Intake air IA-AIR-IN is 0.

2. Size. 296.6 kg/d of nitrogen-class gas is about 10 m³/h. An isothermal compressor to 8 bar on that flow is 0.6 kW. A real machine is about 1.5 kW. The expander shaft is 5 kW, SIDE_CRYO.md. The node CRYO_ASU is 18 kW. The gas rate does not support 18 kW. Argon at 5.3 kg/d does not fit a 1 L can: at 10 bar that can holds about 0.018 kg. The argon receiver is 20 L, about one hour. Helium, neon, krypton, and xenon stay at 1 L. Their slips are 0.01, 0.05, 0.02, and 0.01 kg/d.

3. Material. Receivers 316L. Column and expander as SIDE_CRYO.md.

4. Nozzles. Feed DN25. Argon DN15 to the fab and back. Noble slips DN15 to the cans.

5. Instruments. Can pressure. High pressure stops the feed.

6. Relief. Can to can, then back to the feed. Not to the room.

7. Code. Shop.

8. Open items. The 18 kW node is not this flow. The compressor and the expander are.
