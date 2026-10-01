# Scale-down → unreclaimed-resource map

Document number: AQS-SCALE-UR-001  
Revision: C  
Date: 2026-10-01  
Authority: AQS-SCALE-001 Rev C (`cad/SCALE_MODEL.md`); MVS framing
AQS-UI-001 Rev C §3.2; sector map AQS-SEC-001 Rev D; streams AQS-STR-001;
mass-flow AQS-MF-001; vent AQS-VENT-001; continuous kW AQS-REQ-KW-001;
planning gap audit AQS-MVS-GAP-001 (local planning artefacts, not published).  
Style: AQS-DOC-001.  
**Stage = encode policy.** Not a PE stamp. Not vendor nameplates.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | First map: SCALE_M / sector / module offs → stream_id unreclaimed | 2026-10-01 |
| B | 1 | MeOH / hydro SCALE_M notes; energy-mismatch study; VCD/litho/ORC study-unit streams | 2026-10-01 |
| C | 2 | Unit-level off→stream map; solver `UNIT_OFF_UNRECLAIMED` + `unit_enabled` (WP-A7) | 2026-10-01 |

Licence: **CERN-OHL-S-2.0**.

Canonical in this tree: `docs-authority/SCALE_DOWN_UNRECLAIMED.md`  
Solver encoding: `design_tool/aqs_design_tool/solver/scale_down_map.py`

---

## 1. Purpose

AQS-UI-001 §3.2 item 2: scaled-down configurations may omit capabilities
for practical reasons, but the model **shall** treat missing capabilities
as **incompletely closed loops / unreclaimed resource streams** — problems
to solve — **not** accepted pollution, emissions, or silent losses.

This document maps **which** `SCALE_M` derates, sector offs, and module
omissions reopen **which** `stream_id`s (and Sector Definitions) as gap
reason `unreclaimed_resource`. The P0 solver stub consumes the same map
and **does not invent mass closure**.

---

## 2. Framing (locked)

| Case | Gap reason | Meaning |
|---|---|---|
| Required ESS peer off (ZNBR2 / MEOH / PUMPED_HYDRO) | `unreclaimed_resource` | Incomplete closure; redundancy broken |
| Other `required_for_mvs_closure` sector off | `unreclaimed_resource` (+ `required_sector_disabled` summary) | Not MVS-equivalent |
| Optional sector off (listed in map) | `unreclaimed_resource` on tied streams + `sector_disabled` | Capability omitted → stream gap |
| `SCALE_M` &lt; 1.0 (below M1 baseline) | `unreclaimed_resource` | Derate breaks M1 cassette / life / water closure rules |
| Rate still null / open_boundary | `rate_incomplete_study` / `open_boundary` | Incomplete balance — not invented closure |

Study / stand-in rates remain labeled. No vendor nameplates invented.

---

## 3. Sector / module off → unreclaimed streams

