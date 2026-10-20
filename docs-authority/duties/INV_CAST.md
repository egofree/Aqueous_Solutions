# INV_CAST

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 10 kg/d. Mass out 10 kg/d. Electrical duty 0.1500 kW. In: BURNOUT_TO_CAST 8 kg/d (fired shell); IND_TO_INV 2 kg/d (melt for investment pour); VAC_TO_INV 0 kg/d (reactive melt for investment pour). Out: INV_TO_BREAK 10 kg/d (cast + shell).

2. Size.
- Envelope 1500×800×1500 mm, 1.8 m³. That box over this flow would be 4320.0 h if it were full. It is not a residence time.
- Envelope basis (graph node): A-M-199 forming class; live on IND_TO_INV (A-M-281).
- Sizing study AQS-DUTY-072 (study): pour_kg_d 2; shell_kg_d 8; basis live melt output 2 kg/d through the fired shell (A-M-281).
- Graph design (AQS-PAR-001 sizing): machine investment casting tilt-pour station; pour_kg_d 2; shell_kg_d 8; molds_per_campaign 8.

3. Material. Selection pending (unit task 09, AQS-STD-002 across the AQS-ASSAY-001 Rev C bounding cases). Not chosen on this page.

4. Nozzles. Schedule at `nozzles/INV_CAST.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/INV_CAST.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
