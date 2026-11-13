# BMED_BASE

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 1302 kg/d. Mass out 1302 kg/d. Electrical duty 0.0000 kW. In: IA-BMED-04 490.8 kg/d (CRU → BMED base regen loop); IA-EVAP_BASE-COND 811.2 kg/d (evaporator condensate return (BMED water make-up)). Out: IA-BMED-02 0.2701 kg/d (NaOH product); IA-EVAP_BASE-FEED 1302 kg/d (NaOH 2 M from BMED); IA-VS-NAOH 0.0005 kg/d (NaOH 2 M bleed).

2. Size.
- In 118.7 kg/d, out 118.7 kg/d. No holdup claimed.

3. Material. Wetted path of PVC-U (spacer frames, gasket seals, drip tray, nozzles; above 60 C the thermoplastic class is CPVC) with the two electrode end plates as the only wetted metal, allowed as BMED electrodes per M6: Ti/MMO anode end plate and 316L annealed cathode end plate; 316L tie rods clamping the stack from outside the wetted and vapour zone per M4. Basis: AQS-STD-002 M2 holds the chlor-alkali and acid-regeneration systems on PVC-U, and M3 bans a wetted metal part in the reducing catholyte unless M6 names it; M6 names the BMED electrodes, and its hydrogen clause decides the cathode-plate alloy between 316L and nickel: metal in wet H2 or at a cathode is austenitic stainless or titanium only with the H2 partial pressure and temperature stated, and titanium at a cathode is held for hydriding, so the plate is 316L annealed - nickel has no M6 basis, and AQS-REV-H2-001 names 316L annealed for EW cathodes, the same cathode class. The anode plate takes the Ti/MMO dimensionally-stable-anode class of section 9 (chloride, anodic Cl2). The tie rods sit outside the wetted envelope and stay isolated from the liquor path (M4). Inlets arrive trim-cooled at 35 C (X-MAT-19), inside the PVC-U M5 limits on the polymer path. X-QA-13 reselection of the former undecided 316L-or-nickel cathode-plate class. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: Nickel 200 cathode hardware only if the caustic compartment later runs hot strong caustic above the 316L class (ULLMANN_NAOH nickel practice); CPVC frames if the loop moves above 60 C. wetted by the NaOH base-side loop; the electrode end plates are the M6 hardware and the tie rods the external clamp steel - no other metal is wetted. (X-QA-13)

4. Nozzles. At 1.5 m/s and 1000 kg/m³ the bore is 1.08 mm. That is not a specification. Nozzle is DN15. No flange class. Atmospheric tube or hose. Not to the room.

5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The envelope is `cad/stl/BMED_BASE.stl`. Manufacturing model `models/mfg/BMED_BASE/bmed_base.py` (AQS-PLAN-006).

8. Open items. No holdup basis for this class.

9. Revision (X-PAR acid-loop decision, AQS-PAR-001). BMED runs at 2 M (A-M-088). Product to EVAP_BASE on IA-EVAP_BASE-FEED; condensate returns on IA-EVAP_BASE-COND. IA-BASE-01 and IA-BASE-PPT now leave EVAP_BASE. Stack power is booked on BMED_ACID.
