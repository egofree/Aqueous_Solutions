# Sizing calculation - DRY_COOLER

Document number: AQS-SIZE-DRY_COOLER
Revision: A
Date: 2026-10-20
Authority: graph + params.design: duty=dry rejection of the ADS_CHILL 7.25 kW + the Q4 dry share + the ZNBR2 cycling heat, airflow_m3_s=10.64, fan_kw=7.9 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: duty=dry rejection of the ADS_CHILL 7.25 kW + the Q4 dry share + the ZNBR2 cycling heat, airflow_m3_s=10.64, fan_kw=7.9 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.000 m3; vessel D 0.00137391 x H 0.00206087 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
