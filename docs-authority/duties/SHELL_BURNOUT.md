# SHELL_BURNOUT

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 10 kg/d. Mass out 10 kg/d. Electrical duty 0.2500 kW. In: SHELL_TO_BURNOUT 10 kg/d (green shell). Out: BURNOUT_TO_CAST 8 kg/d (fired shell); WAX_RECLAIM_TO_PATTERN 1.8 kg/d (wax condensate reclaim); WAX_TO_OIL 0 kg/d (unrecovered wax to oil line); IA-BURNOUT-VENT 0.2 kg/d (dewax/burnout off-gas (burned wax + steam)).

2. Size.
- Envelope 1000×1000×1500 mm, 1.5 m³. That box over this flow would be 3600.0 h if it were full. It is not a residence time.
- Envelope basis (graph node): A-M-199 melt class at the fired-shell duty (A-M-281).
- Sizing study AQS-DUTY-072 (study): shell_kg_d 8; wax_reclaim_kg_d 1.8; burned_wax_kg_d 0.2; T_C 900; basis flash dewax + fire at 900 C (A-M-281).
- Graph design (AQS-PAR-001 sizing): service flash-dewax + shell fire furnace, 900 C; shell_kg_d 8; wax_reclaim_kg_d 1.8; burned_wax_kg_d 0.2; T_C 900; kW 0.25; condenser wax condensate to WAX_PATTERN.

3. Material. Alumina-silica kiln hot face + castable hearth, 80Ni-20Cr elements, mild-steel casing; 304L wax condenser on the condensate leg. Basis: flash dewax + shell fire at 900 C (graph design; A-M-281): lining class per SCHACHT2004 ch. 4/13; element class to 1100 C per ASM_V1; condensate is recovered wax (ULLMANN_WAX). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: SiC elements if element-zone hot spotting appears at the first-article campaign. dewax off-gas books to IA-BURNOUT-VENT (dry hot M7); no measured rate claimed. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/SHELL_BURNOUT.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Vent edge IA-BURNOUT-VENT on the graph (to NORTH_DOCK). Atmospheric operation is not claimed beyond this edge. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/SHELL_BURNOUT.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
