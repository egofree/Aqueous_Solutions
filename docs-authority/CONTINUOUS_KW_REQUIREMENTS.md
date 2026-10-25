# Continuous power requirements for generation, fuel cells, PV fabrication, cryogenics and manufacturing

Document number: AQS-REQ-KW-001  
Revision: B  
Date: 2026-10-24  
Basis: AQS-SCALE-001 (`SCALE_M = 1.0`), AQS-AUD-001, AQS-ELC-001 (`ELECTRICAL.md`), the AQS-GAS-003 Faraday check, AQS-FC-001, AQS-PWR-002, AQS-CRY-002, AQS-MFG-MET-001, AQS-EQP-FAB-PV-001 and AQS-MeOH-001.  
Status: design requirements. Not a purchase order and not a set of stamped nameplates.  
Licence: CERN-OHL-S-2.0. Style: AQS-DOC-002.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First-principles continuous kW + labeled stand-in products | 2026-10-01 |
| B | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, scope and terms added to §1, captions. Section numbers, requirements, ranges and stand-ins unchanged. | 2026-10-24 |

## 1. Purpose, scope and method

This page sets the continuous electrical power each of the following must deliver or may draw at the baseline plant size (`SCALE_M = 1.0`): the backup generator, the PEM fuel cell, the methanol fuel cell, the Stirling cryocooler bank, the PV-cell fabrication tools (PECVD and belt firing) and the manufacturing shop. These requirements feed the electrical design (AQS-ELC-001) and the energy-storage duties.

In scope: continuous and capacity-class power, the hydrogen they share, and the commercial products used as stand-ins to bound them. Out of scope: purchase decisions and vendor nameplates, which stay to be decided at procurement.

Terms:

- Continuous power: the power expected in normal steady operation, fed by the plant's own process streams alone.
- Capacity class: the upper electrical envelope allowed by the Sol-Ark inverter, the zinc-bromide battery or the module peak. It may exceed the continuous power when running on stored or contingency fuel.
- Stand-in: a cited commercial product (vendor, model and datasheet or URL) used to bound a calculation. A stand-in is not part of the bill of materials and is not purchased equipment.
- kW_e, kW_dc, kW_th: electrical (AC), direct-current electrical and thermal power.
- M1: the first module of the plant at the baseline size.
- PRP, ESP: prime power and emergency standby power, the two standard generator ratings (ISO 8528-1).

Other abbreviations are in `docs-authority/GLOSSARY.md`.

Method:

1. Requirements are derived from first principles using the plant's issued streams: the Faraday hydrogen yield, the module bus, the wet feed of 150 kg/d, and the life and basement loads at `SCALE_M = 1.0`.
2. Where a commercial class is needed to bound a calculation, a stand-in is cited (Table 2.1).
3. The older campus figures (280 / 336 / 400 kW and 100–200 kW stacks) are not used as issued ratings for M1.

## 2. Stand-in products

These products bound the calculations; they are not a bill of materials (Table 2.1).

Table 2.1. Stand-in products

