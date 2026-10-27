# SHELL_BUILD

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 10 kg/d. Mass out 10 kg/d. Electrical duty 0.3000 kW. In: WAX_TO_SHELL 2 kg/d (wax pattern); IA-SILICA-MU 1 kg/d (foundry silica (flour/stucco/binder make-up)); IA-SHELL-RECLAIM 7 kg/d (reclaimed shell stucco/flour). Out: SHELL_TO_BURNOUT 10 kg/d (green shell).

2. Size.
- Envelope 1500×800×1500 mm, 1.8 m³. That box over this flow would be 4320.0 h if it were full. It is not a residence time.
- Envelope basis (graph node): A-M-199 forming class at the 4 kg/kg shell duty (A-M-281); 1 d slurry/flour staging at 1600 kg/m3.
- Sizing study AQS-DUTY-072 (study): shell_kg_d 8; silica_makeup_kg_d 1; reclaim_kg_d 7; basis 6-dip shell 4 kg/kg castings, 87.5 % reclaim (A-M-281).
- Graph design (AQS-PAR-001 sizing): machine dip-coat + stucco rainfall shell-building booth; shell_kg_d 8; silica_makeup_kg_d 1; reclaim_kg_d 7; dips 6; slurry_L 40.

3. Material. PP-H slurry tank and rainfall-sander housing; silica-flour wear faces in PE; PP slurry pump; steel frame isolated from the slurry. Basis: colloidal silica slurry at pH 9-10, 100 L class (graph design A-M-281; 1 d slurry staging at 1600 kg/m3): matches the issued alkaline silica slurry family PP-H (AQS-STD-002 section 12.1 P4 row). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: 316L tank if a binder chemistry change moves the pH below neutral. slurry stays in-house; reclaim dusts are the only loose silica. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/SHELL_BUILD.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/SHELL_BUILD.stl`. Manufacturing model `models/mfg/SHELL_BUILD/draw_shell_build.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
