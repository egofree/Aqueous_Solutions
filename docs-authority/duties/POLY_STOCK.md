# POLY_STOCK

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.6441 kg/d. Mass out 0.6441 kg/d. Electrical duty 0.0000 kW. In: PELLET_TO_STOCK 0.2941 kg/d (pellet stock); POWDER_TO_STOCK 0.09 kg/d (powder stock); FILM_TO_STOCK 0.14 kg/d (film stock); IA-RESIST-STOCK 0.12 kg/d (formulated positive photoresist to stock). Out: POLY_TO_MFG 0.2674 kg/d (polymer feedstock to manufacturing); POLY_TO_FAB 0.12 kg/d (polymer feedstock to fab); POLY_TO_WET 0.02674 kg/d (lining/gasket stock return path); FLUORO_TO_MFG 0.23 kg/d (fluoropolymer stock issue to the shop).

2. Size.
- Envelope 600×400×800 mm, 0.192 m³. That box over this flow would be 7153.9 h if it were full. It is not a residence time.
- Envelope basis (graph node): 1 d shop issue + reject staging at the 500 kg/m3 pellet bulk density (study; A-M-264).
- Sizing study AQS-DUTY-073 (study): out_kg_d 0.4974; fluoro_kg_d 0.23; to_wet_kg_d 0.02674; to_fab_kg_d 0.
- Graph design (AQS-PAR-001 sizing): bin pellet tote bin; issue_kg_d 0.2674; to_wet_kg_d 0.02674; hold_d 1.

3. Material. HDPE tote bins and PP powder drums; steel rack; no wetted streams. Basis: 1 d shop issue + reject staging at the 500 kg/m3 pellet bulk density (graph design; A-M-264): dry resin storage, no process contact (AQS-DUTY-073 class). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: antistatic PP totes if the powder-drum fraction builds charge (a spares-check item). no corrosion load; stock loss is the managed quantity. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/POLY_STOCK.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/POLY_STOCK.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
