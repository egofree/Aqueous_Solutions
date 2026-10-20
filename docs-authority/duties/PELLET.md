# PELLET

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.2941 kg/d. Mass out 0.2941 kg/d. Electrical duty 0.0000 kW. In: OLEFIN_TO_PELLET 0.2941 kg/d (polyolefin resin); POLYF_TO_PELLET 0 kg/d (PVDF/PTFE resin). Out: PELLET_TO_STOCK 0.2941 kg/d (pellet stock).

2. Size.
- Envelope 1500×800×1500 mm, 1.8 m³. That box over this flow would be 146875.3 h if it were full. It is not a residence time.
- Envelope basis (graph node): A-M-199 forming class; hold-up of the resin stream is below the class minimum.
- Sizing study AQS-DUTY-073 (study): pellet_kg_d 0.2941; form 2-4 mm pellets (AQS-DES-POLY).
- Graph design (AQS-PAR-001 sizing): machine underwater die-face pelletizer; rate_kg_d 0.2941; pellet_mm 2-4.

3. Material. Selection pending (unit task 09, AQS-STD-002 across the AQS-ASSAY-001 Rev C bounding cases). Not chosen on this page.

4. Nozzles. Schedule at `nozzles/PELLET.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). The envelope is `cad/stl/PELLET.stl`.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
