# Fab to wet-line interface

Document number: AQS-IF-FAB-WET-001  
Revision: C  
Date: 2026-10-29

Authority: AQS-EQP-FAB-001, AQS-EQP-FAB-RGN-001, AQS-STR-001. Interface edges verified against graph Rev AC.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Short interface map | 2026-09-27 |
| B | Rewritten to the documentation style guide (AQS-DOC-002) and re-based on the graph: retired units (FAB_PREP, FAB_TOOL, ETCH_RETURN) removed, stream list corrected to the present edges (S10 WET_BENCH to LEACH_CSTR_1, S39/S39B from WAFER_FAB), wet-chemical supply train stated with rates. No stream or rate changed; the crossings are read off the graph. | 2026-10-25 |
| C | Route UPW_TO_FAB removed from the stream list | The header feed to FAB_UPW_TANK is retired on the graph because IA-UPW-FAB already fills the tank from the same polisher. | 2026-10-29 |

## 1. Purpose and scope

This page states the physical and stream interface between the wafer fabrication sector (FAB) and the wet-chemical supply line (the WS_* reagent units fed by the BMED acid and base products). It is the walk-down sheet for the piping that crosses the fab boundary; the unit designs are AQS-EQP-FAB-001 and AQS-EQP-FAB-RGN-001, and the streams are AQS-STR-001.

## 2. Physical layout

| Side | Level | Units on the graph |
|---|---|---|
| Wafer fab | L0 | WAFER_FAB, WET_BENCH, FAB_UPW_TANK, the WS_* reagent stores, the LITHO_* tools, SOLAR_PV_CELL |
| Reagent make-up | with BMED on L-1 | WS_NITRIC and WS_PHOS fed by BMED_ACID; WS_KOH fed by BMED_BASE; the other WS_* stores fed from the header sources named in section 3 |

The wet-chemical stores sit with the BMED skids so the acid and base products cross one wall. Reagent and etch piping runs in its own fab chase; there is no shared header with HDR_H2 or with the life-support air.

## 3. Stream crossings (graph Rev AC)

### 3.1 Reagents and services to the wet line and fab

| Stream | From | To | kg/d | Carries |
|---|---|---|---:|---|
| S09 | BMED_ACID | WET_BENCH | 9.28 | HCl |
| S31 | WS_HF_ED | WET_BENCH | 1.5 | HF (aq) |
| S32 | WS_PEROX | WET_BENCH | 3.0 | H2O2 |
| S33 | WS_AMMONIA | WET_BENCH | 3.01 | NH4OH / NH3 (aq) |
| S34 | WS_NITRIC | WET_BENCH | 1.25 | HNO3 |
| S34B | WS_PHOS | WET_BENCH | 0.61 | H3PO4 |
| S35 | WS_KOH | WET_BENCH | 0.27 | KOH |
| IA-SOLV-WB | WS_SOLV | WET_BENCH | 0.21 | ethanol and acetone |
| S27 | FAB_UPW_TANK | WET_BENCH | 60.0 | fab UPW above the 18 megohm-cm class |
| IA-UPW-FAB | BMED_UPW_POLISH | FAB_UPW_TANK | 60.0 | fab UPW |
| IA-UPW-USE | HDR_UPW | WAFER_FAB | 66.5 | fab UPW |
| S03 | CRYO_N2 | WAFER_FAB | 1.50 | N2 purge |
| S37 | WS_SLURRY | WAFER_FAB | 3.3 | colloidal silica slurry |
| IA-PHOS-DOPE | WS_PHOS | WS_DOPE | 0.01 | phosphate to dopant |

### 3.2 Returns from the fab to the wet line and leach

| Stream | From | To | kg/d | Carries |
|---|---|---|---:|---|
| S10 | WET_BENCH | LEACH_CSTR_1 | 79.1 | spent etch |
| S39 | WAFER_FAB | LEACH_CSTR_1 | 3.31 | spent slurry and etch liquor |
| S39B | WAFER_FAB | OIL_FRAC | 0.0 (contingency) | solvent and photoresist |
| IA-FAB-SPENT | WAFER_FAB | LEACH_CSTR_1 | 66.5 | spent UPW |
| IA-FAB-LOSS | WAFER_FAB | BAGHOUSE | 0.51 | kerf |

## 4. Naming

The polish dielectric of the electrowinning train (POLISH_BANK) is not the fab ultrapure-water train (FAB_UPW_TANK, fed by BMED_UPW_POLISH), and neither is a WS_* reagent store. The three names appear together on the piping classes; this note is the disambiguation of record.

## 5. Open items

1. The nozzle schedule and chase sizing for the crossings of section 3 are the next piping pass (unit task 04 for WET_BENCH and WAFER_FAB).
2. The solar-cell KOH branch (S35 to SOLAR_PV_CELL) stays a stub until the solar equipment pass issues that line's equipment.
