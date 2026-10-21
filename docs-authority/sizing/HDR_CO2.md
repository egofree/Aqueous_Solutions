# Sizing calculation - HDR_CO2

Document number: AQS-SIZE-HDR_CO2
Revision: A
Date: 2026-10-20
Authority: graph + params.design: service=CO2 header (crew and cold-box in; farm and methanol-synthesis draws), kind=gas, flow_kg_s=0.0, duty_kW=None, rho_kg_m3=1.84, Q_m3_s=0.0 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: service=CO2 header (crew and cold-box in; farm and methanol-synthesis draws), kind=gas, flow_kg_s=0.0, duty_kW=None, rho_kg_m3=1.84, Q_m3_s=0.0 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.008 m3; vessel D 0.255531 x H 0.383297 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
