# Sizing calculation - AFTERBURNER_FLUE

Document number: AQS-SIZE-AFTERBURNER_FLUE
Revision: A
Date: 2026-10-20
Authority: graph + params.design: service=afterburner flue duct to the knock-out (flue gas at 200 C class), kind=flue, flow_kg_s=0.0016, duty_kW=None, rho_kg_m3=0.75, Q_m3_s=0.0021 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: service=afterburner flue duct to the knock-out (flue gas at 200 C class), kind=flue, flow_kg_s=0.0016, duty_kW=None, rho_kg_m3=0.75, Q_m3_s=0.0021 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.274 m3; vessel D 0.828161 x H 1.24224 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
