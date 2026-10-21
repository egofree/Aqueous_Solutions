# Sizing calculation - HDR_UPW

Document number: AQS-SIZE-HDR_UPW
Revision: A
Date: 2026-10-20
Authority: graph + params.design: service=UPW distribution header (polish skid in; fab and hab draws), kind=liquid, flow_kg_s=0.0008, duty_kW=None, rho_kg_m3=983, Q_m3_s=0.0 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: service=UPW distribution header (polish skid in; fab and hab draws), kind=liquid, flow_kg_s=0.0008, duty_kW=None, rho_kg_m3=983, Q_m3_s=0.0 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.135 m3; vessel D 0.653639 x H 0.980458 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
