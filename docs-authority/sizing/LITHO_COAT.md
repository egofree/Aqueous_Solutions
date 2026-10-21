# Sizing calculation - LITHO_COAT

Document number: AQS-SIZE-LITHO_COAT
Revision: A
Date: 2026-10-20
Authority: graph + params.design: machine=spin-coater line, chuck_mm=150, spin_rpm=5000, dispense_mL_per_wafer=2.0, softbake_C=100, chemistry=novolac resist, 1 um (AQS-LITH-001) | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: machine=spin-coater line, chuck_mm=150, spin_rpm=5000, dispense_mL_per_wafer=2.0, softbake_C=100, chemistry=novolac resist, 1 um (AQS-LITH-001) | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.002 m3; vessel D 0.160021 x H 0.240032 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
