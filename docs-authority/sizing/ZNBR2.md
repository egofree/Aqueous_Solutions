# Sizing calculation - ZNBR2

Document number: AQS-SIZE-ZNBR2
Revision: A
Date: 2026-10-20
Authority: graph + params.design: machine=ZnBr2 flow-battery store: 38 module bays (one per hybrid inverter, AQS-ELEC-008), each a bipolar plate stack over its electrolyte reservoir, pumps and electrolyte cooler, modules=38, module_kwh=72.2, module_charge_kw_ac=23.45, plates_per_module=95, plate_active_L_mm=994.5 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: machine=ZnBr2 flow-battery store: 38 module bays (one per hybrid inverter, AQS-ELEC-008), each a bipolar plate stack over its electrolyte reservoir, pumps and electrolyte cooler, modules=38, module_kwh=72.2, module_charge_kw_ac=23.45, plates_per_module=95, plate_active_L_mm=994.5 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 1.664 m3; vessel D 1.5115 x H 2.26725 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
