# HDR_CO2 consumer duty

Document number: AQS-DUTY-009
Revision: D
Date: 2026-10-25
Authority: plant flow graph Rev AC; AQS-DUTY-008 Rev C section 13.3. Study; not a PE stamp.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First issue. Consumer for S85 chosen, S89 added, HDR_CO2 balance closed | 2026-10-07 |
| B | Section 7 | S90 hab metabolic CO2 joins HDR_CO2; S89 and farm outdoor air re-rated (AQS-DUTY-010) | 2026-10-07 |
| C | Section 8 | Graph Rev M: S11 carbon in the afterburner basis; S85, S89 and farm outdoor air re-rated; S05 retired, H2 pool read from S64 (AQS-DUTY-011) | 2026-10-08 |
| D | All | Rewritten to the documentation style guide (AQS-DOC-002) and updated to graph Rev AC through `_co2_header_study.py`: S85 is 0 (the cold box sends CO2 only on demand), the header runs on hab metabolic CO2, the bed dose is carried on S89, and the remainder goes to MEOH_SYNTH on IA-HCO2-MEOH. Sections 7 and 8 are folded into the subject sections; their content stays in this table. | 2026-10-25 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

This page picks the consumer for the contents of the carbon-dioxide header HDR_CO2, closes the header balance and sizes the branches. The calculation is `docs-authority/_co2_header_study.py`; it reads every rate from the graph and reproduces every number below.

## 2. Decision

The header supplies the grow-bed enrichment dose on S89 (HDR_CO2 to GROW_BED, the FARM air-handler dose) and sends the remainder to methanol synthesis on IA-HCO2-MEOH (HDR_CO2 to MEOH_SYNTH).

| Parameter | Value |
|---|---|
| Medium | Dry CO2 gas, regulated at 3.0 bar a (2 bar g), 20.0 C, density 5.5 kg/m3 |
| Header | DN25 manifold, 29 m run (0.007 m3), from `flow_graph/param/headers.py` (AQS-DUTY-075) |
| Branch line | DN15 316L, bore 15.8 mm; 0.014 m/s at the peak flow of 0.055 kg/h. DN15 is the mechanical minimum. |
| Control | Mass-flow controller and solenoid on the grow-bed CO2 demand; the methanol branch takes what the bed does not |
| Dark-hours buffer | 0.29 kg CO2 (0.29 L liquid) held in CRYO_CO2 for the 8 dark hours |
| Forbidden | No tee to HDR_O2, hab air, the HAB return or BOUNDARY_EXPORT. The FARM air handler is not the HAB air handler. |

## 3. Header balance (graph Rev AC)

| Stream | kg/d | Role |
|---|---:|---|
| S85 CRYO_CO2 to HDR_CO2 | 0.0 | Cold-box CO2 is shipped or held; the header takes none in the present graph |
| S90 HABITATION to HDR_CO2 | 4.021 | Metabolic CO2, desorbed from the HAB CO2 sorbent bed and compressed into the header |
| S89 HDR_CO2 to GROW_BED | 0.882 | Enrichment dose to the grow bed through the FARM air handler |
| IA-HCO2-MEOH HDR_CO2 to MEOH_SYNTH | 3.139 | The remainder: CO2 not taken by the bed, to methanol synthesis |
| Residual | 0.0 | Balance closes |

The crew of 4 exhales 4.021 kg/d CO2 (oxygen use 0.84 x 4 = 3.36 kg/d at a respiratory quotient of 0.87, times 44.01/32.00). The sealed hab's sorbent bed holds this CO2; it desorbs as dry CO2 and is compressed into the header at 3.0 bar a. Hab air itself never enters the header, and oxygen does not tee from this line into the hab.

## 4. Consumers considered

### 4.1 MEOH_SYNTH as the sole consumer (rejected; kept for the remainder)

CO2 + 3 H2 gives CH3OH + H2O at 0.1374 kg H2 per kg CO2. In revision C the whole header stream was offered to methanol synthesis and rejected: the hydrogen pool was already allocated (with the fuel cell running, free hydrogen was negative), methanol is burned again in MEOH_FC and its carbon returns on S82, so a full-stream feed would be a carrier loop, not a sink, and would double-count electrolysis hydrogen.

Graph Rev AC keeps that rejection for the full stream and uses methanol synthesis for the remainder only: the 3.139 kg/d the bed does not take leaves on IA-HCO2-MEOH. The methanol synthesis hydrogen demand is sized on its own duty sheet, not here.

### 4.2 REMIN (negligible)

A lime-and-CO2 remineralizer would take 2 CO2 per calcium as bicarbonate: about 0.55 g/d, a negligible share. REMIN is issued as a hydroxide dose and takes none.

### 4.3 Other users

Hab air is not a consumer (CO2 in hab air is a hazard). BOUNDARY_EXPORT is forbidden on this header. No other unit on the graph takes CO2 from it.

## 5. Grow-bed enrichment basis

Revision B sized the dose to hold 1000 ppm CO2 in the farm air against the minimum outdoor-air rate, with a CO2-controlled outdoor-air damper; that sizing (693.5 to 961.2 m3/h of outdoor air in the photoperiod) belonged to the earlier farm decision and stays in the revision history.

In the present graph the dose is the grow-bed demand rate: the bed (29.12 m2, crew-duty basis A-M-229) takes 0.882 kg/d on S89. At that dose the setpoint of revision B is not held at the minimum outdoor-air rate (the study puts the holding dose at 4.209 kg/d); the setpoint-and-damper basis is therefore not claimed for the present farm. If a setpoint is wanted again, the header needs a source larger than the hab metabolic flow, and S85 (cold-box CO2, only on demand) is the candidate. The question is recorded in `docs-authority/OPEN_QUESTIONS.md` (Q-033).

## 6. Open items

1. Enrichment setpoint: the header, as supplied today (hab metabolic CO2 only), carries about a fifth of the revision B holding dose. Restoring a 1000 ppm setpoint needs S85 back, which depends on the cold-box shipping decision.
2. Outdoor-air heat recovery for the farm exhaust (sensible plate only, no wheel) is not designed.

## 7. History of the earlier eras

Revision A picked the consumer (the grow bed) when S85 still carried 11.616 kg/d from CRYO_CO2 and the header had no other consumer. Revision B added the hab metabolic CO2 on S90 and re-rated the farm outdoor air. Revision C moved the S11 farm-trim carbon into the afterburner basis, retired S05 as an alias of S64, and retired S87 and S88 (farm O2 capture and N2 make-up) per AQS-DUTY-011 section 4.16. The detailed era tables stay in the revision history of `_co2_header_study.py` output and in the task-plan progress record; every present-day number on this page comes from the current study run against graph Rev AC.
