# Vent / scrub / regenerator equipment stubs

Document number: AQS-EQP-VENT-001  
Revision: B  
Date: 2026-10-01  
Authority: AQS-VENT-001, AQS-GAS-002 / AQS-GAS-003, AQS-CRY-002,
AQS-MFG-MET-001, FLOW_BATTERY.md, AQS-STR-001 S64–S72, AQS-AUD-001,
`ELECTRICAL.md`, AQS-MF-001.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: scrub/regen + CRYO KO stubs for vent closure | 2026-09-28 |
| B | 1 | Study-estimate duties (formula + assumptions); FreeCAD stubs | 2026-10-01 |

Licence: CERN-OHL-S-2.0. Figures below marked **study estimate** show
formula and assumptions from issued plant throughputs. They are **not**
vendor nameplates. `SCALE_M = 1.0`. Wet feed design basis = **150 kg/d**.

## 1. Equipment tags

| Tag | Duty | Stream hooks | Status |
|---|---|---|---|
| ACID_POLISH_SCRUB | Post-ALK polish pack; lean BMED NaOH | S65 in; gas residual upset only | **Study estimate** §2.1 |
| ACID_POLISH_REGEN | Blowdown / media regen → CRU | S66 / SCRUBBER_TO_CRU | **Study estimate** §2.1 |
| ZNBR2_BR2_SCRUBBER | Existing Br₂ tower (FLOW_BATTERY) | Br₂ header | Issued massing |
| ZNBR2_BR2_REGEN | Hold + ORP + Br⁻ return to pos. tank | S69 | **Study estimate** §2.2 |
| CRYO_AHU | CRYO room NFPA 2/55 AHU | S56 residual | Issued (AQS-EQP-CRY-001) |
| CRYO_AHU_COND | Condensate knockout / condensable return | S70 → COLD_BOX | **Study estimate** §2.3 |
| MET_AHU | Dedicated MFG metal-aisle capture | S71 | Issued (AQS-EQP-MFG-MET-001) |
| MET_SCRUB | Fume / oil-mist scrub on MET_AHU train | S71 | **Study estimate** §2.4 |
| MET_SCRUB_REGEN | Liquor / media regen toward returns | S72 | **Study estimate** §2.4 |
| FLUE_CAP | AFTERBURNER → CRYO CO₂ / condensate KO | S67 / S18; S68 | Claimed + §2.5 study |

## 2. Study estimates (formula + assumptions)

### 2.1 ACID_POLISH_SCRUB / REGEN

**Source flow (issued):** AQS-GAS-003 HDR_ACID_GAS Q_design = **0.42 m³/s
(1 500 m³/h)** at 40–60 °C into the alkali pack. Polish sees the same
volumetric train after ALK (residual Cl₂ / HCl / wet air).

| Parameter | Study estimate | Formula / assumption |
|---|---|---|
| Gas Q to polish (S65) | **0.42 m³/s (1 500 m³/h)** | = HDR_ACID_GAS design (AQS-GAS-003 §1); not a new generation rate |
| Pack ID / height | **0.5–0.7 m ID; 0.6–1.0 m pack** | ~⅓–½ of ALK 1.8 m pack (AQS-GAS-003); film-area polish, not primary absorb |
| Added SP | **0.4–0.6 kPa** | Scale from ALK pack 1.2 kPa × (H_polish/H_alk) |
| Liquor recirculation | **50–80 L/min** | L/G ≈ 2–3 L/m³ × 1 500 m³/h → 50–75 L/min; lean 5–15 wt% NaOH (AQS-GAS-002 §1) |
| Blowdown → CRU (S66) | **50–200 L / transfer** | On ORP/level (AQS-GAS-002 §1.5); not continuous dump |
| NaOH stoichiometric order | **~2 mol NaOH / mol Cl₂; 1 mol / mol HCl** | AQS-GAS-002 §1.5; size BMED BASE bleed from EW/CRU Faraday + CSTR + 20 % CO₂/slip |

**Not a nameplate.** Vendor pack height / fan curve still require stamped
curves against actual duct takeoff (AQS-GAS-003 §3).

### 2.2 ZNBR2_BR2_REGEN

