# RF_HEAT

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: none. Out: none.

2. Size.
- Envelope 1000×1000×1500 mm, 1.5 m³.
- Envelope basis (graph node): A-M-199 melt class; N+1 rated envelope (A-M-282).
- Sizing study AQS-DUTY-072 (study): duty_kg_d 0; connected_kW 5; backup_of IND_MELT (N+1 at equal melt duty); outage_basis IND_MELT coil/PSU outage; 100-400 kHz through-coil at the 10 kg crucible class (A-M-232 rating held; A-M-282 N+1 envelope).
- Graph design (AQS-PAR-001 sizing): service RF preheat/hold unit, N+1 at equal melt duty of IND_MELT; connected_kW 5; backup_of IND_MELT; outage_d 2; crucible_kg 10; freq_kHz 100-400; duty_note equal-duty backup of the 10 kg crucible class (A-M-282; A-M-232 rating held).

3. Material. Selection pending (unit task 09, AQS-STD-002 across the AQS-ASSAY-001 Rev C bounding cases). Not chosen on this page.

4. Nozzles. No piped process connection on the graph (un-rated or non-mass edges only); no nozzle schedule is issued yet. Nothing to size a bore against.

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/RF_HEAT.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07).