| ID | Use in Aqueous | Stand-in (vendor / model) | Cited continuous / rated | Source | Role |
|---|---|---|---|---|---|
| SI-GEN-01 | BACKUP_GEN capacity-class envelope | **EODev GEH2** (Toyota PEM FC hybrid genset) | PRP **80 kW** / ESP 88 kW; FC core ~70 kW; H₂ use ~0.5 kg/h @ 11 kW, ~4.7 kg/h @ 70 kW | https://www.eo-dev.com/products/geh2-the-zero-emission-hydrogen-power-generator/ ; Generac GEH2 cut sheet | Capacity-class stand-in only — M1 continuous << PRP |
| SI-FC-01 | PEM FC continuous match to Faraday | **Ballard FCgen-1020ACS** | Scalable **0.45–3 kW** air-cooled PEM stack | https://www.ballard.com/wp-content/uploads/2024/08/Ballard_FCgen_1020ACS_specs.pdf | Continuous-duty stand-in ≈ process-H₂ limited stack |
| SI-FC-02 | PEM FC capacity-class ceiling | **Ballard FCgen-LCS** | Scalable to **98 kW** liquid-cooled | https://ballard.blendermedia.com/wp-content/uploads/2024/08/Ballard_FCgen_LCS_specs.pdf | Capacity class — do not claim on M1 without H₂ import |
| SI-CRY-01 | Stirling cold-head unit cell | **AMETEK Sunpower CryoTel GT** | **240 W_e** input → **16 W** lift @ 77 K (23 °C reject) | Sunpower CryoTel GT datasheet (product brochure / GT sheet) | Unit-cell COP class for bank sizing |
| SI-PECVD-01 | SiNₓ ARC tool class | **SINGULUS GENERIS PVD/PECVD** industrial family | Full-line industrial; pilot derate used in §3.4 | https://www.singulus.com/wp-content/uploads/2022/10/GENERIS_PECVD-2.pdf | Architecture class — not M1 nameplate |
| SI-BELT-01 | Contact fire furnace class | Industrial IR / belt fire (lab–pilot literature class) | Study **10–25 kW_e** intermittent for pilot belt | Centrotherm / generic belt-fire practice; see §3.4 | Stand-in duty band |
| SI-MFG-01 | Polymer line motors | **Precious Plastic** Extrusion / Shredder Pro motors | **2.2–4 kW** class motors (kit BOM motors) | DEPENDENCIES.md → ONEARMY/precious-plastic-kit | Intermittent shop loads |
| SI-MFG-02 | Induction melt class | Induction melt furnace class (SuperbMelt-class narrative) | Legacy overview **~35 kW** peak narrative | `MANUFACTURING/Manufacturing_Overview.md` (narrative only) | Peak envelope; continuous share §3.5 |
| SI-DMFC-01 | MeOH IEM/DMFC continuous | **SFC Energy EFOY Pro 12000 Duo** | **500 W** continuous DMFC; ~0.9 L MeOH / kWh | https://www.efoy-pro.com/ ; Vitec EFOY Pro 12000 datasheet | Module cell; bank for M1 MeOH FC |
| SI-MEOH-01 | Air/CO₂→MeOH synthesis class | **Carbon Recycling International — George Olah plant** | Industrial **1.3→4 kt/y** MeOH from CO₂+H₂ | https://carbonrecycling.com/projects/george-olah | Chemistry / P-T class — scaled **down** for M1 |
| SI-MEOH-02 | Air-to-MeOH pilot class | **Air Company Air2Fuel / CO₂ hydrogenation** | Pilot **280 MTPA** MeOH class; bench 100–400 mL/d | NETL AIR2FUEL (DE-FE0032405); Air Company public pilots | DAC+H₂ path stand-in |
| SI-IEM-01 | Preferred IEM membrane fab | **Open-sourced-off-the-shelf-ion-exchange-membrane** (SEM-Tech lineage) | Open membrane fab reference | DEPENDENCIES.md (egofree fork CC0; Rowow-LLC CERN-OHL-S-2.0) | Preferred membrane for MeOH IEM-FC / synthesis cells |

## 3. Continuous power requirements at `SCALE_M = 1.0`

### 3.0 Shared hydrogen supply

All the hydrogen users draw on one process supply (Table 3.1).

Table 3.1. Shared hydrogen supply

| Quantity | Value | Basis |
|---|---|---|
| Process Ḣ₂ | **~0.2 kg/h ≈ 4.8 kg/d** | AQS-GAS-003 Faraday check at 150 kg/d wet feed |
| H₂ LHV | 33.3 kWh/kg | Standard |
| Chemical power | **~6.7 kW_th** | 0.2 × 33.3 |
| Consumers sharing pool | BACKUP_GEN (S45), PEM FC (S49), MeOH synth (S74), S24/S64 contingency | Cannot all draw Faraday max simultaneously |

