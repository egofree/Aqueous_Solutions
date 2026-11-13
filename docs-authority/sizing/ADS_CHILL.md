# Sizing calculation - ADS_CHILL

Document number: AQS-SIZE-ADS_CHILL
Revision: A
Date: 2026-10-20
Authority: graph + params.design: duty=silica gel-water adsorption chiller: 5 kW drive at 65 C -> 2.25 kW chilled at 12 C, 7.25 kW rejected, chilled_kw=2.25, cop_thermal=0.45 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: duty=silica gel-water adsorption chiller: 5 kW drive at 65 C -> 2.25 kW chilled at 12 C, 7.25 kW rejected, chilled_kw=2.25, cop_thermal=0.45 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.000 m3; vessel D 0.00137391 x H 0.00206087 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
