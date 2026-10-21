# Sizing calculation - BLOW_MOLD

Document number: AQS-SIZE-BLOW_MOLD
Revision: A
Date: 2026-10-20
Authority: graph + params.design: machine=continuous-extrusion blow molder, extruder_kW=2.2, clamp_kW=0.75, air_kW=0.75, rate_kg_h=2.8, run_h_d=3.0 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: machine=continuous-extrusion blow molder, extruder_kW=2.2, clamp_kW=0.75, air_kW=0.75, rate_kg_h=2.8, run_h_d=3.0 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.017 m3; vessel D 0.326752 x H 0.490128 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
