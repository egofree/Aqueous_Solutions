# Sizing calculation - MEOH_FERM

Document number: AQS-SIZE-MEOH_FERM
Revision: A
Date: 2026-10-20
Authority: graph + params.design: T_C=35, tau_h=48, V_work_L=0.72, V_L=0.96, D_mm=125, H_mm=100 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: T_C=35, tau_h=48, V_work_L=0.72, V_L=0.96, D_mm=125, H_mm=100 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.001 m3; vessel D 0.114314 x H 0.171471 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
