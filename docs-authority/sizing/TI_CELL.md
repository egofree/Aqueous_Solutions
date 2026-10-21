# Sizing calculation - TI_CELL

Document number: AQS-SIZE-TI_CELL
Revision: A
Date: 2026-10-20
Authority: graph + params.design: service=Kroll chlorinator + Mg-reduction retort train, chemistry=TiO2 + 2C + 2Cl2 -> TiCl4 + 2CO; TiCl4 + 2Mg -> Ti + 2MgCl2 (AQS-BAL-KROLL), tio2_kg_d=0.8342, c_kg_d=0.2509, ti_kg_d=0.5, mg_kg_d=0.5078 | envelope 800 x 800 x 1600 mm, state live | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: service=Kroll chlorinator + Mg-reduction retort train, chemistry=TiO2 + 2C + 2Cl2 -> TiCl4 + 2CO; TiCl4 + 2Mg -> Ti + 2MgCl2 (AQS-BAL-KROLL), tio2_kg_d=0.8342, c_kg_d=0.2509, ti_kg_d=0.5, mg_kg_d=0.5078 | envelope 800 x 800 x 1600 mm, state live | size check: fits

## 2. Geometry
Envelope (params.envelope): 800 x 800 x 1600 mm, state per stamp. Working volume 0.006 m3; vessel D 0.233657 x H 0.350485 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
