# PROD_MEOH

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 27.88 kg/d. Mass out 27.88 kg/d. Electrical duty 0.0000 kW. In: IA-MEOH-PROD 27.88 kg/d (methanol product). Out: IA-MEOH-SHIP 27.88 kg/d (methanol shipped at the dock).

2. Size.
- Envelope 1150×1150×1450 mm, 1.918 m³. That box over this flow would be 1651.2 h if it were full. It is not a residence time.
- Envelope: L x W x H mm, set by docs-authority/_storage_sizing.py (AQS-DUTY-064).
- Storage sizing (AQS-DUTY-064, graph design_storage): hold_d 14; V_nom_m3 0.6267; D_mm 850; H_mm 1150; wall_mm 3.
- Node note: X-PAR-12: methanol product store (carbon leaves the plant as product, no vent).

3. Material. SA-240 304L, welded (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Schedule at `nozzles/PROD_MEOH.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/PROD_MEOH.stl`.

8. Open items. No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
