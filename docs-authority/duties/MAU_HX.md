# MAU_HX

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: none. Out: none.

2. Size.
- Node params (AQS-PAR-001): kW 12; kW_per_K 6.65; dT_K 1.8; season winter.
- Basis (graph node): AQS-HEAT-STUDY-002 Rev A 2026-10-18 §10.3 (A-M-241): 6.65 kW/K make-up air (~23 900 m3/h, AQS-THM-002) x 1.8 K = 12 kW; displaces 12 kW of winter resistance tempering.

3. Material. Aluminium-fin, copper-tube make-up-air heating coil (air side dry and above the dew point in heating), 316L headers; PP condensate tray where any defrost condensate can form; water side on the issued Q3/Q4 M1 316L loop family. Basis: 12 kW make-up-air coil at 1.8 K (graph params; A-M-241): heating-only coil stays above the air dew point (HAB air-handling class), so the corrosion driver is absent on the air side (PERRY9_HEAT air-cooled construction class). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: 316L finned-tube coil if winter commissioning shows fin wetting (cost up). no wetted stream; the filter frames are the machine maintenance surface. (X-MAT-22)

4. Nozzles. No piped process connection on the graph (un-rated or non-mass edges only); no nozzle schedule is issued yet. Nothing to size a bore against.

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07).
