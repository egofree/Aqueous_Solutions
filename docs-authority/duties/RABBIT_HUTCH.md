# RABBIT_HUTCH

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0000 kW. In: RABBIT_FORAGE 0 kg/d (canopy thinnings/greens: rabbit forage). Out: RABBIT_MEAT 0 kg/d (dressed rabbit meat to the food store); RABBIT_MANURE 0 kg/d (cold rabbit manure direct to the mineralisation zone); RABBIT_VAP 0 kg/d (hutch evaporation).

2. Size.
- Graph design (AQS-PAR-001 sizing): service rabbitry, 2 does + 1 buck; does 2; forage_kg_d 0.5; meat_kg_d 0.1; basis A-M-423 (X-FARM-07).

3. Material. Hot-dip galvanised wire floor, HDPE rest mats, PP nest boxes, SS316 waterers. Basis: dry pellet manure on a wire floor with rest mats against sore hocks (graph design; A-M-423): HDG wire is the rabbitry floor standard and the rest mats are the welfare contact surface Alternative: SS wire floor if galvanising wears through at the door wear points. cold manure goes direct to the soil root zones (A-M-423). (X-FARM-07)

4. Nozzles. Schedule at `nozzles/RABBIT_HUTCH.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops RABBIT_HUTCHTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