Hydrogen priority (requirement): (1) the maximum allowable quantity and dryer hold-up; (2) the PEM fuel cell's continuous base load; (3) the backup generator's islanded peaks, from hold-up; (4) methanol synthesis, when the zinc-bromide battery's state of charge and the PV surplus allow it (AQS-MeOH-001).

### 3.1 Backup generator (`BACKUP_GEN`, AQS-EQP-GEN-001)

Table 3.2. Backup generator requirements

| Requirement | Continuous | Capacity class | Basis |
|---|---|---|---|
| **REQ-GEN-CONT** | **2.5 kW_e** (range 2.3–2.7) | — | 6.7 kW_th × η_genset 0.35–0.40 on process H₂ alone |
| **REQ-GEN-CAP** | — | **≤ 60 kW_e** AC on Sol-Ark GEN | Module peak / Sol-Ark continuous; SI-GEN-01 PRP 80 kW is **upper commercial envelope**, not M1 continuous |
| Cont. fuel rate @ REQ-GEN-CONT | **~0.15 kg/h H₂** | — | Scale from SI-GEN-01 ~0.5 kg/h @ 11 kW → ~0.11–0.15 kg/h @ 2.5 kW |
| Diesel | Contingency only | — | Not continuous requirement |

### 3.2 PEM fuel cell (`FUEL_CELL`, AQS-FC-001 and AQS-EQP-FC-001)

Table 3.3. PEM fuel cell requirements

| Requirement | Continuous | Capacity class | Basis |
|---|---|---|---|
| **REQ-FC-CONT** | **4 kW_dc** (range 3–5) | — | 6.7 kW_th × η_PEM 0.50–0.55; SI-FC-01 class matches |
| **REQ-FC-CAP** | — | **≤ 60 kW_dc** into BATT via FC_DCDC | ZnBr2 / Sol-Ark BATT window; SI-FC-02 shows commercial scalability — forbid legacy 100–200 kW claim |
| Cont. fuel @ REQ-FC-CONT | **~0.20 kg/h H₂** (full Faraday) | — | If GEN idle; split with GEN/MeOH per §3.0 |
| Oxidizer | CRYO_O2 (S50) | — | Not ambient air as named M1 stream |

### 3.3 Stirling cryocoolers (AQS-CRY-002 and AQS-EQP-CRY-001)

From first principles, the oxygen, nitrogen and carbon dioxide needed for life support are limited by headcount (a study crew of 4, AQS-AUD-001 §11). The cooling needed to liquefy product gas, a sink at 77–90 K, is dominated by the heat leak of the cold box and by distillation reboil and condensing, not by lift at detector scale.

Table 3.4. Cryocooler requirements

| Requirement | Continuous | Basis |
|---|---|---|
| **REQ-CRY-STIR-CONT** | **4 kW_e** (study band **2–8 kW_e**) | Fit module avg 11–19 kW / peak ~50 kW; bank of SI-CRY-01 units (CryoTel GT @ 0.24 kW_e each) or larger commercial Stirling — **unit cell** SI-CRY-01 proves COP class (~16 W lift / 240 W_e ≈ 6.7% at 77 K) |
| Legacy 15–25 kW cryo bus | **Superseded** | AQS-GAP-001 — folded into module bus |
| Dedicated cool S55 | Sized to Stirling + deep reject | Not Q4 life air |

A single CryoTel GT is an instrument-class cooler, not a plant air-separation unit. The requirement is for a bank of units, or a commercial cold box, whose electrical input falls within the study band of 2–8 kW_e. SI-CRY-01 is the stand-in unit cell that shows the coefficient of performance.

### 3.4 PECVD and belt firing (AQS-EQP-FAB-PV-001)

The pilot line starts 1–5 wafers a day (AQS-AUD-001 §13), so the tools run intermittently, not continuously at industrial wafers per hour (Table 3.5).

Table 3.5. PECVD and belt-firing requirements

