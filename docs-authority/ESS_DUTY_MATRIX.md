# ESS duty matrix — ZnBr₂ / MeOH / pumped hydro (study)

Document number: AQS-ESS-001  
Revision: B  
Date: 2026-10-01  
Authority: AQS-AUTH-001; AQS-UI-001 Rev C §3.2 (all three ESS peers);
AQS-SEC-001; AQS-REQ-KW-001; AQS-MeOH-001; AQS-BLD-001 §3; FLOW_BATTERY.md;
AQS-SCALE-001; AQS-SCALE-UR-001; planning AQS-MVS-GAP-001 §4.5.  
Style: AQS-DOC-002.  
**Stage = study duty sizing.** Not vendor nameplates. Not a PE stamp.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | Study duties for three ESS peers + H₂ contention note | 2026-10-01 |
| B | 1 | Hydro continuous kW incomplete; scale-up V×h path table; seed HYDRO_SET params | 2026-10-01 |

Licence: **CERN-OHL-S-2.0**.

Canonical in this tree: `docs-authority/ESS_DUTY_MATRIX.md`  
---

## 1. Purpose

Prove **catalogue presence** of ZNBR2 / MEOH / PUMPED_HYDRO is backed by
**study duty numbers** and an energy-equivalence note — especially
M1 hydro ≪ ZnBr₂ — without inventing nameplates.

---

## 2. Study duties (SCALE_M = 1.0)

| ESS peer | Presence | Study power | Study energy / fuel | Continuous electrical model | Gap |
|---|---|---|---|---|---|
| **ZNBR2** | Required + enabled | **60 kW** class (`ZNBR_MODULE_KW` × count) | **120 kWh** class (2 h × 60 kW) | Storage role; charge preferred per AQS-SCALE-001 §6 | Cycle life / BMS listing **study**; vendor nameplate **unknown** |
| **MEOH** | Required + enabled; process feed | **REQ-MEOH-FC-CONT 0.5–2 kW_dc** (mid **1.0**) | Synth **~2–8 kg/d** MeOH on surplus H₂ (AQS-MeOH-001); tank inventory study | MEOH_FC generation; MEOH_SYNTH load when priority allows | Dual-role vs process consumers **study**; bank stand-in ≠ purchase |
| **PUMPED_HYDRO** | Required + enabled | Turbine-pump **study** — no continuous kW nameplate at M1 | Ideal **E=ρVgh ≈ 263.6 kWh** @ 2,707 m³ / 35.73 m (AQS-BLD-014 water tower, Q-009); 210.9 kWh recoverable study | HYDRO_SET storage; charge/discharge electrical **incomplete** at P0 | Redundancy **symbolic** at M1 vs ZnBr₂ 120 kWh |

### 2.1 Hydro vs ZnBr₂ energy mismatch (study sizing)

| Store | Study energy | vs ZnBr₂ |
|---|---|---|
| ZnBr₂ M1 | 120 kWh | baseline electrical battery |
| Pumped hydro M1 | 263.6 kWh ideal / 210.9 kWh recoverable | **6 %** of ZnBr₂ 3,501 kWh; sized as the NFPA 111 backup of the night store (A-M-145, AQS-BLD-014) |

**Framing (locked):** hydro remains a **required ESS peer** for redundancy /
closure ontology (AQS-SEC-001 Rev D). At M1 the peer is **present but
energy-asymmetric**. Scale-up of roof/catch volume (AQS-BLD-001 table;
city cistern class) is the path to material hydro energy — do **not**
invent M1 kWh equality. Omitting hydro → `unreclaimed_resource` on S22/S23.

### 2.2 MeOH SCALE_M note

MeOH tank / FC bank have **no** discrete SCALE_M formula in AQS-SCALE-001 §6
(unlike PV_COUNT / ZNBR_COUNT). Study rule (this doc):

| Param | Study rule | Notes |
|---|---|---|
| MEOH_FC bank modules | ceil(REQ-MEOH-FC-CONT_max / 0.5 kW) at M1 → **1–4** | SI-DMFC-01 class stand-in |
| MEOH_TANK days | **≥ 3 d** at mid synth 5 kg/d → ≥ 15 kg inventory study | Not a vendor tank |
| Synth rate vs SCALE_M | Track wet-feed / Faraday H₂ (∝ cassette), not bay stretch | Surplus-H₂ only |

Encode in AQS-SCALE-001 / AQS-SCALE-UR-001 Rev bumps as notes — full module
count formula remains P1 if discrete jumps are preferred.

---


## 2.3 Hydro continuous kW + scale-up volume path (Rev B / WP-A4)

| Item | Study status |
|---|---|
| Continuous charge/discharge kW at M1 | **Incomplete** — no nameplate; HYDRO_SET `continuous_kw.value=null` |
| Energy store M1 | 263.6 kWh ideal / 210.9 recoverable vs ZnBr₂ 3,501 kWh (**6 %**), from AQS-BLD-014 (rev 2026-10-16, X-QA-02) |
| Scale-up path (AQS-BLD-001 §3) | Grow roof/catch **V×h** — not invent M1 kW equality |

| Volume (m³) | Head (m) | Ideal E=ρVgh (kWh) | Recoverable study | vs ZnBr₂ 120 kWh |
|---|---|---|---|---|
| **200** (M1) | 18 | **9.8** | ~7 | ~8% — symbolic redundancy |
| 1 000 | 18 | 49 | ~34 | ~41% |
| 5 000 (city cistern) | 25 | 340 | ~240 | ≫ ZnBr₂ class |

Seed encodes `scale_up_volume_path_m3` / `scale_up_energy_kwh_ideal` on
`HYDRO_SET.params`. Omitting PUMPED_HYDRO still → `unreclaimed_resource` on
S22/S23.

## 3. Shared H₂ pool contention

| Item | Study | Source |
|---|---|---|
| Faraday process H₂ | **~4.8 kg/d** (~0.2 kg/h; ~6.7 kW_th) | AQS-REQ-KW-001 §3.0 |
| Consumers | GEN (S45), PEM FC (S49), MeOH synth (S74), S24/S64 contingency | Cannot all take Faraday max |
| **Priority lock (study)** | (1) MAQ / dryer holdup (2) PEM FC baseload (3) BACKUP_GEN islanded peaks (4) MeOH synth when ZnBr₂ SOC + PV surplus allow | AQS-REQ-KW-001 §3.0; AQS-MeOH-001 |

Solver emits bottleneck `H2_pool_contended` when ≥2 of S45/S49/S74 present
(P0 stub). **Do not** invent simultaneous full-duty schedules.

---

## 4. Next measurement

1. Vendor / listing package for ZnBr₂ BMS (nameplate TBD).
2. Site survey before any GEO_ORC kW (out of ESS matrix; GEO study).
3. Project decision: whether M1 hydro energy asymmetry is accepted as
   study-complete for freeze evidence, or SCALE_M tank growth required
   before freeze language.

---

## 5. Related / sync

AQS-MVS-GAP-001 §4.5; AQS-BLD-001 §3; AQS-MeOH-001; AQS-REQ-KW-001;
AQS-SCALE-UR-001.

```bash
python3 -m flow_graph.param.regen
```
