# Sizing calculation - HDR_N2

Document number: AQS-SIZE-HDR_N2
Revision: A
Date: 2026-10-20
Authority: graph + params.design: service=plant air / N2 header (receiver in; AHU, afterburner air, reagent sparge draws), kind=gas, flow_kg_s=0.0023, duty_kW=None, rho_kg_m3=1.2041, Q_m3_s=0.0019 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: service=plant air / N2 header (receiver in; AHU, afterburner air, reagent sparge draws), kind=gas, flow_kg_s=0.0023, duty_kW=None, rho_kg_m3=1.2041, Q_m3_s=0.0019 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.390 m3; vessel D 0.931584 x H 1.39738 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
