# Load rollup — foundry, polymers, grease

Document number: AQS-PWR-ROLLUP  
Revision: A  
Date: 2026-10-17  
Authority: graph Rev X. Not a PE stamp.  
Design assumptions. Not a measured load.

## Electrical loads added since Rev BH

| Unit | Sector | kW | Duty |
|------|--------|---:|------|
| IND_MELT | FOUNDRY | 25 | Batch induction. Not continuous. |
| VAC_IND | FOUNDRY | 15 | ISM/CCIM. Batch. |
| RF_HEAT | FOUNDRY | 5 | Preheat / sinter. |
| OIL_PYRO | OIL | 15 | Induction pyrolyzer (assumed, same class as small melt). |
| HF_GEN / monomer | POLYMERS | 5 | ED and small reactors. |
| GREASE_CA / GREASE_LI | OIL | 2 | Kettle heat. Resistive hold acceptable. |
| **Peak if overlapped** | | **~67** | Unlikely. Schedule batches. |
| **Average** | | **~20** | Order of magnitude. |

These sit on the existing RECTIFIER / LOAD_AGG path (sector ELEC). No new bus.

## Thermal

| Source | Tier | Notes |
|--------|------|-------|
| AFTERBURNER | Q1 | Existing. Unchanged. |
| OIL_PYRO jacket | Q2 | Existing pyro class. |
| IND_MELT, VAC_IND | via MET_HX_Q4 | Edged. Low-grade. Treat as Q4-class unless a higher-tier HX is later justified. |
| EW residual | Q3 | Unchanged (HX-8). |

HEAT_LADDER.md tiers are unchanged. New melt heat is recovered at Q4 via MET_HX_Q4, not dumped on Q4_BUS directly.

## Status vs plan 0.3

ONE_LINE.md and POWER.md are not in this workspace. This rollup is the Rev X check for the new loads. HEAT_LADDER.md is stamped below as checked against Rev X; tiers unchanged.
