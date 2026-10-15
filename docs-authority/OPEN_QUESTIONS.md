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
| Q-006 | X-PAR-02 | CLOSED (owner): pumped-hydro redundancy is intentional. Restored as a diverse N+1 backup of ZNBR2 (A-M-145): NFPA 111 Level 1 Class X = 14 h night at the 32 kW critical load = 448 kWh, 18 m head, turbine 0.80: 11,417 m3 upper reservoir, held full on standby. | - |
| Q-009 | X-RED-02 | CLOSED (owner, 2026-10-16): make the building taller and build the top floors as the upper reservoir; CATCH_TANK is the lower. Parametric (AQS-BLD-014, A-M-187): 200.3 kWh at eta 0.76 (0.8 less 5 % penstock); with the 451 m3 fire reserve held as dead storage (AQS-SAF-005) the head is 35.73 m centroid to centroid and the live store 2,707 m3 (3,158 t total) on 3 reservoir levels of 3.07 m water over 367 m2 (2 cells each) from +16.8 m, roof PV at +34.8 m; CATCH_TANK 9.20 m water, floor -15.70 m. Seismic base shear from the water 15,490 kN (SDS 1.0 assumed, R 3, Ie 1.5) governs over wind 809 kN; sloshing 1.42 m within 2.63 m freeboard. HAB/FARM levels grow at 2 x shop levels. | Site seismic and wind values; X-BLD-01/03 lateral system and foundations. |
| Q-007 | X-PAR-02 | CLOSED: purge sized from published HER data (ZBFB_REVIEW2023) to 25 % LFL: 42.3 m3/h (was 30). | - |
| Q-008 | X-PAR-02 | CLOSED (owner): bed grown from need to meet the residue lines: 28 -> 120.4 m2 (A-M-151); LED, CO2 uptake, ET, O2, methanol and PV propagated. | - |
| Q-010 | X-MFG-33 | CLOSED (owner, 2026-10-16): keep the EXPANDER for redundancy. It is sized as a full working backup for the cold-box CO2 condenser chiller: N2 reverse-Brayton loop, pressure ratio 5, outlet -56 C, 220 kg/d N2 for 0.082 kW cold at -25 C, 0.44 kW net (COP 0.19 against the chiller's 2.5, acceptable for a standby). Idle in normal operation; starts on chiller failure. AQS-DUTY-069 rev C, A-M-186. | EXPANDER kept, standby; params.design carries the rated duty. |
| Q-011 | X-END-02 | End of life of the fluoropolymer parts (58 BOM lines: PVDF piping, pumps, seals; AQS-END-002). Pyrolysis would release HF, outside the HCl scrubber basis. Options: (a) mechanical regrind and re-use in non-pressure parts only; (b) add an HF-rated scrubber stage so they can be fed to OIL_PYRO; (c) substitute PVDF where another listed polymer serves. Owner picks. | Held with reason in EOL_RETURN.csv. |
