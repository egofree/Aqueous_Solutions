# BMED_ACID

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 1315 kg/d. Mass out 1315 kg/d. Electrical duty 5.6267 kW. In: IA-BMED-03 450.2 kg/d (CRU → BMED acid regen loop); IA-EVAP_ACID-COND 865.1 kg/d (evaporator condensate return (BMED water make-up)); IA-VS-SPENT 0.0006 kg/d (spent scrub liquor (NaCl in NaOH) to the BMED brine). Out: IA-BMED-01 1.246 kg/d (HCl product); S09 9.277 kg/d (HCl); IA-EVAP_ACID-FEED 1305 kg/d (HCl 2 M from BMED).

2. Size.
- In 108.2 kg/d, out 108.2 kg/d. No holdup claimed.

3. Material. PVC-U wetted, per AQS-STD-002 rules M1 and M2. No metal wetted part. The graph gives no temperature for this unit; above 60 °C the thermoplastic is CPVC, never metal. Corrosion allowance does not apply to the polymer. Hot LEACH draw at up to 85 °C exceeds the PVC-U limit (X-MAT-09); cooling before this unit is held under X-MAT-19 (membranes and potable water do not take CPVC as the answer).

4. Nozzles. At 1.5 m/s and 1000 kg/m³ the bore is 1.03 mm. That is not a specification. Nozzle is DN15. No flange class. Atmospheric tube or hose. Not to the room.

5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The envelope is `cad/stl/BMED_ACID.stl`.

8. Open items. No holdup basis for this class.

9. Revision (X-PAR acid-loop decision, AQS-PAR-001). BMED runs at 2 M (A-M-088). Stack power 26.93 kW from the published SEC 6.7 kWh/kg NaOH at 2 M (EDBM_WHEY_2021), was 16.13 kW. Product to EVAP_ACID on IA-EVAP_ACID-FEED; condensate returns on IA-EVAP_ACID-COND. IA-ACID-01 now leaves EVAP_ACID.
