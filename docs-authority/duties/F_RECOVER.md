# F_RECOVER

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 1.52 kg/d. Mass out 1.52 kg/d. Electrical duty 0.0000 kW. In: IA-HF-SRC 1.5 kg/d (fluoride to HF); POLYF_RECLAIM 0.02 kg/d (off-spec fluoropolymer scrap/rework). Out: F_RECOVER_TO_HF_GEN 1.52 kg/d (fluoride concentrate).

2. Size.
- Sizing study AQS-DUTY-073 (study): rate_kg_d 1.52; in_leach_kg_d 1.5; in_reclaim_kg_d 0.02; vessel HF-equivalent concentrate hold tank, PE, 1 d hold.

3. Material. Selection pending (unit task 09, AQS-STD-002 across the AQS-ASSAY-001 Rev C bounding cases). Not chosen on this page.

4. Nozzles. Schedule at `nozzles/F_RECOVER.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
