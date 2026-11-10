# HDR_H2

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 0.9889 kg/d. Mass out 0.9889 kg/d. Electrical duty 0.0000 kW. In: IA-HDR-H2-01 4.8e-05 kg/d (cathode H2 + sweep air); IA-HDR-H2-03 0.000155 kg/d (cathode H2 + sweep air); IA-HDR-H2-04 0.02551 kg/d (cathode H2 + sweep air); IA-H2-IN 0 kg/d (dried hydrogen); 10 more. Out: IA-HDR-H2-02 0.9889 kg/d (process H2).

2. Size.
- In 6.63 kg/d, out 6.63 kg/d. No holdup claimed.

3. Material. PVC-U header: wet H₂ with sweep air and possible acid mist (M3). Ignition, not embrittlement, governs; the dilution basis is held. Metal parts bonded. AQS-REV-H2-001.

4. Nozzles. At 1.5 m/s and 1000 kg/m³ the bore is 0.26 mm. That is not a specification. Nozzle is DN15. No flange class. Atmospheric tube or hose. Not to the room.

5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The solid is still an envelope. `cad/stl/HDR_H2.stl` is the outer envelope only; nothing inside it is modelled yet. Manufacturing model `models/mfg/HDR_H2/hdr_h2.py` (AQS-PLAN-006).

8. Open items. No holdup basis for this class.
