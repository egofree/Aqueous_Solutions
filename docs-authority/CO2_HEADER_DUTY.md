# HDR_CO2 consumer duty

Document number: AQS-DUTY-009
Revision: B
Date: 2026-10-07
Authority: AQS-FLOW-GRAPH-001 Rev K (Rev B: Rev L); AQS-DUTY-008 Rev C §13.3. Not a PE stamp.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First issue. Consumer for S85 chosen, S89 added, HDR_CO2 balance closed | 2026-10-07 |
| B | §7 | S90 hab metabolic CO₂ joins HDR_CO2; S89 and farm OA re-rated (AQS-DUTY-010) | 2026-10-07 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose

Graph Rev J left HDR_CO2 with one inlet, S85 from CRYO_CO2 at 11.616 kg/d, and no consumer (AQS-DUTY-008 §13.8 item 3). This note picks the consumer, closes the balance and sizes the branch. The calculation is `docs-authority/_co2_header_study.py`; it reads the rates from the graph and reproduces every number below.

## 2. Inputs (graph Rev J)

| Stream | kg/d | Role |
|---|---:|---|
| S85 CRYO_CO2 → HDR_CO2 | 11.616 | CO₂ product after FLUE_KO, to be consumed |
| S04 CRYO_CO2 → GROW_BED | 1.109 | Net crop fixation (4.2 kg/d food × 0.08 DM / 0.5 HI × 0.45 C × 44/12) |
| S05 H₂ pool | 4.8 | H₂ from the EW cathodes, dried |
| S49 / S45 / S74 | 4.8 / 3.6 / 0.94 | H₂ to the fuel cell, the genset and MEOH_SYNTH |
| S73 CRYO_CO2 → MEOH_SYNTH | 6.9 | Existing synthesis feed |

## 3. Candidates

### 3.1 MEOH_SYNTH (rejected)

CO₂ + 3 H₂ → CH₃OH + H₂O needs 0.1374 kg H₂ per kg CO₂. All of S85 would need 1.596 kg/d more H₂ and make 8.46 kg/d methanol. The H₂ pool is already allocated: with the fuel cell running, free H₂ is −0.94 kg/d (already over-allocated; MeOH runs only on surplus); with the genset running it is 0.26 kg/d. MEOH_TRAIN puts MeOH behind the PEM and the genset. Counting the same EW hydrogen again would double count it. Methanol is also burned in MEOH_FC and its carbon comes back to CRYO_CO2 on S82, so this is a carrier loop, not a sink.

### 3.2 REMIN (negligible)

A lime-and-CO₂ remineralizer would take 2 CO₂ per Ca as bicarbonate: 10 L/d at 25 mg/L Ca is 0.55 g/d, 0.0047 % of S85. REMIN is issued as a hydroxide dose, so it takes none.

### 3.3 Other users

Hab air is not a consumer (CO₂ there is a hazard). BOUNDARY_EXPORT is forbidden on S85 ("not the dock"). No other unit on the graph takes CO₂.

### 3.4 GROW_BED enrichment (chosen)

The design intent already routes CO₂ to the farm: LIFE_MEP "HAB_AIR → HDR_CO2 → farm" and "FARM AHU: Q4 + CO₂ dose"; FARM_EQUIPMENT S04 "CO₂ → grow air".

FARM room 972 m³ (216 m² × 4.5 m), canopy 28 m². Setpoint 1000 ppm against 420 ppm outdoors, so the farm air holds 1.0469 g/m³ above ambient (CO₂ at 1.805 kg/m³, 24 °C). Dose only in the 16 h photoperiod.

- Crop uptake: 1.109 kg/d, which is 15.6 µmol/m²·s over the canopy in the light hours. That is a normal enriched leafy-crop rate, so the S04 basis holds.
- Minimum outdoor air (2 persons × 2.5 L/s + 0.3 L/s·m²): 251.3 m³/h (0.259 ACH). Holding 1000 ppm at that minimum loses 4.209 kg/d, so the farm needs at least 5.318 kg/d of CO₂ to hold the setpoint.
- S85 is larger than that. If all of it were dosed at the minimum outdoor air the farm would reach 2021 ppm, above the 1500 ppm limit for leafy crops. So the CO₂-controlled outdoor-air damper opens to 693.5 m³/h (0.713 ACH) in the light hours. That is above the minimum, so it is allowed, and it runs at 1.28 m/s in the 500 × 300 FARM AHU duct.
- Extra outdoor-air sensible load at a 10 K difference: 1.48 kW. It is not claimed against the Q4 surplus (1.24 kW, AQS-DUTY-008 §13.8 item 4).

