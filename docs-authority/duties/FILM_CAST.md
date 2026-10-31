# FILM_CAST

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.14 kg/d. Mass out 0.14 kg/d. Electrical duty 0.1087 kW. In: POLYF_TO_FILM 0.14 kg/d (PVDF resin to the film/sheet line). Out: FILM_TO_STOCK 0.14 kg/d (film stock).

2. Size.
- Envelope 1500×800×1500 mm, 1.8 m³. That box over this flow would be 308571.4 h if it were full. It is not a residence time.
- Envelope basis (graph node): forming-class minimum (A-M-199); 25 mm extruder at the 0.14 kg/d sheet duty (A-M-283).
- Sizing study AQS-DUTY-073 (study): rate_kg_d 0.
- Graph design (AQS-PAR-001 sizing): machine PVDF cast film/sheet line; extruder_D_mm 25; die_mm 200; chill_roll_D_mm 150; pvdf_kg_d 0.14; melt_C 220; duty_kW 0.1087; product gasket/lining sheet (AQS-RATE-FP-MET PVDF linings and gaskets).

3. Material. 316L barrel, Hastelloy die (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Schedule at `nozzles/FILM_CAST.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/FILM_CAST.stl`. Manufacturing model `models/mfg/FILM_CAST/draw_film_cast.py` (AQS-PLAN-006).

8. Open items. No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
