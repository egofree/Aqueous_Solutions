# Sizing calculation - LITHO_ALIGN

Document number: AQS-SIZE-LITHO_ALIGN
Revision: A
Date: 2026-10-20
Authority: graph + params.design: machine=contact aligner, source=365 nm LED array, 1 W optical (AQS-LITH-001), dose=10 mW/cm2 x 20 s = 200 mJ/cm2, field_mm=100, stage=leadscrew 1 mm pitch, 10 um repeatability, mask=chrome on glass, 100 um pattern | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: machine=contact aligner, source=365 nm LED array, 1 W optical (AQS-LITH-001), dose=10 mW/cm2 x 20 s = 200 mJ/cm2, field_mm=100, stage=leadscrew 1 mm pitch, 10 um repeatability, mask=chrome on glass, 100 um pattern | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.000 m3; vessel D 0.00137391 x H 0.00206087 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