## 4. Decision

S89 HDR_CO2 → GROW_BED carries all of S85, 11.616 kg/d, as the FARM AHU CO₂ dose.

| Parameter | Value |
|---|---|
| Medium | Dry CO₂ gas from the CRYO_CO2 vaporizer |
| Header pressure | 3.0 bar a (2 bar g), 20.0 °C, ρ 5.5 kg/m³ |
| Flow | 0.484 kg/h daily mean; 0.726 kg/h in the photoperiod (0.132 m³/h) |
| Line | DN15 316L (ID 15.8 mm), 0.187 m/s at peak. DN15 is the mechanical minimum. |
| Header | HDR_CO2 OD40 316 at Z 3200 (AQS-PIP-002) |
| Control | Mass-flow controller and solenoid on farm CO₂ ppm; outdoor-air damper on the high limit |
| Dark-hours buffer | 3.87 kg CO₂ (3.76 L liquid) held in CRYO_CO2 for 8 h |
| Forbidden | No tee to HDR_O2, hab air, the HAB return or BOUNDARY_EXPORT. The FARM AHU is not the HAB AHU. |

## 5. Balance

| | kg/d |
|---|---:|
| HDR_CO2 in (S85) | 11.616 |
| HDR_CO2 out (S89) | 11.616 |
| Residual | 0.0 |
| GROW_BED CO₂ in (S04 + S89) | 12.725 |
| Fixed in biomass | 1.109 |
| Leaves with farm exhaust air | 11.616 |

Fate, stated plainly: the S85 carbon is used once for growth enrichment and then leaves the plant with farm exhaust air. This is use, not sequestration.

## 6. Open items

1. Hab exhaled CO₂ (about 1 kg/person·d) is not on the graph. LIFE_MEP draws HAB_AIR → HDR_CO2; if it is added, the farm outdoor air rises in proportion (4 kg/d more gives about 932 m³/h, still inside the duct).
2. Outdoor-air heat recovery for the farm exhaust (sensible plate only, no wheel) is not designed.
3. S87/S88 (farm O₂ capture and N₂ make-up) are still on HOLD. At 694 m³/h the farm O₂ surplus is diluted; S87 may not be needed.

## 7. Rev B: hab metabolic CO₂ (S90)

Graph Rev L adds S90 HABITATION → HDR_CO2. The crew of 4 uses S02 = 0.84 × 4 = 3.36 kg/d O₂. At a respiratory quotient of 0.87 they exhale 3.36 × 0.87 × 44.01/32.00 = 4.021 kg/d CO₂. The sealed hab's sorbent bed holds this CO₂. It desorbs as dry CO₂ and is compressed into HDR_CO2 at 3.0 bar a. This is the LIFE_MEP route HAB_AIR → HDR_CO2 → farm. Hab air itself never enters the header. O₂ does not tee into the hab from this line.

`_co2_header_study.py` now reads S90 from the graph when it is present:

| | Rev A | Rev B |
|---|---:|---:|
| HDR_CO2 in | S85 11.616 | S85 11.616 + S90 4.021 = 15.637 |
| S89 (out) | 11.616 | 15.637 |
| Residual | 0 | 0 |
| Farm OA in the photoperiod, m³/h | 693.5 | 933.5 (0.96 ACH) |
| Duct velocity at all-OA, m/s | — | 1.73 |
| Extra OA sensible load at 10 K, kW | — | 2.29 |
| S89 peak, kg/h / velocity in DN15, m/s | 0.726 / 0.19 | 0.977 / 0.25 |
| Dark buffer, kg | 3.87 | 5.21 |

GROW_BED still fixes S04 (1.109 kg/d). The 15.637 kg/d on S89 leaves with farm exhaust air. Open item 1 of §6 is closed. Item 3 is answered in AQS-DUTY-010: S87 and S88 stay on HOLD as placeholders.

