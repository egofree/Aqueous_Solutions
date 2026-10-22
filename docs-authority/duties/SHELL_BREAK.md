# SHELL_BREAK

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 10 kg/d. Mass out 10 kg/d. Electrical duty 0.4000 kW. In: INV_TO_BREAK 10 kg/d (cast + shell). Out: BREAK_TO_STOCK 2 kg/d (investment casting); SHELL_TO_GLASS 0 kg/d (spent ceramic shell to solids line); IA-SHELL-RECLAIM 7 kg/d (reclaimed shell stucco/flour); IA-SHELL-EXPORT 1 kg/d (spent foundry silica (solids return class)).

2. Size.
- Envelope 1500×800×1500 mm, 1.8 m³. That box over this flow would be 4320.0 h if it were full. It is not a residence time.
- Envelope basis (graph node): A-M-199 forming class at the spent-shell duty (A-M-281).
- Sizing study AQS-DUTY-072 (study): castings_kg_d 2; spent_shell_kg_d 8; reclaim_kg_d 7; export_kg_d 1; basis A-M-281 knock-out split.
- Graph design (AQS-PAR-001 sizing): machine vibratory shell knock-out station with reclaim sieve; spent_shell_kg_d 8; reclaim_kg_d 7; export_kg_d 1; table_kW 0.4.

3. Material. Vibratory knock-out tray with UHMW-PE wear liner, 304 stainless reclaim sieve, open-steel frame housing the dry, noncombustible silica dust. Basis: shell knock-out + stucco reclaim, 8 kg shell/d (graph design A-M-281): wear selection per the mechanical-metallurgy wear text (DIETER1988 ch. 19); the 304 reclaim sieve keeps spent silica out of the cast surface (AQS-STD-002 silicate/ceramic class handling). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: rubber-lined tray where the noise budget dominates. reclaim split 7 kg stucco + 1 kg export per the graph closure. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/SHELL_BREAK.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/SHELL_BREAK.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
