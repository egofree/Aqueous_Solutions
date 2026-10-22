# SINTER

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: none. Out: SINTER_TO_STOCK 0 kg/d (sintered stock).

2. Size.
- Envelope 1000×1000×1500 mm, 1.5 m³.
- Envelope basis (graph node): A-M-199 melt class at the powder-bulk density 3000 kg/m3 (study); N+1 rated envelope (A-M-282).
- Sizing study AQS-DUTY-072 (study): rate_kg_d 0; connected_kW 8; backup_of ROLL consolidation (press-and-sinter P/M route at the 0.5 kg/d powder class); outage_basis roll-stand outage at the powder-class lots (A-M-282).
- Graph design (AQS-PAR-001 sizing): service Ti/Mo/Cr powder sinter furnace, N+1 consolidation of ROLL; connected_kW 8; backup_of ROLL; outage_d 2; design_case_kg_d 0.5; T_C 1300.

3. Material. Graphite resistance elements + 95 % alumina muffle under inert/vacuum atmosphere; nickel-free hot zone on a water-cooled steel jacket. Basis: Ti/Mo/Cr powder sinter at 1300 C, press-and-sinter consolidation N+1 of ROLL (graph design): reactive-powder sintering furnaces use inert/vacuum hot zones with graphite or MoSi2 elements (ASM_V7); Ti embrittles in air/N2 at the class (CRC_TI). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: Mo elements if an oxidizing (air) sinter variant is ever required - a different duty class (cost up). design_case 0.5 kg/d, T_C 1300 (graph design); no wetted stream - dry hot gas above any dew point (M7). (X-MAT-22)

4. Nozzles. Schedule at `nozzles/SINTER.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/SINTER.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
