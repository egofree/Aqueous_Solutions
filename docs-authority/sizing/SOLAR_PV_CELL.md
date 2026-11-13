# Sizing calculation - SOLAR_PV_CELL

Document number: AQS-SIZE-SOLAR_PV_CELL
Revision: A
Date: 2026-10-20
Authority: graph + params.design: need={'route': 'CZ_PSQ125', 'array_kw': 2718.0, 'life_yr': 39.99999999999999, 'repl_per_yr': 0.025500000000000005, 'W_d': 189.75770020533884, 'cell_area_cm2': 148.5798641851732, 'cell_eff': 0.19, 'cell_W': 2.823017419518291, 'cells_per_d': 67.21804084287882, 'wafer_g': 6.228765066370831, 'slot_g': 13.581752994953481, 'wafer_kg_d': 0.4186853846320113, 'slot_kg_d': 0.9129388275326749, 't_cm': 0.018, 'kerf_cm': 0.015, 'Si_g_per_W': 4.811076581054544}, cells_per_d=67.21804084287882, batches=3, carrier=25, tools=[{'id': 'PV-TEX-01', 'design': 'KOH texture bath, 10 L PP tank, immersion heater, one carrier a batch', 'peak_kW': 1.9835999950403127, 'kWh_d': 0.7838555406764935}, {'id': 'PV-EMIT-01', 'design': 'POCl3 diffusion, quartz tube 200 mm x 1.0 m, 200 mm ceramic fibre, boat of 210 slots', 'peak_kW': 3.7942691188488986, 'kWh_d': 7.353509195683369}, {'id': 'PV-PSG-01', 'design': 'HF PSG etch, room temperature PP bath', 'peak_kW': 0.0, 'kWh_d': 0.0}, {'id': 'PV-ARC-01', 'design': 'PECVD SiNx, parallel-plate RF, 0.37 m2 electrode in a 788 mm chamber, dry vacuum pump', 'peak_kW': 6.077477661970402, 'kWh_d': 7.723503008647393}, {'id': 'PV-CON-01', 'design': 'Screen printer and 200 C dryer', 'peak_kW': 0.7, 'kWh_d': 7.842104765002529}, {'id': 'PV-FIRE-01', 'design': 'IR lamp fast-firing furnace', 'peak_kW': 3.0, 'kWh_d': 11.427066943289399}, {'id': 'PV-IV-01', 'design': 'Flash IV tester', 'peak_kW': 0.1, 'kWh_d': 0.5601503403573236}], kWh_d=35.69018979365651 | envelope  mm, state None | size check: fits. Study. Not a PE stamp.

## 1. Duty
params.design: need={'route': 'CZ_PSQ125', 'array_kw': 2718.0, 'life_yr': 39.99999999999999, 'repl_per_yr': 0.025500000000000005, 'W_d': 189.75770020533884, 'cell_area_cm2': 148.5798641851732, 'cell_eff': 0.19, 'cell_W': 2.823017419518291, 'cells_per_d': 67.21804084287882, 'wafer_g': 6.228765066370831, 'slot_g': 13.581752994953481, 'wafer_kg_d': 0.4186853846320113, 'slot_kg_d': 0.9129388275326749, 't_cm': 0.018, 'kerf_cm': 0.015, 'Si_g_per_W': 4.811076581054544}, cells_per_d=67.21804084287882, batches=3, carrier=25, tools=[{'id': 'PV-TEX-01', 'design': 'KOH texture bath, 10 L PP tank, immersion heater, one carrier a batch', 'peak_kW': 1.9835999950403127, 'kWh_d': 0.7838555406764935}, {'id': 'PV-EMIT-01', 'design': 'POCl3 diffusion, quartz tube 200 mm x 1.0 m, 200 mm ceramic fibre, boat of 210 slots', 'peak_kW': 3.7942691188488986, 'kWh_d': 7.353509195683369}, {'id': 'PV-PSG-01', 'design': 'HF PSG etch, room temperature PP bath', 'peak_kW': 0.0, 'kWh_d': 0.0}, {'id': 'PV-ARC-01', 'design': 'PECVD SiNx, parallel-plate RF, 0.37 m2 electrode in a 788 mm chamber, dry vacuum pump', 'peak_kW': 6.077477661970402, 'kWh_d': 7.723503008647393}, {'id': 'PV-CON-01', 'design': 'Screen printer and 200 C dryer', 'peak_kW': 0.7, 'kWh_d': 7.842104765002529}, {'id': 'PV-FIRE-01', 'design': 'IR lamp fast-firing furnace', 'peak_kW': 3.0, 'kWh_d': 11.427066943289399}, {'id': 'PV-IV-01', 'design': 'Flash IV tester', 'peak_kW': 0.1, 'kWh_d': 0.5601503403573236}], kWh_d=35.69018979365651 | envelope  mm, state None | size check: fits

## 2. Geometry
Envelope (params.envelope): 0 x 0 x 0 mm, state per stamp. Working volume 0.001 m3; vessel D 0.121165 x H 0.181748 mm (upright, H/D 1.5).

## 3. Material
PE/rotomoulded (default per AQS-STD-002 M2).

## 4. Fit
Envelope-consistent by construction; check vs cad/stl envelope STL (test_envelopes gate).
