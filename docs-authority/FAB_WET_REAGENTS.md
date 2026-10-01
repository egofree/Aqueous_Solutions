# Fab wet reagents — wet-line synth forks

Document number: AQS-EQP-FAB-RGN-001  
Revision: B  
Date: 2026-10-01  
PFD: AQS-PFD-FAB-RGN-001 (`fab_reagent_forks_pfd.png`); parent sector
AQS-PFD-FAB-001; wet factory AQS-PFD-WET-001

Authority: `03-silicon-wafer-fabrication.md`,
`MANUFACTURING/SILICON_FAB/Silicon_Fab_overview.md`, root `01-…` /
`02-…` (SEM TECH / BMED / CRU), AQS-STR-001, AQS-MF-001,
AQS-EQP-FAB-001, AQS-WTR-001, DEPENDENCIES.md (SEM-Tech / IEM link-only).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First issue; proposed WS_* synth fork IDs; stream S31–S39 | 2026-09-27 |
| B | 1 | Order-of-magnitude study rates (pilot wafer assumption) | 2026-10-01 |

Licence: CERN-OHL-S-2.0.

---

## 1. Purpose

Map every fab wet / dopant / slurry / solvent need to a **wet-line
source**. Where the source already exists (BMED acid/base, CRU,
metals crib), cite it. Where doc 03 / SILICON_FAB require chemistry
the wet line does not yet schedule, issue a **new synth fork** with a
stable module ID.

**NOTE**

IDs below are **issued names** for PFD / stream work. FreeCAD solids
for WS_* modules remain deferred. **Study** mass rates in §4.1 (labeled assumptions — not vendor schedules).

---

## 2. Existing wet-line sources (no new fork)

| Reagent / duty | Plant source | Stream | Evidence |
|---|---|---|---|
| HCl (RCA SC-2, pH, general acid) | `HCl_PRODUCT` / BMED | S09 | AQS-STR-001; wet_products.py |
| NaOH (pH, clean) | `NaOH_PRODUCT` / BMED | S09 | same |
| Oxidizing leach / chlorate (Salria class) | CRU + REGEN LEACH | (intra wet) | root 01; AQS-PFD-WET-001 |
| Pure Si / metals for charge & contacts | `PROD_METALS` / S08 crib | S08 | EW cascade |
| Fab UPW rinse | FAB_UPW_* train | S27 | AQS-EQP-FAB-UPW-001 |
| N₂ purge / cool | CRYO N2 | S03 | AQS-STR-001 |
| Spent etch / HF-bearing rinse return | ETCH_RETURN | S10 | closed to REGEN LEACH |
| O₂ for thermal ox | CRYO O2 path (life/process split) | TBD branch of S02 | doc 03 ox; do not tee hab air |

SEM-Tech / open IEM membrane designs support BMED / CEM fabrication
(DEPENDENCIES.md). Membrane code is **not** vendored into Aqueous.

---

## 3. New dedicated synth forks (proposed module IDs)

Mark **NEW** clearly. Location intent: L-1 wet / regen aisle or
adjacent util bay east of BMED — exact XY TBD (no FreeCAD this pass).

| Module ID | Product | Fab use | Synthesis / regen basis (evidence) | Status |
|---|---|---|---|---|
| **WS_HF_ED** | HF (aq) | Oxide strip, wet etch, fluoro-complex leach assist | Doc 03 §4.1–4.2, §5.2: membrane ED from recovered fluoride salts; >90% F recovery target | **NEW** — primary safety-critical fork |
| **WS_PEROX** | H₂O₂ | RCA SC-1 / SC-2 | SILICON_FAB RCA station (H₂O₂ + NH₄OH + HCl) | **NEW** — electrosynth / procure seed TBD |
| **WS_AMMONIA** | NH₃ / NH₄OH | RCA SC-1 | SILICON_FAB RCA | **NEW** — N₂/H₂ fix or farm-N path TBD |
| **WS_NITRIC** | HNO₃ | Wet etch mix (HF/HNO₃/…) | SILICON_FAB DopeEtch | **NEW** — NOx / electrochemical path TBD |
| **WS_PHOS** | H₃PO₄ | Wet etch / strip | SILICON_FAB etch list | **NEW** — P from CRU / nutrient cross TBD |
| **WS_KOH** | KOH (aq) | Alkaline clean; **solar texture** when branch opens | SILICON_FAB SolarCell texturing | **NEW** — distinct from NaOH PRODUCT |
| **WS_DOPE** | B / P / As concentrate | Diffusion / implant feed | Doc 03 §4.2, §5.3–5.4: CRU membrane migration >99% dopant recovery; BBr₃ / POCl₃ cabinets | **NEW** — polish/cabinet after CRU; gas cabinets on FAB_TOOL |
| **WS_SLURRY** | Colloidal silica CMP slurry | LAP_CMP | SILICON_FAB CMP; silicate from glass line / SiO₂ | **NEW** — make-up from GLASS silicate + S27 |
| **WS_SOLV** | IPA / acetone / NMP class | Litho strip / clean | Doc 03 §6.3 solvents | **NEW** — oil-line organics recover / make; flammable cabinet on L0 |

