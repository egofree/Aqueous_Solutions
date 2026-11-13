# Sizing calculation - BAGHOUSE

Document number: AQS-SIZE-BAGHOUSE
Revision: A
Date: 2026-10-20
Authority: graph + params.design: machine=pulse-jet dust baghouse: CS housing, tubesheet, 20-bag antistatic-polyester field, 60 deg dust hopper with rotary valve to IA-BAG-01, pulse-clean header and solenoid/diaphragm envelopes, dust_kg_d={'IA-MILL-LOSS': 6.82, 'IA-FAB-LOSS': 0.0, 'IA-WIRE-LOSS': 0.358}, hoods_m2={'IA-MILL-LOSS': 0.2, 'IA-FAB-LOSS': 0.12, 'IA-WIRE-LOSS': 0.1}, hood_face_velocity_m_s=0.5, capture_air_m3_h=756.0, ac_basis_m3_min_m2=1.2 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: machine=pulse-jet dust baghouse: CS housing, tubesheet, 20-bag antistatic-polyester field, 60 deg dust hopper with rotary valve to IA-BAG-01, pulse-clean header and solenoid/diaphragm envelopes, dust_kg_d={'IA-MILL-LOSS': 6.82, 'IA-FAB-LOSS': 0.0, 'IA-WIRE-LOSS': 0.358}, hoods_m2={'IA-MILL-LOSS': 0.2, 'IA-FAB-LOSS': 0.12, 'IA-WIRE-LOSS': 0.1}, hood_face_velocity_m_s=0.5, capture_air_m3_h=756.0, ac_basis_m3_min_m2=1.2 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.014 m3; vessel D 0.309984 x H 0.464976 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
