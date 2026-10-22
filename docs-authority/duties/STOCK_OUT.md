# STOCK_OUT

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 36.71 kg/d. Mass out 36.71 kg/d. Electrical duty 0.0000 kW. In: ROLL_TO_STOCK 13 kg/d (plate/sheet); EXTRUDE_TO_STOCK 0 kg/d (rod/profile); DRAW_TO_STOCK 0 kg/d (wire); SINTER_TO_STOCK 0 kg/d (sintered stock); 3 more. Out: IA-STOCK-STORE 36.71 kg/d (formed metal product to the store).

2. Size.
- Envelope 1200×800×1500 mm, 1.44 m³. That box over this flow would be 941.4 h if it were full. It is not a residence time.
- Envelope basis (graph node): 1 d shop issue K at the 2000 kg/m3 staged-metal density (AQS-DUTY-064 METAL_STORE row; A-M-261 loop).
- Sizing study AQS-DUTY-072 (study): stock_out_kg_d 36.71; export_kg_d 10.81.
- Graph design (AQS-PAR-001 sizing): rack three-tier bar/plate/ingot staging rack; issue_kg_d 25.9; export_kg_d 10.81; hold_d 1.

3. Material. Mild-steel staging rack with HDPE wear pads and PE tote carts; no piped wetted service. Basis: bar/plate/ingot staging, 1 d hold at the METAL_STORE class (graph design; AQS-DUTY-064; A-M-261): dry solids storage; machine-marker class grounding (dry dust housing conductive rule M7 where chips fly). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: galvanized rack hardware for the imported-stock bay if atmospheric humidity rules. no corrosion load; wear at the pads is a spares item. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/STOCK_OUT.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/STOCK_OUT.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
