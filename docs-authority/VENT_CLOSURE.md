# Vent and stack closure — scrub / regen or CRYO

Document number: AQS-VENT-001  
Revision: C  
Date: 2026-10-01  
Authority: AQS-AUTH-001, AQS-MF-001, AQS-STR-001, AQS-HSE-001,
AQS-GAS-002 / AQS-GAS-003, AQS-CRY-002, AQS-MFG-MET-001,
AQS-PWR-002 / AQS-FC-001, FLOW_BATTERY.md, AQS-AUD-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: close former outdoor dumps; scrub+regen or CRYO | 2026-09-28 |
| B | 1 | PFD end-to-end Partial/Claimed; AQS-PFD-VENT-001 issued | 2026-09-28 |
| C | 1 | Study-estimate duties for polish/regen/AHU_COND/MET_SCRUB | 2026-10-01 |

Style: AQS-DOC-002. Compliance themes: AQS-COMPL-001.

Licence: CERN-OHL-S-2.0. No invented nameplates. `SCALE_M = 1.0`.
No plant rebuild this pass. No git commit.

**LOCK (owner correction 2026-09-28)**

None of the former “open by intent” discharges are acceptable as design
end states. Every listed stream / stack requires either:

1. a **dedicated scrubber + regenerable media** returning product liquor
   to an existing wet / chem loop, **or**
2. a tie-back to the **cold-head / CRYO** system for condensation and
   separation,

with return product streams named. Free outdoor dump is **not** design
intent. Upset / emergency contingency paths may remain for AHJ relief
and life safety, but they are not the normal operating discharge.

Prefer:

| Class | Closure preference |
|---|---|
| Condensable / separable (H₂, CO₂, boil-off, NCG after oxidation) | **CRYO** condensation / separation |
| Toxic / acid / Cl₂ / Br₂ | **Dedicated scrubber + regenerable media** → wet/chem loop already on plant |

---

## 1. Purpose

Require scrub+regen or CRYO end states for former outdoor dumps; no free dump as design intent. The LOCK block above is normative.

## 2. Decision table (former open streams)

| # | Former open path | Required end state | Decision | Return product streams | Status |
|---|---|---|---|---|---|
| 1 | **S24 H₂ roof vent / SHAFT_H2** | CRYO hold + fuel consumers | Primary: H2_DRYER → **CRYO_H2** → BACKUP_GEN (S45) + FUEL_CELL (S49). Roof lip = **emergency contingency only** (NFPA 2). | S64 (normal to CRYO_H2); S45 / S49 consumers; S24 contingency | **Partial** — architecture closed; GEN/FC kW TBD |
| 2 | **Acid-gas stack** (post ALK_SCRUBBER) | Scrub + regen | DEMISTER → ALK_SCRUBBER → **ACID_POLISH_SCRUB** → liquor → CRU. Residual non-condensables after polish may keep a **permitted upset stack**; normal design is scrub+regen, not free dump. | S65 scrub feed; S66 liquor → CRU; SCRUBBER_TO_CRU | **Partial / Claimed** — PFD path named; study duty AQS-EQP-VENT-001 |
| 3 | **AFTERBURNER flue** (SHAFT_OIL) | CRYO condensation after destruction | Thermal oxidizer remains (required NCG/tar destruction). Flue products → **FLUE_CAP / CRYO** for CO₂ (+ condensables); heat still to Q1 jacket. Not free outdoor dump. | S67 flue → CRYO (extends S18); S68 condensate return | **Partial / Claimed** — PFD path named; study duty AQS-EQP-VENT-001 |
| 4 | **ZnBr2 Br₂ stack** | Scrub + regen (own liquor) | Existing PVDF Br₂ tower + **ZNBR2_BR2_REGEN** → bromide return to positive tank. Do **not** tee to CRU. Outdoor skid stays; outdoor **dump** does not. | S69 regen → ZnBr2 pos.; FLOW_BATTERY liquor path | **Partial / Claimed** — PFD path named |
| 5 | **CRYO_AHU (S56)** | CRYO condensation of condensables | Dedicated NFPA 2/55 room AHU retained. Condensable boil-off / purge → **CRYO_AHU_COND** → COLD_BOX / condensate return before any outdoor contingency. Never HAB return. | S70 condensable → CRYO; S56 residual contingency | **Partial** — PFD path named; study duty AQS-EQP-VENT-001 |
| 6 | **MET_AHU (S62)** | Dedicated scrub / baghouse | Aisle capture → **MET_SCRUB** (fume/mist) + baghouse fines path (S19 class). Regenerable liquor / fines → CSTR / OIL / HDR_ORG as chemistry allows. Never HAB return; not acid-gas as primary. | S71 AHU → scrub/BH; S72 returns | **Partial / Claimed** — PFD path named; study duty; liquor chem dual-path |

