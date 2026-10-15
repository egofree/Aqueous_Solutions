# DIGESTER

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 1.148 kg/d. Mass out 1.148 kg/d. Electrical duty 0.4000 kW. In: IA-FERM-RES 0.345 kg/d (fermenter residue); IA-CLOSE-8 0.29 kg/d (shop scrap to the digester); IA-IL-SPENT 0.233 kg/d (spent [Bmim]OAc); IA-ABE-STILL 0.18 kg/d (ABE stillage); 2 more. Out: IA-DIG-GAS 0.625 kg/d (biogas from the biological feeds); IA-DIG-SOL 0.523 kg/d (shop scrap and spent solvent); S30 0 kg/d (digest liquor / nutrients); IA-DIG-BLK 0 kg/d (digest liquor); 1 more.

2. Size.
- V = (1.15/1000)×(480/24) = 0.0230 m³. 20 days on the whole wet feed, including the passthrough. The node class is farm.

3. Material. HDPE or PVC for the water. The frame is not the wetted part. Corrosion allowance does not apply to the polymer.

4. Nozzles. At 1.5 m/s and 1000 kg/m³ the bore is 0.11 mm. That is not a specification. Nozzle is DN15. No flange class. Atmospheric tube or hose. Not to the room.

5. Instruments. Temperature and pressure. High pressure trips the feed. Gas stays on the gas edge, not the room.

6. Relief. Atmospheric. The vent is IA-DIG-GAS to EMETH. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The envelope is `cad/stl/DIGESTER.stl`.

8. Open items. IA-FERM-RES 0.3454 kg/d, IA-STILL 0.1000 kg/d, and IA-ABE-STILL 0.1800 kg/d sum to IA-DIG-GAS 0.6254 kg/d. There is no volatile-solids measurement on those three edges, so no digestate split is calculated. IA-DIG-GAS composition is the liquid placeholder, not a gas analysis.
