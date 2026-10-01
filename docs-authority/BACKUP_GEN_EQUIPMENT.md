# Backup generator equipment list

Document number: AQS-EQP-GEN-001  
Revision: B  
Date: 2026-10-01  
PFD: AQS-PFD-GEN-001 (`backup_gen_pfd.png`)  
Authority: AQS-PWR-001, `ELECTRICAL.md` (Sol-Ark GEN port),
`POWER/Power_System_overview.md`, GAS_SYSTEM exhaust-recapture intent,
AQS-STR-001 S45–S47, AQS-HSE-001 / AQS-MF-001 (H₂ MAQ).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: H₂ genset closes Sol-Ark GEN spare | 2026-09-27 |
| B | 1 | Study continuous / capacity bounds from Faraday + ELECTRICAL | 2026-10-01 |

Licence: CERN-OHL-S-2.0.

## 1. Locked unit tags

| Tag | Duty | Status |
|---|---|---|
| BACKUP_GEN | H₂-fueled AC genset → Sol-Ark GEN (S47) | Issued — **REQ-GEN-CONT ≈ 2.5 kW_e**; CAP ≤ 60 kW (AQS-REQ-KW-001; SI-GEN-01) |
| GEN_H2_BUFFER | Dried H₂ hold / manifold from CRYO_H2 / H2_DRYER (S45) | Issued — volume TBD |
| GEN_EXHAUST_HX | Exhaust cooler; condensate → grey/condensate class (S46) | Issued |
| GEN_SCRUB_BRANCH | NOx / residual gas to alkali scrubber path (not CRU Cl₂) | Claimed |
| GEN_ATS_NOTE | Sol-Ark internal transfer; external ATS remains utility bypass | Per ELECTRICAL.md |

## 2. Fuel decision

| Fuel | Role |
|---|---|
| **Plant H₂** (S05 / CRYO_H2 / S24 holdup) | **Primary** — closes GEN with on-site stream |
| Diesel / biodiesel | External contingency only — not named M1 duty |
| Biogas (S30) | Deferred — no gas-cleanup schedule |
| Methanol (root 06 DMFC) | Fuel-cell path — not this genset |

## 3. Electrical interconnect

| Port | Connection |
|---|---|
| Sol-Ark **GEN** | S47 from BACKUP_GEN (480 V 3φ); was spare |
| Sol-Ark **LOAD** | Unchanged → ATS S2 |
| Sol-Ark **GRID** | Unchanged bidirectional |
| RECT / MCC | Remain on plant main after ATS — genset does not feed DC bus directly |
| ZnBr2 / PV | Unchanged; genset is failover, not daily peak shaving |

**Study estimates** (not issued nameplates) — AQS-AUD-001 §10.2:

| Bound | Value | Basis |
|---|---|---|
| Continuous from process H₂ | **~2.3–2.7 kW_e** | 0.2 kg/h H₂ (AQS-GAS-003) × 33.3 kWh/kg × η 0.35–0.40 |
| Capacity class upper | **≤ ~50–60 kW** | Module peak / Sol-Ark continuous (`ELECTRICAL.md`); GEN 200 A class |
| Vendor continuous nameplate | **TBD** | Do not claim legacy campus kW |

Prefer GEN for AC failover; continuous process-H₂-limited duty is far
below capacity class.

## 4. Exhaust / gas handling

H₂ combustion in air yields primarily H₂O (+ N₂, O₂, NOx). Route:

1. Condensate → S13 / grey-condensate class (S46 liquid branch).
2. Gas residual → scrubber branch (S46 gas); **not** raw AFTERBURNER
   flue and **not** a substitute for S18 CO₂ capture.
3. Do not claim diesel-style CO₂ recapture as the primary H₂ path.

## 5. Separation rules

1. GEN fuel manifold ≠ HDR_H2 process capture without isolation +
   flame arrestors.
2. ZnBr2 Br₂ tower stays isolated (NFPA 855).
3. Genset outdoor pad / weather enclosure on L0 POWER yard beside
   SOL_ARK_60K.

## 6. Regenerate

```bash
cd Diagrams/aqueous_diagrams/pfd_scripts
python3 backup_gen_pfd.py
python3 electrical_sld.py
```
