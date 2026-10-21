# Sizing calculation - SOLAR_PV_CELL

Document number: AQS-SIZE-SOLAR_PV_CELL
Revision: A
Date: 2026-10-20
Authority: graph + params.design: cells_per_d=3, tools=[{'id': 'PV-TEX-01', 'design': 'KOH texture bath, 10 L PP tank, immersion heater', 'peak_kW': 1.9835999950403127, 'kWh_d': 0.6870259209662386}, {'id': 'PV-EMIT-01', 'design': 'POCl3 diffusion, quartz tube 200 mm x 1.0 m, 200 mm ceramic fibre', 'peak_kW': 3.7942691188488986, 'kWh_d': 5.876082069096683}, {'id': 'PV-PSG-01', 'design': 'HF PSG etch, room temperature PP bath', 'peak_kW': 0.0, 'kWh_d': 0.0}, {'id': 'PV-ARC-01', 'design': 'PECVD SiNx, parallel-plate RF, 5 kg heated platen, dry vacuum pump', 'peak_kW': 2.2514027215504537, 'kWh_d': 1.9534860548837867}, {'id': 'PV-CON-01', 'design': 'Screen printer and 200 C dryer', 'peak_kW': 0.7, 'kWh_d': 0.35}, {'id': 'PV-FIRE-01', 'design': 'IR lamp fast-firing furnace', 'peak_kW': 3.0, 'kWh_d': 0.51}, {'id': 'PV-IV-01', 'design': 'Flash IV tester', 'peak_kW': 0.1, 'kWh_d': 0.025}], kWh_d=9.401594044946709, avg_kW=0.3917330852061129, peak_kW=3.7942691188488986, kWh_per_cell=3.133864681648903 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: cells_per_d=3, tools=[{'id': 'PV-TEX-01', 'design': 'KOH texture bath, 10 L PP tank, immersion heater', 'peak_kW': 1.9835999950403127, 'kWh_d': 0.6870259209662386}, {'id': 'PV-EMIT-01', 'design': 'POCl3 diffusion, quartz tube 200 mm x 1.0 m, 200 mm ceramic fibre', 'peak_kW': 3.7942691188488986, 'kWh_d': 5.876082069096683}, {'id': 'PV-PSG-01', 'design': 'HF PSG etch, room temperature PP bath', 'peak_kW': 0.0, 'kWh_d': 0.0}, {'id': 'PV-ARC-01', 'design': 'PECVD SiNx, parallel-plate RF, 5 kg heated platen, dry vacuum pump', 'peak_kW': 2.2514027215504537, 'kWh_d': 1.9534860548837867}, {'id': 'PV-CON-01', 'design': 'Screen printer and 200 C dryer', 'peak_kW': 0.7, 'kWh_d': 0.35}, {'id': 'PV-FIRE-01', 'design': 'IR lamp fast-firing furnace', 'peak_kW': 3.0, 'kWh_d': 0.51}, {'id': 'PV-IV-01', 'design': 'Flash IV tester', 'peak_kW': 0.1, 'kWh_d': 0.025}], kWh_d=9.401594044946709, avg_kW=0.3917330852061129, peak_kW=3.7942691188488986, kWh_per_cell=3.133864681648903 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.000 m3; vessel D 0.0346199 x H 0.0519298 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