**Issued tower (FLOW_BATTERY):** 200 mm ID, 1.5 m pack, **5–10 L/min**
BMED NaOH recirculation.

| Parameter | Study estimate | Formula / assumption |
|---|---|---|
| Hold / regen volume | **50–150 L** | Tower sump + hold tank class; ORP settle before S69 |
| Liquor return (S69) | **Intermittent at 5–10 L/min** | Match tower recirculation when transferring Br⁻ to pos. tank |
| Headspace purge gas | **10–50 m³/h** class | Abuse/offgas (FLOW_BATTERY §Off-gas); **not** continuous Faraday Br₂ product |
| Chemistry | Br₂ + 2 NaOH → NaBr + NaOBr; return as Br⁻ | AQS-GAS-002 §3; never hot-hold to bromate; never CRU |

### 2.3 CRYO_AHU_COND

**Room envelope:** after layout relief CRYO = **9 × 6 × 4 m** → V =
**216 m³** (`params.py`; was 144 m³ at 6 × 6).

| Parameter | Study estimate | Formula / assumption |
|---|---|---|
| Room ACH | **6–12 ACH** | NFPA 2/55 mechanical ventilation practice class for H₂ fire area |
| AHU volumetric | **1 300–2 600 m³/h** | Q = ACH × V; V = 216 m³ |
| Condenser / KO duty | **~2–5 kW** | m·Cp·ΔT: Q_vol × 1.2 kg/m³ × 1.0 kJ/(kg·K) × 5–10 K / 3600; dehumidifier class, not Stirling |
| S70 condensable mass | **Method TBD** until CRYO holdup kg issued | Rate ≈ boil-off + purge condensable fraction × AHU flow; do not invent kg/h |

S56 residual after KO = contingency only (AQS-VENT-001).

### 2.4 MET_SCRUB / REGEN

| Parameter | Study estimate | Formula / assumption |
|---|---|---|
| Capture Q (S71) | **0.15–0.25 m³/s (540–900 m³/h)** | Local LEV for atomizer + mist hoods; ~⅓–½ of HDR_DUST 0.55 m³/s (AQS-GAS-003) |
| Train SP | **0.8–1.2 kPa** | Mist eliminator + light pack; fan after treatment |
| Liquor | Aqueous demist + oil coalescer | Fines → CSTR (S19/S72); organics → OIL / HDR_ORG; not HDR_ACID_GAS primary |
| Regen transfer (S72) | Intermittent on level/turbidity | No continuous sewer |

### 2.5 FLUE_CAP (AFTERBURNER → CRYO)

| Parameter | Study estimate | Formula / assumption |
|---|---|---|
| NCG into AFTERBURNER | **0.05 m³/s (180 m³/h)** | AQS-GAS-003 HDR_OIL_VAPOR NCG |
| Flue products after oxidation | Air + CO₂ + H₂O (destruction remains) | Capture efficiency **TBD** — Claimed architecture S67/S18 |
| Condensate S68 | Order of NCG moisture + oxidation water | Treat as S13 class; not potable |

## 3. Separation rules

1. Acid polish liquor → CRU only — no Br⁻, no organics, no NH₃.
2. Br₂ regen liquor → ZnBr2 positive tank only — never CRU.
3. CRYO_AHU_COND returns condensables to COLD_BOX — never HAB return.
4. MET_SCRUB fines → CSTR (S19 class); organic mist → OIL / HDR_ORG;
   do not tee metal fume into HDR_ACID_GAS as primary.
5. H₂ is not scrubbed wet (AQS-GAS-002 §5) — path is dryer → CRYO_H2.

## 4. FreeCAD

Stubs attached (Wave 1): `gas_handling.py` ACID_POLISH_*; `cryo.py`
CRYO_AHU_COND + FLUE_CAP; `mfg_shop.py` MET_SCRUB*; `electrical_yard.py`
ZNBR2_BR2_REGEN. Rebuild: `/usr/bin/freecadcmd models/freecad/build_plant.py`.

## 5. Regenerate related PFDs

```bash
# Optional — run only in a local working hub (not published):
python3 rebuild.py --group vent
python3 rebuild.py --group power
python3 rebuild.py --group cryo
python3 rebuild.py --group mfg
python3 rebuild.py --sync
```
