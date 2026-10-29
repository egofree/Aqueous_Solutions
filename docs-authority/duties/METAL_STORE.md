# METAL_STORE

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 36.94 kg/d. Mass out 36.94 kg/d. Electrical duty 0.0000 kW. In: IA-STOCK-STORE 36.71 kg/d (formed metal product to the store); IA-SI-IMPORT 0.2264 kg/d (imported polysilicon for the CZ charge). Out: STOCK_TO_MFG 25.9 kg/d (plate/rod/wire to manufacturing); STOCK_TO_FAB 0.2264 kg/d (polysilicon CZ charge from the store); STOCK_TO_WIRE_DRAW 0 kg/d (rod/wire for final sizing); IA-METAL-SHIP 10.81 kg/d (surplus foundry metal export (pot-line product, dispatch campaign)).

2. Size.
- Envelope 800×800×950 mm, 0.608 m³. That box over this flow would be 395.0 h if it were full. It is not a residence time.
- Envelope: L x W x H mm, set by docs-authority/_storage_sizing.py (AQS-DUTY-064).
- Storage sizing (AQS-DUTY-064, graph design_storage): hold_d 14; V_nom_m3 0.1225; D_mm 500; H_mm 650; wall_mm 4.75.
- Node note: D-DOCK product buffer (A-M-270): IA-STOCK-STORE in, STOCK_TO_* draws out at steady state.

3. Material. PE (rotomoulded / fabricated) (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Schedule at `nozzles/METAL_STORE.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/METAL_STORE.stl`.

8. Open items. No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