| Sector off | Sector Definition | Stream IDs reopened as unreclaimed | Notes |
|---|---|---|---|
| **ZNBR2** | Energy Storage System (Electrochemical) | S69, S17 | Br₂ regen; DC storage path |
| **MEOH** | Energy Storage System (Electrochemical) | S73, S74, S76, S79 | Synth feeds + MEOH_FC DC (also process) |
| **PUMPED_HYDRO** | Energy Storage System (Gravity) | S22, S23 | Roof↔catch penstock |
| **WET** | Process (Mass transform) | S08, S05, S64 | Metals crib; Faraday H₂ generation |
| **OIL** | Process (Mass transform) | S11, S18 | Organics; afterburner→CRYO |
| **GLASS** | Process (Mass transform) | S08G | Silicate/ceramic goods export |
| **GAS** | Process (Mass transform) | S05, S64, S65, S24 | Dryer / polish / contingency |
| **FAB** | Process (Mass transform) | S03, S09, S10 | Wafer gases / etch; goods surplus |
| **MFG** | Process (Mass transform) | S08, S16 | Metals crib / scrap; goods surplus |
| **NUT** | Process (Mass transform) | S07, S12 | Dose / grey→dose |
| **FARM** | Life support / habitat | S14, S14X, S15, S11 | Food / O₂ / organics |
| **HAB** | Life support / habitat | S02, S12, S21 | Life O₂ / grey / potable draw |
| **CRYO** | Utility / header | S02–S04, S64, S45, S49, S50, S73, S74 | Product gases + H₂/CO₂ consumers |
| **WTR** | Utility / header | S01, S21–S23, S40 | UPW / roof–catch / terrace |
| **ELEC** | Utility / header | S17, S47, S51, S79 | Hub AC/DC injectors |
| **ELEC_PV** | Energy Production (Electrical) | S17, S20 | PV generation / load bus |
| **DOCK** | Export / dock | S14X, S08G | Surplus export boundaries |
| TRR (optional) | Utility / header | S40 | Clean terrace overflow |
| BACKUP_GEN (optional) | Energy Production (Combustion Engine) | S45, S47 | H₂→GEN AC |
| FUEL_CELL (optional) | Energy Production (Electrochemical) | S49, S50, S51 | PEM path |
| GEO (optional) | Utility / header | S06 | Q4 heat (ORC TBD) |

**Module-level (within sector):** disabling a required ESS or process
module that carries the only closure path for a listed stream **shall**
be treated the same as the parent sector off for that stream (sandbox
`unit_enabled` overrides → same `unreclaimed_resource` reason). P0/P1
consume **§3.1** unit map via `solver/scale_down_map.py` `UNIT_OFF_UNRECLAIMED`.

---


## 3.1 Unit-level off → unreclaimed streams (Rev C / WP-A7)

Sandbox: `SandboxOverrides.unit_enabled`; units carry `enabled` (default true).

| Unit off | Parent sector | Stream IDs unreclaimed | Notes |
|---|---|---|---|
| VCD_TRAIN | WTR | S25, S28, S29 | Potable Present blocked |
| REMIN | WTR | S26 | Potable remin |
| GEO_ORC | GEO | S48 | unknown kW |
| LITHO_STUB | FAB | S38 | Electronic self-copy Incomplete |
| SOLAR_PV_CELL | FAB | S03, S10 | Partial PV branch |
| HYDRO_SET | PUMPED_HYDRO | S22, S23 | ESS peer incomplete at unit |
| ZNBR2 | ZNBR2 | S69, S17 | |
| MEOH_FC | MEOH | S79 | |
| MEOH_SYNTH | MEOH | S73, S74, S76 | |
| MEOH_TANK | MEOH | S76 | |
| GROW_BED | FARM | S14, S14X, S15 | |
| ROOF_TANK | WTR | S21, S22, S40 | |
| CATCH_TANK | WTR | S21, S23 | |
| H2_DRYER | GAS | S64, S24 | |
| ALK_SCRUBBER | GAS | S65 | |
| WAFER_FAB | FAB | S03, S09, S10, S38 | |
| MFG_SHOP | MFG | S08, S16 | |
| BLOW_MOLD | MFG | (none in seed) | **Out-of-MVS-at-M1** — gap if claimed closed without unit |

## 4. SCALE_M derate rules that break closure

Baseline manufacturing MVS candidate: **`SCALE_M = 1.0`** (M1 cassette,
150 kg/d wet feed, `LIFE_LEVELS=1`, `BASEMENT_LEVELS=1`) — AQS-SCALE-001.

| Rule id | Trigger | Streams flagged | Sectors implicated | Rationale |
|---|---|---|---|---|
| `below_m1_scale` | `scale_m` &lt; 1.0 | S08, S05, S64, S14, S21 | WET, FARM, WTR | Below M1: wet-feed / Faraday / food / water inventory rules no longer close |
| `life_levels_collapse` | `scale_m` &lt; 1.0 | S14, S02, S12 | FARM, HAB | Discrete life plates cannot shrink below one HAB∥FARM pair without unreclaimed life streams |

