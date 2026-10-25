# Air liquefaction cold box: internals and heat rejection

Document number: AQS-CRY-002
Revision: D
Date: 2026-10-25
PFD: AQS-PFD-CRY-001 (`cryo_pfd.png`)
Streams: AQS-STR-001, S02 to S04, S18, S24, S44, S45, S49, S50, S53 to S56, S64, S67, S70

Authority: `09-air-liquefaction-cryogenic.md` (air liquefaction narrative; topology only, its figures are not issued), `GAS_SYSTEM/Gas_System_overview.md`, AQS-EQP-CRY-001, AQS-BLD-001 (level L-1, east of the recycle core; fire barriers FB_CRYO and FB_CRYO_PROCESS), AQS-HSE-001 (NFPA 2 and NFPA 55; maximum allowable quantities), AQS-PHF-001, AQS-PWR-002 and AQS-FC-001 (CRYO_H2 consumers), AQS-EQP-GEO-001 (Q4 peer), `models/freecad/cryo.py`.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First issue: cold-box internals plus the HVAC and geothermal heat-rejection split | 2026-09-28 |
| B | Vent closure | S64 hydrogen as the normal path; S67 flue-cap CO2; S70 AHU condensable return (AQS-VENT-001) | 2026-09-28 |
| C | Label | The unexplained label of revision B replaced by "air liquefaction cold box" (Q-017 closed) | 2026-10-24 |
| D | All | Rewritten to the documentation style guide (AQS-DOC-002). Section numbering repaired; session wording removed; stream list corrected to the present graph (S05 and S06 are retired; S54 feeds Q4_BUS among S44/S53/S63/S80 and the rectifier and electrolyser contributions). No design decision changed. | 2026-10-25 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

This page fixes the air liquefaction cold-box internals, the split of its rejected heat between the life-side Q4 water loop and the dedicated cooling loop, and the normal hydrogen path, consistent with the vent closure of AQS-VENT-001. It turns the keep-out envelope of the earlier narrative into a named internals schedule with consumer branches. The duty figures (kilowatts, kilograms per hour) are not issued here; they wait on the heat and mass balance (Section 9). The narrative document 09 is cited for topology only; its column and coefficient-of-performance figures are legacy study narrative, not issued nameplates. The ZnBr2 bromine tower stays a separate outdoor skid and is out of scope.

## 2. Placement

| Item | Decision |
|---|---|
| Level | L-1 process basement (`Z_Lm1`); replicas `_B2...` if `BASEMENT_LEVELS` is greater than 1 |
| Plan position | East of the recycle core (`CRYO_X`, `CRYO_Y` in `models/freecad/params.py`), opposite the wet aisle |
| Fire | Fire barriers FB_CRYO and FB_CRYO_PROCESS are 2 h; no process-air duct passes through (AQS-BLD-001, AQS-HSE-001) |
| Envelope | The campus `CRYO` keep-out of 6 x 6 x 4 m; the internals sit inside it |

## 3. Separation rules

1. CRYO_H2 is not HDR_H2. CRYO_H2 is the product hold that feeds the consumers; HDR_H2 is the aisle capture header feeding the dryer.
2. Acid gas, oil vapour and the ZnBr2 bromine stream never enter the cold box.
3. The S18 and S67 flue-cap CO2 is claimed capture (AQS-VENT-001), not raw afterburner flow into HDR_CO2; a flue dump is not the end state.
4. No shared HVAC return exists between the hab and farm air and the cryo or process air (AQS-HSE-001 section 8).

## 4. CRYO_H2 consumers

The hold is sized for concurrent draws. The maximum allowable quantity cap of AQS-HSE-001 section 5 stays; no holdup mass is invented here.

| Consumer | Stream | Authority |
|---|---|---|
| BACKUP_GEN | S45 | AQS-PWR-002 / AQS-EQP-GEN-001 |
| FUEL_CELL (PEM) | S49 | AQS-FC-001 / AQS-EQP-FC-001 |
| Normal dryer feed | S64 (H2_DRYER to CRYO_H2) | AQS-VENT-001 partial closure (ends the continuous roof dump) |
| Roof vent contingency | S24 | AQS-VENT-001, emergency only, not a design dump |

The fuel-cell oxidiser is CRYO_O2 on S50. The generator and fuel-cell branches are separately isolated with flame arrestors (AQS-HSE-001 section 11).

## 5. Heat rejection: three destinations

