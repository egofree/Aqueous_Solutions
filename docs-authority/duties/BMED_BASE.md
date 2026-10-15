# BMED_BASE

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 1302 kg/d. Mass out 1302 kg/d. Electrical duty 0.0000 kW. In: IA-BMED-04 502.8 kg/d (CRU → BMED base regen loop); IA-EVAP_BASE-COND 799.2 kg/d (evaporator condensate return (BMED water make-up)). Out: IA-BMED-02 0.2701 kg/d (NaOH product); IA-EVAP_BASE-FEED 1302 kg/d (NaOH 2 M from BMED); IA-VS-NAOH 0.0005 kg/d (NaOH 2 M bleed); IA-BLK-NAOH 0 kg/d (NaOH for the standby alkaline barrier (normally zero)).

2. Size.
- In 118.7 kg/d, out 118.7 kg/d. No holdup claimed.

3. Material. PVC-U wetted, per AQS-STD-002 rules M1 and M2. No metal wetted part. The graph gives no temperature for this unit; above 60 °C the thermoplastic is CPVC, never metal. Corrosion allowance does not apply to the polymer. Hot LEACH draw at up to 85 °C exceeds the PVC-U limit (X-MAT-09); cooling before this unit is held under X-MAT-19 (membranes and potable water do not take CPVC as the answer).

4. Nozzles. At 1.5 m/s and 1000 kg/m³ the bore is 1.08 mm. That is not a specification. Nozzle is DN15. No flange class. Atmospheric tube or hose. Not to the room.

5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The envelope is `cad/stl/BMED_BASE.stl`.

8. Open items. No holdup basis for this class.

9. Revision (X-PAR acid-loop decision, AQS-PAR-001). BMED runs at 2 M (A-M-088). Product to EVAP_BASE on IA-EVAP_BASE-FEED; condensate returns on IA-EVAP_BASE-COND. IA-BASE-01 and IA-BASE-PPT now leave EVAP_BASE. Stack power is booked on BMED_ACID.
