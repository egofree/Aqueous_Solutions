# CHICKEN_COOP

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: IA-CHICK-H2O 0 kg/d (flock drinking water); LARVAE_FEED 0 kg/d (larvae meal to the layer ration); DUCK_LAYERS 0 kg/d (duckweed: layer ration base (dry-equivalent)). Out: EGG_HARVEST 0 kg/d (eggs to the food store); CHICK_MANURE 0 kg/d (poultry manure to the larvae bin); CHICK_VAP 0 kg/d (flock respiration/evaporation).

2. Size.
- Graph design (AQS-PAR-001 sizing): service layer flock, 12 birds; stock_birds 12; egg_kg_d 0.6; feed_kg_d 1.44; basis A-M-417 (X-FARM-02).

3. Material. Hot-dip galvanised steel frame and hardware cloth, SS316 feeders and waterers, HDPE drop-board liner. Basis: wet uric-acid manure with ammonia offgas and periodic wash-down (graph design; A-M-417): ammonia plus moisture pits zinc at the droppings line, so the wet contact points step up to SS316 (standard poultry-housing practice) Alternative: SS304 frame if wash-down frequency rises past the weekly class. the drop board is the manure harvest surface to the BSFL bin. (X-FARM-02)

4. Nozzles. Schedule at `nozzles/CHICKEN_COOP.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops CHICKEN_COOPTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
