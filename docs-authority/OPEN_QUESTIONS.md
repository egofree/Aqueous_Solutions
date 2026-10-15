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
| Q-009 | X-RED-02 | Where does the upper reservoir go? Rev 2026-10-16: the critical load fell 32 -> 14.32 kW (CRYO_ASU 18 -> 1.67 kW by X-MFG-33, CRYO_H2 from its compressor design), so the backup store is 200 kWh (14 h x 14.32 kW) and every volume is 0.45 x the earlier figure. Trade study AQS-RED-002 (HYDRO_SITING.md), eta 0.8, V = E/(rho g h eta). A roof 5,110 m3 at 18 m (25.5 m dia x 10 m, about 5,100 t on the roof; the present roof tank is 200 m3), still not credible. B tower 25/30/40/50 m: 3,679/3,066/2,299/1,839 m3, 0.25-0.49 MPa, AWWA D100 tower and foundation. C hillside 50/100/200 m: 1,839/920/460 m3 lined pond at grade, 0.49-1.96 MPa penstock, needs site relief (survey). D deep shaft 100-500 m: 920-184 m3, 307 m3 at 300 m (2.94 MPa casing), terrain-independent but geology-dependent. Owner picks A-D and head. | Volume carried in HYDRO_SET params (5,109 m3 at 18 m); roof tank left at 200 m3 until sited. |
| Q-007 | X-PAR-02 | CLOSED: purge sized from published HER data (ZBFB_REVIEW2023) to 25 % LFL: 42.3 m3/h (was 30). | - |
| Q-008 | X-PAR-02 | CLOSED (owner): bed grown from need to meet the residue lines: 28 -> 120.4 m2 (A-M-151); LED, CO2 uptake, ET, O2, methanol and PV propagated. | - |
| Q-010 | X-MFG-33 | The cold box has no air intake and its N2 feed is already 99.9 % N2 once CO2 is out, so the redesign (AQS-DUTY-069) needs no cryogenic column and the EXPANDER refrigeration loop (1,576 kg/d, 0.61 kW, models/mfg/EXPANDER) has no duty. Retire the EXPANDER and its model, or keep it for a future air-intake case? | Loop set idle (0 kg/d, 0 kW); unit and model kept until decided. |
