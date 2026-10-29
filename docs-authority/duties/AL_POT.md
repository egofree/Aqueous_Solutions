# AL_POT

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 49.42 kg/d. Mass out 49.42 kg/d. Electrical duty 5.6578 kW. In: IA-ALCL3-MU 49.42 kg/d (anhydrous AlCl3 feed (mining-waste chloride class)). Out: AL_POT_TO_IND 10 kg/d (Al metal); AL_POT_CL2 0 kg/d (Cl2 return); IA-CL2-SHIP 39.21 kg/d (chlorine byproduct export (water-treatment class product)); IA-CL2-SIREF 0.2137 kg/d (chlorine make-up of the chlorosilane loop).

2. Size.
- Envelope 800×800×1600 mm, 1.024 m³. That box over this flow would be 497.3 h if it were full. It is not a residence time.
- Envelope basis (graph node): cell-class study minimum; live on the D-DOCK chloride import (A-M-284); bath 0.5 d hold at 1800 kg/m3, electrodes and busbar from the Faraday current (A-M-282).
- Sizing study AQS-DUTY-072 (study): al_kg_d 10; line_kg_d 8; export_kg_d 2; alcl3_kg_d 49.42; cl2_kg_d 39.42; chemistry 2 AlCl3 -> 2 Al + 3 Cl2, 700 C NaCl-KCl-AlCl3 bath (GREENWOOD stoichiometry); I_A 1461; V 3.8; dc_kW 5.551; hold_kW 0.1069; kW 5.658; basis D-DOCK anhydrous AlCl3 import; Faraday at CE 0.85 (A-M-282); A-M-284 feedstock ruling.
- Graph design (AQS-PAR-001 sizing): service molten AlCl3-(NaCl-KCl) electrolysis cell, 700 C; chemistry 2 AlCl3 -> 2 Al + 3 Cl2; feed_kg_d 49.42; metal_kg_d 10; cl2_kg_d 39.42; I_A 1461; cell_V 3.8; dc_kW 5.551; hold_kW 0.1069; connected_kW 7; bath_T_C 700; anode_D_mm 75; anode_imm_mm 400; cathodes 5; busbar_mm2 975.

3. Material. Graphite cell liner (design allowance 10 mm on the wetted faces), graphite anodes at j 0.5 A/cm2 (A-M-282 class), steel cathode bus above the melt with copper busbar frame-isolated to AQS-STD-002 section 11; 90 % alumina brick + ceramic-fibre backup lining; mild-steel outer shell below the liner. Basis: molten NaCl-KCl-AlCl3 bath at 700 C (graph design): Fe-Cr-Ni alloys lose Cr selectively to the melt (DING2018_CL_REVIEW, KRUIZENGA2012); graphite is the standard fused-chloride wetted face; alumina backup lining per SCHACHT2004 ch. 4/13; M6/M7 with the section 11 bus isolation. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: SiC hot face if AlCl3 carryover concentrates beyond the dry-gas headspace design; Ni-200 baffling at the take-off. dry Cl2 headspace at 700 C: the 39.4 kg/d Cl2 export leaves on a dry hot line above the AlCl3 dew point (M7) with PVDF (P3 family) only below the dew point. No measured pit rate; the anode/liner change-out is the unit task 12 work order. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/AL_POT.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/AL_POT.stl`. Manufacturing model `models/mfg/AL_POT/al_pot.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
