# AIR_RECEIVER

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 192 kg/d. Mass out 192 kg/d. Electrical duty 0.0000 kW. In: S84 192 kg/d (N2 product). Out: IA-AIR-RX-OUT 192 kg/d (plant air from the receiver bank).

2. Size.
- Envelope 1000×1000×1200 mm, 1.2 m³. That box over this flow would be 150.0 h if it were full. It is not a residence time.
- Envelope: L x W x H mm, set by docs-authority/_storage_sizing.py (AQS-DUTY-064).
- Storage sizing (AQS-DUTY-064, graph design_storage): hold_d 1; V_nom_m3 0.3312; D_mm 700; H_mm 900; wall_mm 3.06.
- Node note: D-DOCK product buffer (A-M-270): S84 in from the cold box, IA-AIR-RX-OUT to HDR_N2; the surplus margin exports on IA-N2-VENT at the dock.

3. Material. SA-240 304L, welded (graph node material). Corrosion allowance per the AQS-STD-001 shop rule; no measured pit rate.

4. Nozzles. Schedule at `nozzles/AIR_RECEIVER.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/AIR_RECEIVER.stl`.

8. Open items. No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
