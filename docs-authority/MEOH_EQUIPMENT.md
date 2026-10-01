# Methanol train equipment list

Document number: AQS-EQP-MEOH-001  
Revision: A  
Date: 2026-10-01  
PFD: AQS-PFD-MEOH-001 (`meoh_train_pfd.png`)  
Authority: AQS-MeOH-001, AQS-REQ-KW-001, AQS-FC-001 Rev B, AQS-ASM-001,
AQS-HSE-001, AQS-VENT-001, DEPENDENCIES.md (SI-IEM-01).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Dual-source MeOH + IEM-FC equipment tags | 2026-10-01 |

Licence: CERN-OHL-S-2.0. `SCALE_M = 1.0`.

## 1. Locked unit tags

| Tag | Duty | Status |
|---|---|---|
| MEOH_DAC_OR_CO2 | CO₂ intake: CRYO_CO2 / flue-cap / optional DAC | Issued — architecture |
| MEOH_IEM_CELL | Electrochemical CO₂→MeOH intermediates on **IEM** (SEM-Tech preferred) | Issued — study; SI-IEM-01 |
| MEOH_SYNTH | Catalytic CO₂+3H₂→MeOH reactor (SI-MEOH-01/02 class, **scaled**) | Issued — study P/T; MAWP on AQS-ASM-001 |
| MEOH_COMP_H2 | H₂ boost if CRYO_H2 P insufficient for synth | Stub — P TBD |
| MEOH_COND | Condenser / crude MeOH-water | Issued |
| MEOH_DIST | Distillation / polish to fuel grade | Issued — duty TBD |
| MEOH_TANK | Bulk MeOH store 50–200 L study | Issued — Atm / low-P |
| MEOH_DAY_TANK | Day tank at FC 20–50 L | Issued |
| MEOH_FERM_DIG | Digester / methylotrophic ferment on farm-hab waste | Partial |
| MEOH_FERM_STILL | Biogenic MeOH recovery still | Partial |
| MEOH_FC | **IEM-DMFC** stack bank (SI-DMFC-01 packaging OK) | Issued — 0.5–2 kW_dc cont. |
| MEOH_DCDC | DC/DC into Sol-Ark BATT 160–700 V | Issued |
| MEOH_HX_Q4 | Low-grade heat → Q4 (S80) | Issued |
| MEOH_HX_Q3 | Synth exotherm → Q3 / oil preheat stub | Stub |
| MEOH_VENT_KO | Exhaust KO before Claimed CO₂ return (S82) | Issued |
| MEOH_LEL | LEL / VOC detection + fuel trip | Issued — HSE |

## 2. Continuous ratings (requirements)

See AQS-REQ-KW-001 §3.6. **REQ-MEOH-FC-CONT = 0.5–2 kW_dc.**  
Synth electric / heat: study; catalytic path is thermally driven with
compressor loads TBD (do not invent full-plant kW beyond H₂ allocation).

## 3. Separation rules

1. MEOH_FC ≠ BACKUP_GEN; ≠ RECT hard-tee.
2. MEOH liquid piping = new class **PC-11** (AQS-ASM-001) — flammable;
   not PC-06 potable.
3. PEM FC manifolds (S49/S50) remain isolated from MeOH day tank.
4. Spill to HDR_ORG / bonded sump — never CATCH / ROOF potable.
5. No free outdoor MeOH vapor dump (AQS-VENT-001).

## 4. Regenerate

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 meoh_train_pfd.py
```
