# Sizing calculation - COMB_HEAT

Document number: AQS-SIZE-COMB_HEAT
Revision: A
Date: 2026-10-20
Authority: graph + params.design: service=combustion reheating furnace (C5-C10 fuel class), tertiary N+1 of IND_MELT, connected_kW=0.05, thermal_kW=30.0, backup_of=IND_MELT, outage_d=2.0, offgas=to MET_SCRUB when energized (COMB_OFFGAS) | envelope 1000 x 1000 x 1500 mm, state standby_rated | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: service=combustion reheating furnace (C5-C10 fuel class), tertiary N+1 of IND_MELT, connected_kW=0.05, thermal_kW=30.0, backup_of=IND_MELT, outage_d=2.0, offgas=to MET_SCRUB when energized (COMB_OFFGAS) | envelope 1000 x 1000 x 1500 mm, state standby_rated | size check: fits

## 2. Geometry
Envelope (params.envelope): 1000 x 1000 x 1500 mm, state per stamp. Working volume 1.875 m3; vessel D 1.57274 x H 2.35911 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
