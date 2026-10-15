# Storage and generation sizing

Document number: AQS-ELEC-007
Revision: D
Date: 2026-10-15
Authority: AQS-PLAN-007 X-ELS-05. From AQS-ELEC-002 Rev C bus demand. Script `docs-authority/_power_sizing.py`. Study. Not a PE stamp. Study values in AQS-REG-002 (A-M-060 to A-M-062). Graph sources are not changed (the EW power rate change awaits the owner).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Two cases; PV, storage, inverters, backup. | 2026-10-15 |
| C | X-PAR acid-loop decision: BMED 26.93 kW, EVAP_ACID and EVAP_BASE, RECT-EW at 2.12 V / CE 0.85. Values written by `flow_graph/param/write_graph.py power`. | 2026-10-15 |

## 1. Basis

Flat 24 h profile (continuous process; study). PV yield 5.41 kWh/kWp/d before losses (NREL PVWatts, AQS-SITE-002), system derate 0.80. Night 14 h served from storage at 0.70 round-trip efficiency (ZnBr₂ flow battery class, study). Inverters in 60 kW SOL_ARK units. Backup covers critical loads for 2 days without sun.

## 2. Results

| Item | Bounding EW | Reference EW | Graph now |
| --- | --- | --- | --- |
| Bus demand, kW | 155.4 | 122.3 | PV average 144.8 |
| Energy, kWh/d | 3730 | 2935 | — |
| PV, kWp | 1077 | 848 | 1078 |
| PV area at about 5 m²/kWp, m² | 5386 | 4238 | — |
| Storage energy, kWh | 2176 | 1712 | 2176 |
| Storage power, kW | 155 | 122 | 156 |
| Inverters | 3 × 60 = 180.0 kW | 3 × 60 = 180.0 kW | 180.0 kW |

Backup. Critical loads 32 kW (HABITATION 3, CRYO_H2 4, CRYO_ASU 18, GROW_BED 5, controls 2; study list). Generator 40 kW (125 %, rounded). Two days' critical energy 1536 kWh; on H₂ at about 33 kWh/kg LHV and 40 % engine efficiency that is about 115 kg H₂ held in CRYO_H2 (study). Graph: BACKUP_GEN 2.5 kW, FUEL_CELL 4.0 kW.

## 3. Findings

Rev D (X-PAR-07, owner decision 2026-10-15: roof-only PV, grow the building). `flow_graph/param/solver.py` roof_close iterates the footprint on the 6 m bay grid until the roof, after IFC 2021 1205.3 / NFPA 1 11.12 pathways (1829 mm perimeter, 1219 mm between arrays of at most 45.72 m), carries the PV that closes the balance including the extension's own loads (IECC 2021 lighting, ASHRAE 62.1 ventilation, ISO 16798-3 fans; unconditioned hall). Converged: 120 x 96 m (20 x 16 bays, 11,520 m2, extension 11,088 m2), extension load 13.9 kW, bus 169.3 kW, PV 1174 kWp on 10,379 m2 of arrays (roof capacity 1183 kWp), ZNBR2 2371 kWh / 170 kW, SOL_ARK_60K 3 x 60 kW unchanged. Roof framing LRFD 1.72 kPa (ASCE 7-22). Ground field removed. Sensitivity: a conditioned extension needs about 33,500 m2. A-M-103 to A-M-105.

Rev C (X-PAR acid-loop decision, AQS-PAR-001, 2026-10-15). BMED_ACID at the published SEC 26.93 kW (was 16.13), EVAP_ACID 2.41 kW and EVAP_BASE 2.51 kW added (2.40 kW after the NaOH balance, X-PAR-06), RECT_EW 38.66 kW AC (was 38.02). Bus load +16.36 kW, carried on IA-PV-01. Graph: PV_ARRAY 1078 kWp (was 984), about 5390 m²; ZNBR2 2176 kWh / 156 kW (was 1987 / 142); SOL_ARK_60K 3 × 60 kW unchanged. Rev B text below keeps its own figures.

Rev B (X-RSZ-02, 2026-10-15). The bounding case is booked on the graph: PV_ARRAY 984 kWp nameplate (1968 × 0.5 kW, about 4918 m² ground field off the plate), ZNBR2 1987 kWh / 142 kW, SOL_ARK_60K 3 × 60 kW. RECT_EW (38.02 kW AC) and BMED_ACID (16.13 kW) have graph feeds; PV average raised by 54.15 kW to carry them. Items 1 and 2 below are superseded: the plate restriction is revised by the off-plate PV field (site area to confirm, X-BAS-03).


1. The graph's energy system (70 kWp PV, 120 kWh ZnBr₂, one 60 kW inverter) covers about a tenth of the calculated demand. Most of the demand is still study shares (AQS-ELEC-003); CRYO_ASU 18 kW, MFG_SHOP 12 kW and RECT-EW dominate.
2. PV at 758–984 kWp needs 3792–4918 m², far beyond the plate. Owner choices: a utility service, a smaller plant rate, or load reduction. None is taken here.
3. Pumped hydro (HYDRO_SET, about 7 kWh recoverable) does not change the result.
4. The backup generator and the H₂ store must grow with the critical list, or the critical list must shrink.
