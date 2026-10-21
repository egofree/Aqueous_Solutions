# Sizing calculation - RES_HEAT

Document number: AQS-SIZE-RES_HEAT
Revision: A
Date: 2026-10-20
Authority: graph + params.design: service=resistance radiant reheating furnace, N+1 of SHELL_BURNOUT/SINTER heating, connected_kW=12.0, backup_of=SHELL_BURNOUT/SINTER, outage_d=2.0, T_C=900.0 | envelope 1000 x 1000 x 1500 mm, state standby_rated | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: service=resistance radiant reheating furnace, N+1 of SHELL_BURNOUT/SINTER heating, connected_kW=12.0, backup_of=SHELL_BURNOUT/SINTER, outage_d=2.0, T_C=900.0 | envelope 1000 x 1000 x 1500 mm, state standby_rated | size check: fits

## 2. Geometry
Envelope (params.envelope): 1000 x 1000 x 1500 mm, state per stamp. Working volume 1.875 m3; vessel D 1.57274 x H 2.35911 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
