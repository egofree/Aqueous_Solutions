# MFG_SHOP

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 371.6 kg/d. Mass out 371.6 kg/d. Electrical duty 2.5500 kW. In: S08 42 kg/d (metals/Si); S08G 26.7 kg/d (glass/ceramic goods); S58 3.941 kg/d (wire product); S59 4.392 kg/d (sheet / strip); 18 more. Out: S16 12.3 kg/d (scrap); S61 1.197 kg/d (metal scrap); MFG_SCRAP_TO_IND 26.16 kg/d (manufacturing scrap return); IA-MFG-OUT 0 kg/d (goods in service); 2 more.

2. Size.
- In 610.3 kg/d, out 610.3 kg/d. No holdup claimed.

3. Material. 316L where the stream is wet. Corrosion allowance 0 mm. Pit rate is not measured.

4. Nozzles. At 1.5 m/s and 1000 kg/m³ the bore is 2.45 mm. That is not a specification. Nozzle is DN15. No flange class. Atmospheric tube or hose. Not to the room.

5. Instruments. Level and temperature where the node is a liquid holdup. High level trips the inlet.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The envelope is `cad/stl/MFG_SHOP.stl`. Manufacturing model `models/mfg/MFG_SHOP/mfg_shop.py` (AQS-PLAN-006).

8. Open items. No holdup basis for this class. S08 is the cathode split plus entrained silicate, SiO₂ 0.00005 from the rate residual, an assumption. S16 follows S08. Neither is a weighed sample. No resize.
