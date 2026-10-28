# GALLEY

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 6.4 kg/d. Mass out 6.4 kg/d. Electrical duty 0.0000 kW. In: FOOD_GALLEY 4 kg/d (food issue to the galley); DUCK_GREENS 2.4 kg/d (human-grade fresh duckweed greens to the galley). Out: GALLEY_MEALS 4.84 kg/d (prepared meals to the crew); GALLEY_BIO 0.5 kg/d (galley biowaste to the larvae bin); EGGSHELL_RET 0.06 kg/d (baked crushed eggshell return (38 g Ca/d)); GAL_GREY 1 kg/d (galley wash grey water to the treatment train).

2. Size.
- Envelope 4000×3000×2400 mm, 28.8 m³. That box over this flow would be 108000.0 h if it were full. It is not a residence time.
- Envelope: 12 m2 fitout shell at the A-M-419 room basis, 2400 ceiling (AQS-HAB-001) (X-HAB sec3).
- Graph design (AQS-PAR-001 sizing): service galley / kitchen, 12 m2; area_m2 12; basis A-M-419; AQS-HAB-001.

3. Material. SS304 worktops and splashbacks, food-contact PP preparation boards; no copper-bearing alloys on food paths. Basis: food-contact sanitation class with wipe-down chemistry (AQS-HAB-001; A-M-419): 304 is sufficient at the chloride-light galley service; Cu alloys are excluded from food paths outright (AQS-STD-002 food-contact rule) Alternative: SS316 where chlorinated sanitisers concentrate (same family, higher cost). the galley biowaste stream feeds the BSFL bin (A-M-418). (X-HAB-01)

4. Nozzles. Schedule at `nozzles/GALLEY.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops GALLEYPT-01, GALLEYTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/GALLEY.stl` (a thick-walled tray at the claimed envelope; X-PAR-04). Manufacturing model `models/mfg/GALLEY/draw_galley.py` (AQS-PLAN-006; build log and drawings in the same folder).

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
