# Sizing calculation - FILM_CAST

Document number: AQS-SIZE-FILM_CAST
Revision: A
Date: 2026-10-20
Authority: graph + params.design: machine=PVDF cast film/sheet line, extruder_D_mm=25, die_mm=200, chill_roll_D_mm=150, pvdf_kg_d=0.14, melt_C=220 | envelope 1500 x 800 x 1500 mm, state live | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: machine=PVDF cast film/sheet line, extruder_D_mm=25, die_mm=200, chill_roll_D_mm=150, pvdf_kg_d=0.14, melt_C=220 | envelope 1500 x 800 x 1500 mm, state live | size check: fits

## 2. Geometry
Envelope (params.envelope): 1500 x 800 x 1500 mm, state per stamp. Working volume 0.000 m3; vessel D 0.0834402 x H 0.12516 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
