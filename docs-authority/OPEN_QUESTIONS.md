# Open questions

Document number: AQS-OQ-001
Revision: A
Date: 2026-10-15

Questions logged while the owner is away. Each names the default the work proceeded on.

| # | Task | Question | Default proceeded on |
| --- | --- | --- | --- |
| Q-001 | X-PAR-12 | CO2 sink: methanol (about 6 x less power) was picked over enlarging the grow bed (see AQS-PAR-005 section 3). Does the owner want a larger bed for food anyway? | Methanol; bed stays 28 m2, light-limited. |
| Q-002 | X-PAR-12 | Surplus O2 (43.5 kg/d) and methanol (53.6 kg/d) leave as shipped product at NORTH_DOCK; dock water make-up 97.1 kg/d replaces the H and O they carry. Acceptable boundary flows? | Yes, shipped product (not vent). |
| Q-003 | X-PAR-12 | CLOSED (owner): genset standby, NFPA 110 exercise basis; 0.054 kg/d fuel, 0.21 kg/d O2. | - |
| Q-004 | X-PAR-12 | CLOSED (owner): H2 bank from need, 19 kg H2 / 151 kg O2 at 200 bar (was 115 kg). | - |
| Q-005 | X-PAR-12 | Roof footprint grows 32,364 -> 37,800 m2 (PV 3,392 -> 3,961 kWp) for the electrolyser (26.1 kW average). | Accepted (sizing changes approved by default). |
| Q-006 | X-PAR-02 | RESOLVED by calculation (A-M-135): no storage gap remains after ZNBR2 and the H2 bank; hydro cycle set to zero. Owner decision: remove the turbine-pump hardware (tanks stay as water inventory)? | Cycle zero; hardware kept on the graph pending removal. |
| Q-007 | X-PAR-02 | CLOSED: purge sized from published HER data (ZBFB_REVIEW2023) to 25 % LFL: 42.3 m3/h (was 30). | - |
| Q-008 | X-PAR-02 | Grow-bed carbon (A-M-141, BVAD2022): the light-limited 28 m2 bed fixes 0.85 kg CO2/d = 0.54 kg DM/d, i.e. 4.03 kg/d edible and 2.96 kg/d inedible fresh. Food fits (S14 2.81 + S14X 1.22). The inedible lines claim 12.73 kg/d (IA-RES-01 8.69 to LIGNO_PRE, IA-COMP-01 3.19 to HTC, browse 0.55, straw 0.30), 4.3 x the carbon. Choose: (a) shrink the residue product lines (lignin/cellulose board, yeast, ABE, mushrooms, hydrochar, goats) to 2.96 kg/d; or (b) grow the bed to about 120 m2 (+92 m2 at 1.69 kWh/m2/d LED = +155 kWh/d, about +40 kWp PV; it also fixes about 2.8 kg/d more CO2 and shrinks the methanol train, see Q-001). | Lines held at the study rates; the gap is carried in GROW_BED params.crop_carbon, not hidden. |
