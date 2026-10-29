# MG_POT

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 1.989 kg/d. Mass out 1.989 kg/d. Electrical duty 0.3375 kW. In: IA-MGCL2-KROLL 1.949 kg/d (Kroll retort MgCl2 return (net of drag-out)); IA-MGCL2-MU 0.03978 kg/d (CaCl2-MgCl2 brine concentrate (mining-waste class)). Out: MG_POT_TO_IND 0 kg/d (Mg metal); MG_POT_CL2 0 kg/d (Cl2 return); IA-MG-TI 0.5078 kg/d (Mg reductant to the Kroll retort); IA-CL2-MG-TI 1.481 kg/d (chlorine to the Kroll chlorinator).

2. Size.
- Envelope 800×800×1600 mm, 1.024 m³. That box over this flow would be 12355.5 h if it were full. It is not a residence time.
- Envelope basis (graph node): cell-class study minimum; live on the D-DOCK chloride import (A-M-284); bath 0.5 d hold at 1800 kg/m3, electrodes and busbar from the Faraday current (A-M-282).
- Sizing study AQS-DUTY-072 (study): mg_kg_d 0.5078; mgcl2_return_kg_d 1.949; mgcl2_makeup_kg_d 0.0398; cl2_kg_d 1.481; chemistry MgCl2 -> Mg + Cl2, 700 C (AQS-BAL-KROLL closure); I_A 54.89; V 4.2; dc_kW 0.2306; hold_kW 0.1069; kW 0.3375; basis Kroll Mg recycle at the 0.50 kg/d Ti line; CaCl2-MgCl2 brine make-up covers the drag-out (A-M-284/280).
- Graph design (AQS-PAR-001 sizing): service molten MgCl2 electrolysis cell (Kroll Mg recycle), 700 C; chemistry MgCl2 -> Mg + Cl2; feed_kg_d 1.989; metal_kg_d 0.5078; cl2_kg_d 1.481; I_A 54.89; cell_V 4.2; dc_kW 0.2306; hold_kW 0.1069; connected_kW 1; bath_T_C 700; anode_D_mm 50; anode_imm_mm 300; cathodes 4; busbar_mm2 50.

3. Material. Graphite anodes, steel cathode plates, mullite-class alumina-silica refractory cell lining in a mild-steel shell; skim launder kept graphite-wetted. Basis: molten MgCl2 at 700 C: the industrial MgCl2-electrolysis pot class is graphite anodes + steel cathodes (ULLMANN_MAGNESIUM); alloy containment loses Cr to the melt (DING2021_ENG, KRUIZENGA2012); backup lining per SCHACHT2004. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: monolithic graphite pot if the CaCl2-brine impurity load runs above the design, at the cost of a brittle liner. MgCl2 is hygroscopic: the pot-feed import leg stays PVDF (P3) and the headspace stays dry; no measured rate (unit task 12 first article). (X-MAT-22)

4. Nozzles. Schedule at `nozzles/MG_POT.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/MG_POT.stl`. Manufacturing model `models/mfg/MG_POT/draw_mg_pot.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