**Scale-up** (SCALE_M ≥ 1, cassette M2/M3) remains governed by AQS-SCALE-001
§3–6 and does **not** by itself clear unreclaimed flags from disabled
required sectors.

Continuous derate of tank footprint ∝ plan (AQS-SCALE-001 §2) is allowed
at SCALE_M ≥ 1 without automatic unreclaimed flags; inventory still must
close S21–S23 when WTR + PUMPED_HYDRO are enabled.

---


## 4.1 MeOH / pumped-hydro SCALE_M notes (Rev B)

| Capability | SCALE_M formula in AQS-SCALE-001 §6? | Study rule (this map) | Unreclaimed if omitted |
|---|---|---|---|
| PV / ZnBr₂ / RECT | Yes — module counts | Unchanged | ELEC_PV / ZNBR2 streams |
| MeOH tank / FC bank | **No** discrete formula | AQS-ESS-001 §2.2: bank 1–4 × 0.5 kW cells; tank ≥3 d @ mid synth; synth tracks Faraday H₂ not bay stretch | S73, S74, S76, S79 |
| Pumped hydro energy | Geometry from roof/catch V×h (AQS-BLD-001 §3) | M1 ~9.8 kWh ideal ≪ ZnBr₂ 120 kWh — **study sizing asymmetry**; grow V×h for material hydro | S22, S23 |

Hydro vs ZnBr₂ mismatch is **documented study sizing**, not accepted silent loss.
Disabling PUMPED_HYDRO still emits `unreclaimed_resource` even when M1 energy is symbolic.

## 4.2 Study-unit omissions (VCD / remin / ORC / litho / solar)

| Study unit (AQS-EQP-STUDY-001) | Parent sector | Streams / paths flagged if capability claimed closed without unit | Label |
|---|---|---|---|
| VCD_TRAIN / REMIN | WTR | S25/S26/S28/S29 class; potable surplus claim | study / deferred |
| GEO_ORC | GEO | S48 | unknown kW |
| LITHO_STUB | FAB | electronic self-copy path | Missing → unreclaimed if scale-down omits fab copy |
| SOLAR_PV_CELL | FAB | PV_* branch | Partial |

P0 solver consumes sector-level **and** unit-level maps (Rev C). Blow-mold remains out-of-MVS-at-M1.

## 5. Solver behaviour (P0)

1. Load sector + unit maps from `solver/scale_down_map.py`.
2. On solve: for each disabled sector, emit `unreclaimed_resource` per stream.
3. For each `unit.enabled=false`, emit unit-map unreclaimed gaps (§3.1).
4. If `model.scale_m` &lt; 1.0, emit derate-rule gaps (§4).
5. Mass residual study polish may compute pool residuals; plant balance stays `incomplete`.
6. `mvs_equivalent` stays false while unreclaimed / rate-null / Partial self-copy.

---

## 6. Related documents

| Doc | ID | Role |
|---|---|---|
| SCALE_MODEL.md | AQS-SCALE-001 | Growth / discrete jumps |
| DESIGN_TOOL_ARCHITECTURE.md | AQS-UI-001 Rev C | Unreclaimed framing §3.2 |
| SECTOR_DEFINITIONS.md | AQS-SEC-001 Rev D | required_for_mvs_closure |
| Local planning (not published): MVS_GAP_AUDIT | AQS-MVS-GAP-001 | Gap list; this map closes §4.4 encode item |
| STREAM_REGISTER.md | AQS-STR-001 | Stable S## |
| AUTHORITY.md | AQS-AUTH-001 | Hub pointer |

---

## 7. Sync

```bash
cd models   # or local hub root
python3 rebuild.py --sync
```