| Requirement | Continuous-equivalent | Peak intermittent | Basis |
|---|---|---|---|
| **REQ-PECVD-CONT** | **0.5–2 kW_e** avg | **5–15 kW_e** while running | RF + heaters + vacuum; SI-PECVD-01 industrial family derated to pilot; full-line 80–150 kW **forbidden** as M1 continuous |
| **REQ-BELT-CONT** | **0.5–2 kW_e** avg | **10–25 kW_e** while firing | SI-BELT-01 IR/belt class; heat reject → PV_HX_Q4 (S53 peer) |
| Combined FAB PV strip budget | **≤ 20 kW_e** coincident peak | — | Inside module ~50 kW peak; staged so CZ + PECVD + belt not all peak together |

### 3.5 Manufacturing (polymer and metal forming)

Table 3.6. Manufacturing requirements

| Requirement | Continuous | Peak | Basis |
|---|---|---|---|
| **REQ-MFG-POLY-CONT** | **1–3 kW_e** avg intermittent | **4 kW_e** per machine | SI-MFG-01 Precious Plastic motor class; campaign use |
| **REQ-MET-MELT-CONT** | **5–15 kW_e** study share | **≤ 25 kW_e** induction coil class | ELECTRICAL induction 0–25 kW; SI-MFG-02 35 kW = narrative peak only |
| **REQ-MFG-FORM-CONT** | **1–5 kW_e** draw/mill/atomize share | — | Throughput 0.2–2 kg/h (AQS-AUD-001 §10.6) |
| **REQ-MFG-TOTAL-CONT** | **~8–20 kW_e** plant share | **≤ 30 kW_e** coincident | Must remain inside module peak with wet/FAB |

### 3.6 Methanol fuel cell with ion-exchange membrane (AQS-MeOH-001)

This is a continuous power path added alongside the PEM fuel cell (Table 3.7). Both the PEM hydrogen fuel cell and the methanol fuel cell exist (AQS-FC-001 Rev B, AQS-MeOH-001).

Table 3.7. Methanol fuel cell requirements

| Requirement | Continuous | Capacity class | Basis |
|---|---|---|---|
| **REQ-MEOH-FC-CONT** | **0.5–2 kW_dc** | **≤ 5 kW_dc** bank | SI-DMFC-01 @ 0.5 kW × 1–4 modules; MeOH from §4 sources; IEM membrane preferred (SI-IEM-01) |
| MeOH burn rate @ 1 kW | **~0.9 L/h ≈ 0.71 kg/h** | — | SI-DMFC-01 0.9 L/kWh; ρ_MeOH ≈ 0.79 kg/L |
| Electrical tie | Sol-Ark **BATT DC** via **MEOH_DCDC** (peer to FC_DCDC) | — | ≠ GEN port; ≠ RECT process DC |

## 4. Summary of requirements

Table 4.1. Summary of requirements

| Tag | Continuous kW (requirement) | Capacity / peak | Stand-in IDs |
|---|---|---|---|
| BACKUP_GEN | **2.5 kW_e** | ≤ 60 kW_e | SI-GEN-01 |
| FUEL_CELL (PEM) | **4 kW_dc** | ≤ 60 kW_dc | SI-FC-01 / SI-FC-02 |
| MEOH_FC (IEM/DMFC) | **0.5–2 kW_dc** | ≤ 5 kW_dc | SI-DMFC-01 / SI-IEM-01 |
| STIRLING_COLD_HEAD bank | **4 kW_e** (2–8) | within module | SI-CRY-01 |
| PV_ARC (PECVD) | 0.5–2 avg / 5–15 peak | ≤ 15 peak | SI-PECVD-01 |
| PV_FIRE (belt) | 0.5–2 avg / 10–25 peak | ≤ 25 peak | SI-BELT-01 |
| MFG total | **8–20 kW_e** | ≤ 30 coincident | SI-MFG-01 / SI-MFG-02 |

All rows are study requirements for design. Vendor nameplates remain to be decided at procurement. The stand-ins are cited in §2.

## 5. Canonical copy

The canonical copy of this page is `docs-authority/CONTINUOUS_KW_REQUIREMENTS.md`.
