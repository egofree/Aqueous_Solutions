# Electrode fabrication and coating

Document number: AQS-MFG-ELC-001  
Revision: D  
Date: 2026-10-25  
Authority: AQS-MFG-MET-001 and AQS-EQP-MFG-MET-001; AQS-BOM-SC-001 Rev C; AQS-EQP-STUDY-001; AQS-AUTH-001; project decision of 2026-10-01 placing electrode coating in scope. The first issue also cited AQS-GAP-001, which is not a document in the repository.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First issue: placeholder for electrode coating, raised from "remaining" to "partly designed" at architecture level | 2026-10-01 |
| B | 1 | Project decision: electrode coating is in scope. Unit `ELECTRODE_COAT` added to the graph seed in the MFG sector; other sectors may use it. | 2026-10-01 |
| C | 2 | Study ST-ELC-01: average electrical load 0.3 kW; non-precious formulation class for step M1; ruthenium and iridium oxide coatings deferred | 2026-10-01 |
| D | — | Purpose and scope rewritten to the documentation style guide (AQS-DOC-002). The revision line now states the latest revision (it said B after revision C had been issued). Section 5 records the coating load in the graph. No study result changed. | 2026-10-25 |

The design is licensed under CERN-OHL-S-2.0. The model scale factor `SCALE_M` is 1.0.

## 1. Purpose

The electrowinning (EW) and bipolar membrane electrodialysis (BMED) cells use electrodes that wear out and must be replaced. Making and coating replacement electrodes on site is a capability that the minimum viable system (MVS) requires. This page states where electrode coating sits in the plant, relative to the metal-forming aisle, and records the result of the coating study ST-ELC-01. It does not specify coating recipes or equipment nameplates, which have not been designed.

## 2. Scope

Table 2.1 lists what this page covers and what it leaves to later work.

Table 2.1. Scope

| Covered | Not covered at this revision |
|---|---|
| The substrate route from the metal-forming wire, sheet and powder lines (AQS-MFG-MET-001) | Vendor duty and slurry recipes for ruthenium–iridium oxide (RuO₂–IrO₂) coatings |
| The unit `ELECTRODE_COAT` in the MFG sector | FreeCAD solids of the coating booth |
| Health, safety and environment: coating fumes are drawn to MET_AHU and then MET_SCRUB (streams S71 and S72) | Electrodes for the methanol fuel cell (AQS-FC-001 and the methanol train) |
| Use of fab wet-bench practice in the MFG sector | Setting `electrode_coating_on_site=true` |

## 3. Arrangement

1. The substrates are 316L stainless steel or titanium mesh or plate, made on the cold-mill and mesh line of the metal-forming aisle (AQS-EQP-MFG-MET-001).
2. Coating is done in a booth in the metal aisle of the MFG sector. The booth exhausts to the air-handling unit MET_AHU and then to the scrubber MET_SCRUB, in accordance with AQS-VENT-001 and AQS-HSE-001. The afterburner is not the primary treatment for the fumes.
3. The products are replaceable anodes and cathodes for the EW and BMED cells. The page does not claim that precious-metal coatings can be made on site at the rates of step M1.
4. The design-tool flag `electrode_coating_on_site` stays false (`design_tool/aqs_design_tool/data/candidate_mvs.json`) until the booth model and the formulation study are complete.

## 4. Results of study ST-ELC-01

Table 4.1 gives the results of the study, which is reported in AQS-EQP-STUDY-001 Rev E section 10 (`STUDY_UNITS_STUB.md`).

Table 4.1. Coating study results

| Item | Study result |
|---|---|
| Continuous electrical load | About 0.3 kW on average, with peaks of 1 to 2 kW during exhaust and curing campaigns |
| Formulation class | Non-precious carbon, nickel or passivation coatings for the step M1 EW cells |
| Dimensionally stable anode (DSA) with RuO₂–IrO₂ | Deferred; no slurry recipe is assumed |
| Next step (external) | FreeCAD model of the booth and a laboratory formulation trial; owner and date to be decided |

An equipment list, AQS-EQP-MFG-ELC-001, will be written when nameplates exist for the metal-forming equipment.

## 5. Representation in the flow graph at this revision

In the graph, ELECTRODE_COAT is supplied with 0.0792 kW from SOL_ARK_60K (stream SF-ELECTRODE_COAT) and exchanges 0.02 kg/d of electrode material with EW_1 (streams IA-COAT-IN and IA-COAT-OUT). The graph load is lower than the 0.3 kW average of Table 4.1; the two have not been reconciled.
