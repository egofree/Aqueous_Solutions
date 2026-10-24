# Continuous kW requirements — GEN / FC / PECVD / belt fire / CRYO / MFG

Document number: AQS-REQ-KW-001  
Revision: A  
Date: 2026-10-01  
Authority: AQS-SCALE-001 (`SCALE_M = 1.0`), AQS-AUD-001, AQS-ELC-001
(`ELECTRICAL.md`), AQS-GAS-003 Faraday check, AQS-FC-001 / AQS-PWR-002 /
AQS-CRY-002 / AQS-MFG-MET-001 / AQS-EQP-FAB-PV-001, AQS-MeOH-001.  
**Stage = define requirements.** Not a purchase order. Not stamped nameplates.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First-principles continuous kW + labeled stand-in products | 2026-10-01 |

Licence: CERN-OHL-S-2.0. Style: AQS-DOC-001.

---

## 1. Method

1. **First principles** from issued plant streams (H₂ Faraday, module bus,
   wet feed 150 kg/d, life/basement at `SCALE_M = 1.0`).
2. Where a commercial class is needed for calculation envelope, cite a
   **stand-in** (vendor / model / URL or datasheet). Stand-ins are **not**
   BOM and are **not** purchased equipment.
3. **Continuous kW** = duty expected under normal steady operation on
   process streams alone. **Capacity class** = upper electrical envelope
   allowed by Sol-Ark / ZnBr2 / module peak — may exceed continuous when
   fueled from holdup or contingency fuel.
4. Do **not** hard-code legacy campus narratives (280 / 336 / 400 /
   100–200 kW stacks) as M1 issued ratings.

---

## 2. Stand-in product table (labeled — not BOM)

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

---

## 3. Continuous kW requirements (SCALE_M = 1.0)

### 3.0 Shared H₂ pool (first principles)

| Quantity | Value | Basis |
|---|---|---|
| Process Ḣ₂ | **~0.2 kg/h ≈ 4.8 kg/d** | AQS-GAS-003 Faraday check at 150 kg/d wet feed |
| H₂ LHV | 33.3 kWh/kg | Standard |
| Chemical power | **~6.7 kW_th** | 0.2 × 33.3 |
| Consumers sharing pool | BACKUP_GEN (S45), PEM FC (S49), MeOH synth (S74), S24/S64 contingency | Cannot all draw Faraday max simultaneously |

**H₂ priority (requirements lock):** (1) MAQ / dryer holdup, (2) PEM FC continuous baseload,
(3) BACKUP_GEN islanded peaks from holdup, (4) MeOH synthesis when ZnBr2 SOC and
PV surplus allow (AQS-MeOH-001).

### 3.1 BACKUP_GEN (AQS-EQP-GEN-001)

| Requirement | Continuous | Capacity class | Basis |
|---|---|---|---|
| **REQ-GEN-CONT** | **2.5 kW_e** (range 2.3–2.7) | — | 6.7 kW_th × η_genset 0.35–0.40 on process H₂ alone |
| **REQ-GEN-CAP** | — | **≤ 60 kW_e** AC on Sol-Ark GEN | Module peak / Sol-Ark continuous; SI-GEN-01 PRP 80 kW is **upper commercial envelope**, not M1 continuous |
| Cont. fuel rate @ REQ-GEN-CONT | **~0.15 kg/h H₂** | — | Scale from SI-GEN-01 ~0.5 kg/h @ 11 kW → ~0.11–0.15 kg/h @ 2.5 kW |
| Diesel | Contingency only | — | Not continuous requirement |

### 3.2 PEM FUEL_CELL (AQS-FC-001 / AQS-EQP-FC-001)

| Requirement | Continuous | Capacity class | Basis |
|---|---|---|---|
| **REQ-FC-CONT** | **4 kW_dc** (range 3–5) | — | 6.7 kW_th × η_PEM 0.50–0.55; SI-FC-01 class matches |
| **REQ-FC-CAP** | — | **≤ 60 kW_dc** into BATT via FC_DCDC | ZnBr2 / Sol-Ark BATT window; SI-FC-02 shows commercial scalability — forbid legacy 100–200 kW claim |
| Cont. fuel @ REQ-FC-CONT | **~0.20 kg/h H₂** (full Faraday) | — | If GEN idle; split with GEN/MeOH per §3.0 |
| Oxidizer | CRYO_O2 (S50) | — | Not ambient air as named M1 stream |

### 3.3 CRYO Stirling (AQS-CRY-002 / AQS-EQP-CRY-001)

First principles: life O₂/N₂/CO₂ product rates are headcount-limited (study
4 persons — AQS-AUD-001 §11). Product gas liquefaction / 77–90 K sink is
dominated by cold-box heat leak + distillation reboil/condense, not by
detector-scale lift alone.