---

## 3. Stream detail

### 2.1 S24 / S64 — process H₂

| Item | Lock |
|---|---|
| Source | EW cathode hoods → HDR_H2 → arrestor → H2_DRYER |
| Normal end | **S64** → CRYO_H2 product hold |
| Consumers | S45 BACKUP_GEN; S49 FUEL_CELL (isolated manifolds + flame arrestors) |
| Contingency | S24 roof via SHAFT_H2 — trip / overpressure / MAQ relief only |
| Forbidden | Hab air; HDR_O2; intentional continuous roof dump |
| HSE | NFPA 2; MAQ AQS-HSE-001 §5; < 25% LFL capture |

Do not invent GEN / FC continuous kW this pass. Closing quantitative
balance = size CRYO_H2 + consumers so dryer holdup stays under MAQ and
S24 stays dark in normal operation.

### 2.2 Acid-gas — ALK + ACID_POLISH

| Item | Lock |
|---|---|
| Source | CSTR lid + EW / polish anode hoods → HDR_ACID_GAS |
| Train | DEMISTER → ALK_SCRUBBER (AQS-GAS-002 §1) → **ACID_POLISH_SCRUB** |
| Liquor | Lean BMED NaOH; blowdown / polish liquor → **CRU** (S66 / SCRUBBER_TO_CRU) |
| Gas residual | After polish: permitted **upset** stack only (AQS-GAS-003 height still applies for relief) |
| Forbidden | Free continuous outdoor dump as design; Br⁻ into this liquor; ammonia/organics in pack |

Why scrub not CRYO: Cl₂ / HCl / acid mist are toxic oxidizers — plant
already regenerates them through CRU → REGEN LEACH. Cold-box must not
see acid-gas (AQS-CRY-002 §2.2).

### 2.3 AFTERBURNER flue → CRYO

| Item | Lock |
|---|---|
| Source | HDR_OIL_VAPOR → QUENCH → AFTERBURNER (destruction required on M1) |
| Heat | Flue jackets Q1 / glass BURNOUT as today — atmospheres stay separate |
| Capture | **S67 / S18** flue-cap CO₂ (+ condensable water) → CRYO feed / CRYO_CO2 |
| Condensate | **S68** → S13 class / treat — not potable; not HDR_ACID_GAS |
| Forbidden | Raw flue into HDR_CO2 or HAB air; acid-gas header tee |

Destruction duty remains. Closure is of the **flue product**, not
elimination of the oxidizer.

### 2.4 ZnBr2 Br₂

| Item | Lock |
|---|---|
| Source | Positive-tank headspace, pump seals, stack vents |
| Train | Existing Br₂ packed tower (FLOW_BATTERY / AQS-GAS-002 §3) + **ZNBR2_BR2_REGEN** |
| Liquor | NaBr / NaOBr → hold → ORP check → **S69** return to ZnBr2 positive tank as Br⁻ |
| Forbidden | Tee to CRU; hot-hold to bromate; shared liquor with alkali tower |
| Outdoor | Skid remains outdoor (NFPA 855); continuous stack dump is **not** the end state |

### 2.5 CRYO_AHU (S56)

| Item | Lock |
|---|---|
| Source | CRYO fire-area room air + boil-off / purge contingency |
| Normal | Condensables → **CRYO_AHU_COND** → **S70** into COLD_BOX / condensate return |
| Residual | Non-condensable safe vent after knockout — contingency, not continuous product dump |
| Forbidden | Shared HAB / FARM return; acid-gas header |

NFPA 2/55 mechanical ventilation of the room remains mandatory. Closure
means condensable inventory returns to CRYO rather than outdoor dump.

### 2.6 MET_AHU (S62)

| Item | Lock |
|---|---|
| Source | MFG metal aisle (fume, oil mist, N₂ dilution, atomizer hood) |
| Train | **MET_SCRUB** (mist/fume) + baghouse branch for solids |
| Returns | **S72** — fines → CSTR 1 (S19 class); organic mist → OIL / HDR_ORG; aqueous scrub liquor → treat / SALT as chemistry allows |
| Forbidden | HAB / FARM return; HDR_ACID_GAS as primary; melt hot gas as Q4 flue |

Prefer dedicated scrub over CRYO: metal fume / oil mist fit existing
dust + oil patterns better than cold-box chemistry.

---

## 4. Claimed-but-incomplete — closure architecture (no invented kW)

| Loop | Architecture (document only) | Status | TBD |
|---|---|---|---|
| **H₂ → GEN / FC** | S64 → CRYO_H2 → S45 + S49; S24 contingency | Partial | Continuous kW; holdup kg under MAQ |
| **CO₂ capture** | S67 / S18 flue-cap → CRYO_CO2 → S04 FARM | Claimed | Capture efficiency; condenser duty |
| **WS_* forks** | S31–S38 forwards; spent → S10 / S39 → REGEN LEACH / OIL / HDR_ORG; HF ED regen on WS_HF_ED | Claimed | Synth vs seed; mass rates |
| **ORC electric** | GEO_ORC → S48 → Sol-Ark AC couple | Claimed stub | Rating after site survey — **do not invent kW** |

