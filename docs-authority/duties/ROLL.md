# ROLL

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 13 kg/d. Mass out 13 kg/d. Electrical duty 0.0000 kW. In: CAST_TO_ROLL 3 kg/d (billet to roll); CONT_TO_ROLL 10 kg/d (continuous billet/slab). Out: ROLL_TO_STOCK 13 kg/d (plate/sheet).

2. Size.
- Envelope 1500×800×1500 mm, 1.8 m³. That box over this flow would be 3323.1 h if it were full. It is not a residence time.
- Envelope basis (graph node): A-M-199 forming class; hold-up of the 13 kg/d charge is below the class minimum.
- Sizing study AQS-DUTY-072 (study): rolled_kg_d 13; kWh_d 0.416; basis 0.032 kWh/kg cold-rolling class (A-M-177 DIETER1988); hot rolling cheaper.
- Graph design (AQS-PAR-001 sizing): machine two-high bench rolling mill; rolled_kg_d 13; rolls_D_mm 300; roll_L_mm 640; kWh_d 0.416.

3. Material. Selection pending (unit task 09, AQS-STD-002 across the AQS-ASSAY-001 Rev C bounding cases). Not chosen on this page.

4. Nozzles. Schedule at `nozzles/ROLL.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/ROLL.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
