# Fuel-cell equipment list

Document number: AQS-EQP-FC-001  
Revision: C  
Date: 2026-10-01  
PFD: AQS-PFD-FC-001 (`fuel_cell_pfd.png`)  
Authority: AQS-FC-001, `ELECTRICAL.md` (Sol-Ark BATT DC 160–700 V),
`POWER/Power_System_overview.md` (legacy PEM narrative only),
AQS-PWR-002 (BACKUP_GEN ≠ FC), AQS-STR-001 S49–S53,
AQS-HSE-001 / AQS-MF-001 (H₂ MAQ; S24 closing), AQS-EQP-CRY-001,
AQS-EQP-GEO-001 (Q4 peer).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: PEM stack skid on Sol-Ark BATT DC; heat → Q4 | 2026-09-28 |
| B | 1 | Study continuous bounds | 2026-10-01 |
| C | 1 | REQ-FC-CONT 4 kW_dc; MeOH peer; stand-in SI-FC-01 | 2026-10-01 |

Licence: CERN-OHL-S-2.0.

## 1. Locked unit tags

| Tag | Duty | Status |
|---|---|---|
| FUEL_CELL | PEM stack module(s); plant H₂ + O₂ → DC + heat + product water | Issued — **REQ-FC-CONT ≈ 4 kW_dc** (AQS-REQ-KW-001; SI-FC-01) |
| FC_H2_MANIFOLD | Dried H₂ from CRYO_H2 / H2_DRYER (S49); isolation + flame arrestor | Issued — volume TBD |
| FC_O2_MANIFOLD | O₂ from CRYO_O2 (S50); oxidizer separation from H₂ | Issued |
| FC_AIR_BLOWER | Cathode blower / recirculation (vendor option) | Stub — if air-breathing later |
| FC_HUMIDIFIER | Anode / cathode humidification as required by stack OEM | Issued — duty TBD |
| FC_DCDC | DC/DC into Sol-Ark BATT DC window (S51) | Issued — rating TBD |
| FC_HX_Q4 | Low-grade heat → Q4 water (S53); same header as GEO_HP / S44 / S06 | Issued |
| FC_PURGE | Anode / cathode purge to safe vent / scrub branch | Issued — MAQ |
| FC_PRODUCT_H2O | Product-water knockout → condensate / S13 class (S52) | Issued |
| FC_COMP_H2 | Optional H₂ boost compressor if CRYO_H2 pressure insufficient | Stub — pressure TBD |

## 2. Chemistry and media

| Item | Spec intent |
|---|---|
| Stack chemistry | **PEM** (proton-exchange membrane) |
| Fuel | Dried process H₂ (S05 / CRYO_H2 / S24 holdup) |
| Oxidizer | CRYO_O2 (S02 class); air-breathing = deferred vendor option |
| Coolant / heat | Closed stack loop → FC_HX_Q4 → Q4 (< 80 °C into life air) |
| Product water | Liquid to condensate class; not potable without remin + UV |

**NOTE**

Legacy POWER claim “100–200 kW modular stacks” is **study narrative
only** (`POWER/Power_System_overview.md`). M1 continuous **requirement** =
**≈ 4 kW_dc** (3–5) from process H₂ — AQS-REQ-KW-001; stand-in
Ballard FCgen-1020ACS class (SI-FC-01). Capacity class ≤ 60 kW_dc
(SI-FC-02). Vendor purchase nameplate still TBD.

## 3. Electrical interconnect

| Port | Connection |
|---|---|
| Sol-Ark **BATT DC** (160–700 V) | S51 via FC_DCDC — **selected** generation bus |
| Sol-Ark **GEN** | Reserved for BACKUP_GEN (S47) — FC shall not use |
| RECT-EW / BMED / PK | Process loads only — FC shall not hard-tee |
| ZnBr2 | Peer on same BATT DC window; BMS / CAN discipline unchanged |
| HVDC / LVDC (legacy) | Not issued on M1 CAD — do not invent |

Study bounds (not issued nameplates): module peak ~50 kW;
Sol-Ark continuous 60 kW; ZnBr2 ~60 kW class (`ELECTRICAL.md`).

## 4. Heat and water

1. Stack reject heat → FC_HX_Q4 → Q4 only (S53).
2. Product water → S52 → S13 / grey-condensate class.
3. Purge gas → safe vent or scrubber branch; **not** hab AHU;
   **not** AFTERBURNER as primary sink.
4. Never route BACKUP_GEN exhaust (S46) through FC_HX_Q4 or life AHU.

## 5. Separation rules

1. FC H₂ manifold ≠ HDR_H2 process capture without isolation +
   flame arrestors (same rule as GEN_H2_BUFFER).
2. S49 (FC) and S45 (GEN) may share CRYO_H2 source only through
   separately isolated branches.
3. HDR_O2 / S50 shall never tee HDR_H2.
4. ZnBr2 Br₂ tower stays isolated (NFPA 855).
5. FC outdoor pad / weather enclosure on L0 POWER yard near
   SOL_ARK_60K / ZnBr2 DC couple.

## 6. CRYO_H2 interface

CRYO_H2 shall be sized for **BACKUP_GEN + FUEL_CELL + S24 vent
contingency**. Cold-box internals (columns, sieves, expanders) remain
AQS-EQP-CRY-001 next-pass solids — interface only this pass.

## 7. Regenerate

```bash
cd flow_graph/exporters/matplotlib  # or local hub pfd_scripts/
python3 fuel_cell_pfd.py
python3 electrical_sld.py
```


## Study continuous / capacity bounds (2026-10-01)

**Study estimates** (AQS-AUD-001 §10.3) — not vendor nameplates:

| Bound | Value | Basis |
|---|---|---|
| Continuous from process H₂ | **~3–5 kW_dc** | 0.2 kg/h × 33.3 kWh/kg × η_PEM 0.50–0.55 |
| Capacity class upper | **≤ ~60 kW** BATT window | ZnBr2 / Sol-Ark; forbid legacy 100–200 kW |
| Shared H₂ with GEN | Split TBD | Faraday pool is one stream |
| Vendor nameplate | **TBD** | — |

MeOH IEM-FC is a **peer** path (AQS-MeOH-001 / AQS-EQP-MEOH-001) — not deferred.
