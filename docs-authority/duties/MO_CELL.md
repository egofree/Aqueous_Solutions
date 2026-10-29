# MO_CELL

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.1055 kg/d. Mass out 0.1055 kg/d. Electrical duty 0.1141 kW. In: IA-MOO3-MU 0.09377 kg/d (MoO3-equivalent concentrate (dock import class)); IA-C-MO 0.01174 kg/d (carbon reductant (petcoke/char class)). Out: MO_CELL_ANODE_GAS_TO_CRU 0 kg/d (anode gas (Cl2 or O2) from molten-salt pot); MO_TO_IND 0.0625 kg/d (Mo metal); IA-MO-VENT 0.043 kg/d (chlorinator CO2 (vent class)).

2. Size.
- Envelope 800×800×1600 mm, 1.024 m³. That box over this flow would be 232943.5 h if it were full. It is not a residence time.
- Envelope basis (graph node): cell-class study minimum; live on the D-DOCK chloride import (A-M-284); bath 0.5 d hold at 1800 kg/m3, electrodes and busbar from the Faraday current (A-M-282).
- Sizing study AQS-DUTY-072 (study): mo_kg_d 0.0625; moo3_kg_d 0.0938; c_kg_d 0.0117; co2_kg_d 0.043; chemistry MoO3 + 1.5C + 1.5Cl2 -> MoCl3 + 1.5CO2; MoCl3 -> Mo + 1.5Cl2 (anode gas recycled); I_A 2.57; V 2.8; dc_kW 0.0072; hold_kW 0.1069; kW 0.1141; basis dock tech-oxide import; internal chlorine loop; A-M-280 (grade envelope 95-99 % MoO3).
- Graph design (AQS-PAR-001 sizing): service Mo(III) molten-salt electrolysis cell with carbochlorination loop, 650 C; chemistry MoO3 + 1.5C + 1.5Cl2 -> MoCl3 + 1.5CO2; MoCl3 -> Mo + 1.5Cl2; feed_kg_d 0.1055; metal_kg_d 0.0625; co2_kg_d 0.043; I_A 2.57; cell_V 2.8; dc_kW 0.0072; hold_kW 0.1069; connected_kW 1; bath_T_C 650; anode_D_mm 50; anode_imm_mm 250; cathodes 3; busbar_mm2 25.

3. Material. Graphite liner and graphite anode for the carbochlorination melt (MoCl3 wetted); 90 % alumina brick backup in a mild-steel shell; dry CO2-laden headspace. Basis: MoO3 + 1.5C + 1.5Cl2 at 650 C (graph design): same pot-cell class as CR_CELL - graphite wetted face, alumina backup (DING2018_CL_REVIEW, SCHACHT2004). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: SiC bed brick above the design temperature class. the 0.0625 kg/d Mo line is also the house Mo-rod source for cell hardware; anode gas is the internal Cl2 loop; no measured rate. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/MO_CELL.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Vent edge IA-MO-VENT on the graph (to NORTH_DOCK). Atmospheric operation is not claimed beyond this edge. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/MO_CELL.stl`. Manufacturing model `models/mfg/MO_CELL/draw_mo_cell.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
