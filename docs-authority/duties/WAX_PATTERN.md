# WAX_PATTERN

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 2 kg/d. Mass out 2 kg/d. Electrical duty 0.5000 kW. In: WAX_RECLAIM_TO_PATTERN 1.8 kg/d (wax condensate reclaim); IA-WAX-MU 0.2 kg/d (pattern wax make-up (petro-wax class import)). Out: WAX_TO_SHELL 2 kg/d (wax pattern).

2. Size.
- Envelope 800×600×1200 mm, 0.576 m³. That box over this flow would be 6912.0 h if it were full. It is not a residence time.
- Envelope basis (graph node): prep-class study minimum; live on the wax make-up import + 90 % reclaim (A-M-281).
- Sizing study AQS-DUTY-072 (study): wax_kg_d 2; makeup_kg_d 0.2; reclaim_kg_d 1.8; basis 1 kg wax per kg castings, 90 % reclaim (A-M-281).
- Graph design (AQS-PAR-001 sizing): bench wax pattern injection bench; wax_kg_d 2; makeup_kg_d 0.2; reclaim_kg_d 1.8; injector_kW 0.5; pot_L 10.

3. Material. 304L wax melt tank with steam/hot-water manifold; PP-H storage bins; PE drain pans. Basis: pattern-wax melt at 70-90 C (dry hydrocarbon, no corrosion load; graph design A-M-281): 304/316L hot-melt practice per ULLMANN_WAX; the PP-H bins respect the house thermoplastic temperature rule (AQS-STD-002 M5 at the 80 C P4-class house limit). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: PP-H melt tank for the 70 C case if the wax family is confirmed with a lower melt band. wax reclaim returns to the tank; no corrosive species. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/WAX_PATTERN.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/WAX_PATTERN.stl`. Manufacturing model `models/mfg/WAX_PATTERN/draw_wax_pattern.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