| Destination | Tag / stream | What goes there | What does not |
|---|---|---|---|
| Q4 life water loop | `CRYO_HX_Q4` to S54 | Recoverable warm reject after the pinch: compressor intercooler residual and molecular-sieve TSA cool-down that meets the below-80 C water class (peer to S44, S53 and the other Q4_BUS contributors) | Stirling deep reject; cryogenic condenser boil-off; flue gas; generator exhaust |
| Dedicated cryo cooling | `CRYO_DED_COOL` to S55 (closed utility loop) | Stirling cold-head reject and deep condenser or expander heat that cannot enter life air | Polished water, the catch tank, blackwater, the hab air handler |
| Vent and room exhaust | `CRYO_AHU` and `CRYO_AHU_COND`, to S56 and S70 | The NFPA 2/55 room air handler; condensables return through S70 to FLUE_KO and the cold-box CO2 train; S56 is the non-condensable contingency, not a continuous outdoor dump | A shared return with hab or farm air; the process acid-gas header |

Flue gas from the afterburner and generator exhaust (S46) never routes through `CRYO_HX_Q4` or the life air handler. Q4 stays water-only into FARM and HABITATION.

## 6. Process scheme

```
Ambient air -> AIR_INTAKE -> MOL_SIEVE -> HEPA_BANK --+
H2_DRYER (S64) ---------------------------------------+-> COLD_BOX
S18 CO2 claim (optional) - - - - - - - - - - - - - - -+
         |
         +- STIRLING_COLD_HEAD (77-90 K)
         +- DIST_COL_PRI / SEC / TER (+ PSA where issued)
         +- REBOILER_COND (column heat integration)
         +- COMP_EXPAND (variable-speed compressors + expanders)
         +- VJ_LINES -> CRYO_O2 / N2 / CO2 / H2 receivers
```

The pressure-swing adsorption train may share the cold-box envelope where distillation is not the sole path; no second outdoor gas plant is created.

## 7. Internals schedule

AQS-EQP-CRY-001 Rev C carries the full equipment table. The tags:

| Tag | Role |
|---|---|
| COLD_BOX | Parent envelope (Stirling plus distillation / PSA) |
| AIR_INTAKE | Centrifugal inlet plus demister |
| MOL_SIEVE | CO2 and H2O drying (5A TSA class) |
| HEPA_BANK | Final particulate polish |
| STIRLING_COLD_HEAD | Cryocooler, 77 to 90 K |
| DIST_COL_PRI / SEC / TER | Cryogenic distillation train (primary, secondary, tertiary columns) |
| REBOILER_COND | Reboiler and condenser heat integration |
| COMP_EXPAND | Variable-speed compressors and expanders |
| VJ_LINES | Vacuum-jacketed transfer lines (schedule; CAD stub optional) |
| CRYO_HX_Q4 | Named heat exchanger to Q4 (S54) |
| CRYO_DED_COOL | Dedicated utility cooling loop (S55) |
| CRYO_AHU / CRYO_AHU_COND | Room air handler plus condensate knock-out (S56 / S70) |
| CRYO_H2 / O2 / N2 / CO2 | Product receivers |

## 8. Room ventilation and the Q4 loop

### 8.1 CRYO room ventilation (NFPA 2 / 55)

| Requirement | Design intent |
|---|---|
| Mechanical ventilation | Dedicated `CRYO_AHU` serving the CRYO fire area only |
| Discharge | Condensables to S70 and the cold box; S56 as the residual contingency; never the hab or farm return; no continuous dump (AQS-VENT-001) |
| Detection | Hydrogen at 25 % of the lower flammable limit trips: isolate the hydrogen trains and freeze the cold-box feed (AQS-HSE-001 section 8) |
| Fire barrier | No process-atmosphere duct through FB_CRYO_PROCESS |
| Make-up | Outdoor air, or listed energy recovery on Q4 water only; never a process-air energy-recovery wheel into life air |

### 8.2 The Q4 water loop

The Q4_BUS contributors in the present graph are S44 (GEO_HP), S53 (FUEL_CELL), S54 (CRYO_HX_Q4), S63 (MET_HX_Q4), S80 (MEOH_FC), the ZNBR2 heat edge, the rectifier loss edge and the electrolyser heat edge. The former building-HVAC stream S06 is retired. The cryo contribution to Q4 is only the warm residual from `CRYO_HX_Q4` that meets the Q4 temperature class; deep cryo heat stays on S55. Geothermal remains the primary building Q4 thermal path.

## 9. Remaining gaps

1. Quantitative cold-box, Stirling and column duties (kilowatts, kilograms per hour) are not issued; the document-09 numbers are narrative only.
2. The CRYO_H2 holdup mass against the maximum allowable quantity is not issued (the AQS-HSE-001 section 5 cap remains the limit).
3. A `plant.FCStd` rebuild on the build machine is needed before the child envelopes and any `_Bn` replicas appear in the assembled plant.
4. The detailed vacuum-jacket-line isometric and nozzle schedule wait for the piping pass.
5. The molecular-sieve regeneration heat balance (how much residual truly meets Q4) waits for the first heat and mass model.
6. The `CRYO_AHU_COND` / S70 duty and the S67 flue-cap condenser are not issued (AQS-VENT-001).

## 10. Regenerating the diagram

Run `python3 flow_graph/exporters/matplotlib/cryo_pfd.py` from the repository root.
