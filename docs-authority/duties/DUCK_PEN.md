# DUCK_PEN

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 8.313 kg/d. Mass out 8.313 kg/d. Electrical duty 0.0000 kW. In: IA-DUCK-H2O 1.98 kg/d (duck drinking/washing water); DUCK_FODDER 4 kg/d (fresh duckweed forage (ad lib)); DUCK_RATION 2.333 kg/d (pressed duckweed mash to the duck ration). Out: DUCK_EGGS 0.34 kg/d (duck eggs to the food store); DUCK_MANURE 1.44 kg/d (duck manure to the larvae bin); DUCK_VAP 0.8 kg/d (duck pen evaporation); DUCK_GREY 5.733 kg/d (duck wash water).

2. Size.
- Envelope 2500×1300×1300 mm, 4.225 m³. That box over this flow would be 12197.3 h if it were full. It is not a residence time.
- Envelope: 6 ducks x 0.3 m2 + wallow strip (A-M-421; TECHTREE ducks.md) (X-FARM sec3).
- Graph design (AQS-PAR-001 sizing): service duck pen, 6 Khaki Campbell ducks; stock 6; egg_kg_d 0.34; ration_kg_d 0.9; basis A-M-421 (X-FARM-05).

3. Material. Hot-dip galvanised steel frame and hardware cloth, EPDM liner in the wallow, SS316 waterers. Basis: permanently wet pen with a wallow (graph design; A-M-421): standing water governs the zinc budget, so the wet zone is EPDM-lined and drinking-water contact is SS316 Alternative: FRP wet panels in place of the liner if the pen geometry changes. the ducks forage the aquaponic loop water; pen drainings join the BSFL feedstock. (X-FARM-05)

4. Nozzles. Schedule at `nozzles/DUCK_PEN.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops DUCK_PENPT-01, DUCK_PENTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/DUCK_PEN.stl` (a thick-walled tray at the claimed envelope; X-PAR-04). Manufacturing model `models/mfg/DUCK_PEN/draw_duck_pen.py` (AQS-PLAN-006; build log and drawings in the same folder).

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
