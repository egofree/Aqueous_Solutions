# Sizing calculation - HDR_H2

Document number: AQS-SIZE-HDR_H2
Revision: A
Date: 2026-10-20
Authority: graph + params.design: service=H2 header (EW cathode gas in, dryer and trim draws out), kind=gas, flow_kg_s=0.0, duty_kW=None, rho_kg_m3=0.084, Q_m3_s=0.0003 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: service=H2 header (EW cathode gas in, dryer and trim draws out), kind=gas, flow_kg_s=0.0, duty_kW=None, rho_kg_m3=0.084, Q_m3_s=0.0003 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.004 m3; vessel D 0.201628 x H 0.302442 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