| Requirement | Continuous | Basis |
|---|---|---|
| **REQ-CRY-STIR-CONT** | **4 kW_e** (study band **2–8 kW_e**) | Fit module avg 11–19 kW / peak ~50 kW; bank of SI-CRY-01 units (CryoTel GT @ 0.24 kW_e each) or larger commercial Stirling — **unit cell** SI-CRY-01 proves COP class (~16 W lift / 240 W_e ≈ 6.7% at 77 K) |
| Legacy 15–25 kW cryo bus | **Superseded** | AQS-GAP-001 — folded into module bus |
| Dedicated cool S55 | Sized to Stirling + deep reject | Not Q4 life air |

**NOTE:** A single CryoTel GT is **instrumentation class**, not plant air-sep.
Requirement is a **bank / commercial cold-box** whose electric input lands in
the 2–8 kW_e study band; SI-CRY-01 is the labeled COP/stand-in cell.

### 3.4 PECVD / belt fire (AQS-EQP-FAB-PV-001)

Pilot wafer starts **1–5 /d** (AQS-AUD-001 §13) → tools are **intermittent**,
not 24 h continuous at industrial wph.

| Requirement | Continuous-equivalent | Peak intermittent | Basis |
|---|---|---|---|
| **REQ-PECVD-CONT** | **0.5–2 kW_e** avg | **5–15 kW_e** while running | RF + heaters + vacuum; SI-PECVD-01 industrial family derated to pilot; full-line 80–150 kW **forbidden** as M1 continuous |
| **REQ-BELT-CONT** | **0.5–2 kW_e** avg | **10–25 kW_e** while firing | SI-BELT-01 IR/belt class; heat reject → PV_HX_Q4 (S53 peer) |
| Combined FAB PV strip budget | **≤ 20 kW_e** coincident peak | — | Inside module ~50 kW peak; staged so CZ + PECVD + belt not all peak together |

### 3.5 MFG (polymer + metal forming)

| Requirement | Continuous | Peak | Basis |
|---|---|---|---|
| **REQ-MFG-POLY-CONT** | **1–3 kW_e** avg intermittent | **4 kW_e** per machine | SI-MFG-01 Precious Plastic motor class; campaign use |
| **REQ-MET-MELT-CONT** | **5–15 kW_e** study share | **≤ 25 kW_e** induction coil class | ELECTRICAL induction 0–25 kW; SI-MFG-02 35 kW = narrative peak only |
| **REQ-MFG-FORM-CONT** | **1–5 kW_e** draw/mill/atomize share | — | Throughput 0.2–2 kg/h (AQS-AUD-001 §10.6) |
| **REQ-MFG-TOTAL-CONT** | **~8–20 kW_e** plant share | **≤ 30 kW_e** coincident | Must remain inside module peak with wet/FAB |

### 3.6 MeOH IEM-FC (AQS-MeOH-001) — new continuous path

| Requirement | Continuous | Capacity class | Basis |
|---|---|---|---|
| **REQ-MEOH-FC-CONT** | **0.5–2 kW_dc** | **≤ 5 kW_dc** bank | SI-DMFC-01 @ 0.5 kW × 1–4 modules; MeOH from §4 sources; IEM membrane preferred (SI-IEM-01) |
| MeOH burn rate @ 1 kW | **~0.9 L/h ≈ 0.71 kg/h** | — | SI-DMFC-01 0.9 L/kWh; ρ_MeOH ≈ 0.79 kg/L |
| Electrical tie | Sol-Ark **BATT DC** via **MEOH_DCDC** (peer to FC_DCDC) | — | ≠ GEN port; ≠ RECT process DC |

PEM H₂ FC and MeOH IEM-FC **both exist** (AQS-FC-001 Rev B / AQS-MeOH-001).

---

## 4. Summary requirements board

| Tag | Continuous kW (requirement) | Capacity / peak | Stand-in IDs |
|---|---|---|---|
| BACKUP_GEN | **2.5 kW_e** | ≤ 60 kW_e | SI-GEN-01 |
| FUEL_CELL (PEM) | **4 kW_dc** | ≤ 60 kW_dc | SI-FC-01 / SI-FC-02 |
| MEOH_FC (IEM/DMFC) | **0.5–2 kW_dc** | ≤ 5 kW_dc | SI-DMFC-01 / SI-IEM-01 |
| STIRLING_COLD_HEAD bank | **4 kW_e** (2–8) | within module | SI-CRY-01 |
| PV_ARC (PECVD) | 0.5–2 avg / 5–15 peak | ≤ 15 peak | SI-PECVD-01 |
| PV_FIRE (belt) | 0.5–2 avg / 10–25 peak | ≤ 25 peak | SI-BELT-01 |
| MFG total | **8–20 kW_e** | ≤ 30 coincident | SI-MFG-01 / SI-MFG-02 |

All rows = **study requirements** for design. Vendor purchase nameplates remain
TBD until procurement. CERN-OHL-S-friendly cites in §2.

---

## 5. Sync

Canonical in this tree: `docs-authority/CONTINUOUS_KW_REQUIREMENTS.md`  
