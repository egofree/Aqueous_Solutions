# Methanol train — diverse MeOH sources + IEM fuel cell (gap fill)

Document number: AQS-MeOH-001  
Revision: A  
Date: 2026-10-01  
PFD: AQS-PFD-MEOH-001 (`meoh_train_pfd.png`)  
Equipment: AQS-EQP-MEOH-001  
Streams: AQS-STR-001 **S73–S82**  
Authority: root `06-energy-carbon-oxygen.md` (legacy MeOH narrative — **scaled**),
AQS-FC-001 (PEM retained), AQS-REQ-KW-001, AQS-HSE-001, AQS-VENT-001,
AQS-STR-001 / AQS-MF-001, DEPENDENCIES.md (SEM-Tech IEM), AQS-GAP-001 §4.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Close MeOH DMFC gap: dual sources + IEM-FC coexist with PEM | 2026-10-01 |

Licence: CERN-OHL-S-2.0. Style: AQS-DOC-001. `SCALE_M = 1.0`. No git.

---

## 1. Purpose

Fill the **MeOH DMFC gap** previously marked Deferred in AQS-FC-001 /
AQS-GAP-001. Issue requirements-grade architecture: **diverse MeOH
sources**, preferred **IEM-based fuel cell** (SEM-Tech lineage membranes),
integration with existing **PEM H₂ FC** (both remain in authority),
streams, PFD, equipment list, HSE, Q4 heat, and electrical tie.

**NOTE**

Root-06 figures (1,200 kg/d MeOH, 200–500 kW DMFC) are **legacy campus
narrative**. M1 requirements below are first-principles from the Faraday
H₂ pool and farm/hab waste rates at `SCALE_M = 1.0`.

---

## 2. Architecture decisions (locked)

| ID | Decision | Verdict |
|---|---|---|
| D1 | MeOH at M1 | **In scope** — gap filled (no longer deferred) |
| D2 | PEM H₂ FC | **Retained** — AQS-FC-001; plant H₂ + O₂ → BATT DC |
| D3 | MeOH fuel cell chemistry | **IEM-based DMFC preferred** (SEM-Tech / open IEM membranes — SI-IEM-01). Conventional DMFC (SI-DMFC-01) allowed as stand-in packaging |
| D4 | MeOH sources (diverse) | **(A)** Air/CO₂→MeOH via **IEM / catalytic** path; **(B)** **Fermentation** of farm/hab organics |
| D5 | Electrical | MeOH FC → **MEOH_DCDC** → Sol-Ark **BATT DC** (peer to FC_DCDC). Never GEN port / RECT hard-tee |
| D6 | Heat | Stack / condenser reject → **MEOH_HX_Q4** → Q4 (< 80 °C). Synth exotherm → process Q3 / oil preheat stub — **not** hab AHU flue |
| D7 | H₂ split | MeOH synth draws from CRYO_H₂ only when surplus vs PEM/GEN priority (AQS-REQ-KW-001 §3.0) |
| D8 | SCALE_M / git | Unchanged **1.0**; no git commit |

### 2.1 Why IEM-based FC (not PEM reformate-only)

- Matches plant wet-line / BMED membrane culture and **CERN-OHL-S** /
  CC0 open IEM work (DEPENDENCIES.md).
- Direct MeOH anode reaction avoids a separate reformer skid at M1.
- PEM H₂ path stays for high-η use of process H₂; MeOH path valorizes
  stored liquid carbon when H₂ gas holdup is constrained by MAQ.

---

## 3. MeOH sources (first principles + stand-ins)

### 3.1 Source A — Air / CO₂ → MeOH (IEM + catalytic)

```
Ambient air / CRYO_CO2 (S04) / S67 flue-cap CO₂
        │
        ▼
 MEOH_DAC_OR_CO2   (optional DAC; or take CRYO_CO2)
        │
        ▼
 MEOH_IEM_CELL     (electrochemical CO₂→MeOH intermediates on IEM)
   and/or
 MEOH_SYNTH        (CO₂ + 3 H₂ → CH₃OH + H₂O; catalytic; SI-MEOH-01/02 class)
        │
        ▼
 MEOH_COND / DIST  → MEOH_TANK
```

| Item | Study requirement | Basis |
|---|---|---|
| Stoichiometry | CO₂ + 3 H₂ → CH₃OH + H₂O | Olah methanol economy; SI-MEOH-01 |
| H₂ specific | **0.188 kg H₂ / kg MeOH** | 6/32 |
| CO₂ specific | **1.375 kg CO₂ / kg MeOH** | 44/32 |
| M1 synth rate (surplus H₂) | **~2–8 kg/d MeOH** | 10–40 % of 4.8 kg/d H₂ → MeOH when priority allows |
| Full-Faraday theoretical max | **~25 kg/d** | 4.8/0.188 — **not** a duty (starves PEM/GEN) |
| Stand-in P-T class | **220–280 °C, 50–100 bar** (catalytic) | Root-06 / SI-MEOH-01; **study MAWP** on AQS-ASM-001 |
| IEM electrochem path | Ambient–soft conditions preferred for M1 pilot cell | SI-IEM-01 membrane; SI-MEOH-02 Air2Fuel class for DAC+H₂ narrative |

**Stand-ins (not BOM):** SI-MEOH-01 CRI George Olah; SI-MEOH-02 Air Company
Air2Fuel; SI-IEM-01 open IEM repo.

### 3.2 Source B — Fermentation of farm / hab waste

