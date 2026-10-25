# Backup generator equipment list

Document number: AQS-EQP-GEN-001  
Revision: C  
Date: 2026-10-24  
Process flow diagram: AQS-PFD-GEN-001 (`backup_gen_pfd.png`)  
Basis: AQS-PWR-002; `ELECTRICAL.md` (AQS-ELC-001, Sol-Ark generator port); `POWER/Power_System_overview.md`; the exhaust-recapture intent of the gas system; AQS-STR-001 streams S45 to S47; AQS-HSE-001 and AQS-MF-001 (hydrogen maximum allowable quantity).  
Licence: CERN-OHL-S-2.0.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: H₂ genset closes Sol-Ark GEN spare | 2026-09-27 |
| B | 1 | Study continuous / capacity bounds from Faraday + ELECTRICAL | 2026-10-01 |
| C | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, scope and terms, captions; sections renumbered. Tags, ratings and rules unchanged. | 2026-10-24 |

## 1. Purpose and scope

The plant has a hydrogen-fuelled generator for AC failover. It connects to the generator port of the Sol-Ark inverter, which was otherwise spare. This page lists the units that make up the backup generator, its fuel, its electrical connection, its exhaust handling and the separation rules around it.

It does not set vendor nameplates. The ratings here are study bounds; continuous and capacity-class power are set in AQS-REQ-KW-001 §3.1.

## 2. Terms

- Continuous power: power that the plant's own process hydrogen can sustain (AQS-REQ-KW-001).
- Capacity class: the upper electrical envelope the generator port and module allow; it may exceed the continuous power when the generator runs on stored hydrogen.
- ATS: automatic transfer switch.
- M1: the first module of the plant at the baseline size.
- Stream numbers (S45 and so on) are those of the stream register AQS-STR-001. Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Unit tags

Table 3.1. Backup generator units

| Tag | Duty | Status |
|---|---|---|
| BACKUP_GEN | H₂-fueled AC genset → Sol-Ark GEN (S47) | Issued — **REQ-GEN-CONT ≈ 2.5 kW_e**; CAP ≤ 60 kW (AQS-REQ-KW-001; SI-GEN-01) |
| GEN_H2_BUFFER | Dried H₂ hold / manifold from CRYO_H2 / H2_DRYER (S45) | Issued — volume TBD |
| GEN_EXHAUST_HX | Exhaust cooler; condensate → grey/condensate class (S46) | Issued |
| GEN_SCRUB_BRANCH | NOx / residual gas to alkali scrubber path (not CRU Cl₂) | Claimed |
| GEN_ATS_NOTE | Sol-Ark internal transfer; external ATS remains utility bypass | Per ELECTRICAL.md |

## 4. Fuel

Plant hydrogen is the primary fuel (Table 4.1).

Table 4.1. Fuel options

| Fuel | Role |
|---|---|
| **Plant H₂** (S05 / CRYO_H2 / S24 holdup) | **Primary** — closes GEN with on-site stream |
| Diesel / biodiesel | External contingency only — not named M1 duty |
| Biogas (S30) | Deferred — no gas-cleanup schedule |
| Methanol (root 06 DMFC) | Fuel-cell path — not this genset |

## 5. Electrical connection

Table 5.1 gives the connection at each Sol-Ark port. The generator provides AC failover; it is not used for daily peak shaving.

Table 5.1. Sol-Ark port connections

| Port | Connection |
|---|---|
| Sol-Ark **GEN** | S47 from BACKUP_GEN (480 V 3φ); was spare |
| Sol-Ark **LOAD** | Unchanged → ATS S2 |
| Sol-Ark **GRID** | Unchanged bidirectional |
| RECT / MCC | Remain on plant main after ATS — genset does not feed DC bus directly |
| ZnBr2 / PV | Unchanged; genset is failover, not daily peak shaving |

Table 5.2 gives the study estimates (AQS-AUD-001 §10.2). They are not issued nameplates.

Table 5.2. Study power bounds

| Bound | Value | Basis |
|---|---|---|
| Continuous from process H₂ | **~2.3–2.7 kW_e** | 0.2 kg/h H₂ (AQS-GAS-003) × 33.3 kWh/kg × η 0.35–0.40 |
| Capacity class upper | **≤ ~50–60 kW** | Module peak / Sol-Ark continuous (`ELECTRICAL.md`); GEN 200 A class |
| Vendor continuous nameplate | **TBD** | Do not claim legacy campus kW |

The generator port is preferred for AC failover. The continuous duty that process hydrogen can sustain is far below the capacity class.

## 6. Exhaust and gas handling

Burning hydrogen in air produces mainly water, with nitrogen, oxygen and nitrogen oxides. The exhaust is routed as follows:

1. Condensate goes to S13, the grey and condensate class (the liquid branch of S46).
2. Residual gas goes to the scrubber branch (the gas branch of S46). It is not raw afterburner flue, and it does not replace the S18 carbon dioxide capture.
3. Diesel-style carbon dioxide recapture is not claimed as the primary path for hydrogen.

## 7. Separation rules

1. The generator fuel manifold is not connected to `HDR_H2` process capture without isolation and flame arrestors.
2. The bromine tower of the zinc-bromide battery stays isolated (NFPA 855).
3. The generator stands on an outdoor pad, or in a weather enclosure, in the level 0 power yard beside `SOL_ARK_60K`.

## 8. Rebuilding the drawings

Run from the repository root:

```bash
cd flow_graph/exporters/matplotlib
python3 backup_gen_pfd.py
python3 electrical_sld.py
```
