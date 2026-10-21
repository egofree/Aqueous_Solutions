# Sizing calculation - SINTER

Document number: AQS-SIZE-SINTER
Revision: A
Date: 2026-10-20
Authority: graph + params.design: service=Ti/Mo/Cr powder sinter furnace, N+1 consolidation of ROLL, connected_kW=8.0, backup_of=ROLL, outage_d=2.0, design_case_kg_d=0.5, T_C=1300.0 | envelope 1000 x 1000 x 1500 mm, state standby_rated | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: service=Ti/Mo/Cr powder sinter furnace, N+1 consolidation of ROLL, connected_kW=8.0, backup_of=ROLL, outage_d=2.0, design_case_kg_d=0.5, T_C=1300.0 | envelope 1000 x 1000 x 1500 mm, state standby_rated | size check: fits

## 2. Geometry
Envelope (params.envelope): 1000 x 1000 x 1500 mm, state per stamp. Working volume 1.875 m3; vessel D 1.57274 x H 2.35911 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
