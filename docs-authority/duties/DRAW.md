# DRAW

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: none. Out: none.

2. Size.
- Envelope 1500×800×1500 mm, 1.8 m³.
- Envelope basis (graph node): A-M-199 forming class; N+1 rated envelope (A-M-282).
- Sizing study AQS-DUTY-072 (study): rate_kg_d 0; connected_kW 3; backup_of ROLL (wire/rod bench at the 3 kg/d class); outage_basis roll-stand outage on wire-class lots; wire sizing stays MFG WIRE_DRAW S57 (A-M-282).
- Graph design (AQS-PAR-001 sizing): machine bench wire/rod draw bench, N+1 former of ROLL; connected_kW 3; backup_of ROLL; outage_d 2; bench_mm 1200; dies 6.

3. Material. Tungsten-carbide drawing dies in tool-steel casings; steel bench; die capstan hardware carries the machine lubricant programme (no wetted stream). Basis: bench wire/rod draw N+1 of ROLL (graph design): carbide die class is the wire-drawing standard at this scale (DIETER1988 ch. 20/21). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: polished diamond die only for a fine-wire last pass if the product class demands it (cost up, exotic supply). dry process; wire stock stays inside the shop loop. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/DRAW.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/DRAW.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
