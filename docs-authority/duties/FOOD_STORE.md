# FOOD_STORE

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 10.66 kg/d. Mass out 10.66 kg/d. Electrical duty 0.0000 kW. In: S14 4.2 kg/d (food); EGG_HARVEST 0.6 kg/d (eggs to the food store); FISH_HARVEST 0.81 kg/d (fish harvest to the food store); DUCK_EGGS 0.34 kg/d (duck eggs to the food store); 5 more. Out: S14D 4.2 kg/d (food); FOOD_GALLEY 4 kg/d (food issue to the galley); FOOD_HAB 2.46 kg/d (food issue to the habitation (direct)); FOOD_EXPORT 0 kg/d (surplus food to the reserve/trade boundary).

2. Size.
- Envelope 650×650×750 mm, 0.3169 m³. That box over this flow would be 713.5 h if it were full. It is not a residence time.
- Envelope: L x W x H mm, set by docs-authority/_storage_sizing.py (AQS-DUTY-064).
- Storage sizing (AQS-DUTY-064, graph design_storage): hold_d 80; V_nom_m3 0.042; D_mm 350; H_mm 450; wall_mm 4.75.
- Node note: D-DOCK product buffer (A-M-270): S14 harvest in, S14D galley draw out; the sized hold is the 80 d dry-matter reserve.

3. Material. PE (rotomoulded / fabricated) (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Schedule at `nozzles/FOOD_STORE.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/FOOD_STORE.stl`.

8. Open items. No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
