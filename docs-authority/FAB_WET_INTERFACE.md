# Fab ↔ wet-line interface

Document number: AQS-IF-FAB-WET-001  
Revision: A  
Date: 2026-09-27

Authority: AQS-EQP-FAB-001, AQS-EQP-FAB-RGN-001, AQS-PFD-FAB-001,
AQS-PFD-FAB-RGN-001, AQS-PFD-WET-001, AQS-STR-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Short interface map | 2026-09-27 |

## 1. Physical

| Side | Level | Notes |
|---|---|---|
| WAFER_FAB tools | L0 | FAB_PREP / WET_BENCH / FAB_TOOL / ETCH_RETURN |
| Wet synth forks WS_* | L-1 (intent) | Adjacent BMED / CRU / product totes; XY TBD |
| Fab UPW | L0 util | AQS-EQP-FAB-UPW-001; feed S01/S21 |

Pipe risers: acids/bases/HF up CORE_PROCESS or dedicated fab chase
(TBD). Etch return S10 down to REGEN LEACH. No shared header with
HDR_H2 or life air.

## 2. Stream crossing

| Crossing | Streams |
|---|---|
| Wet → fab reagents | S09, S31–S38 |
| Fab → wet return | S10, S39 |
| Crib solids | S08 |
| UPW | S27 (detail FAB-UPW) |
| N₂ | S03 |

## 3. Naming

EW `POLISH BANK` ≠ `FAB_UPW_*` ≠ `WS_*` synth forks.

## 4. Open

Exact nozzle schedule and chase sizing — next piping pass.
Solar-cell KOH (S35) branch remains stub until solar equipment pass.
