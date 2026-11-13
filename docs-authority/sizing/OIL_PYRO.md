# Sizing calculation - OIL_PYRO

Document number: AQS-SIZE-OIL_PYRO
Revision: A
Date: 2026-10-20
Authority: graph + params.design: T_C=500.0, tau_h=1.0, V_work_L=1.9056, V_L=3.8111, D_mm=200, H_mm=170 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: T_C=500.0, tau_h=1.0, V_work_L=1.9056, V_L=3.8111, D_mm=200, H_mm=170 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.078 m3; vessel D 0.544369 x H 0.816554 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
