# Storage and generation sizing

Document number: AQS-ELEC-007
Revision: A
Date: 2026-10-15
Authority: AQS-PLAN-007 X-ELS-05. From AQS-ELEC-002 Rev C bus demand. Script `docs-authority/_power_sizing.py`. Study. Not a PE stamp. Study values in AQS-REG-002 (A-M-060 to A-M-062). Graph sources are not changed (the EW power rate change awaits the owner).

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Two cases; PV, storage, inverters, backup. | 2026-10-15 |

## 1. Basis

Flat 24 h profile (continuous process; study). PV yield 5.41 kWh/kWp/d before losses (NREL PVWatts, AQS-SITE-002), system derate 0.80. Night 14 h served from storage at 0.70 round-trip efficiency (ZnBr₂ flow battery class, study). Inverters in 60 kW SOL_ARK units. Backup covers critical loads for 2 days without sun.

## 2. Results

| Item | Bounding EW | Reference EW | Graph now |
| --- | --- | --- | --- |
| Bus demand, kW | 141.9 | 109.4 | sources 39.6 |
| Energy, kWh/d | 3406 | 2626 | — |
| PV, kWp | 984 | 758 | 70 |
| PV area at about 5 m²/kWp, m² | 4918 | 3792 | — |
| Storage energy, kWh | 1987 | 1532 | 120 |
| Storage power, kW | 142 | 109 | 60 |
| Inverters | 3 × 60 = 180.0 kW | 2 × 60 = 120.0 kW | 60 kW |

Backup. Critical loads 32 kW (HABITATION 3, CRYO_H2 4, CRYO_ASU 18, GROW_BED 5, controls 2; study list). Generator 40 kW (125 %, rounded). Two days' critical energy 1536 kWh; on H₂ at about 33 kWh/kg LHV and 40 % engine efficiency that is about 115 kg H₂ held in CRYO_H2 (study). Graph: BACKUP_GEN 2.5 kW, FUEL_CELL 4.0 kW.

## 3. Findings

Rev B (X-RSZ-02, 2026-10-15). The bounding case is booked on the graph: PV_ARRAY 984 kWp nameplate (1968 × 0.5 kW, about 4918 m² ground field off the plate), ZNBR2 1987 kWh / 142 kW, SOL_ARK_60K 3 × 60 kW. RECT_EW (38.02 kW AC) and BMED_ACID (16.13 kW) have graph feeds; PV average raised by 54.15 kW to carry them. Items 1 and 2 below are superseded: the plate restriction is revised by the off-plate PV field (site area to confirm, X-BAS-03).


1. The graph's energy system (70 kWp PV, 120 kWh ZnBr₂, one 60 kW inverter) covers about a tenth of the calculated demand. Most of the demand is still study shares (AQS-ELEC-003); CRYO_ASU 18 kW, MFG_SHOP 12 kW and RECT-EW dominate.
2. PV at 758–984 kWp needs 3792–4918 m², far beyond the plate. Owner choices: a utility service, a smaller plant rate, or load reduction. None is taken here.
3. Pumped hydro (HYDRO_SET, about 7 kWh recoverable) does not change the result.
4. The backup generator and the H₂ store must grow with the critical list, or the critical list must shrink.
