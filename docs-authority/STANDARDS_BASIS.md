# Standards basis for the audit fixes

Document: AQS-STD-001
Date: 2026-10-02
Jurisdiction for construction remains USA: NFPA and NEC as in AQS-HSE-001, City of Dallas amendments, OSHA 1910. This file is not a PE stamp and not a NASA safety review.

Earth plant. ISO and NASA clauses below are the design rules for the hab, the gas headers, and the fab room. They do not certify the building.

## Rules applied

| Fault | Rule | Fix |
|---|---|---|
| Solvent / resist / organic mist into chlorate leach | NFPA 400 oxidizer kept off combustibles | S39 slurry and etch only. S39B and S72B to the oil line. |
| Product cuts into the afterburner | NFPA 30 flammable liquid stays in the diked tank | Cuts to PROD_C5_C10 … PROD_C29. NCG_HEADER only to the burner. |
| Flue called CO2 | Process gas is not a product until separated | S67 to FLUE_KO. S67B is the CO2-rich cut only. |
| NOx water and MeOH condensate on grey | Life water is not a process sink. NASA-STD-3001 Vol 2 §6.3 is the hab water target, not the leach. | S46 to NOX_SCRUB. S81 to MEOH_COND. |
| Acid and base into the UPW polish node | Separate duties, separate names | Acid and base leave BMED to their use points. |
| Condensate into CRYO_H2 | NFPA 2 fuel header stays fuel. ISO 11114 material and purity on the gas side. | S70 to FLUE_KO. |
| Flue condensate to class treat | Same split | S68 to leach. |
| Shared oil/water down the ladder | A leak must not put oil in Q4 | Own thermosyphon per step. Cross-tie both directions, 5 K, hot to cold. |
| H2 and cryo residual ends | NFPA 2 and NFPA 55 require relief | S24 and S56 stay, labeled contingency. Not a normal sink. |
| Br2 regen self-loop | Own tower, not CRU | ZNBR2_BR2_REGEN. |
| Oxygen and hydrogen headers | NFPA 55 oxidizer, NFPA 2 fuel, 25 ft or rated barrier. NASA-STD-6016 oxygen compatibility for anything that later flies. ISO 11114-2 for non-metals on O2. | Unchanged split. No new tee. |
| Fab room | ISO 14644 is the cleanroom family. Class not assigned. | No class number invented. |
| Cryogenic fluids | ISO 21010 for materials in cryogenic service, not ISO 11114. | CRYO nodes stay on their own headers. |

## Not claimed

No ISO 14644 class. No NASA-STD-3001 numerical water table copied into the graph. No statement that Dallas has accepted NFPA 855 for this skid. Relief devices are not sized.
