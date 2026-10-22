# CAST_LINE

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 3 kg/d. Mass out 3 kg/d. Electrical duty 0.0000 kW. In: IND_MELT_TO_CAST 3 kg/d (molten metal). Out: CAST_SCRAP_TO_IND 0 kg/d (foundry scrap); CAST_TO_ROLL 3 kg/d (billet to roll); CAST_TO_EXTRUDE 0 kg/d (billet to extrude).

2. Size.
- Envelope 1500×800×1500 mm, 1.8 m³. That box over this flow would be 14400.0 h if it were full. It is not a residence time.
- Envelope basis (graph node): A-M-199 forming class; 1 h hold-up of the Cu pour is below the class minimum.
- Sizing study AQS-DUTY-072 (study): pour_kg_d 3; products Cu ingot/billet, permanent mold; scrap_return_kg_d 0.
- Graph design (AQS-PAR-001 sizing): machine permanent-mould cast line; pour_kg_d 3; moulds 2; table_L_mm 700.

3. Material. Graphite permanent moulds with steel backing platens (Cu pour, melt 1085 C per CRC_CU); graphite launder; steel tilt table. Basis: permanent-mould Cu casting at the 3 kg/d pour (graph design; A-M-199 class): graphite is the standard Cu-mould hot face at the melt temperature and is chemically indifferent to the melt (SCHACHT2004 ch. 8; DIETER1988 tool class for the platens). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: cast-iron mould inserts if the run profile stays cold-metal short-batch (cost down, shorter mould life to be measured). mould change-out is a unit task 12 work order; no rate claimed. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/CAST_LINE.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/CAST_LINE.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
