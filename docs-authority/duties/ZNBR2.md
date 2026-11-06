# ZNBR2

Standard: AQS-STD-001 Rev A. Graph Rev BH. Study. Not a PE stamp.

1. Basis. Mass in 811.1 kg/d. Mass out 811.1 kg/d. Electrical duty 190.9992 kW. In: S69B 802.6 kg/d (NaBr after ORP); IA-ZNBR-MU 8.486 kg/d (electrolyte water make-up). Out: S69 802.6 kg/d (Br2 vapor); IA-ZNBR-BD 7.877 kg/d (electrolyte bleed); IA-ZNBR-H2 0.6098 kg/d (ZNBR2 HER hydrogen stripped with the purge air to the H2 header).

2. Size.
- Store and electrolyte thermal management are solved in the graph (X-ELS-02 / X-THM-01 F-4, A-M-455).
- Store: 2674 kWh/d cycled at round trip 0.7 (A-M-062/179); charge 3820 kWh/d.
- Electrolyte thermal-management duty: cycling loss 1146 kWh/d = 47.8 kW average thermal, rejected on IA-ZNBR-HEAT to the Q4 bus and the dry cooler.
- Charge-window sizing case: 114.6 kW thermal over the 10 h charge window; sizes the electrolyte cooling loop.
- Electrical: 190.9992 kW continuous discharge rating (storage; the charge draw rides IA-ESS-ZNBR2-CHG).
- Stack (X-MFG-43, A-M-456): 37 module bays x 95 bipolar plates of 995.2 x 500.0 mm active at the 20 mA/cm2 book fill the booked electrode area 1749.1 m2 (purge basis); j.A = current closes at 99.5 A x 172.9 V DC and 17.207 kW charge per module.
- Electrolyte (A-M-457): 69.2 kg Zn cycled per module per day at 2.0 M ZnBr2 = 529.1 L per module in a 700.0 x 700.0 x 1155.0 reservoir; Br2 inventory 169.1 kg per module; cooler 3.1 kW at the charge-window rate (A-M-455).
- Machine envelope 7900 x 6050 x 1970 mm (the X-MFG-43 rack hall, models/mfg/ZNBR2); the placement seed block (1800 x 1200 x 1600 mm) under-books it - the floor-space reservation is the named consequence (ZNBR2 WORK_ORDER W12).

3. Material. No wetted alloy. Conductors are copper. Corrosion allowance does not apply.

4. Nozzles. Origin -4848, 10000, 0 mm. Size 1800 × 1200 × 1600 mm. Inlets are the center of the −Y face. Outlets are the center of the +Y face. Atmospheric joints are hose. DN is copied from the edge and is not recalculated.
- N1, IA-E-ZNIN, inlet, -Y face center, -3948, 10000, 800 mm. Height 800 mm from the bottom. Rating conductor. Not a hose.
- N2, IA-ESS-ZNBR2-CHG, inlet, -Y face center, -3948, 10000, 800 mm. Height 800 mm from the bottom. Rating conductor. Not a hose.
- N3, IA-ZNBR-MU, inlet, -Y face center, -3948, 10000, 800 mm. Height 800 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N4, S69B, inlet, -Y face center, -3948, 10000, 800 mm. Height 800 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N5, IA-ESS-ZNBR2-DIS, outlet, +Y face center, -3948, 11200, 800 mm. Height 800 mm from the bottom. Rating conductor. Not a hose.
- N6, IA-ZNBR-BD, outlet, +Y face center, -3948, 11200, 800 mm. Height 800 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N7, IA-ZNBR-HEAT, outlet, +Y face center, -3948, 11200, 800 mm. Height 800 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
- N8, IA-ZNBR-LOSS, outlet, +Y face center, -3948, 11200, 800 mm. Height 800 mm from the bottom. Rating conductor. Not a hose.
- N9, S69, outlet, +Y face center, -3948, 11200, 800 mm. Height 800 mm from the bottom. Bore not calculated. Rating hose, atmospheric.
5. Instruments. Current. Overcurrent opens the breaker.

6. Relief. Atmospheric. No vent edge. Not to the room. Stored design_kPa is the old head-plus-10 figure. It is not a set point.
7. Code. Shop. Not stamped. The envelope is `cad/stl/ZNBR2.stl`. Manufacturing model `models/mfg/ZNBR2/znbr2.py` (AQS-PLAN-006).

8. Open items. This unit has not been measured.
