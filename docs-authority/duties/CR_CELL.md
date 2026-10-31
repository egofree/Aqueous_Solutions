# CR_CELL

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.452 kg/d. Mass out 0.452 kg/d. Electrical duty 0.1600 kW. In: IA-CR2O3-MU 0.3654 kg/d (Cr2O3-equivalent chromite concentrate (dock import class)); IA-C-CR 0.08662 kg/d (carbon reductant (petcoke/char class)). Out: CR_TO_IND 0.25 kg/d (Cr metal); IA-CR-VENT 0.202 kg/d (chlorinator CO (fuel-gas class export)).

2. Size.
- Envelope 800×800×1600 mm, 1.024 m³. That box over this flow would be 54370.1 h if it were full. It is not a residence time.
- Envelope basis (graph node): cell-class study minimum; live on the D-DOCK chloride import (A-M-284); bath 0.5 d hold at 1800 kg/m3, electrodes and busbar from the Faraday current (A-M-282).
- Sizing study AQS-DUTY-072 (study): cr_kg_d 0.25; cr2o3_kg_d 0.3654; c_kg_d 0.0866; co_kg_d 0.202; chemistry Cr2O3 + 3C + 3Cl2 -> 2CrCl3 + 3CO; 2CrCl3 -> 2Cr + 3Cl2 (anode gas recycled); I_A 18.95; V 2.8; dc_kW 0.0531; hold_kW 0.1069; kW 0.16; basis dock chromite-equivalent import; internal chlorine loop; A-M-280 (grade envelope 40-52 % Cr2O3).
- Graph design (AQS-PAR-001 sizing): service Cr(III) molten-salt electrolysis cell with carbochlorination loop, 700 C; chemistry Cr2O3 + 3C + 3Cl2 -> 2CrCl3 + 3CO; 2CrCl3 -> 2Cr + 3Cl2; feed_kg_d 0.452; metal_kg_d 0.25; co_kg_d 0.202; I_A 18.95; cell_V 2.8; dc_kW 0.0531; hold_kW 0.1069; connected_kW 1; bath_T_C 700; anode_D_mm 50; anode_imm_mm 250; cathodes 3; busbar_mm2 25.

3. Material. Graphite liner and graphite anode for the carbochlorination melt (CrCl3 wetted), dry CO/CO2/Cl2 headspace; 90 % alumina brick backup in a mild-steel shell. Basis: Cr2O3 + 3C + 3Cl2 carbochlorination at 700 C with an internal anode-gas loop (graph design): the bed is a dry hot face (M7); the melt physics is the pot-cell class (DING2018_CL_REVIEW, KRUIZENGA2012). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: SiC/SiAlON bed brick if chloride carryover drives the hot face past graphite life; Cr metal cathode-worked parts passivate in situ. 0.25 kg/d Cr line; the CO off-gas (0.202 kg/d) leaves on the dry IA-CR-VENT (M7); no measured rate. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/CR_CELL.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Vent edge IA-CR-VENT on the graph (to NORTH_DOCK). Atmospheric operation is not claimed beyond this edge. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/CR_CELL.stl`. Manufacturing model `models/mfg/CR_CELL/cr_cell.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
