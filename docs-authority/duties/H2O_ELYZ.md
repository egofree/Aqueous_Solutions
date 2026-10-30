# H2O_ELYZ

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 82.64 kg/d. Mass out 82.64 kg/d. Electrical duty 21.1934 kW. In: IA-ELY-H2O 82.64 kg/d (electrolyser feed water). Out: IA-ELY-H2 9.248 kg/d (electrolyser H2); IA-ELY-O2 73.39 kg/d (electrolyser O2).

2. Size.
- Node note: X-PAR-12: PEM water electrolyser; H2 and O2 leave on separate lines (NFPA 2, ISO 22734).
- Internals (graph node): PEM stack, H2 and O2 gas-liquid separators, deoxo on H2, dryer.
- Sizing calculation pending (unit task 02). The graph node carries no design and no envelope.

3. Material. PEM stack: Ti porous transport layers, Ir/Ru mixed-oxide anode with Pt cathode catalyst, PTFE-class ionomer membrane, Ti cell hardware and PTFE compression seals; deoxo on a bed of 316L hardware; dry product H2/O2 lines on the issued M1 316L family. Basis: PEM water electrolysis (X-PAR-12 note; relief basis A-M-19 blocked-outlet class): cell hardware is metal-as-electrode per M6 with the hydride/reverse-current guards of the house rule; Ir dissolution is the electrode basis at the anode (BERNT2018); construction follows the electrolyser standards (IEC62282_3_100, ISO22734_2019). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: carbon-composite bipolar plates as the stack replacement class (PEMFC-family hardware) with the same hydride check. electrode degradation is the first-article bench basis: no rate claimed here; the P5 water feed legs are the issued house family. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/H2O_ELYZ.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops H2O_ELYZLSH-01, H2O_ELYZLT-01, H2O_ELYZPT-01, H2O_ELYZTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Node relief basis: blocked outlet at full inflow 1.789 kg/h (hydrogen side of the PEM stack at the compressor suction (h2c_P1_bar 10 bar a); O2 side on its own valve at the same set, A-M-196); operating 9 bar, design 9.9 bar g. Bore 3.3 mm. Design 990 kPa g (node design_kPa). Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
