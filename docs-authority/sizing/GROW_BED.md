# Sizing calculation - GROW_BED

Document number: AQS-SIZE-GROW_BED
Revision: A
Date: 2026-10-20
Authority: graph + params.design: grow_bed_layout_mm={'interior_xy_mm': [7280, 4000], 'wall_mm': 15, 'canopy_top_mm': 900, 'rail_allowance_mm': 10.6, 'bay_module_mm': [2000, 1000, 400]} | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: grow_bed_layout_mm={'interior_xy_mm': [7280, 4000], 'wall_mm': 15, 'canopy_top_mm': 900, 'rail_allowance_mm': 10.6, 'bay_module_mm': [2000, 1000, 400]} | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.157 m3; vessel D 0.6883 x H 1.03245 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
