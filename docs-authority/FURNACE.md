# Induction furnace module

Document number: AQS-FURN-001
Revision: A
Date: 2026-10-10
Authority: critical path item 4. Sits on AQS-MOD-001. Not a PE stamp.

Duty. Melt 50 kg of steel to 1500 °C. Sensible heat is 50 × 0.5 × 1480 = 37 MJ. Latent heat is 50 × 0.27 = 13.5 MJ. Total 50.5 MJ. At 10 kW and 40% coupling, melt time is 50.5 / (10 × 0.4) = 12.6 h. That is the honest rate on one module. A second module halves it.

Crucible. Graphite, 200 mm inside diameter, 250 mm tall, 8 L. Holds 50 kg of steel. For silicon, the same coil with a larger crucible and a slower rate. The coil does not change.

Coil. Copper tube, 8 mm, water cooled. 15 turns over 250 mm. Frequency 10 kHz. Skin depth in hot steel is under 1 mm at that frequency, so the coupling is to the surface.

Supply. 48 V DC in, resonant inverter, 10 kW. Two SB350 connectors. Capacitor bank across the coil. Current in the coil is hundreds of amperes at low voltage. The connectors carry the DC.

Cooling. Coil loss is about 6 kW. Water at 10 L/min and a 10 K rise removes 7 kW. The return goes to the Q3 bus, not to a drain.

Frame. 1200 × 600 × 800 mm. Crucible on the centerline. Inverter in the base. Coil leads out the −X face.

This furnace melts scrap and sinters the silicon charge. It does not reduce silica. Reduction is the next module.