| Feed | Study mass | Path |
|---|---|---|
| Black/grey organics (S12 / S30) | Order **~100–120 L/d** liquid + solids (AQS-AUD-001 §11) | Anaerobic digester already narrative (S30); **methylotrophic / wood-alcohol branch** or syngas→MeOH from digest gas — **Partial** |
| Farm trim / inedible biomass | **~0.2–1 kg/d** dry (fraction of 1.4–4.2 kg/d food) | Hydrolysis → ferment → MeOH or MeOH via biogas reform — study |
| **REQ-MEOH-FERM** | **0.1–1 kg/d MeOH** study | Conservative biogenic yield; does not replace Source A |

Tags: `MEOH_FERM_DIG`, `MEOH_FERM_STILL` (crude → polish into MEOH_TANK).

**CAUTION:** Biogas burner (S30) remains deferred as **power** fuel
(AQS-PWR-001). Fermentation MeOH is a **liquid product** path, not a
raw digester-gas genset.

### 3.3 Inventory

| Tag | Duty | Study size |
|---|---|---|
| MEOH_TANK | Atmospheric / low-P MeOH storage | **50–200 L** working (days of MEOH_FC at 0.5–2 kW) |
| MEOH_DAY_TANK | Fire-rated day use at FC skid | **20–50 L** |

---

## 4. MeOH fuel cell + electrical / Q4

```
MEOH_TANK ──S76──► MEOH_FC (IEM-DMFC) ──S79──► MEOH_DCDC ──► Sol-Ark BATT DC
                         │
                         ├──S80──► MEOH_HX_Q4 ──► Q4
                         ├──S81──► condensate / S13 class (product H₂O + CO₂ wet)
                         └──S82──► CO₂ return → CRYO_CO2 / FARM (Claimed)
```

| Requirement | Value | Doc |
|---|---|---|
| Continuous | **0.5–2 kW_dc** | AQS-REQ-KW-001 REQ-MEOH-FC-CONT |
| Membrane | Prefer SEM-Tech / open IEM (SI-IEM-01) | DEPENDENCIES.md |
| Stand-in module | EFOY Pro 12000 Duo 500 W (SI-DMFC-01) | Bank 1–4 |
| ≠ BACKUP_GEN | Yes | GEN port reserved |
| ≠ PEM hard-replace | Yes — both on BATT DC | AQS-FC-001 Rev B |

---

## 5. HSE (MeOH toxicity / fire)

1. **Toxicity:** MeOH — ingestion / inhalation / dermal hazard; OSHA /
   NIOSH exposure limits apply. SDS class storage; eye wash at day tank;
   no open containers in HAB.
2. **Fire:** Flash point ~11 °C; Class IB flammable liquid theme (NFPA 30).
   MEOH_TANK outdoors or fire-rated nook; bonding/grounding; no smoking /
   hot work without permit in MEOH zone.
3. **Separation:** MeOH liquid ≠ HDR_H2 dwell; ≠ Br₂ / ZnBr2; ≠ life AHU.
   Spill → bonded sump → HDR_ORG / treat (not CATCH potable).
4. **Detection:** LEL / VOC detection at MEOH_FC enclosure; isolate fuel
   solenoid on alarm.
5. **MAQ:** Liquid MeOH inventory kept modest (50–200 L) — far below
   large bulk MAQ; still track under AQS-HSE-001 chemical inventory.
6. **Vent:** MEOH_FC cathode exhaust / CO₂ → Claimed return (S82); no
   free outdoor dump (AQS-VENT-001).

---

## 6. Stream summary (S73–S82)

| ID | From → To | Carries |
|---|---|---|
| S73 | CRYO_CO2 / S67 / air → MEOH_DAC_OR_CO2 / MEOH_SYNTH | CO₂ feedstock |
| S74 | CRYO_H2 → MEOH_SYNTH | H₂ for catalytic / IEM synth |
| S75 | MEOH_SYNTH / MEOH_IEM_CELL → MEOH_COND | Crude MeOH + water |
| S76 | MEOH_TANK → MEOH_FC | Liquid MeOH fuel |
| S77 | MEOH_FERM_STILL → MEOH_TANK | Biogenic MeOH |
| S78 | Farm/hab organics → MEOH_FERM_DIG | Waste feed |
| S79 | MEOH_FC / MEOH_DCDC → Sol-Ark BATT DC | DC power |
| S80 | MEOH_HX_Q4 → Q4 | Heat < 80 °C |
| S81 | MEOH_FC / MEOH_COND → S13 class | Product / process water |
| S82 | MEOH_FC exhaust CO₂ → CRYO_CO2 / FARM | Claimed carbon return |

---

## 7. Relationship to PEM FC and GEN

```
CRYO_H2
  ├── S49 ──► FUEL_CELL (PEM) ── S51 ──► BATT DC
  ├── S45 ──► BACKUP_GEN ── S47 ──► GEN AC
  └── S74 ──► MEOH_SYNTH (surplus only)
MEOH_TANK ── S76 ──► MEOH_FC (IEM) ── S79 ──► BATT DC (peer)
```

---

## 7.1 SCALE_M / ESS duty pointer (2026-10-01)

No discrete MeOH tank/FC `SCALE_M` formula in AQS-SCALE-001 §6. Study sizing:
**AQS-ESS-001** / **AQS-SCALE-UR-001** Rev B (bank 1–4 × 0.5 kW; synth ∝ surplus H₂).
Hydro vs ZnBr₂ energy mismatch documented there — not MeOH-specific.

## 8. Rebuild / sync

```bash
cd Diagrams/aqueous_diagrams/pfd_scripts
python3 meoh_train_pfd.py
python3 fuel_cell_pfd.py
python3 electrical_sld.py
python3 mass_flow_pfd.py
python3 vent_closure_pfd.py
```

Share: `docs-authority/MEOH_TRAIN.md`, `process/MEOH_EQUIPMENT.md`,
`pfd/scripts/meoh_train_pfd.py`, `pfd/images/meoh_train_pfd.png`.
