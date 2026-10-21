# Sizing calculation - EVAP_ACID

Document number: AQS-SIZE-EVAP_ACID
Revision: A
Date: 2026-10-20
Authority: graph + params.design: unit=EVAP_ACID, T_boil_C=108.6, T_cond_C=114.6, p_body_kPa=101.325, p_shell_kPa=166.98, ratio=1.648 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: unit=EVAP_ACID, T_boil_C=108.6, T_cond_C=114.6, p_body_kPa=101.325, p_shell_kPa=166.98, ratio=1.648 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 2.610 m3; vessel D 1.75595 x H 2.63393 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
