# Methanol train equipment list

Document number: AQS-EQP-MEOH-001  
Revision: B  
Date: 2026-10-25  
Process flow diagram: AQS-PFD-MEOH-001 (`meoh_train_pfd.png`)  
Authority: AQS-MeOH-001, AQS-REQ-KW-001, AQS-FC-001 Rev B, AQS-ASM-001, AQS-HSE-001, AQS-VENT-001, and dependency SI-IEM-01 in `DEPENDENCIES.md`.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Equipment tags for methanol from two sources and for the fuel cell with ion-exchange membrane | 2026-10-01 |
| B | — | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). Table 2.1 gains a column showing which tags are nodes of the plant flow graph. No tag, duty or rating changed. | 2026-10-25 |

The design is licensed under CERN-OHL-S-2.0. The model scale factor `SCALE_M` is 1.0.

## 1. Purpose and scope

The methanol (MeOH) train makes methanol from carbon dioxide and hydrogen, and also recovers methanol of biological origin from farm and habitation waste. It stores the methanol and uses it in a direct methanol fuel cell (DMFC) as a continuous source of electric power. The process is described in AQS-MeOH-001. This page lists the equipment tags of the train, the duty of each, its design status, and the separation rules that apply to the methanol equipment.

## 2. Equipment tags

Table 2.1 lists the tags. The status column gives the state of the design at revision A. The last column shows whether the tag is a node of `flow_graph/plant_flow_graph.json` at this revision; tags that are not nodes exist only on this list and on the process flow diagram.

Table 2.1. Methanol train equipment

| Tag | Duty | Status | Graph node |
|---|---|---|---|
| MEOH_DAC_OR_CO2 | Carbon dioxide intake from CRYO_CO2, from flue-gas capture, or optionally by direct air capture (DAC) | Issued at architecture level | No |
| MEOH_IEM_CELL | Electrochemical conversion of carbon dioxide to methanol intermediates on an ion-exchange membrane (IEM); the SEM-Tech membrane is preferred | Issued as a study; dependency SI-IEM-01 | No |
| MEOH_SYNTH | Catalytic reactor for CO₂ + 3H₂ → CH₃OH + H₂O, of the SI-MEOH-01/02 class, scaled to this plant | Issued; pressure and temperature are study values, and the maximum allowable working pressure (MAWP) is in AQS-ASM-001 | Yes |
| MEOH_COMP_H2 | Hydrogen booster compressor, needed if the pressure from CRYO_H2 is too low for the synthesis | Not designed; pressure to be determined | No |
| MEOH_COND | Condenser producing crude methanol and water | Issued | Yes |
| MEOH_DIST | Distillation and polishing to fuel grade | Issued; duty to be determined | No |
| MEOH_TANK | Bulk methanol store of 50 to 200 L (study value) | Issued; atmospheric or low pressure | Yes |
| MEOH_DAY_TANK | Day tank of 20 to 50 L at the fuel cell | Issued | No |
| MEOH_FERM_DIG | Digester or methylotrophic fermenter for farm and habitation waste | Partly designed | No; the graph has the single node MEOH_FERM |
| MEOH_FERM_STILL | Still recovering methanol of biological origin | Partly designed | No; see MEOH_FERM |
| MEOH_FC | Bank of direct methanol fuel cell stacks with ion-exchange membranes; the SI-DMFC-01 packaging is accepted | Issued; 0.5 to 2 kW DC continuous | Yes |
| MEOH_DCDC | DC-to-DC converter feeding the Sol-Ark battery bus at 160 to 700 V | Issued | No |
| MEOH_HX_Q4 | Heat exchanger passing low-grade heat to the Q4 heat loop (S80) | Issued | No; S80 runs from MEOH_FC to Q4_BUS |
| MEOH_HX_Q3 | Heat exchanger passing the heat of the synthesis reaction to the Q3 loop, or for oil preheat | Not designed | No |
| MEOH_VENT_KO | Knock-out (KO) vessel on the exhaust before the carbon dioxide returns to CRYO_CO2 (S82) | Issued | No; S82 runs from MEOH_FC to CRYO_CO2 |
| MEOH_LEL | Detection of flammable vapour against the lower explosive limit (LEL) and of volatile organic compounds (VOC), with a fuel trip | Issued under AQS-HSE-001 | No |

## 3. Continuous rating

The continuous rating of the methanol fuel cell is set in section 3.6 of AQS-REQ-KW-001 as requirement REQ-MEOH-FC-CONT, 0.5 to 2 kW DC. The electrical and heat loads of the synthesis are study values. The catalytic route is driven by heat, and its compressor loads are still to be determined. No plant-level electrical load is to be assigned to the synthesis beyond its share of the hydrogen allocation.

## 4. Separation rules

1. MEOH_FC is separate from BACKUP_GEN, and it is not connected directly by a tee to the rectifier (RECT) DC bus.
2. Methanol liquid piping is in piping class PC-11 (AQS-ASM-001 section 6.11), a flammable-service class. It is not in class PC-06, which serves ultrapure, potable and grey water.
3. The manifolds of the hydrogen fuel cell with proton-exchange membrane (PEM), streams S49 and S50, stay isolated from the methanol day tank.
4. A methanol spill drains to HDR_ORG or to a bonded sump, never to the catch tank (CATCH) or the potable roof water.
5. Methanol vapour is never vented freely outdoors (AQS-VENT-001).

## 5. Regenerating the diagram

The process flow diagram is regenerated with:

```bash
cd flow_graph/exporters/matplotlib
python3 meoh_train_pfd.py
```