---

## 5. Equipment stubs (AQS-EQP-VENT-001 Rev B)

| Tag | Role | Status |
|---|---|---|
| ACID_POLISH_SCRUB | Post-alkali polish pack; lean NaOH | **Study estimate** — 1 500 m³/h train; pack/liquor in AQS-EQP-VENT-001 §2.1 |
| ACID_POLISH_REGEN / liquor to CRU | Regenerable media / blowdown → CRU | **Study estimate** — with SCRUBBER_TO_CRU |
| ZNBR2_BR2_REGEN | Hold + ORP + Br⁻ return to pos. tank | **Study estimate** — extends issued 200 mm / 5–10 L/min tower |
| CRYO_AHU_COND | Condensate knockout on S56 train | **Study estimate** — 6–12 ACH on 216 m³; ~2–5 kW KO |
| MET_SCRUB | Metal-aisle fume / mist scrubber | **Study estimate** — 540–900 m³/h LEV |
| MET_SCRUB_REGEN | Liquor / media regen toward S72 returns | **Study estimate** |
| FLUE_CAP (existing claim) | AFTERBURNER → CRYO CO₂ capture HX / KO | Claimed — capture η TBD; NCG 180 m³/h issued |

Study figures are **not** vendor nameplates. See AQS-EQP-VENT-001 §2.

---

## 6. HSE notes (summary)

1. No process-atmosphere duct through FB_* into HAB / FARM.
2. Acid / Br₂ scrubbers: fan **after** pack; separate liquors (AQS-GAS-002).
3. H₂: arrestor + dryer; never water-wash as primary treatment.
4. AFTERBURNER destruction stays; capture is downstream of oxidation.
5. Upset stacks (acid polish residual, S24 contingency, S56 residual)
   remain available for AHJ / life-safety — labeled contingency, not
   normal product discharge.
6. MAQ / PSM caps unchanged (AQS-HSE-001 §5).

---

## 7. Diagram / register hooks

| Doc | Update this pass |
|---|---|
| AQS-STR-001 | S64–S72; S24/S56/S62 endpoint language |
| AQS-MF-001 | Reclassify former Open → Closure required / Partial |
| AQS-AUD-001 | Remove “open by intent”; §6.3 rewrite |
| AQS-HSE-001 | Ventilation table → scrub/CRYO end states |
| AQS-CRY-002 / AQS-EQP-CRY-001 | S56 condensable return; S64 / S67 feeds |
| AQS-MFG-MET-001 / AQS-EQP-MFG-MET-001 | MET_SCRUB on S62 |
| AQS-GAS-002 | Polish + Br₂ regen end-state notes |
| PFDs | AQS-PFD-VENT-001 + cryo, mass_flow, metal_forming, znbr2, oil, wet, GEN/FC, GEO, fab reagents, building, hazard |

---

## 8. Remaining TBD

1. ~~Quantitative gas balance (Nm³/h) for polish / MET_SCRUB / flue-cap.~~
   **Study estimates issued** (AQS-EQP-VENT-001 Rev B). Vendor / AERMOD
   confirmation still open.
2. GEN / FC / ORC continuous kW — **study bounds** in AQS-EQP-GEN/FC/GEO
   and AQS-AUD-001 Rev D; vendor nameplates still TBD.
3. CRYO_H2 holdup kg under MAQ — **study buffer 5–10 kg** (AQS-AUD-001);
   MAQ cap unchanged (< 150 lb class).
4. MET_SCRUB liquor chemistry selection (aqueous vs oil-side) — dual-path
   study retained; final media selection TBD.
5. ~~FreeCAD solids for new scrub / KO tags~~ — stubs added Wave 1;
   plant.FCStd rebuild this pass.
6. Permit stack residual after polish — AHJ (unchanged).

---

## MeOH train vents (AQS-MeOH-001 — 2026-10-01)

| Stream / tag | End state | Note |
|---|---|---|
| MEOH_FC exhaust CO₂ (S82) | **Claimed** → CRYO_CO2 / FARM | No free outdoor dump |
| MEOH_TANK conservation vent | Flame arrester; LEL zone | NFPA 30; PC-11 |
| MEOH_SYNTH / COND vents | To scrub / Claimed carbon header | Prefer IEM soft path (low-P) |
| MeOH spill | Bonded sump → HDR_ORG | Never CATCH / potable |

Continuous kW / MeOH FC: AQS-REQ-KW-001. Relief sets: AQS-ASM-001 §5.1.
