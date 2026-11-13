# Sizing calculation - H2O_ELYZ

Document number: AQS-SIZE-H2O_ELYZ
Revision: A
Date: 2026-10-20
Authority: graph + params.design: duty=PEM electrolysis: 83.62 kg/d water -> 9.358 kg/d H2 + 74.263 kg/d O2 at 21.445 kW, kwh_per_kg_h2=55.0, machine=PEM stack skid + balance-of-plant deck (H2/O2 gas-liquid separators, deoxo on H2, dryer on H2 per params.internals), rated_kw=85.8, window_h=6.0, h2_rate_kg_h=1.5597 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: duty=PEM electrolysis: 83.62 kg/d water -> 9.358 kg/d H2 + 74.263 kg/d O2 at 21.445 kW, kwh_per_kg_h2=55.0, machine=PEM stack skid + balance-of-plant deck (H2/O2 gas-liquid separators, deoxo on H2, dryer on H2 per params.internals), rated_kw=85.8, window_h=6.0, h2_rate_kg_h=1.5597 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.185 m3; vessel D 0.726407 x H 1.08961 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
