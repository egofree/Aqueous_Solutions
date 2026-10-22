# RES_HEAT

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: none. Out: none.

2. Size.
- Envelope 1000×1000×1500 mm, 1.5 m³.
- Envelope basis (graph node): A-M-199 melt class; N+1 rated envelope (A-M-282).
- Sizing study AQS-DUTY-072 (study): rate_kg_d 0; connected_kW 12; backup_of SHELL_BURNOUT / SINTER heating duty (resistance radiant); outage_basis burnout-element outage during a shell campaign (A-M-282).
- Graph design (AQS-PAR-001 sizing): service resistance radiant reheating furnace, N+1 of SHELL_BURNOUT/SINTER heating; connected_kW 12; backup_of SHELL_BURNOUT/SINTER; outage_d 2; T_C 900.

3. Material. Ceramic-fibre module lining + 80Ni-20Cr resistance elements on a mild-steel casing at the 900 C box-furnace class. Basis: resistance radiant reheating, N+1 of SHELL_BURNOUT/SINTER heating at 900 C (graph design): element and lining class to 1100 C per ASM_V1; lining design per SCHACHT2004 ch. 13. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: MoSi2 elements if the duty class moves above 1100 C (cost up). dry hot air, M7; element life rides the first-article campaign. (X-MAT-22)

4. Nozzles. No piped process connection on the graph (un-rated or non-mass edges only); no nozzle schedule is issued yet. Nothing to size a bore against.

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/RES_HEAT.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07).
