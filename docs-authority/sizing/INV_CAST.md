# Sizing calculation - INV_CAST

Document number: AQS-SIZE-INV_CAST
Revision: A
Date: 2026-10-20
Authority: graph + params.design: machine=investment casting tilt-pour station, pour_kg_d=2.0, shell_kg_d=8.0, molds_per_campaign=8 | envelope 1500 x 800 x 1500 mm, state live | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: machine=investment casting tilt-pour station, pour_kg_d=2.0, shell_kg_d=8.0, molds_per_campaign=8 | envelope 1500 x 800 x 1500 mm, state live | size check: fits

## 2. Geometry
Envelope (params.envelope): 1500 x 800 x 1500 mm, state per stamp. Working volume 0.020 m3; vessel D 0.346204 x H 0.519306 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
