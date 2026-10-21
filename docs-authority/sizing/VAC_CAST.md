# Sizing calculation - VAC_CAST

Document number: AQS-SIZE-VAC_CAST
Revision: A
Date: 2026-10-20
Authority: graph + params.design: machine=vacuum tilt-pour casting station, N+1 of CAST_LINE, connected_kW=7.5, backup_of=CAST_LINE, outage_d=2.0, design_case_kg_d=3.0 | envelope 1500 x 800 x 1500 mm, state standby_rated | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: machine=vacuum tilt-pour casting station, N+1 of CAST_LINE, connected_kW=7.5, backup_of=CAST_LINE, outage_d=2.0, design_case_kg_d=3.0 | envelope 1500 x 800 x 1500 mm, state standby_rated | size check: fits

## 2. Geometry
Envelope (params.envelope): 1500 x 800 x 1500 mm, state per stamp. Working volume 2.250 m3; vessel D 1.67128 x H 2.50692 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
