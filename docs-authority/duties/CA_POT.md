# CA_POT

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.1525 kg/d. Mass out 0.1525 kg/d. Electrical duty 0.1221 kW. In: IA-CACL2-MU 0.1525 kg/d (CaCl2 brine concentrate (mining-waste class)). Out: CA_POT_TO_IND 0.05507 kg/d (Ca metal); IA-CA-CL2-SHIP 0.09743 kg/d (chlorine byproduct export (water-treatment class)).

2. Size.
- Envelope 800×800×1600 mm, 1.024 m³. That box over this flow would be 161157.3 h if it were full. It is not a residence time.
- Envelope basis (graph node): cell-class study minimum; live on the D-DOCK chloride import (A-M-284); bath 0.5 d hold at 1800 kg/m3, electrodes and busbar from the Faraday current (A-M-282).
- Sizing study AQS-DUTY-072 (study): ca_kg_d 0.05507; cacl2_kg_d 0.1525; cl2_kg_d 0.09743; chemistry CaCl2 -> Ca + Cl2, 700 C; I_A 3.61; V 4.2; dc_kW 0.0152; hold_kW 0.1069; kW 0.1221; basis grease-thickener Ca line (AQS-DUTY-GREASE 0.1 kg/d Ca(OH)2); brine import per A-M-284.
- Graph design (AQS-PAR-001 sizing): service molten CaCl2 electrolysis cell, 700 C; chemistry CaCl2 -> Ca + Cl2; feed_kg_d 0.1525; metal_kg_d 0.0551; cl2_kg_d 0.0974; I_A 3.61; cell_V 4.2; dc_kW 0.0152; hold_kW 0.1069; connected_kW 1; bath_T_C 700; anode_D_mm 50; anode_imm_mm 250; cathodes 3; busbar_mm2 25.

3. Material. Graphite anodes, steel cathode rods carrying the solid Ca deposit to the tap work order; 90 % alumina backup lining + ceramic-fibre in a mild-steel shell. Basis: molten CaCl2 at 700 C (graph design; Ca m.p. 842 C per GREENWOOD element chemistry - the deposit leaves as a solid at the tap work order): the same fused-chloride physics governs the selection as AL_POT (DING2018_CL_REVIEW, KRUIZENGA2012; SCHACHT2004). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: electrode upgrade to Mo dip legs if the Ca-metal contact interface becomes the unit task 12 bottleneck (cost up; Mo is in-house at MO_CELL class rates). the 0.055 kg/d Ca line feeds the grease thickener: the pot is sheet-lined rather than monolithic (cost-down variant of the pot family). (X-MAT-22)

4. Nozzles. Schedule at `nozzles/CA_POT.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/CA_POT.stl`. Manufacturing model `models/mfg/CA_POT/ca_pot.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
