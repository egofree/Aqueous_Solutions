# DUCK_PEN

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: IA-DUCK-H2O 0 kg/d (duck drinking/washing water); DUCK_FODDER 0 kg/d (fresh duckweed forage (ad lib)). Out: DUCK_EGGS 0 kg/d (duck eggs to the food store); DUCK_MANURE 0 kg/d (duck manure to the larvae bin); DUCK_VAP 0 kg/d (duck pen evaporation); DUCK_GREY 0 kg/d (duck wash water).

2. Size.
- Graph design (AQS-PAR-001 sizing): service duck pen, 6 Khaki Campbell ducks; stock 6; egg_kg_d 0.34; ration_kg_d 0.9; basis A-M-421 (X-FARM-05).

3. Material. Hot-dip galvanised steel frame and hardware cloth, EPDM liner in the wallow, SS316 waterers. Basis: permanently wet pen with a wallow (graph design; A-M-421): standing water governs the zinc budget, so the wet zone is EPDM-lined and drinking-water contact is SS316 Alternative: FRP wet panels in place of the liner if the pen geometry changes. the ducks forage the aquaponic loop water; pen drainings join the BSFL feedstock. (X-FARM-05)

4. Nozzles. Schedule at `nozzles/DUCK_PEN.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops DUCK_PENTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
