# ROLL

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 13 kg/d. Mass out 13 kg/d. Electrical duty 0.0000 kW. In: CAST_TO_ROLL 3 kg/d (billet to roll); CONT_TO_ROLL 10 kg/d (continuous billet/slab). Out: ROLL_TO_STOCK 13 kg/d (plate/sheet).

2. Size.
- Envelope 1500×800×1500 mm, 1.8 m³. That box over this flow would be 3323.1 h if it were full. It is not a residence time.
- Envelope basis (graph node): A-M-199 forming class; hold-up of the 13 kg/d charge is below the class minimum.
- Sizing study AQS-DUTY-072 (study): rolled_kg_d 13; kWh_d 0.416; basis 0.032 kWh/kg cold-rolling class (A-M-177 DIETER1988); hot rolling cheaper.
- Graph design (AQS-PAR-001 sizing): machine two-high bench rolling mill; rolled_kg_d 13; rolls_D_mm 300; roll_L_mm 640; kWh_d 0.416.

3. Material. Induction-hardened H13/D2-class alloy-steel rolls on cast-steel housings; planar roller bearings; steel frame. Basis: two-high bench mill, 13 kg/d plate/sheet incl. the Cu line (graph design; A-M-177 DIETER1988 energies): hot-work tool-steel roll class per ASM_V1/DIETER1988 ch. 20. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: cast-iron roll blanks for the short Cu runs (cost down, lighter surface class). dry metal contact - no corrosive stream; roll surface is the wear face (A-M-177). (X-MAT-22)

4. Nozzles. Schedule at `nozzles/ROLL.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/ROLL.stl`. Manufacturing model `models/mfg/ROLL/draw_roll.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
