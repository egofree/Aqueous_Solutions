# Sizing calculation - POWDER_RESIN

Document number: AQS-SIZE-POWDER_RESIN
Revision: A
Date: 2026-10-20
Authority: graph + params.design: machine=PTFE powder line: pin mill + cyclone classifier + collector, ptfe_kg_d=0.09, mill_kWh_kg=0.05, duty_kW=0.0152, product=fine powder for compression sintering (PTFE is not melt-processable; ULLMANN_FLUOROPOLY), material=316L mill, PE-lined collector | envelope 1500 x 800 x 1500 mm, state live | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: machine=PTFE powder line: pin mill + cyclone classifier + collector, ptfe_kg_d=0.09, mill_kWh_kg=0.05, duty_kW=0.0152, product=fine powder for compression sintering (PTFE is not melt-processable; ULLMANN_FLUOROPOLY), material=316L mill, PE-lined collector | envelope 1500 x 800 x 1500 mm, state live | size check: fits

## 2. Geometry
Envelope (params.envelope): 1500 x 800 x 1500 mm, state per stamp. Working volume 0.000 m3; vessel D 0.0720134 x H 0.10802 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
