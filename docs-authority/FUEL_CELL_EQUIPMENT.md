# Fuel-cell equipment list

Document number: AQS-EQP-FC-001  
Revision: E  
Date: 2026-10-24  
Process flow diagram: AQS-PFD-FC-001 (`fuel_cell_pfd.png`)  
Basis: AQS-FC-001; `ELECTRICAL.md` (AQS-ELC-001, Sol-Ark battery DC port, 160–700 V); `POWER/Power_System_overview.md` (older PEM narrative only); AQS-PWR-002 (the backup generator is not the fuel cell); AQS-STR-001 streams S49 to S53; AQS-HSE-001 and AQS-MF-001 (hydrogen maximum allowable quantity; closing S24); AQS-EQP-CRY-001; AQS-EQP-GEO-001 (Q4 header).  
Licence: CERN-OHL-S-2.0.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Basic issue: PEM stack skid on Sol-Ark BATT DC; heat → Q4 | 2026-09-28 |
| B | 1 | Study continuous bounds | 2026-10-01 |
| C | 1 | REQ-FC-CONT 4 kW_dc; MeOH peer; stand-in SI-FC-01 | 2026-10-01 |
| D | 1 | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose, scope and terms, captions; the study bounds given a section number. Tags, ratings and rules unchanged. | 2026-10-24 |
| E | 2 | Fuel stream corrected to S49 from CRYO_H2 (S05 is retired). | 2026-10-24 |

## 1. Purpose and scope

The plant has a PEM fuel cell that turns its own hydrogen and oxygen into DC power, low-grade heat and water. The DC goes to the battery port of the Sol-Ark inverter, the heat to the Q4 water header and the water to the condensate class. This page lists the fuel-cell units, their chemistry and fluids, the electrical connection, the heat and water routes, the separation rules and the interface with the cryogenic hydrogen store.

A methanol fuel cell runs alongside it as a separate path (AQS-MeOH-001, AQS-EQP-MEOH-001). Vendor nameplates are not set here; continuous and capacity-class power are in AQS-REQ-KW-001 §3.2.

## 2. Terms

- PEM: proton-exchange membrane, the fuel-cell type.
- Continuous power: power the plant's own process hydrogen can sustain. Capacity class: the upper envelope the battery port allows.
- Q4: the lowest-temperature water header, the only heat that enters life-support air.
- OEM: original equipment manufacturer, here the maker of the fuel-cell stack.
- HVDC, LVDC: high-voltage and low-voltage DC buses, named in older narratives and not used on M1.
- M1: the first module of the plant at the baseline size.

Stream numbers (S49 and so on) are those of AQS-STR-001. Other abbreviations are in `docs-authority/GLOSSARY.md`.

## 3. Unit tags

Table 3.1. Fuel-cell units

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

## 4. Chemistry and fluids

Table 4.1. Chemistry and fluids

| Item | Spec intent |
|---|---|
| Stack chemistry | **PEM** (proton-exchange membrane) |
| Fuel | Dried process H₂, S49 from CRYO_H2 |
| Oxidizer | CRYO_O2 (S02 class); air-breathing = deferred vendor option |
| Coolant / heat | Closed stack loop → FC_HX_Q4 → Q4 (< 80 °C into life air) |
| Product water | Liquid to condensate class; not potable without remin + UV |

The older power narrative's "100–200 kW modular stacks" is study narrative only (`POWER/Power_System_overview.md`). The continuous requirement on M1 is about 4 kW_dc (3–5) from process hydrogen (AQS-REQ-KW-001), with the Ballard FCgen-1020ACS class as stand-in (SI-FC-01). The capacity class is at most 60 kW_dc (SI-FC-02). The vendor nameplate is still to be decided.

## 5. Electrical connection

Table 5.1 gives the connection at each port.

Table 5.1. Electrical connection

| Port | Connection |
|---|---|
| Sol-Ark **BATT DC** (160–700 V) | S51 via FC_DCDC — **selected** generation bus |
| Sol-Ark **GEN** | Reserved for BACKUP_GEN (S47) — FC shall not use |
| RECT-EW / RECT-BMED / RECT-PK | Process loads only — FC shall not hard-tee |
| ZnBr2 | Peer on same BATT DC window; BMS / CAN discipline unchanged |
| HVDC / LVDC (legacy) | Not issued on M1 CAD — do not invent |

Study bounds, not issued nameplates: module peak about 50 kW; Sol-Ark continuous 60 kW; zinc-bromide battery about 60 kW class (`ELECTRICAL.md`).

## 6. Heat and water

1. Stack reject heat goes through `FC_HX_Q4` to Q4 only (S53).
2. Product water goes by S52 to S13, the grey and condensate class.
3. Purge gas goes to a safe vent or the scrubber branch: not to the habitation air handler, and not to the afterburner as its main sink.
4. Backup generator exhaust (S46) never passes through `FC_HX_Q4` or a life-support air handler.

## 7. Separation rules

1. The fuel-cell hydrogen manifold is not connected to `HDR_H2` process capture without isolation and flame arrestors (the same rule as `GEN_H2_BUFFER`).
2. S49 (fuel cell) and S45 (generator) may share the `CRYO_H2` source only through separately isolated branches.
3. `HDR_O2` and S50 shall never tee into `HDR_H2`.
4. The bromine tower of the zinc-bromide battery stays isolated (NFPA 855).
5. The fuel cell stands on an outdoor pad, or in a weather enclosure, in the level 0 power yard near `SOL_ARK_60K` and the zinc-bromide DC connection.

## 8. Interface with the cryogenic hydrogen store

`CRYO_H2` shall be sized for the backup generator, the fuel cell and the S24 vent contingency together. The cold-box internals (columns, sieves, expanders) are modelled in AQS-EQP-CRY-001; this page covers only the interface.

## 9. Study bounds

These are study estimates (AQS-AUD-001 §10.3, 2026-10-01), not vendor nameplates (Table 9.1).

Table 9.1. Study power bounds

| Bound | Value | Basis |
|---|---|---|
| Continuous from process H₂ | **~3–5 kW_dc** | 0.2 kg/h × 33.3 kWh/kg × η_PEM 0.50–0.55 |
| Capacity class upper | **≤ ~60 kW** BATT window | ZnBr2 / Sol-Ark; forbid legacy 100–200 kW |
| Shared H₂ with GEN | Split TBD | Faraday pool is one stream |
| Vendor nameplate | **TBD** | — |

The methanol fuel cell with ion-exchange membrane is a parallel path (AQS-MeOH-001, AQS-EQP-MEOH-001), not a deferred option.

## 10. Rebuilding the drawings

Run from the repository root:

```bash
cd flow_graph/exporters/matplotlib
python3 fuel_cell_pfd.py
python3 electrical_sld.py
```
