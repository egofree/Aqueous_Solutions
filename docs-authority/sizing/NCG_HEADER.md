# Sizing calculation - NCG_HEADER

Document number: AQS-SIZE-NCG_HEADER
Revision: A
Date: 2026-10-20
Authority: graph + params.design: service=pyrolysis non-condensable gas header (OIL_FRAC in; afterburner out), kind=gas, flow_kg_s=0.0001, duty_kW=None, rho_kg_m3=0.5, Q_m3_s=0.0001 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: service=pyrolysis non-condensable gas header (OIL_FRAC in; afterburner out), kind=gas, flow_kg_s=0.0001, duty_kW=None, rho_kg_m3=0.5, Q_m3_s=0.0001 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.010 m3; vessel D 0.274783 x H 0.412174 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
