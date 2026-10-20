# H2O_ELYZ

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 83.65 kg/d. Mass out 83.65 kg/d. Electrical duty 21.4517 kW. In: IA-ELY-H2O 83.65 kg/d (electrolyser feed water). Out: IA-ELY-H2 9.361 kg/d (electrolyser H2); IA-ELY-O2 74.29 kg/d (electrolyser O2).

2. Size.
- Node note: X-PAR-12: PEM water electrolyser; H2 and O2 leave on separate lines (NFPA 2, ISO 22734).
- Internals (graph node): PEM stack, H2 and O2 gas-liquid separators, deoxo on H2, dryer.
- Sizing calculation pending (unit task 02). The graph node carries no design and no envelope.

3. Material. Selection pending (unit task 09, AQS-STD-002 across the AQS-ASSAY-001 Rev C bounding cases). Not chosen on this page.

4. Nozzles. Schedule at `nozzles/H2O_ELYZ.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops H2O_ELYZLSH-01, H2O_ELYZLT-01, H2O_ELYZPT-01, H2O_ELYZTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Node relief basis: blocked outlet at full inflow 1.789 kg/h (hydrogen side of the PEM stack at the compressor suction (h2c_P1_bar 10 bar a); O2 side on its own valve at the same set, A-M-196); operating 9 bar, design 9.9 bar g. Bore 3.3 mm. Design 990 kPa g (node design_kPa). Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
