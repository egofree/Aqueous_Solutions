# AQUA_TANK

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 203.8 kg/d. Mass out 203.8 kg/d. Electrical duty 0.0000 kW. In: IA-AQUA-TOPUP 27.36 kg/d (loop top-up: root-zone growth water and evaporation); AQUA_RETURN2 158.5 kg/d (polished loop water return (2.2 kg/d duckweed growth drawn from the loop)); DUCK_FISH 18 kg/d (fresh duckweed: tilapia ration (dry-equivalent, 1.5 % BW)). Out: AQUA_LOOP1 200 kg/d (ammonia-rich fish waste water (NH3/NH4+ from the gills)); FISH_SLUDGE 3 kg/d (fish sludge to the larvae bin); FISH_HARVEST 0.81 kg/d (fish harvest to the food store).

2. Size.
- Envelope 2100×1100×1100 mm, 2.541 m³. That box over this flow would be 299.2 h if it were full. It is not a residence time.
- Envelope: 2.0 m3 working volume at the 60 kg stock / 30 kg-per-m3 class (TECHTREE tilapia glossary; A-M-415): 2000 x 1000 x 1000 ID + 50 walls, EPDM-lined HDPE (X-FARM sec3).
- Graph design (AQS-PAR-001 sizing): service aquaponic fish tanks, 60 kg standing stock; stock_kg 60; ration_kg_d 0.9; basis A-M-415 (X-FARM-01); ammonia_load fish excrete NH3/NH4+ through the gills: ~30 g NH4+-N per kg feed (protein metabolism); toxic above 1 mg/L un-ionised NH3; O2_demand dissolved O2 for fish respiration: ~5 mg/L minimum (aeration required); the air stones are the O2 source; notes_extra the fish are the ammonia SOURCE and the O2 SINK of the aquaponic loop; the biofilter bacteria are the ammonia CONSUMER and the O2 SINK.

3. Material. HDPE tank body with a food-grade LDPE aquaculture liner, SS316 hardware above the waterline, CPVC loop fittings. Basis: the tank holds the fish stock in the RAS loop at 26-28 C (graph design; A-M-415): ichthyotoxicity governs the wetted set, so Cu/Zn/brass are excluded outright; the liner is the aquaculture food-contact class over the 2.5 m3 envelope (203.8 kg/d loop). Alternative: FRP tank with gelcoat in place of the liner if liner abrasion ever shows. loop top-up 27.4 kg/d and duckweed ration 18 kg/d in; 200 kg/d to the biofilter, 3 kg/d sludge to the BSFL bin. (X-FARM-11)

4. Nozzles. Schedule at `nozzles/AQUA_TANK.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops AQUA_TANKPT-01, AQUA_TANKTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/AQUA_TANK.stl` (a thick-walled tray at the claimed envelope; X-PAR-04). Manufacturing model `models/mfg/AQUA_TANK/draw_aqua_tank.py` (AQS-PLAN-006; build log and drawings in the same folder).

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
