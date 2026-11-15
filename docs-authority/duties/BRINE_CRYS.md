# BRINE_CRYS

Standard: AQS-STD-001 Rev A. Graph Rev AD. Study. Not a PE stamp.

1. Basis. Mass in 2 kg/d. Mass out 2 kg/d. Electrical duty 0.0700 kW. In: IA-BRINE-SRC 2 kg/d (leach-liquor side-stream to the crystallizer). Out: IA-BRINE-CACL2 0.1162 kg/d (crystallized CaCl2 to the calcium pot (recovered, was the dock import)); IA-BRINE-MGCL2 0.03978 kg/d (crystallized MgCl2 to the magnesium pot (recovered, was the dock import)); IA-BRINE-ML 1.844 kg/d (mother liquor (residual chlorides) returned to the leach).

2. Size.
- Graph design (AQS-PAR-001 sizing): cacl2_kg_d 0.1161; mgcl2_kg_d 0.03978; feed_kg_d 2; ml_kg_d 1.844; kw 0.07.
- Node note: Brine crystallizer (A-M-496).

3. Material. Selection pending (unit task 09, AQS-STD-002 across the AQS-ASSAY-001 Rev C bounding cases). Not chosen on this page.

4. Nozzles. Schedule at `nozzles/BRINE_CRYS.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
