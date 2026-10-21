# Sizing calculation - LITHO_DEV

Document number: AQS-SIZE-LITHO_DEV
Revision: A
Date: 2026-10-20
Authority: graph + params.design: machine=wet develop bench, developer=TMAH 2.38 % class, shared WET_BENCH chemistry fork, puddle_mL_per_wafer=40.0, waste=S38-class resist/solvent loop to OIL_FRAC, duty_kW=0.008, peak_kW=0.05 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: machine=wet develop bench, developer=TMAH 2.38 % class, shared WET_BENCH chemistry fork, puddle_mL_per_wafer=40.0, waste=S38-class resist/solvent loop to OIL_FRAC, duty_kW=0.008, peak_kW=0.05 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.002 m3; vessel D 0.160021 x H 0.240032 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
