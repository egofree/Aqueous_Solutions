# Sizing calculation - VAC_IND

Document number: AQS-SIZE-VAC_IND
Revision: A
Date: 2026-10-20
Authority: graph + params.design: service=vacuum induction skull melt (ISM), N+1 diverse of IND_MELT, design_case_kg=2.0, connected_kW=15.0, backup_of=IND_MELT, outage_d=2.0, duty_note=equal-duty backup of the 25 kW melt at the 2 kg ISM batch class (A-M-282) | envelope 1000 x 1000 x 1500 mm, state standby_rated | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: service=vacuum induction skull melt (ISM), N+1 diverse of IND_MELT, design_case_kg=2.0, connected_kW=15.0, backup_of=IND_MELT, outage_d=2.0, duty_note=equal-duty backup of the 25 kW melt at the 2 kg ISM batch class (A-M-282) | envelope 1000 x 1000 x 1500 mm, state standby_rated | size check: fits

## 2. Geometry
Envelope (params.envelope): 1000 x 1000 x 1500 mm, state per stamp. Working volume 1.875 m3; vessel D 1.57274 x H 2.35911 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