### 3.1 Seed / procurement vs full in-house

| Module | M1 seed | Closed-loop target |
|---|---|---|
| WS_HF_ED | Recovered fluoride inventory + ED stack | On-site HF from spent etch (doc 03) |
| WS_PEROX, WS_AMMONIA, WS_NITRIC, WS_PHOS, WS_KOH | Procure seed drums TBD | Electrosynth / CRU / nutrient cross when proven |
| WS_DOPE | Seed dopants + CRU concentrate | Membrane migration return |
| WS_SLURRY | Seed silica + glass silicate | Kerf SiO₂ + glass digest |
| WS_SOLV | Seed solvents | Oil-line fractionator / resin organics |

---

## 4. Qualitative stream IDs (S31–S39)

Issued on AQS-STR-001. Qualitative routes below; **study rates in §4.1**.

| ID | From | To | Ph | Carries |
|---|---|---|---|---|
| S31 | WS_HF_ED | WET_BENCH | L | HF (aq) |
| S32 | WS_PEROX | WET_BENCH | L | H₂O₂ |
| S33 | WS_AMMONIA | WET_BENCH | L | NH₄OH / NH₃ (aq) |
| S34 | WS_NITRIC + WS_PHOS | WET_BENCH | L | HNO₃ / H₃PO₄ etch suite |
| S35 | WS_KOH | WET_BENCH / solar texture stub | L | KOH |
| S36 | WS_DOPE / CRU polish | FAB_TOOL dopant cabinets | L/G | B/P/As concentrate; BBr₃ / POCl₃ class |
| S37 | WS_SLURRY | LAP_CMP / FAB_PREP | L | colloidal silica slurry |
| S38 | WS_SOLV | FAB_TOOL litho / strip | L | IPA / acetone / NMP class |
| S39 | LAP_CMP / WET_BENCH / FAB_TOOL | REGEN LEACH / OIL / HDR_ORG | L/S | spent slurry, solvent waste, photoresist sludge |

Forbidden: S26 potable into any WS_* make-up; sewer for S10/S31–S39
returns; Salria into life water.

---

## 4.1 Order-of-magnitude study rates

Wafer starts/day are **not issued**. Study assumption: **pilot 1–5
starts/d**. If starts remain TBD, method = bath volume × cycles/d ×
recipe concentration (SILICON_FAB / doc 03).

| Module | Stream | Study rate | Assumption |
|---|---|---|---|
| WS_HF_ED | S31 | **0.5–2.5 L/d** aq dilute | 0.1–0.5 L/wafer × 1–5 |
| WS_PEROX | S32 | **1–5 L/d** dilute | RCA SC-1/SC-2 |
| WS_AMMONIA | S33 | **1–5 L/d** dilute | RCA SC-1 |
| WS_NITRIC / WS_PHOS | S34 | **0.5–2 L/d** | Intermittent etch |
| WS_KOH | S35 | **< 0.5 L/d** | Low until solar branch |
| WS_DOPE | S36 | **grams/d** | CRU + cabinets |
| WS_SLURRY | S37 | **1–5 L/d** makeup | CMP; glass silicate + S27 |
| WS_SOLV | S38 | **0.5–2 L/d** | Litho/strip |
| Spent | S10 / S39 | Same order as forwards | Closed return |

**Not** vendor drum schedules. Seed vs electrosynth: §3.1.

## 5. RCA / etch recipe map (qualitative)

| Step | Chemistry | Sources |
|---|---|---|
| SC-1 | NH₄OH + H₂O₂ + UPW | S33 + S32 + S27 |
| SC-2 | HCl + H₂O₂ + UPW | S09 + S32 + S27 |
| Oxide strip | HF + UPW | S31 + S27 |
| Wet etch | HF / HNO₃ / H₃PO₄ class | S31 + S34 |
| CMP | silica slurry | S37 |
| Dopant | BBr₃ / POCl₃ / implant | S36 |
| Strip / clean | solvents | S38 |

---

## 6. HSE hooks

| Hazard | Control (from doc 03 / AQS-HSE-001) |
|---|---|
| HF | Enclosed baths, Ca-gluconate stations, vapor detect, S10 closed return |
| Dopant gases | Gas cabinets, dedicated exhaust, never into hab AHU |
| Solvents | Flammable cabinet, LEV to scrubber / oil vapor rules |
| KOH / acids | Secondary containment; no floor drain |

---

## 7. Regenerate

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 fab_reagent_forks_pfd.py
python3 wafer_fab_pfd.py
```
